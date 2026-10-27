"""Pengujian runner klasifikasi status ruangan (SS1-11).

Memverifikasi orkestrasian sistem pakar harian, idempotensi penyimpanan,
pengamanan invarian Data Contract Bagian 5, dan penanganan kasus khusus.
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest

from app.classification.runner import jalankan_klasifikasi
from app.models import (
    CalendarException,
    ClassificationResult,
    OccupancyLog,
    Room,
    Schedule,
    ThresholdSetting,
)

SENIN = date(2026, 10, 5)
SELASA = date(2026, 10, 6)
RABU = date(2026, 10, 7)
WAKTU_EVAL_AKHIR = datetime(2026, 10, 8, 0, 0, 0)
COMPUTED_AT_TEST = datetime(2026, 10, 27, 12, 0, 0)


def _siapkan_ambang(db_session):
    """Menyiapkan threshold_settings standar untuk pengujian."""
    db_session.query(ThresholdSetting).delete()
    standar = {
        "empty_min_occupied_minutes": "10",
        "outside_schedule_min_minutes": "30",
        "utilization_low_max": "40",
        "utilization_medium_max": "80",
        "empty_status_evaluation_timing": "after_schedule_finished",
    }
    for k, v in standar.items():
        db_session.add(ThresholdSetting(key=k, value=v))
    db_session.flush()


def _tambah_slot(db_session, room_id, dt, is_occupied=True):
    """Menambahkan satu slot log okupansi (10 menit)."""
    log = OccupancyLog(
        room_id=room_id,
        slot_mulai=dt,
        is_occupied=is_occupied,
        source="dummy",
    )
    db_session.add(log)


def _siapkan_data_uji(db_session):
    """Menyiapkan data buatan tangan untuk pengujian lengkap."""
    _siapkan_ambang(db_session)

    ruang_a = Room(nama_ruangan="RUANG-TEST-A", status="tersedia")
    ruang_b = Room(nama_ruangan="RUANG-TEST-B", status="tersedia")
    db_session.add_all([ruang_a, ruang_b])
    db_session.flush()

    # Jadwal pada ruang_a
    # 1. Sesi Senin 08.00 - 10.00 (akan terisi -> sesuai_jadwal)
    j_senin = Schedule(
        room_id=ruang_a.id,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Algoritma",
    )
    # 2. Sesi Selasa 08.00 - 10.00 (akan kosong -> kosong_meski_terjadwal)
    j_selasa = Schedule(
        room_id=ruang_a.id,
        hari="Selasa",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Struktur Data",
    )
    # 3. Sesi Rabu 08.00 - 10.00 (hari libur -> sesi tidak dievaluasi)
    j_rabu = Schedule(
        room_id=ruang_a.id,
        hari="Rabu",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Basis Data",
    )
    db_session.add_all([j_senin, j_selasa, j_rabu])
    db_session.flush()

    # Kalender libur pada hari Rabu
    libur = CalendarException(
        tanggal_mulai=RABU,
        tanggal_selesai=RABU,
        tipe="libur",
        keterangan="Libur Nasional Uji",
    )
    db_session.add(libur)

    # Log Okupansi ruang_a:
    # SENIN:
    # - Terisi selama sesi: 08.00 s.d. 09.30 (9 slot = 90 menit)
    dt_slot = datetime.combine(SENIN, time(8, 0))
    for _ in range(9):
        _tambah_slot(db_session, ruang_a.id, dt_slot, is_occupied=True)
        dt_slot += timedelta(minutes=10)
    # Sisa slot sesi (09.30, 09.40, 09.50) tidak terisi
    for _ in range(3):
        _tambah_slot(db_session, ruang_a.id, dt_slot, is_occupied=False)
        dt_slot += timedelta(minutes=10)

    # - Episode luar jadwal: 14.00 s.d. 14.40 (4 slot = 40 menit terisi)
    dt_ep = datetime.combine(SENIN, time(14, 0))
    for _ in range(4):
        _tambah_slot(db_session, ruang_a.id, dt_ep, is_occupied=True)
        dt_ep += timedelta(minutes=10)

    # SELASA:
    # Sesi kosong (seluruh slot 08.00 s.d. 10.00 tidak terisi)
    dt_selasa = datetime.combine(SELASA, time(8, 0))
    for _ in range(12):
        _tambah_slot(db_session, ruang_a.id, dt_selasa, is_occupied=False)
        dt_selasa += timedelta(minutes=10)

    # RABU (Libur):
    # Okupansi pada hari libur: 10.00 s.d. 10.40 (4 slot = 40 menit terisi)
    # Karena hari libur, sesi diabaikan dan seluruh pemakaian menjadi episode luar jadwal.
    dt_rabu = datetime.combine(RABU, time(10, 0))
    for _ in range(4):
        _tambah_slot(db_session, ruang_a.id, dt_rabu, is_occupied=True)
        dt_rabu += timedelta(minutes=10)

    db_session.flush()
    return ruang_a, ruang_b, j_senin, j_selasa, j_rabu


def test_hasil_klasifikasi_sesuai_ekspektasi(db_session):
    """Memverifikasi hasil 1 sesi terisi, 1 kosong, 1 episode luar jadwal, dan 1 hari libur."""
    ruang_a, ruang_b, j_senin, j_selasa, j_rabu = _siapkan_data_uji(db_session)

    ringkasan = jalankan_klasifikasi(
        session=db_session,
        tanggal_mulai=SENIN,
        tanggal_selesai=RABU,
        waktu_evaluasi=WAKTU_EVAL_AKHIR,
        computed_at=COMPUTED_AT_TEST,
    )

    # Ekspektasi:
    # Senin: 1 sesi (sesuai_jadwal) + 1 episode (dipakai_di_luar_jadwal)
    # Selasa: 1 sesi (kosong_meski_terjadwal)
    # Rabu: 0 sesi (libur) + 1 episode (dipakai_di_luar_jadwal)
    # Ruang B: 0 baris
    # Total: 4 baris
    assert ringkasan.total_baris == 4
    assert ringkasan.jumlah_baris_per_status["sesuai_jadwal"] == 1
    assert ringkasan.jumlah_baris_per_status["kosong_meski_terjadwal"] == 1
    assert ringkasan.jumlah_baris_per_status["dipakai_di_luar_jadwal"] == 2

    # Verifikasi baris di database
    rows = (
        db_session.query(ClassificationResult)
        .filter(ClassificationResult.room_id == ruang_a.id)
        .order_by(ClassificationResult.tanggal, ClassificationResult.waktu_mulai)
        .all()
    )
    assert len(rows) == 4

    # 1. Senin - Sesi sesuai_jadwal
    r1 = rows[0]
    assert r1.tanggal == SENIN
    assert r1.schedule_id == j_senin.id
    assert r1.status == "sesuai_jadwal"
    assert r1.menit_terjadwal == 120
    assert r1.menit_terpakai == 90
    assert r1.utilisasi_pct == Decimal("75.00")

    # 2. Senin - Episode luar jadwal
    r2 = rows[1]
    assert r2.tanggal == SENIN
    assert r2.schedule_id is None
    assert r2.status == "dipakai_di_luar_jadwal"
    assert r2.waktu_mulai == time(14, 0)
    assert r2.waktu_selesai == time(14, 40)
    assert r2.menit_terjadwal == 0
    assert r2.menit_terpakai == 40
    assert r2.utilisasi_pct is None

    # 3. Selasa - Sesi kosong_meski_terjadwal
    r3 = rows[2]
    assert r3.tanggal == SELASA
    assert r3.schedule_id == j_selasa.id
    assert r3.status == "kosong_meski_terjadwal"
    assert r3.menit_terjadwal == 120
    assert r3.menit_terpakai == 0
    assert r3.utilisasi_pct == Decimal("0.00")

    # 4. Rabu - Episode luar jadwal pada hari libur
    r4 = rows[3]
    assert r4.tanggal == RABU
    assert r4.schedule_id is None
    assert r4.status == "dipakai_di_luar_jadwal"
    assert r4.waktu_mulai == time(10, 0)
    assert r4.waktu_selesai == time(10, 40)
    assert r4.menit_terjadwal == 0
    assert r4.menit_terpakai == 40
    assert r4.utilisasi_pct is None


def test_menjalankan_dua_kali_tidak_menggandakan_baris(db_session):
    """Memverifikasi idempotensi: menjalankan runner dua kali menghasilkan jumlah dan isi identik."""
    ruang_a, _, _, _, _ = _siapkan_data_uji(db_session)

    for _ in range(2):
        ringkasan = jalankan_klasifikasi(
            session=db_session,
            tanggal_mulai=SENIN,
            tanggal_selesai=RABU,
            waktu_evaluasi=WAKTU_EVAL_AKHIR,
            computed_at=COMPUTED_AT_TEST,
        )
        assert ringkasan.total_baris == 4

    count = (
        db_session.query(ClassificationResult)
        .filter(ClassificationResult.room_id == ruang_a.id)
        .count()
    )
    assert count == 4


def test_ruang_tanpa_data_tidak_menghasilkan_galat(db_session):
    """Ruang tanpa jadwal dan tanpa log okupansi tidak menimbulkan galat dan menghasilkan 0 baris."""
    _siapkan_ambang(db_session)
    ruang_kosong = Room(nama_ruangan="RUANG-KOSONG", status="tersedia")
    db_session.add(ruang_kosong)
    db_session.flush()

    ringkasan = jalankan_klasifikasi(
        session=db_session,
        tanggal_mulai=SENIN,
        tanggal_selesai=RABU,
        waktu_evaluasi=WAKTU_EVAL_AKHIR,
        daftar_room_id=[ruang_kosong.id],
    )
    assert ringkasan.total_baris == 0
    assert ringkasan.jumlah_ruang == 1


def test_daftar_room_id_membatasi_ruang(db_session):
    """Hanya ruang yang tercantum di daftar_room_id yang dihitung dan diubah."""
    ruang_a, ruang_b, _, _, _ = _siapkan_data_uji(db_session)

    # Jalankan hanya untuk ruang_b
    ringkasan = jalankan_klasifikasi(
        session=db_session,
        tanggal_mulai=SENIN,
        tanggal_selesai=RABU,
        waktu_evaluasi=WAKTU_EVAL_AKHIR,
        daftar_room_id=[ruang_b.id],
    )
    assert ringkasan.total_baris == 0

    count_a = (
        db_session.query(ClassificationResult)
        .filter(ClassificationResult.room_id == ruang_a.id)
        .count()
    )
    assert count_a == 0


def test_sesi_belum_berakhir_pada_waktu_evaluasi_tidak_ditulis(db_session):
    """Sesi perkuliahan yang belum selesai pada waktu_evaluasi tidak ditulis (DATA_CONTRACT 7.1)."""
    ruang_a, _, _, _, _ = _siapkan_data_uji(db_session)

    # Waktu evaluasi Senin pukul 09.00 (sesi Senin selesai pukul 10.00)
    waktu_eval_pagi = datetime.combine(SENIN, time(9, 0))

    ringkasan = jalankan_klasifikasi(
        session=db_session,
        tanggal_mulai=SENIN,
        tanggal_selesai=SENIN,
        waktu_evaluasi=waktu_eval_pagi,
    )
    # Sesi belum selesai -> tidak menghasilkan baris sesi.
    # Episode luar jadwal 14.00 juga setelah 09.00 -> tidak menghasilkan baris episode.
    assert ringkasan.total_baris == 0


def test_semua_baris_tulis_memenuhi_invarian_bagian_5(db_session):
    """Setiap baris yang ditulis wajib mematuhi seluruh invarian DATA_CONTRACT Bagian 5."""
    _siapkan_data_uji(db_session)

    jalankan_klasifikasi(
        session=db_session,
        tanggal_mulai=SENIN,
        tanggal_selesai=RABU,
        waktu_evaluasi=WAKTU_EVAL_AKHIR,
    )

    semua_baris = db_session.query(ClassificationResult).all()
    assert len(semua_baris) > 0

    for b in semua_baris:
        # Invarian 1: status == 'dipakai_di_luar_jadwal' <=> schedule_id IS NULL
        if b.status == "dipakai_di_luar_jadwal":
            assert b.schedule_id is None
            # Invarian 3: episode luar jadwal
            assert b.menit_terjadwal == 0
            assert b.utilisasi_pct is None
            assert b.menit_terpakai >= 30  # outside_schedule_min_minutes
        else:
            assert b.schedule_id is not None
            # Invarian 2: baris sesi perkuliahan
            assert 0 <= b.menit_terpakai <= b.menit_terjadwal
            assert b.menit_terjadwal > 0
            assert b.utilisasi_pct is not None
