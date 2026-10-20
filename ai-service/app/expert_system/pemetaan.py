"""Pemetaan hasil klasifikasi sistem pakar ke entitas utilisasi dan baris database."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Any

from app.analytics.utilization import Sesi
from app.expert_system.tipe import HasilKlasifikasi


def ke_sesi(hasil: HasilKlasifikasi) -> Sesi | None:
    """Memetakan HasilKlasifikasi ke tipe Sesi untuk penghitungan analitik utilisasi (SS1-10).

    Mengembalikan None untuk baris episode di luar jadwal (schedule_id IS NULL)
    karena utilisasi hanya dihitung untuk sesi terjadwal.
    """
    if hasil.schedule_id is None:
        return None

    return Sesi(
        room_id=hasil.room_id,
        tanggal=hasil.tanggal,
        menit_terjadwal=hasil.menit_terjadwal,
        menit_terpakai=hasil.menit_terpakai,
    )


def ke_baris_classification_results(
    hasil: HasilKlasifikasi, computed_at: datetime
) -> dict[str, Any]:
    """Memetakan HasilKlasifikasi ke kamus baris tabel classification_results (DATA_CONTRACT Bagian 5).

    Aturan:
    - utilisasi_pct dibulatkan 2 desimal menggunakan ROUND_HALF_UP (mis. 33.335 -> 33.34).
    - Mempertahankan None untuk utilisasi_pct dan schedule_id.
    - Menjaga invarian integritas: status == 'dipakai_di_luar_jadwal' <==> schedule_id IS NULL.
    """
    if (hasil.status == "dipakai_di_luar_jadwal") != (hasil.schedule_id is None):
        raise ValueError(
            f"Invarian dilanggar: status '{hasil.status}' tidak selaras dengan schedule_id {hasil.schedule_id}."
        )

    if hasil.utilisasi_pct is not None:
        utilisasi_decimal: Decimal | None = Decimal(str(hasil.utilisasi_pct)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        utilisasi_decimal = None

    return {
        "room_id": hasil.room_id,
        "schedule_id": hasil.schedule_id,
        "tanggal": hasil.tanggal,
        "waktu_mulai": hasil.waktu_mulai,
        "waktu_selesai": hasil.waktu_selesai,
        "status": hasil.status,
        "menit_terjadwal": hasil.menit_terjadwal,
        "menit_terpakai": hasil.menit_terpakai,
        "utilisasi_pct": utilisasi_decimal,
        "rule_id": hasil.rule_id,
        "penjelasan": hasil.penjelasan,
        "computed_at": computed_at,
    }
