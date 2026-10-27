"""Waktu evaluasi untuk klasifikasi (SS1-11).

Semua waktu memakai WIB tanpa informasi zona (DATA_CONTRACT Bagian 2).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

SELISIH_WIB_DARI_UTC = timedelta(hours=7)


def waktu_evaluasi_historis(tanggal: date) -> datetime:
    """Waktu evaluasi untuk run historis: 00.00 hari berikutnya.

    Pada waktu itu semua sesi dan semua slot pada tanggal tersebut sudah
    berakhir, termasuk slot terakhir 22.50 yang berakhir 23.00 (Bagian 7.1).
    Bila waktunya jatuh sebelum sesi berakhir, sesi itu tidak menghasilkan baris.
    """
    return datetime.combine(tanggal + timedelta(days=1), time.min)


def waktu_sekarang_wib() -> datetime:
    """Waktu sekarang dalam WIB tanpa informasi zona, untuk kolom computed_at.

    WIB selalu UTC+7 tanpa perubahan musim, jadi tidak perlu paket tzdata.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None) + SELISIH_WIB_DARI_UTC
