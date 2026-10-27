from datetime import date, datetime, time, timedelta

import pytest

from app.classification.pelaksana import (
    DataOkupansiKosongError,
    RuangTidakDitemukanError,
    jalankan_klasifikasi,
    klasifikasikan_data,
)
from app.expert_system.tipe import Ambang, FaktaJadwal, FaktaRuang, SlotOkupansi
from app.models import ClassificationResult, OccupancyLog, Room, Schedule, ThresholdSetting

AMBANG = Ambang(
    empty_min_occupied_minutes=10,
    outside_schedule_min_minutes=30,
    batas_rendah=40.0,
    batas_sedang=80.0,
)
SENIN = date(2026, 10, 5)
SELASA = date(2026, 10, 6)
COMPUTED_AT = datetime(2026, 10, 27, 12, 0, 0)

RUANG_A = FaktaRuang(room_id=1, nama_ruangan="UJI-A", is_open_space=False)
RUANG_B = FaktaRuang(room_id=2, nama_ruangan="UJI-B", is_open_space=False)
JADWAL_A = FaktaJadwal(11, 1, "Senin", time(8, 0), time(10, 0), "MK A")
JADWAL_B = FaktaJadwal(12, 2, "Senin", time(8, 0), time(10, 0), "MK B")


def _slot(room_id, tanggal, jam_mulai, jumlah, terisi=True):
    awal = datetime.combine(tanggal, jam_mulai)
    return [
        SlotOkupansi(room_id, awal + timedelta(minutes=10 * i), terisi)
        for i in range(jumlah)
    ]


def test_sesi_terisi_penuh_sesuai_jadwal():
    hasil = klasifikasikan_data(
        [RUANG_A], [JADWAL_A], {1: _slot(1, SENIN, time(8, 0), 12)},
        frozenset(), SENIN, SENIN, AMBANG,
    )

    assert len(hasil) == 1
    h = hasil[0]
    assert (h.status, h.rule_id, h.schedule_id) == ("sesuai_jadwal", "R01", 11)
    assert (h.menit_terjadwal, h.menit_terpakai) == (120, 120)
    assert h.utilisasi_pct == pytest.approx(100.0)


def test_sesi_tanpa_okupansi_kosong_meski_terjadwal():
    hasil = klasifikasikan_data(
        [RUANG_A], [JADWAL_A], {}, frozenset(), SENIN, SENIN, AMBANG,
    )

    assert len(hasil) == 1
    assert (hasil[0].status, hasil[0].rule_id) == ("kosong_meski_terjadwal", "R02")
    assert hasil[0].menit_terpakai == 0


def test_hanya_slot_ruang_sendiri_yang_dipakai():
    hasil = klasifikasikan_data(
        [RUANG_A, RUANG_B],
        [JADWAL_A, JADWAL_B],
        {2: _slot(2, SENIN, time(8, 0), 12)},
        frozenset(), SENIN, SENIN, AMBANG,
    )

    status = {h.room_id: h.status for h in hasil}
    assert status == {1: "kosong_meski_terjadwal", 2: "sesuai_jadwal"}


def test_jadwal_hari_lain_tidak_dievaluasi():
    hasil = klasifikasikan_data(
        [RUANG_A], [JADWAL_A], {1: _slot(1, SENIN, time(8, 0), 12)},
        frozenset(), SENIN, SELASA, AMBANG,
    )

    assert [h.tanggal for h in hasil] == [SENIN]


def test_hari_libur_hanya_menghasilkan_episode_di_luar_jadwal():
    hasil = klasifikasikan_data(
        [RUANG_A], [JADWAL_A], {1: _slot(1, SENIN, time(18, 0), 6)},
        frozenset({SENIN}), SENIN, SENIN, AMBANG,
    )

    assert len(hasil) == 1
    h = hasil[0]
    assert h.schedule_id is None
    assert h.status == "dipakai_di_luar_jadwal"
    assert (h.waktu_mulai, h.waktu_selesai) == (time(18, 0), time(19, 0))
    assert h.menit_terpakai == 60


def test_rentang_terbalik_ditolak():
    with pytest.raises(ValueError, match="tanggal_mulai"):
        klasifikasikan_data([RUANG_A], [], {}, frozenset(), SELASA, SENIN, AMBANG)


def _isi_threshold(db_session):
    db_session.query(ThresholdSetting).delete()
    for key, value in {
        "empty_min_occupied_minutes": "10",
        "outside_schedule_min_minutes": "30",
        "utilization_low_max": "40",
        "utilization_medium_max": "80",
    }.items():
        db_session.add(ThresholdSetting(key=key, value=value))
    db_session.flush()


def _siapkan_ruang(db_session, dengan_okupansi=True):
    ruang = Room(nama_ruangan="UJI-SS1-11-PLK", status="tersedia")
    db_session.add(ruang)
    db_session.flush()
    db_session.add(
        Schedule(
            room_id=ruang.id, hari="Senin", jam_mulai=time(8, 0),
            jam_selesai=time(10, 0), mata_kuliah="Mata Kuliah Uji",
        )
    )
    if dengan_okupansi:
        awal = datetime.combine(SENIN, time(8, 0))
        for i in range(12):
            db_session.add(
                OccupancyLog(
                    room_id=ruang.id, slot_mulai=awal + timedelta(minutes=10 * i),
                    is_occupied=True, source="dummy",
                )
            )
    db_session.flush()
    return ruang


def test_jalankan_klasifikasi_menyimpan_dan_idempoten(db_session):
    _isi_threshold(db_session)
    ruang = _siapkan_ruang(db_session)

    for _ in range(2):
        ringkasan = jalankan_klasifikasi(
            db_session, SENIN, SENIN, room_ids=[ruang.id], computed_at=COMPUTED_AT
        )
        assert ringkasan.jumlah_ruang == 1
        assert ringkasan.jumlah_baris == 1
        assert ringkasan.per_status == {"sesuai_jadwal": 1}

    baris = db_session.query(ClassificationResult).filter_by(room_id=ruang.id).one()
    assert baris.status == "sesuai_jadwal"
    assert baris.computed_at == COMPUTED_AT


def test_ruang_tidak_ditemukan(db_session):
    _isi_threshold(db_session)

    with pytest.raises(RuangTidakDitemukanError, match="999999999"):
        jalankan_klasifikasi(db_session, SENIN, SENIN, room_ids=[999999999])


def test_tanpa_data_okupansi_ditolak_dan_tidak_menulis(db_session):
    _isi_threshold(db_session)
    ruang = _siapkan_ruang(db_session, dengan_okupansi=False)

    with pytest.raises(DataOkupansiKosongError):
        jalankan_klasifikasi(db_session, SENIN, SENIN, room_ids=[ruang.id])

    assert db_session.query(ClassificationResult).filter_by(room_id=ruang.id).count() == 0
