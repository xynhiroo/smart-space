"""Fungsi pembantu murni untuk pemrosesan slot okupansi dan episode (DATA_CONTRACT Bagian 7).

Modul ini deterministik, tidak mengakses database atau waktu sistem, dan tidak mengubah masukan.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable, Sequence

from app.expert_system.tipe import SlotOkupansi
from app.waktu_operasional import (
    JAM_BUKA_OPERASIONAL,
    JAM_JEDA,
    JAM_TUTUP_OPERASIONAL,
    MENIT_JEDA,
    MENIT_PER_SLOT,
    WAKTU_BUKA,
    WAKTU_TUTUP,
    generate_operational_slots,
    is_break_slot,
    is_operational_slot,
)


@dataclass(frozen=True)
class EpisodeLuarJadwal:
    """Representasi rangkaian slot terisi di luar jadwal yang telah memenuhi syarat ambang durasi."""

    tanggal: date
    waktu_mulai: time
    waktu_selesai: time
    durasi_menit: int


def hitung_menit_sesi(
    room_id: int,
    tanggal: date,
    jam_mulai: time,
    jam_selesai: time,
    slot_list: Iterable[SlotOkupansi],
    waktu_evaluasi: datetime,
) -> tuple[int, int]:
    """Menghitung menit terjadwal dan menit terpakai untuk satu sesi perkuliahan (Bagian 7.2).

    Aturan:
    - Hanya slot dalam [jam_mulai, jam_selesai) yang berada dalam jam operasional.
    - Slot jeda 17.00 tidak dihitung dalam menit terjadwal maupun menit terpakai.
    - Hanya slot dengan (slot_mulai + 10 menit <= waktu_evaluasi) yang dihitung.
    - Slot hilang diperlakukan sebagai tidak terisi (is_occupied = False).
    - Mengembalikan tuple (menit_terjadwal, menit_terpakai).
    """
    # Petakan slot untuk pencarian instan tanpa mutasi
    slot_map: dict[datetime, bool] = {
        s.slot_mulai: s.is_occupied
        for s in slot_list
        if s.room_id == room_id
    }

    menit_terjadwal = 0
    menit_terpakai = 0

    # Iterasi slot 10 menit dari jam_mulai sampai jam_selesai
    curr_dt = datetime.combine(tanggal, jam_mulai)
    end_dt = datetime.combine(tanggal, jam_selesai)
    step = timedelta(minutes=MENIT_PER_SLOT)

    while curr_dt < end_dt:
        slot_end = curr_dt + step
        # Periksa apakah slot telah selesai dievaluasi pada waktu_evaluasi
        if slot_end <= waktu_evaluasi and is_operational_slot(curr_dt):
            menit_terjadwal += MENIT_PER_SLOT
            if slot_map.get(curr_dt, False):
                menit_terpakai += MENIT_PER_SLOT
        curr_dt += step

    return menit_terjadwal, menit_terpakai


def kumpulkan_episode_luar_jadwal(
    room_id: int,
    tanggal: date,
    rentang_jadwal: Sequence[tuple[time, time]],
    slot_list: Iterable[SlotOkupansi],
    waktu_evaluasi: datetime,
    ambang_durasi_menit: int,
) -> list[EpisodeLuarJadwal]:
    """Membentuk rangkaian (episode) slot terisi di luar semua jadwal pada satu hari (Bagian 7.4).

    Aturan:
    1. Kumpulkan slot operasional di luar seluruh jendela jadwal ruang pada tanggal itu.
    2. Rangkaian berurutan dengan is_occupied = True diambil.
    3. Slot hilang, slot tidak terisi, slot jeda, dan batas jendela jadwal memutus rangkaian.
    4. Rangkaian dengan durasi >= ambang_durasi_menit dijadikan EpisodeLuarJadwal.
    5. Rangkaian yang lebih pendek diabaikan (noise filtering).
    """
    slot_map: dict[datetime, bool] = {
        s.slot_mulai: s.is_occupied
        for s in slot_list
        if s.room_id == room_id
    }

    # Semua slot operasional standar pada hari tersebut
    operational_times = generate_operational_slots()
    step = timedelta(minutes=MENIT_PER_SLOT)

    episodes: list[EpisodeLuarJadwal] = []
    current_run: list[datetime] = []

    def _simpan_run_jika_memenuhi():
        if not current_run:
            return
        durasi = len(current_run) * MENIT_PER_SLOT
        if durasi >= ambang_durasi_menit:
            w_mulai = current_run[0].time()
            w_selesai = (current_run[-1] + step).time()
            episodes.append(
                EpisodeLuarJadwal(
                    tanggal=tanggal,
                    waktu_mulai=w_mulai,
                    waktu_selesai=w_selesai,
                    durasi_menit=durasi,
                )
            )

    for t in operational_times:
        slot_dt = datetime.combine(tanggal, t)
        slot_end = slot_dt + step

        # Slot harus sudah selesai sebelum atau tepat pada waktu evaluasi
        if slot_end > waktu_evaluasi:
            continue

        # Cek apakah slot berada di dalam salah satu jendela jadwal
        terjadwal = any(mulai <= t < selesai for mulai, selesai in rentang_jadwal)

        if terjadwal:
            # Batas jendela jadwal memutus rangkaian
            _simpan_run_jika_memenuhi()
            current_run = []
            continue

        is_occ = slot_map.get(slot_dt, False)

        if is_occ:
            if not current_run:
                current_run.append(slot_dt)
            else:
                # Periksa apakah berurutan langsung (tanpa celah/jeda)
                if current_run[-1] + step == slot_dt:
                    current_run.append(slot_dt)
                else:
                    # Terdapat gap (misalnya terpotong slot jeda 17.00)
                    _simpan_run_jika_memenuhi()
                    current_run = [slot_dt]
        else:
            # Slot tidak terisi atau slot hilang memutus rangkaian
            _simpan_run_jika_memenuhi()
            current_run = []

    # Periksa sisa run di akhir hari operasional
    _simpan_run_jika_memenuhi()

    return episodes
