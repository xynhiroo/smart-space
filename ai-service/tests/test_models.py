from datetime import date, datetime, time
import pytest
from app.models import (
    Room,
    Schedule,
    ThresholdSetting,
    CalendarException,
    OccupancyLog,
    ClassificationResult,
)


def test_occupancy_logs_empty_query(db_session):
    """Test that OccupancyLog model can query 'occupancy_logs' table without error."""
    logs = db_session.query(OccupancyLog).all()
    assert isinstance(logs, list)


def test_classification_results_empty_query(db_session):
    """Test that ClassificationResult model can query 'classification_results' table without error."""
    results = db_session.query(ClassificationResult).all()
    assert isinstance(results, list)


def test_occupancy_log_roundtrip_in_transaction(db_session):
    """Test inserting and querying OccupancyLog model with rollback to keep database clean."""
    room = db_session.query(Room).first()
    assert room is not None, "Tabel rooms harus memiliki data seeder"

    test_log = OccupancyLog(
        room_id=room.id,
        slot_mulai=datetime(2026, 10, 16, 8, 0, 0),
        is_occupied=True,
        source="dummy",
    )
    db_session.add(test_log)
    db_session.flush()

    queried = (
        db_session.query(OccupancyLog)
        .filter_by(room_id=room.id, slot_mulai=datetime(2026, 10, 16, 8, 0, 0))
        .first()
    )
    assert queried is not None
    assert queried.is_occupied is True
    assert queried.source == "dummy"
    assert queried.room.nama_ruangan == room.nama_ruangan

    db_session.rollback()


def test_classification_result_roundtrip_in_transaction(db_session):
    """Test inserting and querying ClassificationResult model with rollback to keep database clean."""
    room = db_session.query(Room).first()
    schedule = db_session.query(Schedule).first()
    assert room is not None and schedule is not None

    test_result = ClassificationResult(
        room_id=room.id,
        schedule_id=schedule.id,
        tanggal=date(2026, 10, 16),
        waktu_mulai=time(8, 0),
        waktu_selesai=time(9, 40),
        status="sesuai_jadwal",
        menit_terjadwal=100,
        menit_terpakai=80,
        utilisasi_pct=80.00,
        rule_id="R01",
        penjelasan="Ruang terisi 80 dari 100 menit terjadwal.",
        computed_at=datetime(2026, 10, 16, 10, 0, 0),
    )
    db_session.add(test_result)
    db_session.flush()

    queried = (
        db_session.query(ClassificationResult)
        .filter_by(room_id=room.id, tanggal=date(2026, 10, 16), waktu_mulai=time(8, 0))
        .first()
    )
    assert queried is not None
    assert queried.status == "sesuai_jadwal"
    assert queried.utilisasi_pct == 80.00
    assert queried.rule_id == "R01"
    assert queried.room.nama_ruangan == room.nama_ruangan

    db_session.rollback()


def test_threshold_settings_contains_updated_keys(db_session):
    """Verify that updated threshold settings keys are accessible via SQLAlchemy model."""
    empty_min = db_session.query(ThresholdSetting).filter_by(key="empty_min_occupied_minutes").first()
    outside_min = db_session.query(ThresholdSetting).filter_by(key="outside_schedule_min_minutes").first()
    obsolete_key = db_session.query(ThresholdSetting).filter_by(key="empty_status_use_start_tolerance").first()

    assert empty_min is not None
    assert empty_min.value == "10"
    assert outside_min is not None
    assert outside_min.value == "30"
    assert obsolete_key is None
