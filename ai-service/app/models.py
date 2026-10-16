from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Numeric,
    Boolean,
    String,
    Text,
    Time,
    Date,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Room(Base):
    """Room model mapped to shared Laravel MySQL table 'rooms'."""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama_ruangan = Column(String(50), unique=True, nullable=False, index=True)
    kapasitas = Column(Integer, nullable=True)
    lokasi = Column(String(100), nullable=True)
    status = Column(String(50), default="tersedia")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    schedules = relationship("Schedule", back_populates="room")

    def __repr__(self):
        return f"<Room(id={self.id}, nama='{self.nama_ruangan}', kapasitas={self.kapasitas}, lokasi='{self.lokasi}', status='{self.status}')>"


class Schedule(Base):
    """Schedule model mapped to shared Laravel MySQL table 'schedules'."""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    hari = Column(String(20), nullable=False)
    jam_mulai = Column(Time, nullable=False)
    jam_selesai = Column(Time, nullable=False)
    mata_kuliah = Column(String(255), nullable=False)
    kelas = Column(String(50), nullable=True)
    dosen = Column(String(100), nullable=True)
    shift = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    room = relationship("Room", back_populates="schedules")


class ThresholdSetting(Base):
    """Threshold settings mapped to shared Laravel MySQL table 'threshold_settings'."""
    __tablename__ = "threshold_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    keterangan = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class CalendarException(Base):
    """Academic calendar exceptions mapped to table 'calendar_exceptions'."""
    __tablename__ = "calendar_exceptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_selesai = Column(Date, nullable=False)
    tipe = Column(String(50), nullable=False)
    keterangan = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class OccupancyLog(Base):
    """Occupancy log mapped to shared Laravel MySQL table 'occupancy_logs'."""
    __tablename__ = "occupancy_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    slot_mulai = Column(DateTime, nullable=False, index=True)
    is_occupied = Column(Boolean, nullable=False)
    source = Column(String(20), nullable=False, default="dummy")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("room_id", "slot_mulai", name="uq_occupancy_logs_room_slot"),
    )

    room = relationship("Room")

    def __repr__(self):
        return f"<OccupancyLog(id={self.id}, room_id={self.room_id}, slot_mulai='{self.slot_mulai}', is_occupied={self.is_occupied}, source='{self.source}')>"


class ClassificationResult(Base):
    """Classification result mapped to shared Laravel MySQL table 'classification_results'."""
    __tablename__ = "classification_results"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(BigInteger, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=True)
    tanggal = Column(Date, nullable=False)
    waktu_mulai = Column(Time, nullable=False)
    waktu_selesai = Column(Time, nullable=False)
    status = Column(String(30), nullable=False, index=True)
    menit_terjadwal = Column(SmallInteger, nullable=False)
    menit_terpakai = Column(SmallInteger, nullable=False)
    utilisasi_pct = Column(Numeric(5, 2), nullable=True)
    rule_id = Column(String(10), nullable=False)
    penjelasan = Column(Text, nullable=False)
    computed_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("room_id", "tanggal", "waktu_mulai", name="uq_classification_room_tanggal_mulai"),
        Index("idx_classification_tanggal_room", "tanggal", "room_id"),
    )

    room = relationship("Room")
    schedule = relationship("Schedule")

    def __repr__(self):
        return f"<ClassificationResult(id={self.id}, room_id={self.room_id}, schedule_id={self.schedule_id}, tanggal='{self.tanggal}', status='{self.status}', utilisasi_pct={self.utilisasi_pct})>"
