"""Basis pengetahuan sistem pakar: aturan sebagai data (DATA_CONTRACT Bagian 12).

Aturan didefinisikan sebagai data terstruktur, terpisah dari mesin inferensi.
Terdiri dari:
1. Aturan Turunan (id F..): menurunkan fakta perantara dari fakta observasi dan ambang batas.
2. Aturan Keputusan (id R..): menetapkan status akhir dan templat penjelasan.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable


@dataclass(frozen=True)
class Aturan:
    """Representasi satu aturan sistem pakar sebagai data."""

    rule_id: str
    nama: str
    kondisi: Callable[[Any], bool]
    kesimpulan: Callable[[Any], dict[str, Any]]
    templat_penjelasan: str | None = None


# ------------------------------------------------------------------------------
# 1. Aturan Turunan (F01 - F04)
# ------------------------------------------------------------------------------

def _kondisi_f01(wm: Any) -> bool:
    # F01: Sesi telah berakhir jika waktu evaluasi >= tanggal + jam_selesai
    if wm.get("jenis_evaluasi") != "sesi":
        return False
    if wm.get("sesi_telah_berakhir") is True:
        return False
    tgl = wm.get("tanggal")
    selesai = wm.get("jam_selesai")
    waktu_eval = wm.get("waktu_evaluasi")
    if tgl is None or selesai is None or waktu_eval is None:
        return False
    return waktu_eval >= datetime.combine(tgl, selesai)


def _kesimpulan_f01(wm: Any) -> dict[str, Any]:
    return {"sesi_telah_berakhir": True}


def _kondisi_f02(wm: Any) -> bool:
    # F02: Okupansi sesi kurang jika menit_terpakai < empty_min_occupied_minutes
    if not wm.get("sesi_telah_berakhir", False):
        return False
    if wm.get("okupansi_sesi_kurang") is True or wm.get("okupansi_sesi_cukup") is True:
        return False
    menit_terpakai = wm.get("menit_terpakai")
    ambang_kosong = wm.get("empty_min_occupied_minutes")
    if menit_terpakai is None or ambang_kosong is None:
        return False
    return menit_terpakai < ambang_kosong


def _kesimpulan_f02(wm: Any) -> dict[str, Any]:
    return {"okupansi_sesi_kurang": True}


def _kondisi_f03(wm: Any) -> bool:
    # F03: Okupansi sesi cukup jika menit_terpakai >= empty_min_occupied_minutes
    if not wm.get("sesi_telah_berakhir", False):
        return False
    if wm.get("okupansi_sesi_kurang") is True or wm.get("okupansi_sesi_cukup") is True:
        return False
    menit_terpakai = wm.get("menit_terpakai")
    ambang_kosong = wm.get("empty_min_occupied_minutes")
    if menit_terpakai is None or ambang_kosong is None:
        return False
    return menit_terpakai >= ambang_kosong


def _kesimpulan_f03(wm: Any) -> dict[str, Any]:
    return {"okupansi_sesi_cukup": True}


def _kondisi_f04(wm: Any) -> bool:
    # F04: Episode luar jadwal cukup panjang jika durasi >= outside_schedule_min_minutes
    if wm.get("jenis_evaluasi") != "episode":
        return False
    if wm.get("episode_cukup_panjang") is True:
        return False
    durasi = wm.get("durasi_episode")
    ambang_luar = wm.get("outside_schedule_min_minutes")
    if durasi is None or ambang_luar is None:
        return False
    return durasi >= ambang_luar


def _kesimpulan_f04(wm: Any) -> dict[str, Any]:
    return {"episode_cukup_panjang": True}


# ------------------------------------------------------------------------------
# 2. Aturan Keputusan (R01 - R03)
# ------------------------------------------------------------------------------

TEMPLAT_R01 = "Ruang terisi {menit_terpakai} dari {menit_terjadwal} menit terjadwal."
TEMPLAT_R02 = (
    "Ruang terisi hanya {menit_terpakai} menit dari {menit_terjadwal} menit terjadwal. "
    "Ruang ini berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU."
)
TEMPLAT_R03 = "Ruang terisi {menit_terpakai} menit di luar jadwal ({waktu_mulai} sampai {waktu_selesai}). Perlu ditinjau Admin."


def _kondisi_r01(wm: Any) -> bool:
    return (
        wm.get("okupansi_sesi_cukup") is True
        and wm.get("status") is None
    )


def _kesimpulan_r01(wm: Any) -> dict[str, Any]:
    return {
        "status": "sesuai_jadwal",
        "rule_id": "R01",
    }


def _kondisi_r02(wm: Any) -> bool:
    return (
        wm.get("okupansi_sesi_kurang") is True
        and wm.get("status") is None
    )


def _kesimpulan_r02(wm: Any) -> dict[str, Any]:
    return {
        "status": "kosong_meski_terjadwal",
        "rule_id": "R02",
    }


def _kondisi_r03(wm: Any) -> bool:
    return (
        wm.get("episode_cukup_panjang") is True
        and wm.get("status") is None
    )


def _kesimpulan_r03(wm: Any) -> dict[str, Any]:
    return {
        "status": "dipakai_di_luar_jadwal",
        "rule_id": "R03",
    }


DAFTAR_ATURAN_DEFAULT: tuple[Aturan, ...] = (
    # Aturan Turunan Fakta
    Aturan(
        rule_id="F01",
        nama="Deteksi Sesi Berakhir",
        kondisi=_kondisi_f01,
        kesimpulan=_kesimpulan_f01,
    ),
    Aturan(
        rule_id="F02",
        nama="Evaluasi Okupansi Sesi Kurang",
        kondisi=_kondisi_f02,
        kesimpulan=_kesimpulan_f02,
    ),
    Aturan(
        rule_id="F03",
        nama="Evaluasi Okupansi Sesi Memenuhi",
        kondisi=_kondisi_f03,
        kesimpulan=_kesimpulan_f03,
    ),
    Aturan(
        rule_id="F04",
        nama="Evaluasi Durasi Episode Cukup",
        kondisi=_kondisi_f04,
        kesimpulan=_kesimpulan_f04,
    ),
    # Aturan Keputusan Status
    Aturan(
        rule_id="R01",
        nama="Klasifikasi Sesuai Jadwal",
        kondisi=_kondisi_r01,
        kesimpulan=_kesimpulan_r01,
        templat_penjelasan=TEMPLAT_R01,
    ),
    Aturan(
        rule_id="R02",
        nama="Klasifikasi Kosong Meski Terjadwal",
        kondisi=_kondisi_r02,
        kesimpulan=_kesimpulan_r02,
        templat_penjelasan=TEMPLAT_R02,
    ),
    Aturan(
        rule_id="R03",
        nama="Klasifikasi Dipakai di Luar Jadwal",
        kondisi=_kondisi_r03,
        kesimpulan=_kesimpulan_r03,
        templat_penjelasan=TEMPLAT_R03,
    ),
)
