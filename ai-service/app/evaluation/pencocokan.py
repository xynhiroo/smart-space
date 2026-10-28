"""Pencocokan label ground truth dengan hasil klasifikasi sistem pakar (SS1-12).

Keluarannya dua urutan label sejajar (benar, prediksi) untuk
``hitung_evaluasi`` di ``metrik.py``.

Aturan pencocokan:
1. Sesi terjadwal (schedule_id terisi): dicocokkan lewat kunci
   (tanggal, room_id, schedule_id). Kunci harus unik di tiap sisi.
2. Episode di luar jadwal (schedule_id kosong): dicocokkan lewat irisan waktu
   pada (tanggal, room_id) yang sama. Satu episode ground truth menjadi SATU
   pasangan, walau runner memecahnya jadi beberapa baris. Pasangan itu benar
   bila ada baris runner beririsan yang statusnya sama dengan label benar.
3. Baris tanpa pasangan tidak dibuang:
   - ground truth tanpa pasangan di runner -> prediksi TIDAK_TERDETEKSI
   - runner tanpa pasangan di ground truth -> label benar BUKAN_EPISODE
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.evaluation.metrik import STATUS

TIDAK_TERDETEKSI = "tidak_terdeteksi"
BUKAN_EPISODE = "bukan_episode"
KELAS_DENGAN_TIDAK_COCOK = tuple(STATUS) + (TIDAK_TERDETEKSI, BUKAN_EPISODE)


@dataclass(frozen=True)
class BarisLabel:
    """Satu baris label, dari ground truth maupun dari runner."""

    tanggal: date
    room_id: int
    schedule_id: int | None
    waktu_mulai: time
    waktu_selesai: time
    status: str


@dataclass(frozen=True)
class Pasangan:
    """Satu pasangan hasil pencocokan."""

    tanggal: date
    room_id: int
    schedule_id: int | None
    waktu_mulai: time
    benar: str
    prediksi: str


@dataclass(frozen=True)
class HasilPencocokan:
    pasangan: tuple[Pasangan, ...]
    benar: tuple[str, ...]
    prediksi: tuple[str, ...]
    tanpa_prediksi: int  # baris ground truth yang tidak ditemukan runner
    tanpa_label: int  # baris runner yang tidak ada di ground truth


def _ke_tanggal(nilai: Any) -> date:
    if isinstance(nilai, datetime):
        return nilai.date()
    if isinstance(nilai, date):
        return nilai
    return date.fromisoformat(str(nilai))


def _ke_waktu(nilai: Any) -> time:
    if isinstance(nilai, time):
        return nilai
    if isinstance(nilai, timedelta):  # pymysql mengembalikan TIME sebagai timedelta
        return (datetime.min + nilai).time()
    return time.fromisoformat(str(nilai))


def _ke_schedule_id(nilai: Any) -> int | None:
    if nilai is None or str(nilai).strip() == "":
        return None
    return int(nilai)


def _baris(isi: Mapping[str, Any], kolom_status: str) -> BarisLabel:
    return BarisLabel(
        tanggal=_ke_tanggal(isi["tanggal"]),
        room_id=int(isi["room_id"]),
        schedule_id=_ke_schedule_id(isi.get("schedule_id")),
        waktu_mulai=_ke_waktu(isi["waktu_mulai"]),
        waktu_selesai=_ke_waktu(isi["waktu_selesai"]),
        status=str(isi[kolom_status]),
    )


def muat_ground_truth_csv(path: Path | str) -> list[BarisLabel]:
    """Membaca CSV ground truth (kolom status_benar)."""
    with open(path, newline="", encoding="utf-8") as f:
        return [_baris(r, "status_benar") for r in csv.DictReader(f)]


def baris_dari_hasil_klasifikasi(rows: Iterable[Mapping[str, Any]]) -> list[BarisLabel]:
    """Mengubah baris classification_results (kolom status) menjadi BarisLabel."""
    return [_baris(r, "status") for r in rows]


def _indeks_sesi(baris: Iterable[BarisLabel], sumber: str) -> dict[tuple, BarisLabel]:
    indeks: dict[tuple, BarisLabel] = {}
    for b in baris:
        if b.schedule_id is None:
            continue
        kunci = (b.tanggal, b.room_id, b.schedule_id)
        if kunci in indeks:
            raise ValueError(f"Kunci sesi ganda di {sumber}: {kunci}")
        indeks[kunci] = b
    return indeks


def _beririsan(a: BarisLabel, b: BarisLabel) -> bool:
    return a.waktu_mulai < b.waktu_selesai and b.waktu_mulai < a.waktu_selesai


def _kelompok_episode(baris: Iterable[BarisLabel]) -> dict[tuple, list[BarisLabel]]:
    kelompok: dict[tuple, list[BarisLabel]] = defaultdict(list)
    for b in baris:
        if b.schedule_id is None:
            kelompok[(b.tanggal, b.room_id)].append(b)
    for daftar in kelompok.values():
        daftar.sort(key=lambda x: (x.waktu_mulai, x.waktu_selesai))
    return kelompok


def cocokkan(
    ground_truth: Iterable[BarisLabel], hasil: Iterable[BarisLabel]
) -> HasilPencocokan:
    """Mencocokkan ground truth dengan hasil runner (opsi A)."""
    ground_truth = list(ground_truth)
    hasil = list(hasil)
    pasangan: list[Pasangan] = []
    tanpa_prediksi = 0
    tanpa_label = 0

    # 1. Sesi terjadwal.
    gt_sesi = _indeks_sesi(ground_truth, "ground truth")
    hs_sesi = _indeks_sesi(hasil, "hasil klasifikasi")
    for kunci in sorted(set(gt_sesi) | set(hs_sesi)):
        g = gt_sesi.get(kunci)
        h = hs_sesi.get(kunci)
        tanggal, room_id, schedule_id = kunci
        if g is not None and h is not None:
            pasangan.append(
                Pasangan(tanggal, room_id, schedule_id, g.waktu_mulai, g.status, h.status)
            )
        elif g is not None:
            tanpa_prediksi += 1
            pasangan.append(
                Pasangan(tanggal, room_id, schedule_id, g.waktu_mulai, g.status, TIDAK_TERDETEKSI)
            )
        else:
            tanpa_label += 1
            pasangan.append(
                Pasangan(tanggal, room_id, schedule_id, h.waktu_mulai, BUKAN_EPISODE, h.status)
            )

    # 2. Episode di luar jadwal: irisan waktu, satu episode ground truth = satu pasangan.
    gt_ep = _kelompok_episode(ground_truth)
    hs_ep = _kelompok_episode(hasil)
    for kunci in sorted(set(gt_ep) | set(hs_ep)):
        tanggal, room_id = kunci
        daftar_hs = hs_ep.get(kunci, [])
        terpakai: set[int] = set()
        for g in gt_ep.get(kunci, []):
            irisan = [i for i, h in enumerate(daftar_hs) if _beririsan(g, h)]
            if not irisan:
                tanpa_prediksi += 1
                prediksi = TIDAK_TERDETEKSI
            else:
                terpakai.update(irisan)
                sama = [i for i in irisan if daftar_hs[i].status == g.status]
                prediksi = daftar_hs[(sama or irisan)[0]].status
            pasangan.append(
                Pasangan(tanggal, room_id, None, g.waktu_mulai, g.status, prediksi)
            )
        for i, h in enumerate(daftar_hs):
            if i not in terpakai:
                tanpa_label += 1
                pasangan.append(
                    Pasangan(tanggal, room_id, None, h.waktu_mulai, BUKAN_EPISODE, h.status)
                )

    pasangan.sort(
        key=lambda p: (
            p.tanggal,
            p.room_id,
            p.waktu_mulai,
            -1 if p.schedule_id is None else p.schedule_id,
        )
    )
    return HasilPencocokan(
        pasangan=tuple(pasangan),
        benar=tuple(p.benar for p in pasangan),
        prediksi=tuple(p.prediksi for p in pasangan),
        tanpa_prediksi=tanpa_prediksi,
        tanpa_label=tanpa_label,
    )
