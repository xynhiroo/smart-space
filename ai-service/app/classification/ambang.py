"""Pembentuk Ambang dari pasangan key-value tabel threshold_settings.

Kolom value di database bertipe teks, jadi nilainya diubah menjadi angka di sini.
Tidak ada angka ambang yang ditulis langsung di kode (DATA_CONTRACT Bagian 8).
"""

from __future__ import annotations

from typing import Mapping

from app.expert_system.tipe import Ambang

KUNCI_WAJIB = (
    "empty_min_occupied_minutes",
    "outside_schedule_min_minutes",
    "utilization_low_max",
    "utilization_medium_max",
)


def bentuk_ambang(nilai: Mapping[str, str]) -> Ambang:
    """Membentuk Ambang dari pasangan key-value threshold_settings.

    Raises:
        ValueError: kunci wajib hilang, nilai bukan angka, menit negatif,
            atau batas rendah tidak lebih kecil dari batas sedang.
    """
    hilang = [kunci for kunci in KUNCI_WAJIB if kunci not in nilai]
    if hilang:
        raise ValueError(
            f"Kunci threshold_settings tidak ditemukan: {', '.join(hilang)}"
        )

    try:
        menit_kosong = int(str(nilai["empty_min_occupied_minutes"]).strip())
        menit_luar = int(str(nilai["outside_schedule_min_minutes"]).strip())
        batas_rendah = float(str(nilai["utilization_low_max"]).strip())
        batas_sedang = float(str(nilai["utilization_medium_max"]).strip())
    except ValueError as galat:
        raise ValueError(f"Nilai threshold_settings tidak valid: {galat}") from galat

    if menit_kosong < 0 or menit_luar < 0:
        raise ValueError("Ambang menit tidak boleh negatif.")
    if batas_rendah >= batas_sedang:
        raise ValueError("utilization_low_max harus lebih kecil dari utilization_medium_max.")

    return Ambang(
        empty_min_occupied_minutes=menit_kosong,
        outside_schedule_min_minutes=menit_luar,
        batas_rendah=batas_rendah,
        batas_sedang=batas_sedang,
    )
