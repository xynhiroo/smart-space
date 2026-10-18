"""Unit test untuk modul bersama calendar_utils."""

import pytest
from app.calendar_utils import (
    hari_to_weekday,
    matches_day_of_week,
    normalize_hari,
)


def test_normalize_hari_senin_sampai_jumat():
    # Uji nama standar
    assert normalize_hari("Senin") == "Senin"
    assert normalize_hari("Selasa") == "Selasa"
    assert normalize_hari("Rabu") == "Rabu"
    assert normalize_hari("Kamis") == "Kamis"
    assert normalize_hari("Jumat") == "Jumat"
    assert normalize_hari("Jum'at") == "Jumat"


def test_normalize_hari_variasi_huruf_besar_kecil_dan_spasi():
    # Huruf kecil
    assert normalize_hari("senin") == "Senin"
    assert normalize_hari("selasa") == "Selasa"
    assert normalize_hari("rabu") == "Rabu"
    assert normalize_hari("kamis") == "Kamis"
    assert normalize_hari("jumat") == "Jumat"
    assert normalize_hari("jum'at") == "Jumat"

    # Huruf besar (uppercase)
    assert normalize_hari("SENIN") == "Senin"
    assert normalize_hari("JUMAT") == "Jumat"
    assert normalize_hari("JUM'AT") == "Jumat"

    # Campuran dan spasi
    assert normalize_hari("  JuM'aT  ") == "Jumat"
    assert normalize_hari("  seNin  ") == "Senin"


def test_normalize_hari_nilai_tak_dikenal():
    # Akhir pekan (di luar cakupan hari kerja)
    assert normalize_hari("Sabtu") is None
    assert normalize_hari("Minggu") is None

    # Bahasa asing / nilai sembarang
    assert normalize_hari("Monday") is None
    assert normalize_hari("Friday") is None
    assert normalize_hari("xyz") is None
    assert normalize_hari("") is None
    assert normalize_hari(None) is None


def test_hari_to_weekday_dan_matches_day_of_week():
    assert hari_to_weekday("Senin") == 0
    assert hari_to_weekday("Selasa") == 1
    assert hari_to_weekday("Rabu") == 2
    assert hari_to_weekday("Kamis") == 3
    assert hari_to_weekday("Jum'at") == 4
    assert hari_to_weekday("Jumat") == 4
    assert hari_to_weekday("Sabtu") is None

    # matches_day_of_week
    assert matches_day_of_week("Senin", 0) is True
    assert matches_day_of_week("senin", 0) is True
    assert matches_day_of_week("Jum'at", 4) is True
    assert matches_day_of_week("Jumat", 4) is True
    assert matches_day_of_week("JUM'AT", 4) is True
    assert matches_day_of_week("Senin", 1) is False
    assert matches_day_of_week("Minggu", 6) is False
    assert matches_day_of_week("invalid", 0) is False
    assert matches_day_of_week(None, 0) is False
