"""Lapisan repositori untuk membaca master data dan menulis occupancy_logs (SS1-08).

Menjamin isolasi database pengujian dan idempotensi penulisan dalam satu transaksi.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.generator.simulator import ObservedSlot
from app.models import CalendarException, OccupancyLog, Room, Schedule

ALLOWED_DATABASES: frozenset[str] = frozenset({"smart_space_ai_dev", "smart_space_ai_test"})


def resolve_database_url(
    target_set: str | None = None,
    allow_any_database: bool = False,
    override_db_name: str | None = None,
) -> tuple[str, str]:
    """Membangun database URL dari .env dan memvalidasi pengaman nama basis data.

    Mengembalikan tuple (target_url, active_db).
    """
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    env_config = dotenv_values(env_path) if env_path.exists() else {}

    raw_url = os.environ.get("DATABASE_URL") or env_config.get("DATABASE_URL")

    if override_db_name:
        target_db = override_db_name
    elif target_set == "dev":
        target_db = "smart_space_ai_dev"
    elif target_set == "test":
        target_db = "smart_space_ai_test"
    else:
        target_db = os.environ.get("DB_DATABASE") or env_config.get("DB_DATABASE", "smart_space_ai_dev")

    # Validasi pengaman nama database
    if target_db not in ALLOWED_DATABASES and not allow_any_database:
        allowed_list = sorted(list(ALLOWED_DATABASES))
        raise ValueError(
            f"PENGAMAN AKTIF: Penulisan ke database '{target_db}' ditolak. "
            f"Database yang diizinkan untuk generator hanya: {allowed_list}. "
            "Database aplikasi 'smart_space' tidak boleh tersentuh secara default. "
            "Gunakan flag --allow-any-database bila benar-benar bermaksud menulis ke database ini."
        )

    if raw_url:
        parsed = make_url(raw_url)
        target_url = parsed.set(database=target_db).render_as_string(hide_password=False)
    else:
        db_user = os.environ.get("DB_USERNAME") or env_config.get("DB_USERNAME", "root")
        db_password = os.environ.get("DB_PASSWORD") or env_config.get("DB_PASSWORD", "")
        db_host = os.environ.get("DB_HOST") or env_config.get("DB_HOST", "127.0.0.1")
        db_port = os.environ.get("DB_PORT") or env_config.get("DB_PORT", "3306")
        if db_password:
            target_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{target_db}"
        else:
            target_url = f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{target_db}"

    return target_url, target_db


def create_db_session_factory(db_url: str) -> tuple[Engine, sessionmaker]:
    """Membuat SQLAlchemy engine dan sessionmaker untuk koneksi target."""
    engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600, echo=False)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session_factory


def load_master_data(session: Session) -> tuple[list[Room], list[Schedule], list[CalendarException]]:
    """Membaca data master rooms, schedules, dan calendar_exceptions."""
    rooms = session.query(Room).order_by(Room.id).all()
    schedules = session.query(Schedule).order_by(Schedule.id).all()
    exceptions = session.query(CalendarException).order_by(CalendarException.tanggal_mulai).all()
    return rooms, schedules, exceptions


def save_occupancy_logs_idempotent(
    session: Session,
    observed_slots: Sequence[ObservedSlot],
    room_ids: Sequence[int],
    min_dt: datetime,
    max_dt: datetime,
    batch_size: int = 5000,
) -> int:
    """Menyimpan data occupancy_logs secara idempoten dalam satu transaksi.

    Aturan:
    1. Hapus baris lama dengan source='dummy' pada ruang dan rentang tanggal yang diproses.
    2. Masukkan baris baru secara batch (default 5000 baris per batch).
    3. Mengembalikan jumlah baris yang berhasil disimpan.
    """
    if not room_ids or not observed_slots:
        return 0

    # Hapus log dummy lama pada rentang waktu dan daftar ruang ini
    session.query(OccupancyLog).filter(
        OccupancyLog.source == "dummy",
        OccupancyLog.room_id.in_(room_ids),
        OccupancyLog.slot_mulai >= min_dt,
        OccupancyLog.slot_mulai <= max_dt,
    ).delete(synchronize_session=False)

    mappings = [
        {
            "room_id": slot.room_id,
            "slot_mulai": slot.slot_mulai,
            "is_occupied": slot.is_occupied,
            "source": slot.source,
        }
        for slot in observed_slots
    ]

    total_inserted = 0
    for i in range(0, len(mappings), batch_size):
        batch = mappings[i : i + batch_size]
        session.bulk_insert_mappings(OccupancyLog, batch)
        total_inserted += len(batch)

    session.commit()
    return total_inserted
