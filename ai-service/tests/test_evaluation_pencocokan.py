"""Test pencocokan label ground truth dengan hasil runner (SS1-12)."""

from datetime import date, time, timedelta

import pytest

from app.evaluation.pencocokan import (
    BUKAN_EPISODE,
    TIDAK_TERDETEKSI,
    BarisLabel,
    baris_dari_hasil_klasifikasi,
    cocokkan,
    muat_ground_truth_csv,
)

TGL = date(2026, 9, 15)
SESUAI = "sesuai_jadwal"
KOSONG = "kosong_meski_terjadwal"
LUAR = "dipakai_di_luar_jadwal"


def baris(mulai, selesai, status, schedule_id=None, room_id=7, tanggal=TGL):
    return BarisLabel(
        tanggal, room_id, schedule_id, time.fromisoformat(mulai), time.fromisoformat(selesai), status
    )


def test_sesi_berpasangan_lewat_kunci_dan_label_boleh_berbeda():
    gt = [baris("18:50", "19:40", KOSONG, schedule_id=16, room_id=3)]
    hs = [baris("18:50", "19:40", SESUAI, schedule_id=16, room_id=3)]
    h = cocokkan(gt, hs)
    assert h.benar == (KOSONG,)
    assert h.prediksi == (SESUAI,)
    assert h.tanpa_prediksi == 0 and h.tanpa_label == 0


def test_sesi_hanya_di_ground_truth_dan_hanya_di_runner():
    gt = [baris("08:00", "09:00", SESUAI, schedule_id=1)]
    hs = [baris("10:00", "11:00", SESUAI, schedule_id=2)]
    h = cocokkan(gt, hs)
    assert sorted(zip(h.benar, h.prediksi)) == sorted(
        [(SESUAI, TIDAK_TERDETEKSI), (BUKAN_EPISODE, SESUAI)]
    )
    assert h.tanpa_prediksi == 1 and h.tanpa_label == 1


def test_kunci_sesi_ganda_ditolak():
    ganda = [baris("08:00", "09:00", SESUAI, schedule_id=1)] * 2
    with pytest.raises(ValueError):
        cocokkan(ganda, [])
    with pytest.raises(ValueError):
        cocokkan([], ganda)


def test_episode_dipecah_runner_menjadi_satu_pasangan():
    gt = [baris("07:20", "09:30", LUAR)]
    hs = [baris("07:20", "08:40", LUAR), baris("08:50", "09:30", LUAR)]
    h = cocokkan(gt, hs)
    assert len(h.pasangan) == 1
    assert h.benar == (LUAR,) and h.prediksi == (LUAR,)
    assert h.tanpa_label == 0


def test_episode_waktu_mulai_berbeda_tetap_cocok():
    gt = [baris("07:20", "08:40", LUAR, room_id=8, tanggal=date(2026, 9, 8))]
    hs = [baris("07:30", "08:40", LUAR, room_id=8, tanggal=date(2026, 9, 8))]
    h = cocokkan(gt, hs)
    assert h.prediksi == (LUAR,) and h.tanpa_prediksi == 0


def test_episode_ground_truth_tanpa_runner_tidak_terdeteksi():
    h = cocokkan([baris("09:00", "10:00", LUAR)], [])
    assert h.prediksi == (TIDAK_TERDETEKSI,)
    assert h.tanpa_prediksi == 1


def test_episode_runner_tanpa_ground_truth_bukan_episode():
    h = cocokkan([], [baris("09:00", "10:00", LUAR)])
    assert h.benar == (BUKAN_EPISODE,) and h.prediksi == (LUAR,)
    assert h.tanpa_label == 1


def test_episode_berimpit_di_batas_tidak_beririsan():
    gt = [baris("09:00", "10:00", LUAR)]
    hs = [baris("10:00", "11:00", LUAR)]
    h = cocokkan(gt, hs)
    assert h.tanpa_prediksi == 1 and h.tanpa_label == 1


def test_episode_beda_ruang_atau_tanggal_tidak_cocok():
    gt = [baris("09:00", "10:00", LUAR, room_id=7)]
    hs = [
        baris("09:00", "10:00", LUAR, room_id=8),
        baris("09:00", "10:00", LUAR, room_id=7, tanggal=date(2026, 9, 16)),
    ]
    h = cocokkan(gt, hs)
    assert h.tanpa_prediksi == 1 and h.tanpa_label == 2


def test_jumlah_pasangan_dan_urutan_deterministik():
    gt = [
        baris("09:00", "10:00", LUAR),
        baris("08:00", "09:00", SESUAI, schedule_id=1),
    ]
    hs = list(reversed([baris("09:00", "10:00", LUAR), baris("08:00", "09:00", SESUAI, schedule_id=1)]))
    h1 = cocokkan(gt, hs)
    h2 = cocokkan(list(reversed(gt)), list(reversed(hs)))
    assert h1 == h2
    assert len(h1.benar) == len(h1.prediksi) == 2


def test_muat_csv_dan_konversi_timedelta(tmp_path):
    csv_path = tmp_path / "gt.csv"
    csv_path.write_text(
        "tanggal,room_id,schedule_id,waktu_mulai,waktu_selesai,status_benar,penyebab\n"
        "2026-09-07,3,16,18:50:00,19:40:00,sesuai_jadwal,terlambat\n"
        "2026-09-08,8,,07:20:00,08:40:00,dipakai_di_luar_jadwal,pemakaian_luar_jadwal\n",
        encoding="utf-8",
    )
    gt = muat_ground_truth_csv(csv_path)
    assert gt[0].schedule_id == 16 and gt[0].waktu_mulai == time(18, 50)
    assert gt[1].schedule_id is None and gt[1].status == LUAR

    hs = baris_dari_hasil_klasifikasi(
        [
            {
                "tanggal": date(2026, 9, 7),
                "room_id": 3,
                "schedule_id": 16,
                "waktu_mulai": timedelta(hours=18, minutes=50),
                "waktu_selesai": timedelta(hours=19, minutes=40),
                "status": SESUAI,
            }
        ]
    )
    assert hs[0].waktu_mulai == time(18, 50)
    h = cocokkan(gt, hs)
    assert (SESUAI, SESUAI) in set(zip(h.benar, h.prediksi))
