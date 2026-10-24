from datetime import date, datetime, time
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.rute import bulatkan
from app.database import get_db
from app.main import app
from app.models import ClassificationResult, Room, Schedule, ThresholdSetting

COMPUTED_AT = datetime(2026, 10, 27, 12, 0, 0)
SENIN = date(2026, 10, 5)
SELASA = date(2026, 10, 6)
RABU = date(2026, 10, 7)
SENIN_BERIKUTNYA = date(2026, 10, 12)
RENTANG = f"tanggal_mulai={SENIN}&tanggal_selesai={SELASA}"


@pytest.fixture
def klien(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _isi_threshold(db_session, rendah="40", sedang="80"):
    db_session.query(ThresholdSetting).delete()
    nilai = {
        "empty_min_occupied_minutes": "10",
        "outside_schedule_min_minutes": "30",
        "utilization_low_max": rendah,
        "utilization_medium_max": sedang,
    }
    for key, value in nilai.items():
        db_session.add(ThresholdSetting(key=key, value=value))
    db_session.flush()


def _buat_ruang(db_session, nama):
    ruang = Room(nama_ruangan=nama, status="tersedia")
    db_session.add(ruang)
    db_session.flush()
    return ruang


def _buat_jadwal(db_session, ruang):
    jadwal = Schedule(
        room_id=ruang.id,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Mata Kuliah Uji",
    )
    db_session.add(jadwal)
    db_session.flush()
    return jadwal


def _tambah_hasil(
    db_session,
    ruang,
    jadwal,
    tanggal,
    terjadwal,
    terpakai,
    status="sesuai_jadwal",
    mulai=time(8, 0),
    selesai=time(10, 0),
):
    utilisasi = None
    if terjadwal:
        utilisasi = (Decimal(terpakai) * 100 / Decimal(terjadwal)).quantize(Decimal("0.01"))
    db_session.add(
        ClassificationResult(
            room_id=ruang.id,
            schedule_id=jadwal.id if jadwal else None,
            tanggal=tanggal,
            waktu_mulai=mulai,
            waktu_selesai=selesai,
            status=status,
            menit_terjadwal=terjadwal,
            menit_terpakai=terpakai,
            utilisasi_pct=utilisasi,
            rule_id="R01",
            penjelasan="Data uji.",
            computed_at=COMPUTED_AT,
        )
    )
    db_session.flush()


def _data_ruang_a(db_session):
    """Dua sesi dalam rentang, satu episode, dan satu sesi di luar rentang."""
    ruang = _buat_ruang(db_session, "UJI-SS1-11-API-A")
    jadwal = _buat_jadwal(db_session, ruang)
    _tambah_hasil(db_session, ruang, jadwal, SENIN, 120, 90)
    _tambah_hasil(
        db_session, ruang, None, SENIN, 0, 60,
        status="dipakai_di_luar_jadwal", mulai=time(18, 0), selesai=time(19, 0),
    )
    _tambah_hasil(db_session, ruang, jadwal, SELASA, 60, 0, status="kosong_meski_terjadwal")
    _tambah_hasil(db_session, ruang, jadwal, SENIN_BERIKUTNYA, 60, 60)
    return ruang, jadwal


def test_root_dan_health(klien):
    assert klien.get("/").json()["status"] == "online"
    assert klien.get("/health").json() == {"status": "healthy"}


def test_results_baris_dalam_rentang_dan_terurut(klien, db_session):
    ruang, _ = _data_ruang_a(db_session)

    respons = klien.get(f"/results?{RENTANG}&room_id={ruang.id}")

    assert respons.status_code == 200
    isi = respons.json()
    assert (isi["total"], isi["limit"], isi["offset"]) == (3, 100, 0)
    assert [(b["tanggal"], b["waktu_mulai"]) for b in isi["items"]] == [
        ("2026-10-05", "08:00:00"),
        ("2026-10-05", "18:00:00"),
        ("2026-10-06", "08:00:00"),
    ]
    sesi, episode, kosong = isi["items"]
    assert sesi["status"] == "sesuai_jadwal"
    assert sesi["utilisasi_pct"] == 75.0
    assert episode["schedule_id"] is None
    assert episode["utilisasi_pct"] is None
    assert kosong["status"] == "kosong_meski_terjadwal"


@pytest.mark.parametrize(
    "status, tanggal_harapan",
    [("kosong_meski_terjadwal", "2026-10-06"), ("dipakai_di_luar_jadwal", "2026-10-05")],
)
def test_results_filter_status(klien, db_session, status, tanggal_harapan):
    ruang, _ = _data_ruang_a(db_session)

    isi = klien.get(f"/results?{RENTANG}&room_id={ruang.id}&status={status}").json()

    assert isi["total"] == 1
    assert isi["items"][0]["status"] == status
    assert isi["items"][0]["tanggal"] == tanggal_harapan


def test_results_paginasi(klien, db_session):
    ruang = _buat_ruang(db_session, "UJI-SS1-11-API-A")
    jadwal = _buat_jadwal(db_session, ruang)
    for tanggal in (SENIN, SELASA, RABU):
        _tambah_hasil(db_session, ruang, jadwal, tanggal, 120, 90)
    dasar = f"/results?tanggal_mulai={SENIN}&tanggal_selesai={RABU}&room_id={ruang.id}"

    halaman_1 = klien.get(f"{dasar}&limit=2&offset=0").json()
    halaman_2 = klien.get(f"{dasar}&limit=2&offset=2").json()

    assert halaman_1["total"] == halaman_2["total"] == 3
    assert [b["tanggal"] for b in halaman_1["items"]] == ["2026-10-05", "2026-10-06"]
    assert [b["tanggal"] for b in halaman_2["items"]] == ["2026-10-07"]


@pytest.mark.parametrize(
    "kueri",
    [
        "",
        "tanggal_mulai=2026-10-05",
        "tanggal_mulai=2026-10-06&tanggal_selesai=2026-10-05",
        "tanggal_mulai=2026-10-05&tanggal_selesai=2026-10-06&limit=0",
        "tanggal_mulai=2026-10-05&tanggal_selesai=2026-10-06&limit=1001",
        "tanggal_mulai=2026-10-05&tanggal_selesai=2026-10-06&offset=-1",
        "tanggal_mulai=2026-10-05&tanggal_selesai=2026-10-06&room_id=0",
        "tanggal_mulai=2026-10-05&tanggal_selesai=2026-10-06&status=rusak",
        "tanggal_mulai=bukan-tanggal&tanggal_selesai=2026-10-06",
    ],
)
def test_results_menolak_parameter_tidak_valid(klien, kueri):
    assert klien.get(f"/results?{kueri}").status_code == 422


def test_utilization_sesuai_hitungan_manual(klien, db_session):
    _isi_threshold(db_session)
    ruang, _ = _data_ruang_a(db_session)

    respons = klien.get(f"/utilization?{RENTANG}&room_id={ruang.id}")

    assert respons.status_code == 200
    isi = respons.json()
    assert (isi["batas_rendah"], isi["batas_sedang"]) == (40.0, 80.0)
    assert isi["ruang"] == [
        {
            "room_id": ruang.id,
            "nama_ruangan": "UJI-SS1-11-API-A",
            "menit_terjadwal": 180,
            "menit_terpakai": 90,
            "selisih_menit": 90,
            "utilisasi_pct": 50.0,
            "kategori": "sedang",
            "rata_rata_harian_pct": 37.5,
            "min_harian_pct": 0.0,
            "max_harian_pct": 75.0,
        }
    ]
    assert isi["korelasi"] == {"jumlah_ruang": 1, "pearson": None, "spearman": None}


def test_utilization_semua_ruang_termasuk_ruang_tanpa_jadwal(klien, db_session):
    _isi_threshold(db_session)
    ruang_a, _ = _data_ruang_a(db_session)
    ruang_b = _buat_ruang(db_session, "UJI-SS1-11-API-B")
    jadwal_b = _buat_jadwal(db_session, ruang_b)
    _tambah_hasil(db_session, ruang_b, jadwal_b, SENIN, 100, 100)
    ruang_c = _buat_ruang(db_session, "UJI-SS1-11-API-C")

    isi = klien.get(f"/utilization?{RENTANG}").json()

    per_ruang = {baris["room_id"]: baris for baris in isi["ruang"]}
    assert per_ruang[ruang_a.id]["kategori"] == "sedang"
    assert per_ruang[ruang_b.id]["utilisasi_pct"] == 100.0
    assert per_ruang[ruang_b.id]["kategori"] == "tinggi"
    assert per_ruang[ruang_c.id]["menit_terjadwal"] == 0
    assert per_ruang[ruang_c.id]["utilisasi_pct"] is None
    assert per_ruang[ruang_c.id]["kategori"] is None
    assert per_ruang[ruang_c.id]["rata_rata_harian_pct"] is None
    assert isi["korelasi"]["jumlah_ruang"] >= 2


def test_utilization_pembulatan_dua_desimal(klien, db_session):
    _isi_threshold(db_session)
    ruang = _buat_ruang(db_session, "UJI-SS1-11-API-D")
    jadwal = _buat_jadwal(db_session, ruang)
    _tambah_hasil(db_session, ruang, jadwal, SENIN, 90, 30)

    isi = klien.get(f"/utilization?{RENTANG}&room_id={ruang.id}").json()

    assert isi["ruang"][0]["utilisasi_pct"] == 33.33
    assert isi["ruang"][0]["kategori"] == "rendah"


def test_utilization_memakai_ambang_dari_database(klien, db_session):
    _isi_threshold(db_session, rendah="50", sedang="90")
    ruang, _ = _data_ruang_a(db_session)

    isi = klien.get(f"/utilization?{RENTANG}&room_id={ruang.id}").json()

    assert (isi["batas_rendah"], isi["batas_sedang"]) == (50.0, 90.0)
    assert isi["ruang"][0]["utilisasi_pct"] == 50.0
    assert isi["ruang"][0]["kategori"] == "rendah"


def test_utilization_ruang_tidak_ditemukan(klien):
    assert klien.get(f"/utilization?{RENTANG}&room_id=999999999").status_code == 404


def test_utilization_500_bila_ambang_tidak_lengkap(klien, db_session):
    db_session.query(ThresholdSetting).delete()
    db_session.flush()
    ruang, _ = _data_ruang_a(db_session)

    respons = klien.get(f"/utilization?{RENTANG}&room_id={ruang.id}")

    assert respons.status_code == 500
    assert "threshold_settings" in respons.json()["detail"]


@pytest.mark.parametrize(
    "kueri",
    [
        "",
        "tanggal_mulai=2026-10-06&tanggal_selesai=2026-10-05",
        "tanggal_mulai=2026-10-05&tanggal_selesai=2026-10-06&room_id=0",
    ],
)
def test_utilization_menolak_parameter_tidak_valid(klien, kueri):
    assert klien.get(f"/utilization?{kueri}").status_code == 422


@pytest.mark.parametrize(
    "nilai, desimal, harapan",
    [
        (33.335, 2, 33.34),
        (33.334, 2, 33.33),
        (None, 2, None),
        (0.12345, 4, 0.1235),
        (1.0, 2, 1.0),
    ],
)
def test_bulatkan_half_up(nilai, desimal, harapan):
    assert bulatkan(nilai, desimal) == harapan
