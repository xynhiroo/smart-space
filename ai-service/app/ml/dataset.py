"""Pemuat dataset dari database untuk model ML (SS1-14).

Membaca sesi terjadwal dari classification_results (schedule_id IS NOT NULL)
dan menggabungkannya dengan rooms, schedules, dan calendar_exceptions.
Hanya membaca database (read-only).

Label: 1 bila status = 'kosong_meski_terjadwal', 0 selain itu.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ml.konstanta import STATUS_KOSONG


def muat_sesi_terjadwal(
    session: Session,
    tanggal_mulai: date | None = None,
    tanggal_selesai: date | None = None,
) -> pd.DataFrame:
    """Muat sesi terjadwal dari classification_results + rooms + schedules.

    Hanya baris dengan schedule_id IS NOT NULL (sesi terjadwal).
    Label: 1 = kosong_meski_terjadwal, 0 = lainnya.

    Returns:
        DataFrame dengan kolom: schedule_id, room_id, nama_ruangan,
        tanggal, jam_mulai, jam_selesai, shift, label
    """
    where_clause = "WHERE cr.schedule_id IS NOT NULL"
    params: dict = {}

    if tanggal_mulai is not None:
        where_clause += " AND cr.tanggal >= :tanggal_mulai"
        params["tanggal_mulai"] = tanggal_mulai
    if tanggal_selesai is not None:
        where_clause += " AND cr.tanggal <= :tanggal_selesai"
        params["tanggal_selesai"] = tanggal_selesai

    query = text(f"""
        SELECT
            cr.schedule_id,
            cr.room_id,
            r.nama_ruangan,
            cr.tanggal,
            s.jam_mulai,
            s.jam_selesai,
            s.shift,
            cr.status
        FROM classification_results cr
        JOIN rooms r ON cr.room_id = r.id
        JOIN schedules s ON cr.schedule_id = s.id
        {where_clause}
        ORDER BY cr.tanggal, cr.room_id, s.jam_mulai
    """)

    result = session.execute(query, params)
    rows = result.fetchall()
    columns = list(result.keys())

    df = pd.DataFrame(rows, columns=columns)
    if df.empty:
        return df

    # Label: 1 = kosong, 0 = lainnya
    df["label"] = (df["status"] == STATUS_KOSONG).astype(int)
    # Hapus kolom status (terlarang di fitur)
    df = df.drop(columns=["status"])

    return df


def muat_calendar_exceptions(session: Session) -> pd.DataFrame:
    """Muat seluruh calendar_exceptions dari database."""
    query = text("""
        SELECT id, tanggal_mulai, tanggal_selesai, tipe, keterangan
        FROM calendar_exceptions
        ORDER BY tanggal_mulai
    """)
    result = session.execute(query)
    rows = result.fetchall()
    columns = list(result.keys())
    return pd.DataFrame(rows, columns=columns)
