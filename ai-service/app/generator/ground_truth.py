"""Ground truth generator untuk data okupansi historis (SS1-08).

Label kebenaran dihitung dari okupansi sebenarnya SEBELUM noise berdasarkan
definisi tetap DATA_CONTRACT Bagian 7 pada nilai ambang awal.
Modul ini mandiri dan tidak mengimpor modul klasifikasi sistem pakar.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path
from typing import Iterable, Sequence

from app.generator.params import (
    STATUS_KOSONG_TERJADWAL,
    STATUS_LUAR_JADWAL,
    STATUS_SESUAI_JADWAL,
    PENYEBAB_LUAR_JADWAL,
)

CSV_FIELDNAMES = [
    "tanggal",
    "room_id",
    "schedule_id",
    "waktu_mulai",
    "waktu_selesai",
    "status_benar",
    "penyebab",
]


@dataclass(frozen=True)
class GroundTruthRow:
    """Satu baris data label kebenaran ground truth."""

    tanggal: date
    room_id: int
    schedule_id: int | None
    waktu_mulai: time
    waktu_selesai: time
    status_benar: str
    penyebab: str

    def to_csv_dict(self) -> dict[str, str]:
        """Konversi ke dictionary baris CSV dengan format standar."""
        return {
            "tanggal": self.tanggal.isoformat(),
            "room_id": str(self.room_id),
            "schedule_id": str(self.schedule_id) if self.schedule_id is not None else "",
            "waktu_mulai": self.waktu_mulai.strftime("%H:%M:%S"),
            "waktu_selesai": self.waktu_selesai.strftime("%H:%M:%S"),
            "status_benar": self.status_benar,
            "penyebab": self.penyebab,
        }


def format_time_str(t: time) -> str:
    """Format time ke HH:MM:SS."""
    return t.strftime("%H:%M:%S")


def evaluate_session_ground_truth(
    tanggal: date,
    room_id: int,
    schedule_id: int,
    jam_mulai: time,
    jam_selesai: time,
    menit_terpakai: int,
    penyebab: str,
    empty_threshold_minutes: int = 10,
) -> GroundTruthRow:
    """Menghitung baris ground truth untuk satu sesi perkuliahan terjadwal.

    Aturan DATA_CONTRACT 7.3:
    - Bila menit_terpakai < empty_threshold_minutes (10 menit) maka kosong_meski_terjadwal.
    - Selain itu sesuai_jadwal.
    """
    if menit_terpakai < empty_threshold_minutes:
        status_benar = STATUS_KOSONG_TERJADWAL
    else:
        status_benar = STATUS_SESUAI_JADWAL

    return GroundTruthRow(
        tanggal=tanggal,
        room_id=room_id,
        schedule_id=schedule_id,
        waktu_mulai=jam_mulai,
        waktu_selesai=jam_selesai,
        status_benar=status_benar,
        penyebab=penyebab,
    )


def create_outside_episode_ground_truth(
    tanggal: date,
    room_id: int,
    waktu_mulai: time,
    waktu_selesai: time,
) -> GroundTruthRow:
    """Membuat baris ground truth untuk episode pemakaian di luar jadwal (durasi >= 30 menit)."""
    return GroundTruthRow(
        tanggal=tanggal,
        room_id=room_id,
        schedule_id=None,
        waktu_mulai=waktu_mulai,
        waktu_selesai=waktu_selesai,
        status_benar=STATUS_LUAR_JADWAL,
        penyebab=PENYEBAB_LUAR_JADWAL,
    )


def write_ground_truth_csv(rows: Iterable[GroundTruthRow], file_path: Path | str) -> None:
    """Menulis kumpulan baris ground truth ke berkas CSV secara deterministik."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sorted_rows = sorted(
        rows,
        key=lambda r: (
            r.tanggal,
            r.room_id,
            r.waktu_mulai,
            r.schedule_id if r.schedule_id is not None else -1,
        ),
    )

    with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in sorted_rows:
            writer.writerow(row.to_csv_dict())
