"""Endpoint POST /classify (SS1-11).

Menulis classification_results pada database yang dikonfigurasi aplikasi.
Python hanya boleh menulis occupancy_logs dan classification_results (DATA_CONTRACT Bagian 3).
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.classification.pelaksana import (
    DataOkupansiKosongError,
    RuangTidakDitemukanError,
    jalankan_klasifikasi,
)
from app.database import get_db

router = APIRouter()

BATAS_HARI = 400


class PermintaanKlasifikasi(BaseModel):
    tanggal_mulai: date
    tanggal_selesai: date
    room_id: int | None = Field(default=None, ge=1)


class KlasifikasiOut(BaseModel):
    tanggal_mulai: date
    tanggal_selesai: date
    jumlah_ruang: int
    jumlah_baris: int
    per_status: dict[str, int]


@router.post(
    "/classify",
    response_model=KlasifikasiOut,
    summary="Jalankan klasifikasi dan simpan hasilnya",
    description=(
        "Mengganti hasil klasifikasi pada ruang dan rentang tanggal itu (idempoten). "
        "Menjawab 409 bila belum ada data okupansi pada rentang itu."
    ),
)
def klasifikasikan(
    permintaan: PermintaanKlasifikasi,
    session: Session = Depends(get_db),
) -> KlasifikasiOut:
    if permintaan.tanggal_mulai > permintaan.tanggal_selesai:
        raise HTTPException(
            status_code=422,
            detail="tanggal_mulai tidak boleh setelah tanggal_selesai.",
        )
    if (permintaan.tanggal_selesai - permintaan.tanggal_mulai).days + 1 > BATAS_HARI:
        raise HTTPException(
            status_code=422,
            detail=f"Rentang tanggal maksimal {BATAS_HARI} hari.",
        )

    try:
        ringkasan = jalankan_klasifikasi(
            session,
            permintaan.tanggal_mulai,
            permintaan.tanggal_selesai,
            room_ids=[permintaan.room_id] if permintaan.room_id is not None else None,
        )
        session.commit()
    except RuangTidakDitemukanError as galat:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(galat)) from galat
    except DataOkupansiKosongError as galat:
        session.rollback()
        raise HTTPException(status_code=409, detail=str(galat)) from galat
    except ValueError as galat:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Klasifikasi gagal: {galat}") from galat
    except Exception:
        session.rollback()
        raise

    return KlasifikasiOut(
        tanggal_mulai=ringkasan.tanggal_mulai,
        tanggal_selesai=ringkasan.tanggal_selesai,
        jumlah_ruang=ringkasan.jumlah_ruang,
        jumlah_baris=ringkasan.jumlah_baris,
        per_status=ringkasan.per_status,
    )
