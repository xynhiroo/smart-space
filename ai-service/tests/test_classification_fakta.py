from datetime import date, datetime, time

import pytest

from app.classification.fakta import (
    bentuk_fakta_jadwal,
    bentuk_fakta_ruang,
    kelompokkan_slot_per_ruang,
    kumpulkan_tanggal_libur,
    muat_fakta_jadwal,
    muat_fakta_ruang,
    muat_slot_okupansi,
    muat_tanggal_libur,
)
from app.expert_system.tipe import FaktaJadwal, FaktaRuang, SlotOkupansi
from app.models import CalendarException, OccupancyLog, Room, Schedule


def _libur(mulai, selesai, tipe="libur"):
    return CalendarException(
        tanggal_mulai=mulai, tanggal_selesai=selesai, tipe=tipe, keterangan="uji"
    )


def _ruang_uji(db_session, nama="UJI-SS1-11-C"):
    ruang = Room(nama_ruangan=nama, status="tersedia")
    db_session.add(ruang)
    db_session.flush()
    return ruang


def test_fakta_ruang_menandai_open_space_dari_daftar_nama():
    ruang = [Room(id=1, nama_ruangan="GU 701"), Room(id=2, nama_ruangan="GU 604")]

    assert bentuk_fakta_ruang(ruang, {"GU 701"}) == [
        FaktaRuang(room_id=1, nama_ruangan="GU 701", is_open_space=True),
        FaktaRuang(room_id=2, nama_ruangan="GU 604", is_open_space=False),
    ]


def test_fakta_jadwal_menyalin_kolom_yang_dibutuhkan():
    jadwal = Schedule(
        id=7,
        room_id=1,
        hari="Jum'at",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Mata Kuliah Uji",
        kelas="3A",
        dosen="Dosen Uji",
    )

    assert bentuk_fakta_jadwal([jadwal]) == [
        FaktaJadwal(
            schedule_id=7,
            room_id=1,
            hari="Jum'at",
            jam_mulai=time(8, 0),
            jam_selesai=time(10, 0),
            mata_kuliah="Mata Kuliah Uji",
        )
    ]


def test_kelompokkan_slot_per_ruang():
    daftar_log = [
        OccupancyLog(room_id=1, slot_mulai=datetime(2026, 10, 5, 8, 0), is_occupied=True, source="dummy"),
        OccupancyLog(room_id=2, slot_mulai=datetime(2026, 10, 5, 8, 0), is_occupied=False, source="dummy"),
        OccupancyLog(room_id=1, slot_mulai=datetime(2026, 10, 5, 8, 10), is_occupied=False, source="dummy"),
    ]

    hasil = kelompokkan_slot_per_ruang(daftar_log)

    assert set(hasil) == {1, 2}
    assert hasil[1] == [
        SlotOkupansi(1, datetime(2026, 10, 5, 8, 0), True),
        SlotOkupansi(1, datetime(2026, 10, 5, 8, 10), False),
    ]
    assert hasil[2] == [SlotOkupansi(2, datetime(2026, 10, 5, 8, 0), False)]


def test_tanggal_libur_hanya_tipe_libur_dan_dipotong_ke_rentang():
    daftar = [
        _libur(date(2026, 10, 1), date(2026, 10, 3)),
        _libur(date(2026, 10, 5), date(2026, 10, 5), tipe="ujian"),
        _libur(date(2026, 10, 9), date(2026, 10, 12)),
    ]

    hasil = kumpulkan_tanggal_libur(daftar, date(2026, 10, 2), date(2026, 10, 10))

    assert hasil == frozenset(
        {date(2026, 10, 2), date(2026, 10, 3), date(2026, 10, 9), date(2026, 10, 10)}
    )


def test_tanggal_libur_tanpa_irisan_menghasilkan_himpunan_kosong():
    daftar = [_libur(date(2026, 12, 24), date(2026, 12, 26))]

    assert kumpulkan_tanggal_libur(daftar, date(2026, 10, 1), date(2026, 10, 31)) == frozenset()


def test_tanggal_libur_menolak_periode_terbalik():
    with pytest.raises(ValueError, match="tanggal_mulai"):
        kumpulkan_tanggal_libur([], date(2026, 10, 10), date(2026, 10, 1))


def test_muat_fakta_ruang_memakai_daftar_open_space(db_session):
    ruang = _ruang_uji(db_session)

    hasil = muat_fakta_ruang(db_session, {"UJI-SS1-11-C"})

    assert FaktaRuang(room_id=ruang.id, nama_ruangan="UJI-SS1-11-C", is_open_space=True) in hasil


def test_muat_fakta_jadwal_membaca_jadwal_dari_database(db_session):
    ruang = _ruang_uji(db_session)
    jadwal = Schedule(
        room_id=ruang.id,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Mata Kuliah Uji",
    )
    db_session.add(jadwal)
    db_session.flush()

    hasil = muat_fakta_jadwal(db_session)

    assert FaktaJadwal(
        schedule_id=jadwal.id,
        room_id=ruang.id,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Mata Kuliah Uji",
    ) in hasil


def test_muat_slot_okupansi_hanya_dalam_rentang_tanggal(db_session):
    ruang = _ruang_uji(db_session)
    for slot in (
        datetime(2026, 10, 4, 22, 50),
        datetime(2026, 10, 5, 7, 0),
        datetime(2026, 10, 5, 22, 50),
        datetime(2026, 10, 6, 7, 0),
    ):
        db_session.add(
            OccupancyLog(room_id=ruang.id, slot_mulai=slot, is_occupied=True, source="dummy")
        )
    db_session.flush()

    hasil = muat_slot_okupansi(db_session, date(2026, 10, 5), date(2026, 10, 5))

    assert [slot.slot_mulai for slot in hasil[ruang.id]] == [
        datetime(2026, 10, 5, 7, 0),
        datetime(2026, 10, 5, 22, 50),
    ]


def test_muat_tanggal_libur_membaca_kalender_dari_database(db_session):
    db_session.add(_libur(date(2026, 12, 24), date(2026, 12, 26)))
    db_session.flush()

    hasil = muat_tanggal_libur(db_session, date(2026, 12, 25), date(2026, 12, 31))

    assert {date(2026, 12, 25), date(2026, 12, 26)} <= hasil
