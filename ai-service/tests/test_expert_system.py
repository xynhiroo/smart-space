"""Unit test komprehensif sistem pakar klasifikasi status ruangan (Tier 1) - SS1-09.

Memenuhi 10 aspek pengujian wajib:
1. Pengujian per aturan (F.., R01, R02, R03) beserta jejak dan penjelasan.
2. Kasus batas (menit terpakai sama dengan ambang, 0 menit, waktu evaluasi persis, durasi episode 20 vs 30).
3. Slot jeda 17.00 & slot hilang (pengecualian jeda, pemutusan episode, slot hilang dihitung tidak terisi).
4. Batas jendela jadwal (pemotongan episode yang berdempetan dengan jadwal).
5. Hari perkuliahan (pemisahan hari, variasi Jum'at vs Jumat, ruang tanpa jadwal).
6. Hari libur (tanpa baris sesi, episode luar jadwal tetap ada).
7. Bukan hard-code (ambang dinamis via Ambang, inspeksi AST tanpa angka literal ambang).
8. Determinisme dan non-mutasi masukan (input diacak, input tidak berubah).
9. Mesin inferensi forward chaining (fixpoint, urutan tetap, injeksi basis pengetahuan uji).
10. Pemetaan ke Sesi dan baris classification_results (pembulatan Decimal ROUND_HALF_UP, invarian).
"""

import ast
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
import random

import pytest

from app.analytics.utilization import Sesi
from app.expert_system import (
    Ambang,
    Aturan,
    DAFTAR_ATURAN_DEFAULT,
    FaktaJadwal,
    FaktaRuang,
    FrameJadwal,
    FrameRuang,
    HasilKlasifikasi,
    MemoriKerja,
    SlotOkupansi,
    buat_frame_jadwal,
    buat_frame_ruang,
    deteksi_pemakaian_luar_jadwal,
    jalankan_inferensi,
    ke_baris_classification_results,
    ke_sesi,
    klasifikasikan_hari,
    klasifikasikan_sesi,
)
from app.expert_system.penjelasan import bangun_penjelasan, format_waktu_id


# ------------------------------------------------------------------------------
# Fixture Bantuan
# ------------------------------------------------------------------------------

@pytest.fixture
def ambang_standar():
    return Ambang(
        empty_min_occupied_minutes=10,
        outside_schedule_min_minutes=30,
        batas_rendah=40.0,
        batas_sedang=80.0,
    )


@pytest.fixture
def ruang_standar():
    return FaktaRuang(room_id=1, nama_ruangan="GU 604", is_open_space=False)


@pytest.fixture
def jadwal_senin_pagi():
    return FaktaJadwal(
        schedule_id=101,
        room_id=1,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Pemrograman Web",
    )


# ------------------------------------------------------------------------------
# 1. Setiap aturan (F.., R01, R02, R03) punya test sendiri & penjelasan
# ------------------------------------------------------------------------------

def test_aturan_f01_sesi_berakhir():
    wm = MemoriKerja(
        {
            "jenis_evaluasi": "sesi",
            "tanggal": date(2026, 9, 7),
            "jam_selesai": time(10, 0),
            "waktu_evaluasi": datetime(2026, 9, 7, 10, 0),
        }
    )
    aturan_f01 = next(a for a in DAFTAR_ATURAN_DEFAULT if a.rule_id == "F01")
    assert aturan_f01.kondisi(wm) is True
    wm.update(aturan_f01.kesimpulan(wm))
    assert wm.get("sesi_telah_berakhir") is True


def test_aturan_f02_okupansi_sesi_kurang():
    wm = MemoriKerja(
        {
            "sesi_telah_berakhir": True,
            "menit_terpakai": 0,
            "empty_min_occupied_minutes": 10,
        }
    )
    aturan_f02 = next(a for a in DAFTAR_ATURAN_DEFAULT if a.rule_id == "F02")
    assert aturan_f02.kondisi(wm) is True
    wm.update(aturan_f02.kesimpulan(wm))
    assert wm.get("okupansi_sesi_kurang") is True


def test_aturan_f03_okupansi_sesi_cukup():
    wm = MemoriKerja(
        {
            "sesi_telah_berakhir": True,
            "menit_terpakai": 10,
            "empty_min_occupied_minutes": 10,
        }
    )
    aturan_f03 = next(a for a in DAFTAR_ATURAN_DEFAULT if a.rule_id == "F03")
    assert aturan_f03.kondisi(wm) is True
    wm.update(aturan_f03.kesimpulan(wm))
    assert wm.get("okupansi_sesi_cukup") is True


def test_aturan_f04_episode_cukup_panjang():
    wm = MemoriKerja(
        {
            "jenis_evaluasi": "episode",
            "durasi_episode": 30,
            "outside_schedule_min_minutes": 30,
        }
    )
    aturan_f04 = next(a for a in DAFTAR_ATURAN_DEFAULT if a.rule_id == "F04")
    assert aturan_f04.kondisi(wm) is True
    wm.update(aturan_f04.kesimpulan(wm))
    assert wm.get("episode_cukup_panjang") is True


def test_aturan_r01_sesuai_jadwal_dan_penjelasan(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 10, 0)
    # Buat slot terisi 60 menit dari 120 menit terjadwal
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, m), is_occupied=True)
        for m in range(0, 60, 10)
    ]
    hasil = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, slots, tgl, waktu_eval, ambang_standar)

    assert hasil is not None
    assert hasil.status == "sesuai_jadwal"
    assert hasil.rule_id == "R01"
    assert hasil.menit_terjadwal == 120
    assert hasil.menit_terpakai == 60
    assert hasil.penjelasan == "Ruang terisi 60 dari 120 menit terjadwal."


def test_aturan_r02_kosong_meski_terjadwal_dan_penjelasan(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 10, 0)
    # Ruang kosong sama sekali
    hasil = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, [], tgl, waktu_eval, ambang_standar)

    assert hasil is not None
    assert hasil.status == "kosong_meski_terjadwal"
    assert hasil.rule_id == "R02"
    assert hasil.menit_terjadwal == 120
    assert hasil.menit_terpakai == 0
    harapan = (
        "Ruang terisi hanya 0 menit dari 120 menit terjadwal. "
        "Ruang ini berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU."
    )
    assert hasil.penjelasan == harapan


def test_aturan_r03_dipakai_di_luar_jadwal_dan_penjelasan(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 12, 0)
    # Slot terisi di luar jadwal: 10.30 - 11.10 (40 menit)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 30), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 40), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 50), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 11, 0), is_occupied=True),
    ]
    hasil = deteksi_pemakaian_luar_jadwal(ruang_standar, [jadwal_senin_pagi], slots, tgl, waktu_eval, ambang_standar)

    assert len(hasil) == 1
    h = hasil[0]
    assert h.status == "dipakai_di_luar_jadwal"
    assert h.rule_id == "R03"
    assert h.schedule_id is None
    assert h.menit_terjadwal == 0
    assert h.menit_terpakai == 40
    assert h.waktu_mulai == time(10, 30)
    assert h.waktu_selesai == time(11, 10)
    assert h.penjelasan == "Ruang terisi 40 menit di luar jadwal (10.30 sampai 11.10). Perlu ditinjau Admin."


# ------------------------------------------------------------------------------
# 2. Kasus Batas (Boundary Cases)
# ------------------------------------------------------------------------------

def test_kasus_batas_menit_terpakai_tepat_ambang(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 10, 0)
    # Tepat 1 slot terisi (10 menit = empty_min_occupied_minutes) -> sesuai_jadwal
    slots_10m = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, 0), is_occupied=True)
    ]
    res1 = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, slots_10m, tgl, waktu_eval, ambang_standar)
    assert res1.status == "sesuai_jadwal"
    assert res1.rule_id == "R01"

    # 0 menit terisi -> kosong_meski_terjadwal
    res0 = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, [], tgl, waktu_eval, ambang_standar)
    assert res0.status == "kosong_meski_terjadwal"
    assert res0.rule_id == "R02"


def test_kasus_batas_waktu_evaluasi_persis_dan_satu_menit_lebih_awal(
    ruang_standar, jadwal_senin_pagi, ambang_standar
):
    tgl = date(2026, 9, 7)
    # Tepat jam_selesai (10.00) -> dievaluasi
    res_tepat = klasifikasikan_sesi(
        ruang_standar, jadwal_senin_pagi, [], tgl, datetime(2026, 9, 7, 10, 0), ambang_standar
    )
    assert res_tepat is not None

    # Satu menit lebih awal (09.59) -> mengembalikan None (sesi belum berakhir)
    res_awal = klasifikasikan_sesi(
        ruang_standar, jadwal_senin_pagi, [], tgl, datetime(2026, 9, 7, 9, 59), ambang_standar
    )
    assert res_awal is None


def test_kasus_batas_durasi_episode_30m_vs_20m(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 12, 0)

    # Episode 20 menit (10.00 - 10.20) -> disaring, tidak menghasilkan baris
    slots_20m = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 0), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 10), is_occupied=True),
    ]
    res_20m = deteksi_pemakaian_luar_jadwal(ruang_standar, [jadwal_senin_pagi], slots_20m, tgl, waktu_eval, ambang_standar)
    assert len(res_20m) == 0

    # Episode tepat 30 menit (10.00 - 10.30) -> ditandai
    slots_30m = slots_20m + [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 20), is_occupied=True)
    ]
    res_30m = deteksi_pemakaian_luar_jadwal(ruang_standar, [jadwal_senin_pagi], slots_30m, tgl, waktu_eval, ambang_standar)
    assert len(res_30m) == 1
    assert res_30m[0].menit_terpakai == 30
    assert res_30m[0].waktu_mulai == time(10, 0)
    assert res_30m[0].waktu_selesai == time(10, 30)


# ------------------------------------------------------------------------------
# 3. Slot jeda 17.00 & Slot hilang
# ------------------------------------------------------------------------------

def test_slot_jeda_17_tidak_dihitung_dalam_menit_terjadwal(ruang_standar, ambang_standar):
    # Jadwal melintasi jeda: 16.00 sampai 18.00 (rentang 120 menit, tetapi ada jeda 17.00-17.10)
    jadwal_sore = FaktaJadwal(
        schedule_id=102,
        room_id=1,
        hari="Senin",
        jam_mulai=time(16, 0),
        jam_selesai=time(18, 0),
        mata_kuliah="Praktikum Jaringan",
    )
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 18, 0)

    hasil = klasifikasikan_sesi(ruang_standar, jadwal_sore, [], tgl, waktu_eval, ambang_standar)
    assert hasil is not None
    # 120 menit kalender - 10 menit jeda 17.00 = 110 menit terjadwal
    assert hasil.menit_terjadwal == 110


def test_slot_jeda_17_memutus_episode_luar_jadwal(ruang_standar, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 18, 0)
    # Terisi 16.40, 16.50 (20 menit), jeda 17.00, terisi 17.10, 17.20 (20 menit)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 16, 40), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 16, 50), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 17, 10), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 17, 20), is_occupied=True),
    ]
    # Tanpa jadwal, jeda 17.00 memutus episode sehingga menjadi 2 run masing-masing 20 menit (< 30 menit)
    hasil = deteksi_pemakaian_luar_jadwal(ruang_standar, [], slots, tgl, waktu_eval, ambang_standar)
    assert len(hasil) == 0


def test_slot_hilang_dihitung_tidak_terisi_dan_memutus_episode(ruang_standar, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 15, 0)
    # Terisi: 13.00, 13.10 (20 menit), slot 13.20 HILANG (tidak ada di log), terisi: 13.30, 13.40 (20 menit)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 13, 0), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 13, 10), is_occupied=True),
        # 13.20 hilang
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 13, 30), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 13, 40), is_occupied=True),
    ]
    hasil = deteksi_pemakaian_luar_jadwal(ruang_standar, [], slots, tgl, waktu_eval, ambang_standar)
    assert len(hasil) == 0


# ------------------------------------------------------------------------------
# 4. Batas Jendela Jadwal
# ------------------------------------------------------------------------------

def test_batas_jendela_memutus_episode(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 12, 0)
    # Jadwal: 08.00 - 10.00
    # Okupansi berderet dari 09.40 s.d. 10.30 (50 menit total)
    # Slot 09.40 dan 09.50 berada di dalam jendela jadwal
    # Slot 10.00, 10.10, 10.20 berada di luar jendela jadwal (30 menit)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 9, 40), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 9, 50), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 0), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 10), is_occupied=True),
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, 20), is_occupied=True),
    ]
    hasil = deteksi_pemakaian_luar_jadwal(ruang_standar, [jadwal_senin_pagi], slots, tgl, waktu_eval, ambang_standar)

    assert len(hasil) == 1
    # Episode di luar jadwal hanya menghitung slot mulai jam 10.00 sampai 10.30 (30 menit)
    assert hasil[0].waktu_mulai == time(10, 0)
    assert hasil[0].waktu_selesai == time(10, 30)
    assert hasil[0].menit_terpakai == 30


# ------------------------------------------------------------------------------
# 5. Hari Perkuliahan & Normalisasi
# ------------------------------------------------------------------------------

def test_jadwal_hari_lain_tidak_dievaluasi(ruang_standar, ambang_standar):
    # Jadwal di hari Selasa
    jadwal_selasa = FaktaJadwal(
        schedule_id=103,
        room_id=1,
        hari="Selasa",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Basis Data",
    )
    tgl_senin = date(2026, 9, 7)  # Senin
    waktu_eval = datetime(2026, 9, 7, 18, 0)

    hasil = klasifikasikan_hari(
        ruang_standar, [jadwal_selasa], [], tgl_senin, waktu_eval, ambang_standar, is_holiday=False
    )
    # Tidak ada baris sesi karena hari tidak cocok
    assert len(hasil) == 0


def test_nama_hari_jumat_dengan_dan_tanpa_petik(ruang_standar, ambang_standar):
    jadwal_petik = FaktaJadwal(
        schedule_id=104,
        room_id=1,
        hari="Jum'at",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Kalkulus",
    )
    jadwal_polos = FaktaJadwal(
        schedule_id=105,
        room_id=1,
        hari="Jumat",
        jam_mulai=time(13, 0),
        jam_selesai=time(15, 0),
        mata_kuliah="Fisika Terapan",
    )
    tgl_jumat = date(2026, 9, 11)  # Jumat
    waktu_eval = datetime(2026, 9, 11, 18, 0)

    hasil = klasifikasikan_hari(
        ruang_standar,
        [jadwal_petik, jadwal_polos],
        [],
        tgl_jumat,
        waktu_eval,
        ambang_standar,
        is_holiday=False,
    )
    # Keduanya harus dievaluasi karena cocok dengan hari Jumat
    assert len(hasil) == 2
    assert {h.schedule_id for h in hasil} == {104, 105}


def test_ruang_tanpa_jadwal_menghasilkan_semua_rangkaian_sebagai_episode(ruang_standar, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 18, 0)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 9, m), is_occupied=True)
        for m in range(0, 40, 10)
    ]
    hasil = klasifikasikan_hari(
        ruang_standar, [], slots, tgl, waktu_eval, ambang_standar, is_holiday=False
    )
    assert len(hasil) == 1
    assert hasil[0].schedule_id is None
    assert hasil[0].status == "dipakai_di_luar_jadwal"
    assert hasil[0].menit_terpakai == 40


# ------------------------------------------------------------------------------
# 6. Hari Libur (is_holiday=True)
# ------------------------------------------------------------------------------

def test_hari_libur_tanpa_sesi_tetapi_episode_tetap_ada(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 18, 0)
    # Slot terisi saat jam jadwal: 08.00 s.d. 08.40 (40 menit)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, m), is_occupied=True)
        for m in range(0, 40, 10)
    ]
    hasil = klasifikasikan_hari(
        ruang_standar,
        [jadwal_senin_pagi],
        slots,
        tgl,
        waktu_eval,
        ambang_standar,
        is_holiday=True,
    )
    # Pada hari libur: tidak ada baris sesi, okupansi menjadi episode di luar jadwal
    assert len(hasil) == 1
    assert hasil[0].schedule_id is None
    assert hasil[0].status == "dipakai_di_luar_jadwal"
    assert hasil[0].rule_id == "R03"
    assert hasil[0].menit_terpakai == 40


# ------------------------------------------------------------------------------
# 7. Bukan Hard-code (Ambang Dinamis & AST Check)
# ------------------------------------------------------------------------------

def test_mengubah_ambang_mengubah_hasil(ruang_standar, jadwal_senin_pagi):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 12, 0)

    # Masukan: 10 menit terisi pada sesi
    slots_sesi = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, 0), is_occupied=True)
    ]
    # Ambang A: empty=10 -> 10 menit memenuhi -> sesuai_jadwal
    ambang_a = Ambang(10, 30, 40.0, 80.0)
    res_a = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, slots_sesi, tgl, waktu_eval, ambang_a)
    assert res_a.status == "sesuai_jadwal"

    # Ambang B: empty=20 -> 10 menit kurang -> kosong_meski_terjadwal
    ambang_b = Ambang(20, 30, 40.0, 80.0)
    res_b = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, slots_sesi, tgl, waktu_eval, ambang_b)
    assert res_b.status == "kosong_meski_terjadwal"

    # Episode luar jadwal: 30 menit
    slots_ep = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 10, m), is_occupied=True)
        for m in (0, 10, 20)
    ]
    # Ambang C: outside=30 -> lolos
    ambang_c = Ambang(10, 30, 40.0, 80.0)
    res_c = deteksi_pemakaian_luar_jadwal(ruang_standar, [jadwal_senin_pagi], slots_ep, tgl, waktu_eval, ambang_c)
    assert len(res_c) == 1

    # Ambang D: outside=40 -> disaring
    ambang_d = Ambang(10, 40, 40.0, 80.0)
    res_d = deteksi_pemakaian_luar_jadwal(ruang_standar, [jadwal_senin_pagi], slots_ep, tgl, waktu_eval, ambang_d)
    assert len(res_d) == 0


def test_tidak_ada_literal_ambang_di_kode_expert_system():
    """Memeriksa tidak ada angka literal 10 atau 30 yang digunakan sebagai ambang perbandingan di expert_system."""
    pkg_dir = Path(__file__).resolve().parent.parent / "app" / "expert_system"
    python_files = list(pkg_dir.glob("*.py"))
    assert len(python_files) >= 5

    for py_file in python_files:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        # Cari node perbandingan (Compare) yang memuat literal angka 10 atau 30
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for comparator in node.comparators + [node.left]:
                    if isinstance(comparator, ast.Constant) and comparator.value in (10, 30):
                        pytest.fail(
                            f"Ditemukan hard-coded literal {comparator.value} pada perbandingan di {py_file.name}:{node.lineno}"
                        )


# ------------------------------------------------------------------------------
# 8. Determinisme dan Non-mutasi Masukan
# ------------------------------------------------------------------------------

def test_determinisme_urutan_slot_diacak_dan_non_mutasi(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 18, 0)

    slots_asli = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, m), is_occupied=True)
        for m in range(0, 60, 10)
    ] + [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 11, m), is_occupied=True)
        for m in (0, 10, 20, 30)
    ]

    slots_copy = list(slots_asli)
    hasil1 = klasifikasikan_hari(
        ruang_standar, [jadwal_senin_pagi], slots_copy, tgl, waktu_eval, ambang_standar, is_holiday=False
    )

    # Acak urutan slot
    slots_acak = list(slots_asli)
    random.seed(42)
    random.shuffle(slots_acak)

    hasil2 = klasifikasikan_hari(
        ruang_standar, [jadwal_senin_pagi], slots_acak, tgl, waktu_eval, ambang_standar, is_holiday=False
    )

    # Hasil harus identik
    assert hasil1 == hasil2
    # Masukan tidak boleh dimutasi
    assert slots_copy == slots_asli


# ------------------------------------------------------------------------------
# 9. Mesin Inferensi Forward Chaining
# ------------------------------------------------------------------------------

def test_mesin_inferensi_fixpoint_dan_jejak():
    # Buat aturan uji khusus untuk menguji decoupling mesin dari basis pengetahuan default
    aturan_uji = (
        Aturan(
            rule_id="U01",
            nama="Turunkan A",
            kondisi=lambda wm: wm.get("masukan") == 1 and "a" not in wm,
            kesimpulan=lambda wm: {"a": True},
        ),
        Aturan(
            rule_id="U02",
            nama="Turunkan B",
            kondisi=lambda wm: wm.get("a") is True and "b" not in wm,
            kesimpulan=lambda wm: {"b": True},
        ),
        Aturan(
            rule_id="U03",
            nama="Turunkan C",
            kondisi=lambda wm: wm.get("b") is True and "c" not in wm,
            kesimpulan=lambda wm: {"c": True},
        ),
    )

    wm = MemoriKerja({"masukan": 1})
    hasil = jalankan_inferensi(wm, basis_pengetahuan=aturan_uji)

    # Fixpoint tercapai: a -> b -> c
    assert hasil.memori_kerja.get("c") is True
    assert hasil.jejak == ("U01", "U02", "U03")


# ------------------------------------------------------------------------------
# 10. Pemetaan ke Sesi dan Baris classification_results
# ------------------------------------------------------------------------------

def test_pemetaan_ke_sesi(ruang_standar, jadwal_senin_pagi, ambang_standar):
    tgl = date(2026, 9, 7)
    waktu_eval = datetime(2026, 9, 7, 10, 0)
    slots = [
        SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, m), is_occupied=True)
        for m in (0, 10, 20)
    ]
    hasil_sesi = klasifikasikan_sesi(ruang_standar, jadwal_senin_pagi, slots, tgl, waktu_eval, ambang_standar)
    assert hasil_sesi is not None

    sesi = ke_sesi(hasil_sesi)
    assert isinstance(sesi, Sesi)
    assert sesi.room_id == 1
    assert sesi.tanggal == tgl
    assert sesi.menit_terjadwal == 120
    assert sesi.menit_terpakai == 30

    # Episode luar jadwal harus menghasilkan None saat dipetakan ke_sesi
    hasil_ep = HasilKlasifikasi(
        room_id=1,
        schedule_id=None,
        tanggal=tgl,
        waktu_mulai=time(11, 0),
        waktu_selesai=time(11, 30),
        status="dipakai_di_luar_jadwal",
        menit_terjadwal=0,
        menit_terpakai=30,
        utilisasi_pct=None,
        rule_id="R03",
        penjelasan="...",
    )
    assert ke_sesi(hasil_ep) is None


def test_pemetaan_ke_baris_classification_results_dan_pembulatan():
    tgl = date(2026, 9, 7)
    computed_at = datetime(2026, 9, 7, 18, 0)

    # 1. Kasus utilisasi dengan pembulatan ROUND_HALF_UP (33.335 -> 33.34)
    hasil1 = HasilKlasifikasi(
        room_id=1,
        schedule_id=101,
        tanggal=tgl,
        waktu_mulai=time(8, 0),
        waktu_selesai=time(10, 0),
        status="sesuai_jadwal",
        menit_terjadwal=120,
        menit_terpakai=40,
        utilisasi_pct=33.335,  # float mentah
        rule_id="R01",
        penjelasan="Ruang terisi 40 dari 120 menit terjadwal.",
    )
    baris1 = ke_baris_classification_results(hasil1, computed_at)
    assert baris1["utilisasi_pct"] == Decimal("33.34")
    assert baris1["status"] == "sesuai_jadwal"
    assert baris1["schedule_id"] == 101

    # 2. Kasus utilisasi dengan pembulatan ke bawah (33.334 -> 33.33)
    hasil2 = HasilKlasifikasi(
        room_id=1,
        schedule_id=101,
        tanggal=tgl,
        waktu_mulai=time(8, 0),
        waktu_selesai=time(10, 0),
        status="sesuai_jadwal",
        menit_terjadwal=120,
        menit_terpakai=40,
        utilisasi_pct=33.334,
        rule_id="R01",
        penjelasan="Ruang terisi 40 dari 120 menit terjadwal.",
    )
    baris2 = ke_baris_classification_results(hasil2, computed_at)
    assert baris2["utilisasi_pct"] == Decimal("33.33")

    # 3. Episode luar jadwal: utilisasi None dan schedule_id None dipertahankan
    hasil_ep = HasilKlasifikasi(
        room_id=1,
        schedule_id=None,
        tanggal=tgl,
        waktu_mulai=time(11, 0),
        waktu_selesai=time(11, 30),
        status="dipakai_di_luar_jadwal",
        menit_terjadwal=0,
        menit_terpakai=30,
        utilisasi_pct=None,
        rule_id="R03",
        penjelasan="Ruang terisi 30 menit di luar jadwal (11.00 sampai 11.30). Perlu ditinjau Admin.",
    )
    baris_ep = ke_baris_classification_results(hasil_ep, computed_at)
    assert baris_ep["schedule_id"] is None
    assert baris_ep["utilisasi_pct"] is None
    assert baris_ep["menit_terjadwal"] == 0

    # 4. Validasi invarian: status luar_jadwal tetapi schedule_id tidak None harus ditolak
    invarian_rusak = HasilKlasifikasi(
        room_id=1,
        schedule_id=999,  # melanggar invarian
        tanggal=tgl,
        waktu_mulai=time(11, 0),
        waktu_selesai=time(11, 30),
        status="dipakai_di_luar_jadwal",
        menit_terjadwal=0,
        menit_terpakai=30,
        utilisasi_pct=None,
        rule_id="R03",
        penjelasan="...",
    )
    with pytest.raises(ValueError, match="Invarian dilanggar"):
        ke_baris_classification_results(invarian_rusak, computed_at)
