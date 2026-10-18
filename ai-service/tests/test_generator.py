"""Pengujian unit dan integrasi untuk generator data dummy okupansi (SS1-08).

Mencakup 8 aspek pengujian:
1. Determinisme seed dan independensi rentang tanggal
2. Validitas grid waktu (10 menit, 07.00-22.50, tanpa 17.00, tanpa duplikat)
3. Perilaku hari libur (tanpa sesi, hanya episode)
4. Distribusi skenario pada sampel besar & tidak_hadir menghasilkan kosong_meski_terjadwal
5. Episode di luar jadwal (di luar jendela, durasi >= 30, tanpa 17.00, open-space > reguler)
6. Laju noise sensor (salah deteksi ~1%, slot hilang ~2%)
7. Idempotensi penulisan ke database (rollback di smart_space_test)
8. Pengaman database (menolak database di luar dev/test kecuali allow_any_database)
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Sequence
import pytest

from app.generator.calendar_kind import resolve_day_kind
from app.generator.ground_truth import GroundTruthRow, write_ground_truth_csv
from app.generator.params import (
    DEV_SEED,
    TEST_SEED,
    STATUS_KOSONG_TERJADWAL,
    STATUS_LUAR_JADWAL,
    STATUS_SESUAI_JADWAL,
    GeneratorParams,
)
from app.generator.repository import (
    resolve_database_url,
    save_occupancy_logs_idempotent,
)
from app.generator.simulator import (
    DayResult,
    ObservedSlot,
    build_operational_slots,
    simulate_room_day,
)
from app.models import OccupancyLog, Room


@dataclass
class MockRoom:
    id: int
    nama_ruangan: str


@dataclass
class MockSchedule:
    id: int
    room_id: int
    hari: str
    jam_mulai: time
    jam_selesai: time


@dataclass
class MockCalendarException:
    tanggal_mulai: date
    tanggal_selesai: date
    tipe: str


@pytest.fixture
def sample_params():
    return GeneratorParams()


@pytest.fixture
def mock_room_regular():
    return MockRoom(id=1, nama_ruangan="GU 604")


@pytest.fixture
def mock_room_open():
    return MockRoom(id=2, nama_ruangan="GU 701")


@pytest.fixture
def mock_schedules():
    return [
        MockSchedule(
            id=101,
            room_id=1,
            hari="Senin",
            jam_mulai=time(7, 50),
            jam_selesai=time(11, 10),
        ),
        MockSchedule(
            id=102,
            room_id=1,
            hari="Senin",
            jam_mulai=time(13, 40),
            jam_selesai=time(17, 0),
        ),
        MockSchedule(
            id=103,
            room_id=1,
            hari="Senin",
            jam_mulai=time(18, 0),
            jam_selesai=time(20, 30),
        ),
    ]


# ------------------------------------------------------------------------------
# 1. Determinisme seed dan independensi rentang tanggal
# ------------------------------------------------------------------------------
def test_determinism_same_seed_produces_identical_results(
    mock_room_regular, mock_schedules, sample_params, tmp_path
):
    d = date(2026, 9, 7)  # Senin
    res1 = simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed=1001)
    res2 = simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed=1001)

    assert res1.observed_slots == res2.observed_slots
    assert res1.ground_truth_rows == res2.ground_truth_rows

    # Seed berbeda menghasilkan keluaran berbeda
    res_diff = simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed=2002)
    assert res1.observed_slots != res_diff.observed_slots

    # CSV output identik untuk data yang sama
    csv_file1 = tmp_path / "gt1.csv"
    csv_file2 = tmp_path / "gt2.csv"
    write_ground_truth_csv(res1.ground_truth_rows, csv_file1)
    write_ground_truth_csv(res2.ground_truth_rows, csv_file2)
    assert csv_file1.read_text(encoding="utf-8") == csv_file2.read_text(encoding="utf-8")


def test_determinism_single_date_independent_of_range(mock_room_regular, mock_schedules, sample_params):
    target_date = date(2026, 9, 9)  # Rabu
    seed = 1001

    # Simulasi hanya target_date
    res_isolated = simulate_room_day(mock_room_regular, mock_schedules, target_date, "biasa", sample_params, seed)

    # Simulasi urutan beberapa tanggal
    days = [date(2026, 9, 7), date(2026, 9, 8), date(2026, 9, 9)]
    results = [
        simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed)
        for d in days
    ]

    assert res_isolated.observed_slots == results[2].observed_slots
    assert res_isolated.ground_truth_rows == results[2].ground_truth_rows


# ------------------------------------------------------------------------------
# 2. Validitas grid waktu
# ------------------------------------------------------------------------------
def test_grid_no_break_slot_and_10_minute_multiples(mock_room_regular, mock_schedules, sample_params):
    for day_offset in range(5):  # Senin-Jumat
        d = date(2026, 9, 7) + timedelta(days=day_offset)
        res = simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed=1001)

        slots = res.observed_slots
        # Tidak ada slot pada jam 17.00
        for slot in slots:
            assert not (slot.slot_mulai.hour == 17 and slot.slot_mulai.minute == 0)
            assert slot.slot_mulai.minute % 10 == 0
            assert 7 <= slot.slot_mulai.hour <= 22

        # Kunci unik: tidak ada duplikat (room_id, slot_mulai)
        keys = [(s.room_id, s.slot_mulai) for s in slots]
        assert len(keys) == len(set(keys))


# ------------------------------------------------------------------------------
# 3. Perilaku hari libur
# ------------------------------------------------------------------------------
def test_holiday_no_session_ground_truth(mock_room_regular, mock_schedules, sample_params):
    d = date(2026, 9, 7)  # Senin tapi disimulasikan libur
    res = simulate_room_day(mock_room_regular, mock_schedules, d, "libur", sample_params, seed=1001)

    # Semua ground truth di hari libur HANYA episode pemakaian luar jadwal
    for gt in res.ground_truth_rows:
        assert gt.schedule_id is None
        assert gt.status_benar == STATUS_LUAR_JADWAL


# ------------------------------------------------------------------------------
# 4. Distribusi skenario pada sampel besar & tidak_hadir -> kosong_meski_terjadwal
# ------------------------------------------------------------------------------
def test_scenario_distribution_and_absent_empty_status(mock_room_regular, mock_schedules, sample_params):
    single_schedule = [
        MockSchedule(
            id=101,
            room_id=1,
            hari="Senin",
            jam_mulai=time(8, 0),
            jam_selesai=time(11, 0),
        )
    ]
    # Jalankan 3000 hari simulasi dengan seed tetap
    counts = Counter()
    total_samples = 3000

    for i in range(total_samples):
        d = date(2026, 9, 7)
        res = simulate_room_day(mock_room_regular, single_schedule, d, "biasa", sample_params, seed=i + 5000)
        session_gt = [g for g in res.ground_truth_rows if g.schedule_id == 101]
        assert len(session_gt) == 1
        gt = session_gt[0]
        counts[gt.penyebab] += 1

        # Verifikasi: tidak_hadir SELALU menghasilkan kosong_meski_terjadwal
        if gt.penyebab == "tidak_hadir":
            assert gt.status_benar == STATUS_KOSONG_TERJADWAL

    # Evaluasi proporsi mendekati parameter (biasa: 0.78, 0.08, 0.06, 0.06, 0.02)
    p_kelas = counts["kelas_berlangsung"] / total_samples
    p_terlambat = counts["terlambat"] / total_samples
    p_selesai = counts["selesai_awal"] / total_samples
    p_absen = counts["tidak_hadir"] / total_samples
    p_pinjam = counts["dipinjam_kegiatan_lain"] / total_samples

    # Toleransi ±3%
    assert 0.75 <= p_kelas <= 0.81
    assert 0.05 <= p_terlambat <= 0.11
    assert 0.04 <= p_selesai <= 0.08
    assert 0.04 <= p_absen <= 0.08
    assert 0.01 <= p_pinjam <= 0.035


# ------------------------------------------------------------------------------
# 5. Episode di luar jadwal
# ------------------------------------------------------------------------------
def test_outside_schedule_episodes_rules_and_open_space_frequency(
    mock_room_regular, mock_room_open, mock_schedules, sample_params
):
    regular_episodes = 0
    open_episodes = 0
    n_days = 2000

    for i in range(n_days):
        d = date(2026, 9, 7)
        # Ruang reguler
        res_reg = simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed=i + 10000)
        for gt in res_reg.ground_truth_rows:
            if gt.schedule_id is None:
                regular_episodes += 1
                # Validasi: durasi >= 30 menit
                dur_minutes = (
                    datetime.combine(d, gt.waktu_selesai) - datetime.combine(d, gt.waktu_mulai)
                ).total_seconds() / 60
                assert dur_minutes >= 30

                # Validasi: episode tidak melewati slot jeda 17.00
                assert not (gt.waktu_mulai < time(17, 10) and gt.waktu_selesai > time(17, 0))

        # Ruang open-space
        res_open = simulate_room_day(mock_room_open, mock_schedules, d, "biasa", sample_params, seed=i + 10000)
        for gt in res_open.ground_truth_rows:
            if gt.schedule_id is None:
                open_episodes += 1

    # Ruang open-space memiliki frekuensi episode lebih tinggi daripada ruang biasa
    assert open_episodes > regular_episodes
    # Open-space memiliki prob 0.10 vs regular 0.03 (rasio teoritis ~3.3x)
    assert open_episodes >= 2.0 * regular_episodes


# ------------------------------------------------------------------------------
# 6. Laju noise sensor
# ------------------------------------------------------------------------------
def test_noise_rates_on_large_sample(mock_room_regular, mock_schedules, sample_params):
    total_expected_slots = 0
    total_observed_slots = 0
    total_flipped_slots = 0

    n_days = 100
    for i in range(n_days):
        d = date(2026, 9, 7)
        res = simulate_room_day(mock_room_regular, mock_schedules, d, "biasa", sample_params, seed=i + 20000)

        actual_map = {s.slot_mulai: s.is_occupied for s in res.actual_slots}
        observed_map = {s.slot_mulai: s.is_occupied for s in res.observed_slots}

        total_expected_slots += len(actual_map)
        total_observed_slots += len(observed_map)

        for slot_dt, is_occ in observed_map.items():
            if is_occ != actual_map[slot_dt]:
                total_flipped_slots += 1

    # Missing rate ~ 2%
    missing_count = total_expected_slots - total_observed_slots
    missing_rate = missing_count / total_expected_slots
    assert 0.015 <= missing_rate <= 0.025

    # Flip / detection error rate ~ 1% dari observed slots
    flip_rate = total_flipped_slots / total_observed_slots
    assert 0.007 <= flip_rate <= 0.014


# ------------------------------------------------------------------------------
# 7. Penulisan DB idempoten (smart_space_test dengan rollback)
# ------------------------------------------------------------------------------
def test_database_idempotent_write(db_session, sample_params):
    # Pastikan minimal ada 1 room di db_session
    room = db_session.query(Room).first()
    if not room:
        room = Room(id=999, nama_ruangan="TEST_ROOM")
        db_session.add(room)
        db_session.commit()

    room_id = room.id
    target_date = date(2026, 9, 7)

    # Buat slot simulasi
    slots = [
        ObservedSlot(
            room_id=room_id,
            slot_mulai=datetime(2026, 9, 7, 8, 0),
            is_occupied=True,
            source="dummy",
        ),
        ObservedSlot(
            room_id=room_id,
            slot_mulai=datetime(2026, 9, 7, 8, 10),
            is_occupied=True,
            source="dummy",
        ),
    ]

    min_dt = datetime(2026, 9, 7, 0, 0)
    max_dt = datetime(2026, 9, 7, 23, 59)

    # Tulis pertama kali
    inserted1 = save_occupancy_logs_idempotent(
        db_session, slots, [room_id], min_dt, max_dt
    )
    assert inserted1 == 2

    count1 = (
        db_session.query(OccupancyLog)
        .filter(OccupancyLog.room_id == room_id, OccupancyLog.slot_mulai >= min_dt)
        .count()
    )
    assert count1 == 2

    # Tulis kedua kali untuk rentang yang sama (harus menimpa, bukan menduplikasi)
    inserted2 = save_occupancy_logs_idempotent(
        db_session, slots, [room_id], min_dt, max_dt
    )
    assert inserted2 == 2

    count2 = (
        db_session.query(OccupancyLog)
        .filter(OccupancyLog.room_id == room_id, OccupancyLog.slot_mulai >= min_dt)
        .count()
    )
    assert count2 == 2


# ------------------------------------------------------------------------------
# 8. Tolak nama database di luar daftar yang diizinkan
# ------------------------------------------------------------------------------
def test_reject_unauthorized_database():
    # Menolak database aplikasi smart_space tanpa allow_any_database
    with pytest.raises(ValueError, match="PENGAMAN AKTIF"):
        resolve_database_url(override_db_name="smart_space", allow_any_database=False)

    with pytest.raises(ValueError, match="PENGAMAN AKTIF"):
        resolve_database_url(override_db_name="smart_space_production", allow_any_database=False)

    # Mengizinkan database dev dan test resmi
    url_dev, db_dev = resolve_database_url(target_set="dev")
    assert db_dev == "smart_space_ai_dev"

    url_test, db_test = resolve_database_url(target_set="test")
    assert db_test == "smart_space_ai_test"

    # Mengizinkan database lain hanya bila allow_any_database=True
    url_override, db_override = resolve_database_url(
        override_db_name="smart_space_custom", allow_any_database=True
    )
    assert db_override == "smart_space_custom"
