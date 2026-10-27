"""Konstanta bernama untuk paket ML risiko sesi kosong (SS1-14).

Semua angka potong, seed, dan ambang didefinisikan di sini sebagai konstanta
bernama agar tidak ada angka literal tersebar di logika model.
"""

from __future__ import annotations

from datetime import date

# ---------------------------------------------------------------------------
# Random seed
# ---------------------------------------------------------------------------
RANDOM_STATE: int = 42

# ---------------------------------------------------------------------------
# Pembagian kronologis (DATA_CONTRACT §2a, prompt SS1-14)
# ---------------------------------------------------------------------------
TANGGAL_LATIH_MULAI: date = date(2026, 9, 7)
TANGGAL_LATIH_SELESAI: date = date(2026, 11, 13)

TANGGAL_VALIDASI_MULAI: date = date(2026, 11, 16)
TANGGAL_VALIDASI_SELESAI: date = date(2026, 12, 18)

TANGGAL_UJI_MULAI: date = date(2026, 12, 21)
TANGGAL_UJI_SELESAI: date = date(2027, 1, 22)

SEMESTER_START: date = date(2026, 9, 7)

# ---------------------------------------------------------------------------
# Shift — digunakan bila kolom schedules.shift bernilai NULL
# ---------------------------------------------------------------------------
BATAS_JAM_SHIFT_PAGI: int = 12  # jam_mulai < 12 → pagi
BATAS_JAM_SHIFT_SIANG: int = 17  # 12 <= jam_mulai < 17 → siang, >= 17 → malam

SHIFT_PAGI: str = "pagi"
SHIFT_SIANG: str = "siang"
SHIFT_MALAM: str = "malam"

# ---------------------------------------------------------------------------
# Dekat libur — N hari kerja sebelum/sesudah
# ---------------------------------------------------------------------------
JARAK_DEKAT_LIBUR_HARI_KERJA: int = 2

# ---------------------------------------------------------------------------
# Hiperparameter grid
# ---------------------------------------------------------------------------
KEDALAMAN_POHON_RANGE: list[int] = list(range(1, 13))  # 1..12
C_VALUES: list[float] = [0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0]

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
BOOTSTRAP_N_RESAMPLE: int = 1000
BOOTSTRAP_SEED: int = 123

# ---------------------------------------------------------------------------
# Direktori model
# ---------------------------------------------------------------------------
MODEL_DIR_NAME: str = "models"

# ---------------------------------------------------------------------------
# Status label
# ---------------------------------------------------------------------------
STATUS_KOSONG: str = "kosong_meski_terjadwal"

# ---------------------------------------------------------------------------
# Kolom terlarang (anti-kebocoran)
# ---------------------------------------------------------------------------
KOLOM_TERLARANG: frozenset[str] = frozenset({
    "status",
    "menit_terpakai",
    "utilisasi_pct",
    "rule_id",
    "penjelasan",
    "penyebab",
})
