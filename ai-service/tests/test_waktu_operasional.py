"""Pengujian modul konstanta dan utilitas waktu operasional."""

from datetime import datetime, time
import pytest

from app.waktu_operasional import (
    JAM_BUKA_OPERASIONAL,
    JAM_JEDA,
    JAM_TUTUP_OPERASIONAL,
    MENIT_JEDA,
    MENIT_PER_SLOT,
    TOTAL_SLOT_OPERASIONAL_PER_HARI,
    TOTAL_SLOT_PER_HARI,
    WAKTU_BUKA,
    WAKTU_MULAI_JEDA,
    WAKTU_SELESAI_JEDA,
    WAKTU_TUTUP,
    generate_operational_slots,
    is_break_slot,
    is_operational_slot,
)


def test_konstanta_waktu_operasional():
    assert MENIT_PER_SLOT == 10
    assert JAM_BUKA_OPERASIONAL == 7
    assert JAM_TUTUP_OPERASIONAL == 23
    assert JAM_JEDA == 17
    assert MENIT_JEDA == 0
    assert WAKTU_BUKA == time(7, 0)
    assert WAKTU_TUTUP == time(23, 0)
    assert WAKTU_MULAI_JEDA == time(17, 0)
    assert WAKTU_SELESAI_JEDA == time(17, 10)
    assert TOTAL_SLOT_PER_HARI == 96
    assert TOTAL_SLOT_OPERASIONAL_PER_HARI == 95


def test_is_break_slot():
    assert is_break_slot(time(17, 0)) is True
    assert is_break_slot(time(17, 10)) is False
    assert is_break_slot(time(16, 50)) is False
    assert is_break_slot(datetime(2026, 9, 7, 17, 0)) is True
    assert is_break_slot(datetime(2026, 9, 7, 17, 10)) is False


def test_is_operational_slot():
    assert is_operational_slot(time(7, 0)) is True
    assert is_operational_slot(time(22, 50)) is True
    assert is_operational_slot(time(23, 0)) is False
    assert is_operational_slot(time(6, 50)) is False
    assert is_operational_slot(time(17, 0)) is False  # slot jeda
    assert is_operational_slot(time(17, 10)) is True
    assert is_operational_slot(time(8, 5)) is False  # bukan kelipatan 10 menit


def test_generate_operational_slots():
    slots = generate_operational_slots()
    assert len(slots) == 95
    assert slots[0] == time(7, 0)
    assert slots[-1] == time(22, 50)
    assert time(17, 0) not in slots
