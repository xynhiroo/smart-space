"""Endpoint prediksi risiko sesi kosong (SS1-14).

POST /predict/risk
    Masukan: schedule_id, tanggal
    Keluaran: skor_risiko, risiko, ambang, nama_model, fitur
"""

from __future__ import annotations

import json
from datetime import date, time, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.fitur import bangun_fitur, kolom_fitur
from app.ml.konstanta import MODEL_DIR_NAME, STATUS_KOSONG
from app.ml.model import muat_model

router = APIRouter()

AI_SERVICE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = AI_SERVICE_DIR / MODEL_DIR_NAME


class PrediksiRequest(BaseModel):
    """Skema masukan prediksi risiko."""

    schedule_id: int = Field(..., description="ID jadwal")
    tanggal: date = Field(..., description="Tanggal sesi (YYYY-MM-DD)")


class PrediksiResponse(BaseModel):
    """Skema keluaran prediksi risiko."""

    skor_risiko: float = Field(..., description="Probabilitas sesi kosong (0-1)")
    risiko: str = Field(..., description="'tinggi' atau 'rendah'")
    ambang: float = Field(..., description="Ambang keputusan yang dipakai")
    nama_model: str = Field(..., description="Nama model yang dipakai")
    fitur: dict[str, Any] = Field(..., description="Fitur yang dipakai untuk prediksi")


@router.post(
    "/predict/risk",
    response_model=PrediksiResponse,
    summary="Prediksi risiko sesi terjadwal kosong",
    description="Memprediksi probabilitas sesi terjadwal tidak dipakai.",
)
def prediksi_risiko(
    req: PrediksiRequest,
    session: Session = Depends(get_db),
) -> PrediksiResponse:
    """Prediksi risiko sesi kosong berdasarkan jadwal dan tanggal."""
    from sqlalchemy import text

    from app.calendar_utils import matches_day_of_week
    from app.generator.calendar_kind import resolve_day_kind
    from app.models import CalendarException, Room, Schedule

    # 1. Periksa model tersimpan
    metadata_path = MODEL_PATH / "metadata.json"
    if not metadata_path.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Model belum dilatih. Latih model terlebih dahulu dengan perintah: "
                "python -m app.ml latih --set dev"
            ),
        )

    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    nama_model = "logreg"
    ambang = metadata["logreg"]["ambang"]

    # 2. Cari jadwal
    jadwal = session.query(Schedule).filter(Schedule.id == req.schedule_id).first()
    if jadwal is None:
        raise HTTPException(
            status_code=404,
            detail=f"Jadwal dengan ID {req.schedule_id} tidak ditemukan.",
        )

    # 3. Periksa tanggal sesuai hari jadwal
    if not matches_day_of_week(jadwal.hari, req.tanggal.weekday()):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Tanggal {req.tanggal} ({req.tanggal.strftime('%A')}) "
                f"bukan hari '{jadwal.hari}' sesuai jadwal."
            ),
        )

    # 4. Periksa bukan hari libur
    calendar_exceptions = session.query(CalendarException).all()
    jenis_hari = resolve_day_kind(req.tanggal, calendar_exceptions)
    if jenis_hari == "libur":
        raise HTTPException(
            status_code=422,
            detail=f"Tanggal {req.tanggal} adalah hari libur, tidak ada sesi terjadwal.",
        )

    # 5. Ambil data ruang
    ruang = session.query(Room).filter(Room.id == jadwal.room_id).first()
    if ruang is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ruang dengan ID {jadwal.room_id} tidak ditemukan.",
        )

    # 6. Hitung riwayat label sebelum tanggal
    query_riwayat = text("""
        SELECT cr.tanggal, cr.status
        FROM classification_results cr
        WHERE cr.room_id = :room_id
          AND cr.schedule_id IS NOT NULL
          AND cr.tanggal < :tanggal
        ORDER BY cr.tanggal
    """)
    rows = session.execute(
        query_riwayat,
        {"room_id": jadwal.room_id, "tanggal": req.tanggal},
    ).fetchall()

    # Bangun DataFrame sesi tunggal
    sesi_data = {
        "schedule_id": [jadwal.id],
        "room_id": [jadwal.room_id],
        "nama_ruangan": [ruang.nama_ruangan],
        "tanggal": [req.tanggal],
        "jam_mulai": [jadwal.jam_mulai],
        "jam_selesai": [jadwal.jam_selesai],
        "shift": [jadwal.shift],
        "label": [0],  # placeholder, tidak dipakai untuk prediksi
    }
    df_sesi = pd.DataFrame(sesi_data)

    # Calendar exceptions sebagai DataFrame
    cal_data = []
    for ce in calendar_exceptions:
        cal_data.append({
            "tanggal_mulai": ce.tanggal_mulai,
            "tanggal_selesai": ce.tanggal_selesai,
            "tipe": ce.tipe,
        })
    df_cal = pd.DataFrame(cal_data) if cal_data else pd.DataFrame(
        columns=["tanggal_mulai", "tanggal_selesai", "tipe"]
    )

    # Untuk fitur riwayat, kita perlu DataFrame yang juga berisi riwayat
    # agar hitung_kosong_rate_ruang_sebelumnya bisa dihitung
    from app.ml.fitur import hitung_pekan_ke

    pekan_sesi = hitung_pekan_ke(req.tanggal)

    # Hitung kosong_rate dari riwayat
    if rows:
        riwayat_kosong = sum(1 for r in rows if r[1] == STATUS_KOSONG)
        kosong_rate = riwayat_kosong / len(rows)
        ada_riwayat = 1
    else:
        kosong_rate = float("nan")
        ada_riwayat = 0

    # Bangun fitur
    df_fitur = bangun_fitur(df_sesi, df_cal)

    # Override riwayat (karena df_sesi hanya 1 baris, bangun_fitur tidak bisa
    # menghitung riwayat dari pekan sebelumnya)
    df_fitur["kosong_rate_ruang_sebelumnya"] = kosong_rate
    df_fitur["ada_riwayat"] = ada_riwayat

    # 7. Muat model dan prediksi
    pipeline, _ = muat_model(MODEL_PATH, nama_model)

    fitur_cols = kolom_fitur()
    fitur_ada = [f for f in fitur_cols if f in df_fitur.columns]
    X = df_fitur[fitur_ada]

    y_proba = pipeline.predict_proba(X)[:, 1]
    skor = float(y_proba[0])
    risiko = "tinggi" if skor >= ambang else "rendah"

    # Fitur yang dipakai
    fitur_dict: dict[str, Any] = {}
    for col in fitur_ada:
        val = df_fitur[col].iloc[0]
        if isinstance(val, (np.integer,)):
            val = int(val)
        elif isinstance(val, (np.floating,)):
            val = float(val)
        elif isinstance(val, (np.bool_,)):
            val = bool(val)
        fitur_dict[col] = val

    return PrediksiResponse(
        skor_risiko=round(skor, 4),
        risiko=risiko,
        ambang=ambang,
        nama_model=nama_model,
        fitur=fitur_dict,
    )
