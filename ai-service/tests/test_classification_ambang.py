import pytest

from app.classification.ambang import bentuk_ambang
from app.expert_system.tipe import Ambang

NILAI_AWAL = {
    "empty_min_occupied_minutes": "10",
    "outside_schedule_min_minutes": "30",
    "utilization_low_max": "40",
    "utilization_medium_max": "80",
}


def test_bentuk_ambang_dari_nilai_teks():
    assert bentuk_ambang(NILAI_AWAL) == Ambang(
        empty_min_occupied_minutes=10,
        outside_schedule_min_minutes=30,
        batas_rendah=40.0,
        batas_sedang=80.0,
    )


def test_kunci_lain_diabaikan_dan_spasi_dipangkas():
    nilai = {
        **NILAI_AWAL,
        "empty_status_evaluation_timing": "after_schedule_finished",
        "utilization_low_max": " 40 ",
    }

    assert bentuk_ambang(nilai).batas_rendah == pytest.approx(40.0)


def test_batas_boleh_berupa_desimal():
    nilai = {**NILAI_AWAL, "utilization_low_max": "40.5"}

    assert bentuk_ambang(nilai).batas_rendah == pytest.approx(40.5)


def test_kunci_hilang_ditolak_dengan_nama_kunci():
    nilai = {k: v for k, v in NILAI_AWAL.items() if k != "utilization_low_max"}

    with pytest.raises(ValueError, match="utilization_low_max"):
        bentuk_ambang(nilai)


def test_nilai_bukan_angka_ditolak():
    nilai = {**NILAI_AWAL, "empty_min_occupied_minutes": "sepuluh"}

    with pytest.raises(ValueError, match="tidak valid"):
        bentuk_ambang(nilai)


def test_menit_negatif_ditolak():
    nilai = {**NILAI_AWAL, "outside_schedule_min_minutes": "-5"}

    with pytest.raises(ValueError, match="negatif"):
        bentuk_ambang(nilai)


def test_batas_tidak_berurutan_ditolak():
    nilai = {**NILAI_AWAL, "utilization_low_max": "90"}

    with pytest.raises(ValueError, match="lebih kecil"):
        bentuk_ambang(nilai)
