import pytest

from app.evaluation.metrik import STATUS, hitung_evaluasi

A, B, C = STATUS


def test_metrik_dari_hitungan_manual():
    # 5 sesuai (4 benar, 1 salah jadi kosong), 3 kosong (2 benar, 1 salah jadi sesuai), 2 luar jadwal (benar).
    benar = [A] * 5 + [B] * 3 + [C] * 2
    prediksi = [A, A, A, A, B] + [A, B, B] + [C, C]

    hasil = hitung_evaluasi(benar, prediksi)

    assert hasil.jumlah == 10
    assert hasil.accuracy == pytest.approx(0.8)
    assert hasil.matriks[(A, A)] == 4
    assert hasil.matriks[(A, B)] == 1
    assert hasil.matriks[(B, A)] == 1
    assert hasil.matriks[(B, B)] == 2
    assert hasil.matriks[(C, C)] == 2
    assert hasil.matriks[(C, A)] == 0

    sesuai = hasil.per_kelas[A]
    assert (sesuai.precision, sesuai.recall, sesuai.f1) == pytest.approx((0.8, 0.8, 0.8))
    assert sesuai.support == 5

    kosong = hasil.per_kelas[B]
    assert (kosong.precision, kosong.recall, kosong.f1) == pytest.approx((2 / 3, 2 / 3, 2 / 3))
    assert kosong.support == 3

    luar = hasil.per_kelas[C]
    assert (luar.precision, luar.recall, luar.f1) == pytest.approx((1.0, 1.0, 1.0))
    assert luar.support == 2

    assert hasil.macro_f1 == pytest.approx((0.8 + 2 / 3 + 1.0) / 3)


def test_prediksi_sempurna():
    label = [A, B, C, A]

    hasil = hitung_evaluasi(label, label)

    assert hasil.accuracy == pytest.approx(1.0)
    assert hasil.macro_f1 == pytest.approx(1.0)


def test_kelas_tanpa_prediksi_dan_kelas_tanpa_contoh():
    benar = [A, A, B]
    prediksi = [A, A, A]

    hasil = hitung_evaluasi(benar, prediksi)

    sesuai = hasil.per_kelas[A]
    assert sesuai.precision == pytest.approx(2 / 3)
    assert sesuai.recall == pytest.approx(1.0)
    assert sesuai.f1 == pytest.approx(0.8)

    kosong = hasil.per_kelas[B]  # ada contoh benar, tidak pernah diprediksi
    assert kosong.precision is None
    assert kosong.recall == pytest.approx(0.0)
    assert kosong.f1 == pytest.approx(0.0)

    luar = hasil.per_kelas[C]  # tidak ada contoh dan tidak diprediksi
    assert (luar.precision, luar.recall, luar.f1) == (None, None, None)
    assert luar.support == 0

    assert hasil.accuracy == pytest.approx(2 / 3)
    assert hasil.macro_f1 == pytest.approx(0.4)  # rata-rata f1 sesuai dan kosong


def test_panjang_berbeda_ditolak():
    with pytest.raises(ValueError, match="sama"):
        hitung_evaluasi([A, B], [A])


def test_data_kosong_ditolak():
    with pytest.raises(ValueError, match="kosong"):
        hitung_evaluasi([], [])


def test_label_tidak_dikenal_ditolak():
    with pytest.raises(ValueError, match="rusak"):
        hitung_evaluasi([A, "rusak"], [A, B])
