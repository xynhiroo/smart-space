"""Tipe data dataclass frozen untuk sistem pakar klasifikasi status ruangan (Tier 1).

Mengacu pada DATA_CONTRACT Bagian 11.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time


@dataclass(frozen=True)
class FaktaRuang:
    """Fakta master ruangan untuk evaluasi sistem pakar."""

    room_id: int
    nama_ruangan: str
    is_open_space: bool


@dataclass(frozen=True)
class FaktaJadwal:
    """Fakta jadwal perkuliahan terjadwal."""

    schedule_id: int
    room_id: int
    hari: str
    jam_mulai: time
    jam_selesai: time
    mata_kuliah: str


@dataclass(frozen=True)
class SlotOkupansi:
    """Fakta log okupansi satu slot 10 menit (WIB)."""

    room_id: int
    slot_mulai: datetime
    is_occupied: bool


@dataclass(frozen=True)
class Ambang:
    """Parameter ambang batas evaluasi yang diinjeksi ke sistem pakar."""

    empty_min_occupied_minutes: int
    outside_schedule_min_minutes: int
    batas_rendah: float
    batas_sedang: float


@dataclass(frozen=True)
class HasilKlasifikasi:
    """Hasil klasifikasi status ruangan untuk satu sesi atau satu episode."""

    room_id: int
    schedule_id: int | None
    tanggal: date
    waktu_mulai: time
    waktu_selesai: time
    status: str
    menit_terjadwal: int
    menit_terpakai: int
    utilisasi_pct: float | None
    rule_id: str
    penjelasan: str
