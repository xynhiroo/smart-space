import math
from datetime import date

import pytest

from app.analytics.utilization import (
    Sesi,
    StatistikRuang,
    hitung_statistik_ruang,
    hitung_utilisasi_pct,
    korelasi_jadwal_vs_terpakai,
    korelasi_pearson,
    korelasi_spearman,
    tentukan_kategori,
)

BATAS_RENDAH = 40
BATAS_SEDANG = 80


def test_utilisasi_dihitung_dari_menit():
    assert hitung_utilisasi_pct(120, 90) == pytest.approx(75.0)
    assert hitung_utilisasi_pct(100, 0) == pytest.approx(0.0)
    assert hitung_utilisasi_pct(100, 100) == pytest.approx(100.0)


def test_utilisasi_kosong_bila_tidak_ada_jadwal():
    assert hitung_utilisasi_pct(0, 0) is None
    assert hitung_utilisasi_pct(0, 30) is None


def test_utilisasi_menolak_data_tidak_valid():
    with pytest.raises(ValueError):
        hitung_utilisasi_pct(-1, 0)
    with pytest.raises(ValueError):
        hitung_utilisasi_pct(60, 70)


@pytest.mark.parametrize(
    "nilai, harapan",
    [
        (0.0, "rendah"),
        (40.0, "rendah"),
        (40.5, "sedang"),
        (80.0, "sedang"),
        (80.01, "tinggi"),
        (100.0, "tinggi"),
    ],
)
def test_kategori_pada_nilai_batas(nilai, harapan):
    assert tentukan_kategori(nilai, BATAS_RENDAH, BATAS_SEDANG) == harapan


def test_kategori_kosong_bila_utilisasi_kosong():
    assert tentukan_kategori(None, BATAS_RENDAH, BATAS_SEDANG) is None


def test_kategori_menolak_masukan_tidak_valid():
    with pytest.raises(ValueError):
        tentukan_kategori(50.0, 80, 40)
    with pytest.raises(ValueError):
        tentukan_kategori(101.0, BATAS_RENDAH, BATAS_SEDANG)


def test_statistik_per_ruang():
    sesi = [
        Sesi(1, date(2026, 9, 7), 120, 90),
        Sesi(1, date(2026, 9, 8), 60, 0),
        Sesi(1, date(2026, 9, 20), 60, 60),  # di luar periode
        Sesi(2, date(2026, 9, 7), 100, 100),
        Sesi(2, date(2026, 9, 7), 0, 30),  # di luar jadwal, tidak dihitung
    ]

    hasil = hitung_statistik_ruang(
        sesi,
        date(2026, 9, 7),
        date(2026, 9, 13),
        BATAS_RENDAH,
        BATAS_SEDANG,
        daftar_room_id=[1, 2, 3],
    )

    r1 = hasil[1]
    assert (r1.menit_terjadwal, r1.menit_terpakai, r1.selisih_menit) == (180, 90, 90)
    assert r1.utilisasi_pct == pytest.approx(50.0)
    assert r1.kategori == "sedang"
    assert r1.rata_rata_harian_pct == pytest.approx(37.5)
    assert r1.min_harian_pct == pytest.approx(0.0)
    assert r1.max_harian_pct == pytest.approx(75.0)

    r2 = hasil[2]
    assert (r2.menit_terjadwal, r2.menit_terpakai, r2.selisih_menit) == (100, 100, 0)
    assert r2.utilisasi_pct == pytest.approx(100.0)
    assert r2.kategori == "tinggi"

    r3 = hasil[3]
    assert r3.menit_terjadwal == 0
    assert r3.utilisasi_pct is None
    assert r3.kategori is None
    assert r3.rata_rata_harian_pct is None
    assert r3.min_harian_pct is None
    assert r3.max_harian_pct is None


def test_statistik_menolak_periode_terbalik():
    with pytest.raises(ValueError):
        hitung_statistik_ruang(
            [], date(2026, 9, 13), date(2026, 9, 7), BATAS_RENDAH, BATAS_SEDANG
        )


def test_pearson_nilai_diketahui():
    x = [1, 2, 3, 4, 5]
    assert korelasi_pearson(x, [2, 4, 6, 8, 10]) == pytest.approx(1.0)
    assert korelasi_pearson(x, [10, 8, 6, 4, 2]) == pytest.approx(-1.0)
    assert korelasi_pearson(x, [2, 1, 4, 3, 5]) == pytest.approx(0.8)


def test_pearson_kosong_bila_tidak_terdefinisi():
    assert korelasi_pearson([1], [1]) is None
    assert korelasi_pearson([1, 2, 3], [5, 5, 5]) is None
    with pytest.raises(ValueError):
        korelasi_pearson([1, 2], [1])


def test_spearman_menangkap_hubungan_monoton_nonlinier():
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]
    assert korelasi_spearman(x, y) == pytest.approx(1.0)
    assert korelasi_pearson(x, y) < 1.0


def test_spearman_menangani_nilai_kembar():
    assert korelasi_spearman([1, 2, 2, 3], [1, 2, 3, 4]) == pytest.approx(
        3 / math.sqrt(10)
    )


def _ruang(room_id, terjadwal, terpakai):
    return StatistikRuang(
        room_id=room_id,
        menit_terjadwal=terjadwal,
        menit_terpakai=terpakai,
        selisih_menit=terjadwal - terpakai,
        utilisasi_pct=None,
        kategori=None,
        rata_rata_harian_pct=None,
        min_harian_pct=None,
        max_harian_pct=None,
    )


def test_korelasi_antar_ruang_mengabaikan_ruang_tanpa_jadwal():
    ruang = [
        _ruang(1, 100, 20),
        _ruang(2, 200, 40),
        _ruang(3, 300, 60),
        _ruang(4, 400, 80),
        _ruang(5, 500, 100),
        _ruang(6, 0, 0),
    ]

    hasil = korelasi_jadwal_vs_terpakai(ruang)

    assert hasil.jumlah_ruang == 5
    assert hasil.pearson == pytest.approx(1.0)
    assert hasil.spearman == pytest.approx(1.0)