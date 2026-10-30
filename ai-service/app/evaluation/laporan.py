"""Penyusunan laporan evaluasi sistem pakar terhadap ground truth (SS1-12)."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping

from app.evaluation.metrik import STATUS, HasilEvaluasi, hitung_evaluasi
from app.evaluation.pencocokan import (
    BarisLabel,
    HasilPencocokan,
    cocokkan,
)


@dataclass(frozen=True)
class LaporanEvaluasi:
    jumlah_ground_truth: int
    jumlah_hasil: int
    pencocokan: HasilPencocokan
    evaluasi: HasilEvaluasi
    # (label_benar, label_prediksi, penyebab, jumlah), urut jumlah terbanyak
    galat: tuple[tuple[str, str, str, int], ...]


def muat_penyebab_csv(path: Path | str) -> dict[tuple[date, int, int], str]:
    """Peta (tanggal, room_id, schedule_id) -> penyebab untuk sesi terjadwal."""
    peta: dict[tuple[date, int, int], str] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["schedule_id"]:
                kunci = (date.fromisoformat(r["tanggal"]), int(r["room_id"]), int(r["schedule_id"]))
                peta[kunci] = r["penyebab"]
    return peta


def susun_laporan(
    ground_truth: Iterable[BarisLabel],
    hasil: Iterable[BarisLabel],
    penyebab: Mapping[tuple[date, int, int], str],
) -> LaporanEvaluasi:
    ground_truth = list(ground_truth)
    hasil = list(hasil)
    pc = cocokkan(ground_truth, hasil)

    murni = [(b, p) for b, p in zip(pc.benar, pc.prediksi) if b in STATUS and p in STATUS]
    evaluasi = hitung_evaluasi([b for b, _ in murni], [p for _, p in murni])

    hitung: Counter = Counter()
    for p in pc.pasangan:
        if p.benar != p.prediksi:
            sebab = "-"
            if p.schedule_id is not None:
                sebab = penyebab.get((p.tanggal, p.room_id, p.schedule_id), "-")
            hitung[(p.benar, p.prediksi, sebab)] += 1
    galat = tuple(
        (b, p, s, n)
        for (b, p, s), n in sorted(hitung.items(), key=lambda kv: (-kv[1], kv[0]))
    )
    return LaporanEvaluasi(len(ground_truth), len(hasil), pc, evaluasi, galat)


def _angka(nilai: float | None) -> str:
    return "-" if nilai is None else f"{nilai:.4f}"


def format_laporan(laporan: LaporanEvaluasi, nama_set: str, nama_db: str) -> str:
    e = laporan.evaluasi
    baris = [
        "=" * 80,
        " Smart Space Analytics - Evaluasi Sistem Pakar vs Ground Truth (SS1-12)",
        "=" * 80,
        f" Set               : {nama_set.upper()}",
        f" Database          : {nama_db}",
        f" Baris ground truth: {laporan.jumlah_ground_truth:,}",
        f" Baris runner      : {laporan.jumlah_hasil:,}",
        f" Jumlah pasangan   : {len(laporan.pencocokan.pasangan):,}",
        f" Tanpa prediksi    : {laporan.pencocokan.tanpa_prediksi} (ground truth tidak ditemukan runner)",
        f" Tanpa label       : {laporan.pencocokan.tanpa_label} (baris runner tanpa ground truth)",
        "-" * 80,
        f" Dievaluasi (pasangan tiga status): {e.jumlah:,}",
        f" Accuracy : {_angka(e.accuracy)}",
        f" Macro F1 : {_angka(e.macro_f1)}",
        "",
        f" {'Kelas':<24}{'Precision':>10}{'Recall':>10}{'F1':>10}{'Support':>9}",
    ]
    for kelas, m in e.per_kelas.items():
        baris.append(
            f" {kelas:<24}{_angka(m.precision):>10}{_angka(m.recall):>10}"
            f"{_angka(m.f1):>10}{m.support:>9}"
        )
    baris += ["", " Matriks kebingungan (baris = benar, kolom = prediksi):"]
    baris.append(" " + " " * 24 + "".join(f"{k[:12]:>14}" for k in STATUS))
    for b in STATUS:
        baris.append(" " + f"{b:<24}" + "".join(f"{e.matriks.get((b, p), 0):>14}" for p in STATUS))
    baris += ["", " Galat (benar -> prediksi, penyebab ground truth):"]
    if not laporan.galat:
        baris.append("   (tidak ada)")
    for b, p, s, n in laporan.galat:
        baris.append(f"   {n:>5}  {b} -> {p}  [{s}]")
    baris.append("=" * 80)
    return "\n".join(baris)
