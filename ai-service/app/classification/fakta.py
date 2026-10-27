"""Pembentuk dan pemuat fakta untuk sistem pakar (SS1-11).

Fungsi bentuk_*, kelompokkan_*, dan kumpulkan_* murni: objek model masuk,
dataclass sistem pakar keluar. Fungsi muat_* membaca database lalu
memanggil fungsi murni itu. Tidak ada yang menulis ke database.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Collection, Iterable

from sqlalchemy.orm import Session

from app.expert_system.tipe import FaktaJadwal, FaktaRuang, SlotOkupansi
from app.models import CalendarException, OccupancyLog, Room, Schedule

TIPE_LIBUR = "libur"


def bentuk_fakta_ruang(
    daftar_ruang: Iterable[Room], nama_open_space: Collection[str]
) -> list[FaktaRuang]:
    """Membentuk FaktaRuang. Status open space ditentukan dari daftar nama."""
    return [
        FaktaRuang(
            room_id=ruang.id,
            nama_ruangan=ruang.nama_ruangan,
            is_open_space=ruang.nama_ruangan in nama_open_space,
        )
        for ruang in daftar_ruang
    ]


def bentuk_fakta_jadwal(daftar_jadwal: Iterable[Schedule]) -> list[FaktaJadwal]:
    """Membentuk FaktaJadwal. Nama hari dibiarkan apa adanya (dinormalisasi sistem pakar)."""
    return [
        FaktaJadwal(
            schedule_id=jadwal.id,
            room_id=jadwal.room_id,
            hari=jadwal.hari,
            jam_mulai=jadwal.jam_mulai,
            jam_selesai=jadwal.jam_selesai,
            mata_kuliah=jadwal.mata_kuliah,
        )
        for jadwal in daftar_jadwal
    ]


def kelompokkan_slot_per_ruang(
    daftar_log: Iterable[OccupancyLog],
) -> dict[int, list[SlotOkupansi]]:
    """Mengelompokkan log okupansi per room_id. Ruang tanpa log tidak muncul."""
    hasil: dict[int, list[SlotOkupansi]] = defaultdict(list)
    for log in daftar_log:
        hasil[log.room_id].append(
            SlotOkupansi(
                room_id=log.room_id,
                slot_mulai=log.slot_mulai,
                is_occupied=bool(log.is_occupied),
            )
        )
    return dict(hasil)


def kumpulkan_tanggal_libur(
    daftar_pengecualian: Iterable[CalendarException],
    tanggal_mulai: date,
    tanggal_selesai: date,
) -> frozenset[date]:
    """Tanggal libur di dalam rentang (inklusif). Hanya tipe 'libur' (Bagian 7.5)."""
    if tanggal_mulai > tanggal_selesai:
        raise ValueError("tanggal_mulai tidak boleh setelah tanggal_selesai.")

    libur: set[date] = set()
    for pengecualian in daftar_pengecualian:
        if pengecualian.tipe != TIPE_LIBUR:
            continue
        hari = max(pengecualian.tanggal_mulai, tanggal_mulai)
        akhir = min(pengecualian.tanggal_selesai, tanggal_selesai)
        while hari <= akhir:
            libur.add(hari)
            hari += timedelta(days=1)
    return frozenset(libur)


def muat_fakta_ruang(session: Session, nama_open_space: Collection[str]) -> list[FaktaRuang]:
    return bentuk_fakta_ruang(session.query(Room).order_by(Room.id).all(), nama_open_space)


def muat_fakta_jadwal(session: Session) -> list[FaktaJadwal]:
    return bentuk_fakta_jadwal(session.query(Schedule).order_by(Schedule.id).all())


def muat_slot_okupansi(
    session: Session, tanggal_mulai: date, tanggal_selesai: date
) -> dict[int, list[SlotOkupansi]]:
    """Slot okupansi untuk seluruh hari dalam rentang (inklusif), dikelompokkan per ruang."""
    awal = datetime.combine(tanggal_mulai, time.min)
    batas = datetime.combine(tanggal_selesai + timedelta(days=1), time.min)
    daftar_log = (
        session.query(OccupancyLog)
        .filter(OccupancyLog.slot_mulai >= awal, OccupancyLog.slot_mulai < batas)
        .order_by(OccupancyLog.room_id, OccupancyLog.slot_mulai)
        .all()
    )
    return kelompokkan_slot_per_ruang(daftar_log)


def muat_tanggal_libur(
    session: Session, tanggal_mulai: date, tanggal_selesai: date
) -> frozenset[date]:
    return kumpulkan_tanggal_libur(
        session.query(CalendarException).all(), tanggal_mulai, tanggal_selesai
    )
