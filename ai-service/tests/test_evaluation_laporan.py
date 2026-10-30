"""Test penyusunan laporan evaluasi (SS1-12)."""

from datetime import date, time

import pytest

from app.evaluation.cli import parse_args
from app.evaluation.laporan import format_laporan, muat_penyebab_csv, susun_laporan
from app.evaluation.pencocokan import BarisLabel

TGL = date(2026, 9, 7)
SESUAI = "sesuai_jadwal"
KOSONG = "kosong_meski_terjadwal"


def baris(schedule_id, status, mulai="08:00", selesai="09:00"):
    return BarisLabel(
        TGL, 1, schedule_id, time.fromisoformat(mulai), time.fromisoformat(selesai), status
    )


def contoh():
    gt = [baris(1, SESUAI), baris(2, KOSONG, "10:00", "11:00")]
    hs = [baris(1, SESUAI), baris(2, SESUAI, "10:00", "11:00")]
    penyebab = {(TGL, 1, 1): "kelas_berlangsung", (TGL, 1, 2): "tidak_hadir"}
    return gt, hs, penyebab


def test_susun_laporan_menghitung_metrik_dan_galat_per_penyebab():
    laporan = susun_laporan(*contoh())
    assert laporan.evaluasi.jumlah == 2
    assert laporan.evaluasi.accuracy == 0.5
    assert laporan.galat == ((KOSONG, SESUAI, "tidak_hadir", 1),)
    assert laporan.pencocokan.tanpa_prediksi == 0


def test_laporan_tanpa_galat_mencetak_tidak_ada():
    gt = [baris(1, SESUAI)]
    laporan = susun_laporan(gt, gt, {})
    assert laporan.galat == ()
    assert "(tidak ada)" in format_laporan(laporan, "dev", "smart_space_ai_dev")


def test_format_laporan_memuat_bagian_utama():
    teks = format_laporan(susun_laporan(*contoh()), "dev", "smart_space_ai_dev")
    for isi in ("DEV", "smart_space_ai_dev", "Accuracy", "Macro F1", "Matriks", "tidak_hadir"):
        assert isi in teks


def test_muat_penyebab_csv_hanya_sesi_terjadwal(tmp_path):
    berkas = tmp_path / "gt.csv"
    berkas.write_text(
        "tanggal,room_id,schedule_id,waktu_mulai,waktu_selesai,status_benar,penyebab\n"
        "2026-09-07,3,16,18:50:00,19:40:00,sesuai_jadwal,terlambat\n"
        "2026-09-08,8,,07:20:00,08:40:00,dipakai_di_luar_jadwal,pemakaian_luar_jadwal\n",
        encoding="utf-8",
    )
    assert muat_penyebab_csv(berkas) == {(date(2026, 9, 7), 3, 16): "terlambat"}


def test_parse_args_mewajibkan_set_dan_menolak_nilai_lain():
    assert parse_args(["--set", "dev"]).set == "dev"
    with pytest.raises(SystemExit):
        parse_args([])
    with pytest.raises(SystemExit):
        parse_args(["--set", "produksi"])
