"""Runner eksekusi klasifikasi status ruangan (SS1-11).

Mengorkestrasi pembacaan master data dan log okupansi dalam satu transaksi,
menjalankan evaluasi harian sistem pakar, dan menyimpan hasilnya secara idempoten.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable, Sequence

from sqlalchemy.orm import Session

from app.classification.pemuat import muat_ambang
from app.classification.penyimpan import simpan_hasil_idempoten
from app.expert_system.klasifikasi import klasifikasikan_hari
from app.expert_system.tipe import (
    Ambang,
    FaktaJadwal,
    FaktaRuang,
    HasilKlasifikasi,
    SlotOkupansi,
)
from app.generator.calendar_kind import resolve_day_kind
from app.generator.params import NAMA_OPEN_SPACE
from app.models import CalendarException, OccupancyLog, Room, Schedule

WIB = timezone(timedelta(hours=7))


def waktu_sekarang_wib() -> datetime:
    """Mengembalikan waktu saat ini dalam WIB (UTC+7) tanpa komponen zona (naive WIB)."""
    return datetime.now(WIB).replace(tzinfo=None)


@dataclass(frozen=True)
class RingkasanKlasifikasi:
    """Ringkasan eksekusi runner klasifikasi status ruangan."""

    jumlah_baris_per_status: dict[str, int]
    total_baris: int
    jumlah_ruang: int
    tanggal_mulai: date
    tanggal_selesai: date


def jalankan_klasifikasi(
    session: Session,
    tanggal_mulai: date,
    tanggal_selesai: date,
    waktu_evaluasi: datetime,
    daftar_room_id: Iterable[int] | None = None,
    simpan: bool = True,
    computed_at: datetime | None = None,
) -> RingkasanKlasifikasi:
    """Menjalankan klasifikasi status ruangan untuk rentang tanggal tertentu.

    Langkah-langkah:
    1. Memvalidasi rentang tanggal.
    2. Memuat master ruangan, jadwal, kalender akademik, dan log okupansi secara efisien
       (satu kueri per tabel untuk seluruh rentang tanggal, dikelompokkan di memori).
    3. Mengonversi data ke FaktaRuang, FaktaJadwal, dan SlotOkupansi.
    4. Mengambil Ambang batas via muat_ambang.
    5. Menjalankan klasifikasikan_hari per ruang per tanggal secara berurutan.
    6. Menyimpan hasil klasifikasi ke tabel classification_results via simpan_hasil_idempoten.
       CATATAN: Fungsi ini TIDAK melakukan commit transaksi. Pemanggil (CLI atau handler API)
       yang bertanggung jawab melakukan commit atau rollback.

    Returns:
        RingkasanKlasifikasi berisi rekap baris per status, total baris, jumlah ruang, dan rentang.
    """
    if tanggal_mulai > tanggal_selesai:
        raise ValueError(
            f"tanggal_mulai ({tanggal_mulai}) tidak boleh setelah tanggal_selesai ({tanggal_selesai})."
        )

    # 1. Tentukan target ruangan
    query_room = session.query(Room)
    if daftar_room_id is not None:
        room_ids_target = sorted(list(set(daftar_room_id)))
        if not room_ids_target:
            rooms = []
        else:
            rooms = query_room.filter(Room.id.in_(room_ids_target)).order_by(Room.id).all()
    else:
        rooms = query_room.order_by(Room.id).all()
        room_ids_target = [r.id for r in rooms]

    # Ubah ke FaktaRuang
    fakta_ruang_list: list[FaktaRuang] = [
        FaktaRuang(
            room_id=r.id,
            nama_ruangan=r.nama_ruangan,
            is_open_space=r.nama_ruangan in NAMA_OPEN_SPACE,
        )
        for r in rooms
    ]

    target_room_ids_existing = [r.id for r in rooms]

    # 2. Muat jadwal terjadwal (satu kueri untuk seluruh ruang sasaran)
    schedules_by_room: dict[int, list[FaktaJadwal]] = defaultdict(list)
    if target_room_ids_existing:
        schedules = (
            session.query(Schedule)
            .filter(Schedule.room_id.in_(target_room_ids_existing))
            .order_by(Schedule.jam_mulai)
            .all()
        )
        for s in schedules:
            schedules_by_room[s.room_id].append(
                FaktaJadwal(
                    schedule_id=s.id,
                    room_id=s.room_id,
                    hari=s.hari,
                    jam_mulai=s.jam_mulai,
                    jam_selesai=s.jam_selesai,
                    mata_kuliah=s.mata_kuliah,
                )
            )

    # 3. Muat pengecualian kalender (satu kueri untuk rentang tanggal)
    calendar_exceptions = (
        session.query(CalendarException)
        .filter(
            CalendarException.tanggal_mulai <= tanggal_selesai,
            CalendarException.tanggal_selesai >= tanggal_mulai,
        )
        .order_by(CalendarException.tanggal_mulai)
        .all()
    )

    # Pre-resolve jenis hari libur per tanggal
    holiday_by_date: dict[date, bool] = {}
    curr = tanggal_mulai
    delta = timedelta(days=1)
    while curr <= tanggal_selesai:
        holiday_by_date[curr] = resolve_day_kind(curr, calendar_exceptions) == "libur"
        curr += delta

    # 4. Muat log okupansi (satu kueri efisien untuk seluruh rentang dan seluruh ruang sasaran)
    logs_by_room_and_date: dict[tuple[int, date], list[SlotOkupansi]] = defaultdict(list)
    if target_room_ids_existing:
        min_dt = datetime.combine(tanggal_mulai, time.min)
        max_dt = datetime.combine(tanggal_selesai, time.max)
        logs = (
            session.query(OccupancyLog)
            .filter(
                OccupancyLog.room_id.in_(target_room_ids_existing),
                OccupancyLog.slot_mulai >= min_dt,
                OccupancyLog.slot_mulai <= max_dt,
            )
            .order_by(OccupancyLog.slot_mulai)
            .all()
        )
        for log in logs:
            log_date = log.slot_mulai.date()
            logs_by_room_and_date[(log.room_id, log_date)].append(
                SlotOkupansi(
                    room_id=log.room_id,
                    slot_mulai=log.slot_mulai,
                    is_occupied=log.is_occupied,
                )
            )

    # 5. Muat ambang batas sistem pakar
    ambang = muat_ambang(session)

    # 6. Jalankan inferensi sistem pakar per hari per ruang
    daftar_hasil: list[HasilKlasifikasi] = []
    curr = tanggal_mulai
    while curr <= tanggal_selesai:
        is_holiday = holiday_by_date[curr]
        for ruang in fakta_ruang_list:
            jadwal_ruang = schedules_by_room.get(ruang.room_id, [])
            slot_list = logs_by_room_and_date.get((ruang.room_id, curr), [])
            hasil_hari = klasifikasikan_hari(
                ruang=ruang,
                daftar_jadwal=jadwal_ruang,
                slot_list=slot_list,
                tanggal=curr,
                waktu_evaluasi=waktu_evaluasi,
                ambang=ambang,
                is_holiday=is_holiday,
            )
            daftar_hasil.extend(hasil_hari)
        curr += delta

    # 7. Simpan hasil secara idempoten jika diminta
    if simpan:
        waktu_catat = computed_at if computed_at is not None else waktu_sekarang_wib()
        simpan_hasil_idempoten(
            session=session,
            daftar_hasil=daftar_hasil,
            daftar_room_id=room_ids_target,
            tanggal_mulai=tanggal_mulai,
            tanggal_selesai=tanggal_selesai,
            computed_at=waktu_catat,
        )

    # 8. Susun ringkasan klasifikasi
    counter = Counter(h.status for h in daftar_hasil)
    jumlah_baris_per_status: dict[str, int] = {
        "sesuai_jadwal": counter["sesuai_jadwal"],
        "kosong_meski_terjadwal": counter["kosong_meski_terjadwal"],
        "dipakai_di_luar_jadwal": counter["dipakai_di_luar_jadwal"],
    }
    for st, cnt in counter.items():
        if st not in jumlah_baris_per_status:
            jumlah_baris_per_status[st] = cnt

    return RingkasanKlasifikasi(
        jumlah_baris_per_status=jumlah_baris_per_status,
        total_baris=len(daftar_hasil),
        jumlah_ruang=len(fakta_ruang_list),
        tanggal_mulai=tanggal_mulai,
        tanggal_selesai=tanggal_selesai,
    )
