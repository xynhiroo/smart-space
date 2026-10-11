from sqlalchemy import Column, Integer, String, Text, Time, Date, ForeignKey, DateTime
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
