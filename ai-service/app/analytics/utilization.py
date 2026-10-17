"""Utilisasi dan statistik efisiensi ruangan (SS1-10).

Modul ini hanya berisi perhitungan murni: tidak membaca database dan tidak
menyimpan ambang apa pun. Ambang kategori dikirim lewat argumen, nilainya
dibaca dari tabel threshold_settings oleh pemanggil.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Sequence

KATEGORI_RENDAH = "rendah"
KATEGORI_SEDANG = "sedang"
KATEGORI_TINGGI = "tinggi"


@dataclass(frozen=True)
class Sesi:
    """Satu sesi pada satu tanggal, dalam satuan menit."""

    room_id: int
    tanggal: date
    menit_terjadwal: int
    menit_terpakai: int


@dataclass(frozen=True)
class StatistikRuang:
    """Ringkasan utilisasi satu ruang pada satu periode."""

    room_id: int
    menit_terjadwal: int
    menit_terpakai: int
    selisih_menit: int
    utilisasi_pct: float | None
    kategori: str | None
    rata_rata_harian_pct: float | None
    min_harian_pct: float | None
    max_harian_pct: float | None


@dataclass(frozen=True)
class KorelasiRuang:
    """Korelasi menit terjadwal vs menit terpakai antar ruang."""

    jumlah_ruang: int
    pearson: float | None
    spearman: float | None


def hitung_utilisasi_pct(menit_terjadwal: int, menit_terpakai: int) -> float | None:
    """Utilisasi (%) = menit terpakai / menit terjadwal x 100.

    Mengembalikan None bila menit terjadwal nol, karena utilisasi tidak
    terdefinisi (sesuai kolom utilisasi_pct yang boleh kosong).
    """
    if menit_terjadwal < 0 or menit_terpakai < 0:
        raise ValueError("Menit tidak boleh negatif.")
    if menit_terjadwal == 0:
        return None
    if menit_terpakai > menit_terjadwal:
        raise ValueError("Menit terpakai tidak boleh melebihi menit terjadwal.")
    return menit_terpakai * 100 / menit_terjadwal


def tentukan_kategori(
    utilisasi_pct: float | None, batas_rendah: float, batas_sedang: float
) -> str | None:
    """Kategori utilisasi: <= batas_rendah rendah, <= batas_sedang sedang, selebihnya tinggi.

    Memakai batas atas inklusif supaya tidak ada celah desimal di antara
    rentang (misalnya 40,5 tetap terklasifikasi).
    """
    if utilisasi_pct is None:
        return None
    if not 0 <= utilisasi_pct <= 100:
        raise ValueError("Utilisasi harus berada di antara 0 dan 100.")
    if batas_rendah >= batas_sedang:
        raise ValueError("batas_rendah harus lebih kecil dari batas_sedang.")
    if utilisasi_pct <= batas_rendah:
        return KATEGORI_RENDAH
    if utilisasi_pct <= batas_sedang:
        return KATEGORI_SEDANG
    return KATEGORI_TINGGI


def hitung_statistik_ruang(
    sesi: Iterable[Sesi],
    tanggal_mulai: date,
    tanggal_selesai: date,
    batas_rendah: float,
    batas_sedang: float,
    daftar_room_id: Iterable[int] = (),
) -> dict[int, StatistikRuang]:
    """Statistik per ruang untuk rentang tanggal (inklusif).

    - Utilisasi periode = total menit terpakai / total menit terjadwal.
    - Baris dengan menit_terjadwal 0 (pemakaian di luar jadwal) tidak ikut.
    - Rata-rata, minimum, dan maksimum dihitung dari utilisasi harian
      (hanya hari yang punya jadwal).
    - Ruang di daftar_room_id selalu muncul, walau tanpa jadwal.
    """
    if tanggal_mulai > tanggal_selesai:
        raise ValueError("tanggal_mulai tidak boleh setelah tanggal_selesai.")

    dalam_periode = [s for s in sesi if tanggal_mulai <= s.tanggal <= tanggal_selesai]
    ruang_ids = set(daftar_room_id) | {s.room_id for s in dalam_periode}

    per_ruang_hari: dict[int, dict[date, list[int]]] = {
        room_id: defaultdict(lambda: [0, 0]) for room_id in ruang_ids
    }
    for s in dalam_periode:
        hitung_utilisasi_pct(s.menit_terjadwal, s.menit_terpakai)  # validasi data
        if s.menit_terjadwal == 0:
            continue
        total = per_ruang_hari[s.room_id][s.tanggal]
        total[0] += s.menit_terjadwal
        total[1] += s.menit_terpakai

    hasil: dict[int, StatistikRuang] = {}
    for room_id in sorted(ruang_ids):
        hari = per_ruang_hari[room_id]
        terjadwal = sum(t for t, _ in hari.values())
        terpakai = sum(p for _, p in hari.values())
        utilisasi = hitung_utilisasi_pct(terjadwal, terpakai)
        harian = [hitung_utilisasi_pct(t, p) for t, p in hari.values()]
        hasil[room_id] = StatistikRuang(
            room_id=room_id,
            menit_terjadwal=terjadwal,
            menit_terpakai=terpakai,
            selisih_menit=terjadwal - terpakai,
            utilisasi_pct=utilisasi,
            kategori=tentukan_kategori(utilisasi, batas_rendah, batas_sedang),
            rata_rata_harian_pct=sum(harian) / len(harian) if harian else None,
            min_harian_pct=min(harian) if harian else None,
            max_harian_pct=max(harian) if harian else None,
        )
    return hasil


def korelasi_pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Korelasi Pearson. None bila data kurang dari 2 atau salah satu konstan."""
    if len(x) != len(y):
        raise ValueError("x dan y harus sama panjang.")
    n = len(x)
    if n < 2:
        return None
    rata_x = sum(x) / n
    rata_y = sum(y) / n
    sxx = sum((a - rata_x) ** 2 for a in x)
    syy = sum((b - rata_y) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return None
    sxy = sum((a - rata_x) * (b - rata_y) for a, b in zip(x, y))
    return sxy / ((sxx ** 0.5) * (syy ** 0.5))


def _peringkat(nilai: Sequence[float]) -> list[float]:
    """Peringkat mulai dari 1; nilai kembar mendapat rata-rata peringkatnya."""
    urutan = sorted(range(len(nilai)), key=lambda i: nilai[i])
    hasil = [0.0] * len(nilai)
    awal = 0
    while awal < len(urutan):
        akhir = awal
        while akhir + 1 < len(urutan) and nilai[urutan[akhir + 1]] == nilai[urutan[awal]]:
            akhir += 1
        rata = (awal + akhir) / 2 + 1
        for k in range(awal, akhir + 1):
            hasil[urutan[k]] = rata
        awal = akhir + 1
    return hasil


def korelasi_spearman(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Korelasi Spearman = Pearson pada peringkat."""
    if len(x) != len(y):
        raise ValueError("x dan y harus sama panjang.")
    return korelasi_pearson(_peringkat(x), _peringkat(y))


def korelasi_jadwal_vs_terpakai(statistik: Iterable[StatistikRuang]) -> KorelasiRuang:
    """Korelasi menit terjadwal vs terpakai antar ruang.

    Ruang tanpa jadwal pada periode itu tidak diikutkan. Jumlah ruang di
    proyek ini hanya 10, jadi nilai korelasi perlu dibaca dengan hati-hati.
    """
    ruang = [r for r in statistik if r.menit_terjadwal > 0]
    terjadwal = [r.menit_terjadwal for r in ruang]
    terpakai = [r.menit_terpakai for r in ruang]
    return KorelasiRuang(
        jumlah_ruang=len(ruang),
        pearson=korelasi_pearson(terjadwal, terpakai),
        spearman=korelasi_spearman(terjadwal, terpakai),
    )