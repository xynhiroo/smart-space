from datetime import date, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import ClassificationResult, OccupancyLog, Room, Schedule, ThresholdSetting

SENIN = date(2026, 10, 5)


@pytest.fixture
def klien(db_session, monkeypatch):
    # Endpoint memanggil commit. Dalam test cukup flush supaya rollback akhir menghapus semuanya.
    monkeypatch.setattr(db_session, "commit", db_session.flush)
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


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
    ruang = Room(nama_ruangan="UJI-SS1-11-CLS", status="tersedia")
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


def _badan(ruang_id=None):
    isi = {"tanggal_mulai": str(SENIN), "tanggal_selesai": str(SENIN)}
    if ruang_id is not None:
        isi["room_id"] = ruang_id
    return isi


def test_classify_menyimpan_hasil_yang_terbaca_di_results(klien, db_session):
    _isi_threshold(db_session)
    ruang = _siapkan_ruang(db_session)

    respons = klien.post("/classify", json=_badan(ruang.id))

    assert respons.status_code == 200
    assert respons.json() == {
        "tanggal_mulai": str(SENIN),
        "tanggal_selesai": str(SENIN),
        "jumlah_ruang": 1,
        "jumlah_baris": 1,
        "per_status": {"sesuai_jadwal": 1},
    }

    hasil = klien.get(
        f"/results?tanggal_mulai={SENIN}&tanggal_selesai={SENIN}&room_id={ruang.id}"
    ).json()
    assert hasil["total"] == 1
    assert hasil["items"][0]["status"] == "sesuai_jadwal"
    assert hasil["items"][0]["utilisasi_pct"] == 100.0


def test_classify_dua_kali_tidak_menggandakan_baris(klien, db_session):
    _isi_threshold(db_session)
    ruang = _siapkan_ruang(db_session)

    for _ in range(2):
        assert klien.post("/classify", json=_badan(ruang.id)).json()["jumlah_baris"] == 1

    assert db_session.query(ClassificationResult).filter_by(room_id=ruang.id).count() == 1


def test_classify_ruang_tidak_ditemukan(klien, db_session):
    _isi_threshold(db_session)

    respons = klien.post("/classify", json=_badan(999999999))

    assert respons.status_code == 404
    assert "999999999" in respons.json()["detail"]


def test_classify_tanpa_data_okupansi_menjawab_409(klien, db_session):
    _isi_threshold(db_session)
    ruang = _siapkan_ruang(db_session, dengan_okupansi=False)

    respons = klien.post("/classify", json=_badan(ruang.id))

    assert respons.status_code == 409
    assert "okupansi" in respons.json()["detail"]


def test_classify_500_bila_ambang_tidak_lengkap(klien, db_session):
    db_session.query(ThresholdSetting).delete()
    db_session.flush()
    ruang = _siapkan_ruang(db_session)

    respons = klien.post("/classify", json=_badan(ruang.id))

    assert respons.status_code == 500
    assert "threshold_settings" in respons.json()["detail"]


@pytest.mark.parametrize(
    "badan",
    [
        {},
        {"tanggal_mulai": "2026-10-06", "tanggal_selesai": "2026-10-05"},
        {"tanggal_mulai": "2026-01-01", "tanggal_selesai": "2027-12-31"},
        {"tanggal_mulai": "2026-10-05", "tanggal_selesai": "2026-10-05", "room_id": 0},
        {"tanggal_mulai": "bukan-tanggal", "tanggal_selesai": "2026-10-05"},
    ],
)
def test_classify_menolak_permintaan_tidak_valid(klien, badan):
    assert klien.post("/classify", json=badan).status_code == 422
