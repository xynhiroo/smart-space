"""Pembangun fitur untuk model risiko sesi kosong (SS1-14).

Semua fungsi di modul ini adalah fungsi murni: menerima DataFrame dan
mengembalikan DataFrame baru tanpa mengakses database, waktu sistem, atau
state global.

Aturan anti-kebocoran:
- Fitur hanya dihitung dari informasi yang diketahui SEBELUM sesi dimulai.
- Kolom terlarang (status, menit_terpakai, utilisasi_pct, rule_id,
  penjelasan, penyebab) tidak boleh masuk matriks fitur.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import Sequence

import numpy as np
import pandas as pd

from app.generator.params import NAMA_OPEN_SPACE
from app.ml.konstanta import (
    BATAS_JAM_SHIFT_PAGI,
    BATAS_JAM_SHIFT_SIANG,
    JARAK_DEKAT_LIBUR_HARI_KERJA,
    KOLOM_TERLARANG,
    SEMESTER_START,
    SHIFT_MALAM,
    SHIFT_PAGI,
    SHIFT_SIANG,
    STATUS_KOSONG,
)


def turunkan_shift(jam_mulai: time) -> str:
    """Tentukan shift dari jam_mulai jika kolom shift kosong."""
    jam = jam_mulai.hour
    if jam < BATAS_JAM_SHIFT_PAGI:
        return SHIFT_PAGI
    if jam < BATAS_JAM_SHIFT_SIANG:
        return SHIFT_SIANG
    return SHIFT_MALAM


def hitung_durasi_menit(jam_mulai: time, jam_selesai: time) -> int:
    """Hitung durasi sesi dalam menit dari jam_mulai dan jam_selesai."""
    dt_mulai = timedelta(hours=jam_mulai.hour, minutes=jam_mulai.minute)
    dt_selesai = timedelta(hours=jam_selesai.hour, minutes=jam_selesai.minute)
    return int((dt_selesai - dt_mulai).total_seconds() / 60)


def hitung_pekan_ke(tanggal: date, semester_start: date = SEMESTER_START) -> int:
    """Pekan ke berapa sejak awal semester (0-indexed)."""
    delta = (tanggal - semester_start).days
    return max(0, delta // 7)


def _kumpulkan_tanggal_libur(
    calendar_exceptions: pd.DataFrame,
) -> set[date]:
    """Kumpulkan semua tanggal bertipe 'libur' dari calendar_exceptions."""
    if calendar_exceptions.empty:
        return set()
    libur_rows = calendar_exceptions[calendar_exceptions["tipe"] == "libur"]
    tanggal_libur: set[date] = set()
    for _, row in libur_rows.iterrows():
        t_mulai = row["tanggal_mulai"]
        t_selesai = row["tanggal_selesai"]
        if isinstance(t_mulai, str):
            t_mulai = date.fromisoformat(t_mulai)
        if isinstance(t_selesai, str):
            t_selesai = date.fromisoformat(t_selesai)
        curr = t_mulai
        while curr <= t_selesai:
            tanggal_libur.add(curr)
            curr += timedelta(days=1)
    return tanggal_libur


def _is_hari_kerja(d: date, tanggal_libur: set[date]) -> bool:
    """Hari kerja = Senin-Jumat dan bukan libur."""
    return d.weekday() < 5 and d not in tanggal_libur


def hitung_dekat_libur(
    tanggal: date,
    tanggal_libur: set[date],
    n_hari_kerja: int = JARAK_DEKAT_LIBUR_HARI_KERJA,
) -> bool:
    """Ada tanggal libur dalam N hari kerja sebelum atau sesudah tanggal."""
    # Periksa sebelum
    count = 0
    d = tanggal - timedelta(days=1)
    while count < n_hari_kerja:
        if d in tanggal_libur:
            return True
        if _is_hari_kerja(d, tanggal_libur):
            count += 1
        d -= timedelta(days=1)

    # Periksa sesudah
    count = 0
    d = tanggal + timedelta(days=1)
    while count < n_hari_kerja:
        if d in tanggal_libur:
            return True
        if _is_hari_kerja(d, tanggal_libur):
            count += 1
        d += timedelta(days=1)

    return False


def _resolve_jenis_hari(
    tanggal: date, calendar_exceptions: pd.DataFrame
) -> str:
    """Tentukan jenis hari: biasa, ujian, kegiatan_khusus (libur sudah difilter)."""
    if calendar_exceptions.empty:
        return "biasa"

    priority_map = {"ujian": 2, "kegiatan_khusus": 1}
    best_priority = 0
    best_kind = "biasa"

    for _, row in calendar_exceptions.iterrows():
        t_mulai = row["tanggal_mulai"]
        t_selesai = row["tanggal_selesai"]
        tipe = row["tipe"]

        if isinstance(t_mulai, str):
            t_mulai = date.fromisoformat(t_mulai)
        if isinstance(t_selesai, str):
            t_selesai = date.fromisoformat(t_selesai)

        if t_mulai <= tanggal <= t_selesai:
            p = priority_map.get(tipe, 0)
            if p > best_priority:
                best_priority = p
                best_kind = tipe

    return best_kind


def _is_pekan_sebelum_ujian(
    tanggal: date, calendar_exceptions: pd.DataFrame
) -> bool:
    """Apakah tanggal berada di pekan tepat sebelum masa ujian?"""
    if calendar_exceptions.empty:
        return False

    ujian_rows = calendar_exceptions[calendar_exceptions["tipe"] == "ujian"]
    for _, row in ujian_rows.iterrows():
        t_mulai = row["tanggal_mulai"]
        if isinstance(t_mulai, str):
            t_mulai = date.fromisoformat(t_mulai)
        # Pekan sebelum ujian: 7 hari sebelum tanggal_mulai ujian
        if timedelta(days=0) < (t_mulai - tanggal) <= timedelta(days=7):
            return True

    return False


def hitung_kosong_rate_ruang_sebelumnya(
    df: pd.DataFrame,
    tanggal: date,
    room_id: int,
    pekan_ke: int,
) -> tuple[float, bool]:
    """Proporsi sesi kosong pada ruang itu di pekan-pekan SEBELUM pekan sesi.

    Returns:
        (kosong_rate, ada_riwayat): kosong_rate = NaN jika tidak ada riwayat,
        ada_riwayat = False jika tidak ada data pekan sebelumnya.
    """
    if pekan_ke <= 0:
        return float("nan"), False

    mask = (df["room_id"] == room_id) & (df["pekan_ke"] < pekan_ke)
    riwayat = df.loc[mask]
    if riwayat.empty:
        return float("nan"), False

    jumlah_kosong = (riwayat["label"] == 1).sum()
    total = len(riwayat)
    return jumlah_kosong / total, True


def bangun_fitur(
    df_sesi: pd.DataFrame,
    calendar_exceptions: pd.DataFrame,
    semester_start: date = SEMESTER_START,
) -> pd.DataFrame:
    """Bangun matriks fitur dari DataFrame sesi terjadwal.

    df_sesi harus memiliki kolom:
        - room_id, nama_ruangan, tanggal, jam_mulai, jam_selesai,
          shift (boleh null), schedule_id, label

    calendar_exceptions harus memiliki kolom:
        - tanggal_mulai, tanggal_selesai, tipe

    Returns:
        DataFrame dengan fitur-fitur siap pakai (tanpa kolom terlarang).
    """
    if df_sesi.empty:
        return pd.DataFrame()

    df = df_sesi.copy()

    # Pastikan tanggal bertipe date
    if not pd.api.types.is_object_dtype(df["tanggal"]):
        df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date

    # --- Fitur dasar ---
    df["hari_dalam_pekan"] = df["tanggal"].apply(lambda d: d.weekday())

    df["jam_mulai_num"] = df["jam_mulai"].apply(
        lambda t: t.hour + t.minute / 60.0 if isinstance(t, time) else t
    )

    df["durasi_menit"] = df.apply(
        lambda row: hitung_durasi_menit(row["jam_mulai"], row["jam_selesai"])
        if isinstance(row["jam_mulai"], time)
        else 0,
        axis=1,
    )

    df["shift_val"] = df.apply(
        lambda row: row["shift"]
        if pd.notna(row.get("shift"))
        else turunkan_shift(row["jam_mulai"])
        if isinstance(row["jam_mulai"], time)
        else SHIFT_PAGI,
        axis=1,
    )

    # is_open_space dari NAMA_OPEN_SPACE (bukan duplikasi daftar)
    df["is_open_space"] = df["nama_ruangan"].isin(NAMA_OPEN_SPACE).astype(int)

    # Pekan ke
    df["pekan_ke"] = df["tanggal"].apply(
        lambda d: hitung_pekan_ke(d, semester_start)
    )

    # Kalender akademik
    tanggal_libur = _kumpulkan_tanggal_libur(calendar_exceptions)

    df["jenis_hari"] = df["tanggal"].apply(
        lambda d: _resolve_jenis_hari(d, calendar_exceptions)
    )

    df["dekat_libur"] = df["tanggal"].apply(
        lambda d: int(hitung_dekat_libur(d, tanggal_libur))
    )

    df["pekan_sebelum_ujian"] = df["tanggal"].apply(
        lambda d: int(_is_pekan_sebelum_ujian(d, calendar_exceptions))
    )

    # --- Fitur riwayat ---
    # Hitung kosong_rate_ruang_sebelumnya untuk setiap baris
    kosong_rates = []
    ada_riwayats = []
    for _, row in df.iterrows():
        rate, ada = hitung_kosong_rate_ruang_sebelumnya(
            df, row["tanggal"], row["room_id"], row["pekan_ke"]
        )
        kosong_rates.append(rate)
        ada_riwayats.append(int(ada))

    df["kosong_rate_ruang_sebelumnya"] = kosong_rates
    df["ada_riwayat"] = ada_riwayats

    # --- Validasi anti-kebocoran ---
    kolom_hasil = set(df.columns)
    bocor = kolom_hasil & KOLOM_TERLARANG
    if bocor:
        raise ValueError(
            f"Kolom terlarang ditemukan di matriks fitur: {bocor}. "
            "Fitur hanya boleh dari informasi sebelum sesi dimulai."
        )

    return df


def kolom_fitur() -> list[str]:
    """Daftar nama kolom fitur numerik dan kategorik.

    Kolom kategorik (one-hot): nama_ruangan, shift_val, jenis_hari
    Kolom numerik: hari_dalam_pekan, jam_mulai_num, durasi_menit,
                   is_open_space, pekan_ke, dekat_libur,
                   pekan_sebelum_ujian, kosong_rate_ruang_sebelumnya,
                   ada_riwayat
    """
    return [
        "nama_ruangan",
        "hari_dalam_pekan",
        "jam_mulai_num",
        "durasi_menit",
        "shift_val",
        "is_open_space",
        "pekan_ke",
        "jenis_hari",
        "dekat_libur",
        "pekan_sebelum_ujian",
        "kosong_rate_ruang_sebelumnya",
        "ada_riwayat",
    ]


KOLOM_KATEGORIK: list[str] = ["nama_ruangan", "shift_val", "jenis_hari"]
KOLOM_NUMERIK: list[str] = [
    "hari_dalam_pekan",
    "jam_mulai_num",
    "durasi_menit",
    "is_open_space",
    "pekan_ke",
    "dekat_libur",
    "pekan_sebelum_ujian",
    "kosong_rate_ruang_sebelumnya",
    "ada_riwayat",
]
