from datetime import date, datetime, timedelta, timezone

from app.classification.waktu import waktu_evaluasi_historis, waktu_sekarang_wib


def test_waktu_evaluasi_historis_adalah_tengah_malam_hari_berikutnya():
    assert waktu_evaluasi_historis(date(2026, 10, 5)) == datetime(2026, 10, 6, 0, 0)


def test_waktu_evaluasi_historis_melewati_batas_bulan_dan_tahun():
    assert waktu_evaluasi_historis(date(2026, 10, 31)) == datetime(2026, 11, 1, 0, 0)
    assert waktu_evaluasi_historis(date(2026, 12, 31)) == datetime(2027, 1, 1, 0, 0)


def test_waktu_evaluasi_historis_setelah_slot_terakhir_hari_itu():
    # Slot terakhir 22.50 berakhir 23.00 dan harus sudah berakhir saat evaluasi (Bagian 7.1).
    slot_terakhir_berakhir = datetime(2026, 10, 5, 22, 50) + timedelta(minutes=10)

    assert slot_terakhir_berakhir <= waktu_evaluasi_historis(date(2026, 10, 5))


def test_waktu_sekarang_wib_polos_dan_tujuh_jam_dari_utc():
    sekarang = waktu_sekarang_wib()
    harapan = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=7)

    assert sekarang.tzinfo is None
    assert abs(sekarang - harapan) < timedelta(seconds=5)
