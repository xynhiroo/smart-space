"""Endpoint pembacaan hasil klasifikasi dan utilisasi (SS1-11).

Semua endpoint di modul ini hanya membaca database. Python hanya boleh menulis
occupancy_logs dan classification_results (DATA_CONTRACT Bagian 3).
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.utilization import (
    Sesi,
    hitung_statistik_ruang,
    korelasi_jadwal_vs_terpakai,
)
from app.api.skema import (
    DaftarHasilOut,
    HasilKlasifikasiOut,
    KorelasiOut,
    Status,
    UtilisasiOut,
    UtilisasiRuangOut,
)
from app.classification.pemuat import muat_ambang
from app.database import get_db
from app.models import ClassificationResult, Room

router = APIRouter()

BATAS_LIMIT = 1000


def bulatkan(nilai: float | None, desimal: int = 2) -> float | None:
    """Membulatkan untuk tampilan dengan ROUND_HALF_UP (mis. 33.335 menjadi 33.34)."""
    if nilai is None:
        return None
    pola = Decimal(10) ** -desimal
    return float(Decimal(str(nilai)).quantize(pola, rounding=ROUND_HALF_UP))


def _periksa_periode(tanggal_mulai: date, tanggal_selesai: date) -> None:
    if tanggal_mulai > tanggal_selesai:
        raise HTTPException(
            status_code=422,
            detail="tanggal_mulai tidak boleh setelah tanggal_selesai.",
        )


def _ke_keluaran(baris: ClassificationResult) -> HasilKlasifikasiOut:
    return HasilKlasifikasiOut(
        id=baris.id,
        room_id=baris.room_id,
        schedule_id=baris.schedule_id,
        tanggal=baris.tanggal,
        waktu_mulai=baris.waktu_mulai,
        waktu_selesai=baris.waktu_selesai,
        status=baris.status,
        menit_terjadwal=baris.menit_terjadwal,
        menit_terpakai=baris.menit_terpakai,
        utilisasi_pct=float(baris.utilisasi_pct) if baris.utilisasi_pct is not None else None,
        rule_id=baris.rule_id,
        penjelasan=baris.penjelasan,
        computed_at=baris.computed_at,
    )


@router.get(
    "/results",
    response_model=DaftarHasilOut,
    summary="Daftar hasil klasifikasi",
    description="Hasil klasifikasi per sesi atau episode pada rentang tanggal (inklusif).",
)
def daftar_hasil(
    tanggal_mulai: date = Query(..., description="Tanggal awal, format YYYY-MM-DD."),
    tanggal_selesai: date = Query(..., description="Tanggal akhir, format YYYY-MM-DD."),
    room_id: int | None = Query(None, ge=1, description="Batasi pada satu ruang."),
    status: Status | None = Query(None, description="Batasi pada satu status."),
    limit: int = Query(100, ge=1, le=BATAS_LIMIT),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db),
) -> DaftarHasilOut:
    _periksa_periode(tanggal_mulai, tanggal_selesai)

    kueri = session.query(ClassificationResult).filter(
        ClassificationResult.tanggal.between(tanggal_mulai, tanggal_selesai)
    )
    if room_id is not None:
        kueri = kueri.filter(ClassificationResult.room_id == room_id)
    if status is not None:
        kueri = kueri.filter(ClassificationResult.status == status)

    total = kueri.count()
    baris = (
        kueri.order_by(
            ClassificationResult.tanggal,
            ClassificationResult.waktu_mulai,
            ClassificationResult.room_id,
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return DaftarHasilOut(
        total=total,
        limit=limit,
        offset=offset,
        items=[_ke_keluaran(b) for b in baris],
    )


@router.get(
    "/utilization",
    response_model=UtilisasiOut,
    summary="Utilisasi dan statistik efisiensi per ruang",
    description=(
        "Utilisasi periode = total menit terpakai / total menit terjadwal x 100 "
        "(DATA_CONTRACT Bagian 10). Episode di luar jadwal tidak ikut dihitung. "
        "Ambang kategori dibaca dari threshold_settings."
    ),
)
def utilisasi(
    tanggal_mulai: date = Query(..., description="Tanggal awal, format YYYY-MM-DD."),
    tanggal_selesai: date = Query(..., description="Tanggal akhir, format YYYY-MM-DD."),
    room_id: int | None = Query(None, ge=1, description="Batasi pada satu ruang."),
    session: Session = Depends(get_db),
) -> UtilisasiOut:
    _periksa_periode(tanggal_mulai, tanggal_selesai)

    kueri_ruang = session.query(Room.id, Room.nama_ruangan).order_by(Room.id)
    if room_id is not None:
        kueri_ruang = kueri_ruang.filter(Room.id == room_id)
    daftar_ruang = kueri_ruang.all()
    if room_id is not None and not daftar_ruang:
        raise HTTPException(status_code=404, detail=f"Ruang {room_id} tidak ditemukan.")
    nama_ruang = {id_ruang: nama for id_ruang, nama in daftar_ruang}

    try:
        ambang = muat_ambang(session)
    except ValueError as galat:
        raise HTTPException(
            status_code=500,
            detail=f"Pengaturan ambang tidak dapat dipakai: {galat}",
        ) from galat

    kueri_sesi = session.query(
        ClassificationResult.room_id,
        ClassificationResult.tanggal,
        ClassificationResult.menit_terjadwal,
        ClassificationResult.menit_terpakai,
    ).filter(
        ClassificationResult.schedule_id.is_not(None),
        ClassificationResult.tanggal.between(tanggal_mulai, tanggal_selesai),
    )
    if room_id is not None:
        kueri_sesi = kueri_sesi.filter(ClassificationResult.room_id == room_id)
    daftar_sesi = [
        Sesi(
            room_id=baris.room_id,
            tanggal=baris.tanggal,
            menit_terjadwal=baris.menit_terjadwal,
            menit_terpakai=baris.menit_terpakai,
        )
        for baris in kueri_sesi
    ]

    try:
        statistik = hitung_statistik_ruang(
            daftar_sesi,
            tanggal_mulai,
            tanggal_selesai,
            ambang.batas_rendah,
            ambang.batas_sedang,
            daftar_room_id=nama_ruang.keys(),
        )
    except ValueError as galat:
        raise HTTPException(
            status_code=500,
            detail=f"Data classification_results tidak konsisten: {galat}",
        ) from galat

    korelasi = korelasi_jadwal_vs_terpakai(statistik.values())

    return UtilisasiOut(
        tanggal_mulai=tanggal_mulai,
        tanggal_selesai=tanggal_selesai,
        batas_rendah=ambang.batas_rendah,
        batas_sedang=ambang.batas_sedang,
        ruang=[
            UtilisasiRuangOut(
                room_id=s.room_id,
                nama_ruangan=nama_ruang.get(s.room_id, "-"),
                menit_terjadwal=s.menit_terjadwal,
                menit_terpakai=s.menit_terpakai,
                selisih_menit=s.selisih_menit,
                utilisasi_pct=bulatkan(s.utilisasi_pct),
                kategori=s.kategori,
                rata_rata_harian_pct=bulatkan(s.rata_rata_harian_pct),
                min_harian_pct=bulatkan(s.min_harian_pct),
                max_harian_pct=bulatkan(s.max_harian_pct),
            )
            for s in statistik.values()
        ],
        korelasi=KorelasiOut(
            jumlah_ruang=korelasi.jumlah_ruang,
            pearson=bulatkan(korelasi.pearson, 4),
            spearman=bulatkan(korelasi.spearman, 4),
        ),
    )
