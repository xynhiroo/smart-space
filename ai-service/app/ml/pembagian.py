"""Pembagian kronologis dataset ML (SS1-14).

Pembagian berdasarkan tanggal, bukan acak, untuk menghindari kebocoran
temporal. Konstanta tanggal potong didefinisikan di konstanta.py.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from app.ml.konstanta import (
    TANGGAL_LATIH_MULAI,
    TANGGAL_LATIH_SELESAI,
    TANGGAL_UJI_MULAI,
    TANGGAL_UJI_SELESAI,
    TANGGAL_VALIDASI_MULAI,
    TANGGAL_VALIDASI_SELESAI,
)


def bagi_kronologis(
    df: pd.DataFrame,
    kolom_tanggal: str = "tanggal",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Bagi DataFrame menjadi blok latih, validasi, dan uji.

    Blok:
    - Latih:    TANGGAL_LATIH_MULAI s.d. TANGGAL_LATIH_SELESAI
    - Validasi: TANGGAL_VALIDASI_MULAI s.d. TANGGAL_VALIDASI_SELESAI
    - Uji:      TANGGAL_UJI_MULAI s.d. TANGGAL_UJI_SELESAI

    Mencetak distribusi kelas tiap blok.

    Returns:
        (df_latih, df_validasi, df_uji)
    """
    tanggal = df[kolom_tanggal].apply(
        lambda d: d if isinstance(d, date) else date.fromisoformat(str(d))
    )

    mask_latih = (tanggal >= TANGGAL_LATIH_MULAI) & (
        tanggal <= TANGGAL_LATIH_SELESAI
    )
    mask_val = (tanggal >= TANGGAL_VALIDASI_MULAI) & (
        tanggal <= TANGGAL_VALIDASI_SELESAI
    )
    mask_uji = (tanggal >= TANGGAL_UJI_MULAI) & (
        tanggal <= TANGGAL_UJI_SELESAI
    )

    df_latih = df.loc[mask_latih].copy()
    df_val = df.loc[mask_val].copy()
    df_uji = df.loc[mask_uji].copy()

    # Cetak distribusi kelas
    for nama, blok in [("Latih", df_latih), ("Validasi", df_val), ("Uji", df_uji)]:
        if "label" in blok.columns:
            distribusi = blok["label"].value_counts().to_dict()
            total = len(blok)
            positif = distribusi.get(1, 0)
            print(
                f"  [{nama}] Total={total}, Positif(kosong)={positif}, "
                f"Negatif={distribusi.get(0, 0)}, "
                f"Rasio positif={positif / total:.3f}" if total > 0 else
                f"  [{nama}] Total=0 (KOSONG)"
            )
            if positif < 20:
                print(
                    f"  [!] PERINGATAN: Blok {nama} hanya punya {positif} "
                    f"sampel positif (< 20). Metrik mungkin tidak stabil."
                )
        else:
            print(f"  [{nama}] {len(blok)} baris (tanpa kolom label)")

    # Cetak rentang tanggal
    print(f"\n  Rentang tanggal:")
    print(f"    Latih:    {TANGGAL_LATIH_MULAI} s.d. {TANGGAL_LATIH_SELESAI}")
    print(f"    Validasi: {TANGGAL_VALIDASI_MULAI} s.d. {TANGGAL_VALIDASI_SELESAI}")
    print(f"    Uji:      {TANGGAL_UJI_MULAI} s.d. {TANGGAL_UJI_SELESAI}")

    return df_latih, df_val, df_uji


def verifikasi_pembagian(
    df_latih: pd.DataFrame,
    df_val: pd.DataFrame,
    df_uji: pd.DataFrame,
    kolom_tanggal: str = "tanggal",
) -> None:
    """Verifikasi bahwa blok tidak tumpang tindih dan berurutan."""

    def _max_tanggal(df: pd.DataFrame) -> date | None:
        if df.empty:
            return None
        return max(
            d if isinstance(d, date) else date.fromisoformat(str(d))
            for d in df[kolom_tanggal]
        )

    def _min_tanggal(df: pd.DataFrame) -> date | None:
        if df.empty:
            return None
        return min(
            d if isinstance(d, date) else date.fromisoformat(str(d))
            for d in df[kolom_tanggal]
        )

    max_latih = _max_tanggal(df_latih)
    min_val = _min_tanggal(df_val)
    max_val = _max_tanggal(df_val)
    min_uji = _min_tanggal(df_uji)

    if max_latih is not None and min_val is not None:
        assert max_latih < min_val, (
            f"Blok latih ({max_latih}) tumpang tindih dengan validasi ({min_val})"
        )
    if max_val is not None and min_uji is not None:
        assert max_val < min_uji, (
            f"Blok validasi ({max_val}) tumpang tindih dengan uji ({min_uji})"
        )
    if max_latih is not None and min_uji is not None:
        assert max_latih < min_uji, (
            f"Sesi blok uji ({min_uji}) lebih awal dari akhir latih ({max_latih})"
        )

    # Periksa tidak ada index tumpang tindih
    idx_latih = set(df_latih.index)
    idx_val = set(df_val.index)
    idx_uji = set(df_uji.index)

    assert not (idx_latih & idx_val), "Index latih dan validasi tumpang tindih"
    assert not (idx_latih & idx_uji), "Index latih dan uji tumpang tindih"
    assert not (idx_val & idx_uji), "Index validasi dan uji tumpang tindih"
