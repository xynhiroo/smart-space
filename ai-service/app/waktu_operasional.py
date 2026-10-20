"""Konstanta dan utilitas waktu operasional sistem (DATA_CONTRACT Bagian 2).

Modul ini mendefinisikan grid waktu bersama yang digunakan oleh generator
maupun sistem pakar klasifikasi status ruangan.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta

MENIT_PER_SLOT: int = 10

JAM_BUKA_OPERASIONAL: int = 7
JAM_TUTUP_OPERASIONAL: int = 23

JAM_JEDA: int = 17
MENIT_JEDA: int = 0

WAKTU_BUKA: time = time(JAM_BUKA_OPERASIONAL, 0)
WAKTU_TUTUP: time = time(JAM_TUTUP_OPERASIONAL, 0)

WAKTU_MULAI_JEDA: time = time(JAM_JEDA, MENIT_JEDA)
WAKTU_SELESAI_JEDA: time = time(JAM_JEDA, MENIT_JEDA + MENIT_PER_SLOT)

TOTAL_SLOT_PER_HARI: int = 96
TOTAL_SLOT_OPERASIONAL_PER_HARI: int = 95


def is_break_slot(waktu: time | datetime) -> bool:
    """Memeriksa apakah waktu berada pada slot jeda 17.00 (17.00 s.d. 17.10)."""
    t = waktu.time() if isinstance(waktu, datetime) else waktu
    return t.hour == JAM_JEDA and t.minute == MENIT_JEDA


def is_operational_slot(waktu: time | datetime) -> bool:
    """Memeriksa apakah waktu berada dalam jam operasional (07.00 - 23.00) dan bukan slot jeda."""
    t = waktu.time() if isinstance(waktu, datetime) else waktu
    if not (WAKTU_BUKA <= t < WAKTU_TUTUP):
        return False
    if is_break_slot(t):
        return False
    return t.minute % MENIT_PER_SLOT == 0


def generate_operational_slots(
    start_hour: int = JAM_BUKA_OPERASIONAL,
    end_hour: int = JAM_TUTUP_OPERASIONAL,
    step_minutes: int = MENIT_PER_SLOT,
    break_hour: int = JAM_JEDA,
    break_minute: int = MENIT_JEDA,
) -> list[time]:
    """Membangun daftar slot operasional (07.00 - 22.50), mengecualikan slot jeda 17.00."""
    slots: list[time] = []
    current_dt = datetime(2000, 1, 1, start_hour, 0)
    end_dt = datetime(2000, 1, 1, end_hour, 0)
    step = timedelta(minutes=step_minutes)

    while current_dt < end_dt:
        t = current_dt.time()
        if not (t.hour == break_hour and t.minute == break_minute):
            slots.append(t)
        current_dt += step

    return slots
