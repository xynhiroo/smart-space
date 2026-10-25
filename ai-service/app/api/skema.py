"""Skema respons endpoint (SS1-11)."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel

Status = Literal["sesuai_jadwal", "kosong_meski_terjadwal", "dipakai_di_luar_jadwal"]


class HasilKlasifikasiOut(BaseModel):
    id: int
    room_id: int
    schedule_id: int | None
    tanggal: date
    waktu_mulai: time
    waktu_selesai: time
    status: str
    menit_terjadwal: int
    menit_terpakai: int
    utilisasi_pct: float | None
    rule_id: str
    penjelasan: str
    computed_at: datetime


class DaftarHasilOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[HasilKlasifikasiOut]


class UtilisasiRuangOut(BaseModel):
    room_id: int
    nama_ruangan: str
    menit_terjadwal: int
    menit_terpakai: int
    selisih_menit: int
    utilisasi_pct: float | None
    kategori: str | None
    rata_rata_harian_pct: float | None
    min_harian_pct: float | None
    max_harian_pct: float | None


class KorelasiOut(BaseModel):
    jumlah_ruang: int
    pearson: float | None
    spearman: float | None


class UtilisasiOut(BaseModel):
    tanggal_mulai: date
    tanggal_selesai: date
    batas_rendah: float
    batas_sedang: float
    ruang: list[UtilisasiRuangOut]
    korelasi: KorelasiOut
