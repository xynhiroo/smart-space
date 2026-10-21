"""Representasi frame-based knowledge untuk entitas ruangan dan jadwal perkuliahan."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Iterable, Sequence

from app.calendar_utils import matches_day_of_week
from app.expert_system.tipe import FaktaJadwal, FaktaRuang


@dataclass(frozen=True)
class FrameJadwal:
    """Frame representasi pengetahuan untuk satu jadwal sesi kuliah."""

    schedule_id: int
    hari: str
    jam_mulai: time
    jam_selesai: time
    mata_kuliah: str


@dataclass(frozen=True)
class FrameRuang:
    """Frame representasi pengetahuan untuk satu ruangan beserta koleksi jadwalnya."""

    room_id: int
    nama_ruangan: str
    is_open_space: bool
    jadwal: tuple[FrameJadwal, ...] = field(default_factory=tuple)

    def jadwal_pada(self, tanggal: date) -> list[FrameJadwal]:
        """Mengembalikan daftar jadwal yang berlaku pada tanggal tertentu, diurutkan menurut jam_mulai.

        Mencocokkan nama hari (termasuk variasi 'Jum\'at' dan 'Jumat') dengan hari dalam minggu
        menggunakan modul calendar_utils.
        """
        weekday = tanggal.weekday()
        cocok = [j for j in self.jadwal if matches_day_of_week(j.hari, weekday)]
        return sorted(cocok, key=lambda j: j.jam_mulai)


def buat_frame_jadwal(fakta: FaktaJadwal) -> FrameJadwal:
    """Membangun FrameJadwal dari FaktaJadwal."""
    return FrameJadwal(
        schedule_id=fakta.schedule_id,
        hari=fakta.hari,
        jam_mulai=fakta.jam_mulai,
        jam_selesai=fakta.jam_selesai,
        mata_kuliah=fakta.mata_kuliah,
    )


def buat_frame_ruang(
    fakta_ruang: FaktaRuang, daftar_jadwal: Iterable[FaktaJadwal] = ()
) -> FrameRuang:
    """Membangun FrameRuang dari FaktaRuang dan daftar FaktaJadwal terkait."""
    jadwal_ruang = [
        buat_frame_jadwal(j)
        for j in daftar_jadwal
        if j.room_id == fakta_ruang.room_id
    ]
    # Urutkan jadwal berdasarkan jam mulai
    jadwal_ruang.sort(key=lambda j: j.jam_mulai)
    return FrameRuang(
        room_id=fakta_ruang.room_id,
        nama_ruangan=fakta_ruang.nama_ruangan,
        is_open_space=fakta_ruang.is_open_space,
        jadwal=tuple(jadwal_ruang),
    )
