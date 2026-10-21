"""Pembangkit kalimat penjelasan Bahasa Indonesia untuk hasil klasifikasi sistem pakar."""

from __future__ import annotations

from datetime import time
from typing import Mapping

from app.expert_system.basis_pengetahuan import (
    TEMPLAT_R01,
    TEMPLAT_R02,
    TEMPLAT_R03,
)

MAP_TEMPLAT: Mapping[str, str] = {
    "R01": TEMPLAT_R01,
    "R02": TEMPLAT_R02,
    "R03": TEMPLAT_R03,
}


def format_waktu_id(t: time) -> str:
    """Format waktu objek datetime.time ke format Bahasa Indonesia standar ('07.00')."""
    return t.strftime("%H.%M")


def bangun_penjelasan(
    rule_id: str,
    menit_terjadwal: int,
    menit_terpakai: int,
    waktu_mulai: time,
    waktu_selesai: time,
) -> str:
    """Membangun kalimat penjelasan Bahasa Indonesia berdasarkan rule_id dan fakta terkait.

    Sesuai DATA_CONTRACT Bagian 12:
    - R01: 'Ruang terisi {menit_terpakai} dari {menit_terjadwal} menit terjadwal.'
    - R02: 'Ruang terisi hanya {menit_terpakai} menit dari {menit_terjadwal} menit terjadwal.
           Ruang ini berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU.'
    - R03: 'Ruang terisi {menit_terpakai} menit di luar jadwal ({waktu_mulai} sampai {waktu_selesai}).
           Perlu ditinjau Admin.'
    """
    templat = MAP_TEMPLAT.get(rule_id)
    if not templat:
        raise ValueError(f"rule_id '{rule_id}' tidak memiliki templat penjelasan resmi.")

    return templat.format(
        menit_terjadwal=menit_terjadwal,
        menit_terpakai=menit_terpakai,
        durasi_episode=menit_terpakai,
        waktu_mulai=format_waktu_id(waktu_mulai),
        waktu_selesai=format_waktu_id(waktu_selesai),
    )
