"""CLI untuk model ML risiko sesi kosong (SS1-14).

Perintah:
    python -m app.ml latih --set dev
        Melatih model pada set dev, memilih hiperparameter dan ambang di
        blok validasi, dan menyimpan model ke ai-service/models/.

    python -m app.ml evaluasi-akhir --set test
        Evaluasi akhir pada set test. HANYA boleh dijalankan sekali.
        Menolak berjalan tanpa model tersimpan.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from app.ml.konstanta import (
    MODEL_DIR_NAME,
    RANDOM_STATE,
    TANGGAL_LATIH_MULAI,
    TANGGAL_LATIH_SELESAI,
    TANGGAL_UJI_MULAI,
    TANGGAL_UJI_SELESAI,
    TANGGAL_VALIDASI_MULAI,
    TANGGAL_VALIDASI_SELESAI,
)
from app.ml.fitur import bangun_fitur, kolom_fitur
from app.ml.pembagian import bagi_kronologis, verifikasi_pembagian
from app.ml.model import latih_dan_pilih, muat_model, simpan_model
from app.ml.evaluasi import (
    analisis_kesalahan,
    baseline_mayoritas,
    baseline_rata_historis_jenis_hari,
    baseline_rata_historis_ruang,
    bootstrap_ci,
    cetak_irisan_uji,
    cetak_metrik,
    hitung_metrik,
    hitung_rata_per_jenis_hari,
    hitung_rata_per_ruang,
    koefisien_logreg,
    pentingnya_fitur_tree,
)

AI_SERVICE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = AI_SERVICE_DIR / MODEL_DIR_NAME


def _buat_url_database(nama_set: str) -> str:
    """Buat DATABASE_URL untuk set tertentu."""
    import os
    from dotenv import load_dotenv

    load_dotenv(AI_SERVICE_DIR / ".env")

    db_user = os.getenv("DB_USERNAME", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")

    if nama_set == "dev":
        db_name = "smart_space_ai_dev"
    elif nama_set == "test":
        db_name = "smart_space_ai_test"
    else:
        raise ValueError(f"Set tidak dikenal: {nama_set}. Gunakan 'dev' atau 'test'.")

    if db_password:
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}"


def _buat_session(nama_set: str):
    """Buat SQLAlchemy session untuk set tertentu."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    url = _buat_url_database(nama_set)
    engine = create_engine(url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()


def cmd_latih(args: argparse.Namespace) -> None:
    """Latih model pada set dev."""
    from app.ml.dataset import muat_calendar_exceptions, muat_sesi_terjadwal

    nama_set = args.set
    print("====================================================")
    print(f"  ML Risiko Sesi Kosong - Pelatihan (set: {nama_set})")
    print("====================================================")

    session = _buat_session(nama_set)

    try:
        # 1. Muat data
        print("\n[1/6] Memuat data sesi terjadwal...")
        df_sesi = muat_sesi_terjadwal(session)
        print(f"  Jumlah sesi: {len(df_sesi)}")

        if df_sesi.empty:
            print("  [X] Tidak ada data sesi terjadwal di database.")
            print("    Jalankan runner klasifikasi terlebih dahulu:")
            print(f"    python -m app.classification --set {nama_set}")
            sys.exit(1)

        print("\n[2/6] Memuat calendar_exceptions...")
        cal_exc = muat_calendar_exceptions(session)
        print(f"  Jumlah pengecualian kalender: {len(cal_exc)}")

        # 2. Bangun fitur
        print("\n[3/6] Membangun fitur...")
        df_fitur = bangun_fitur(df_sesi, cal_exc)
        print(f"  Jumlah fitur: {len(kolom_fitur())}")

        # 3. Bagi data
        print("\n[4/6] Membagi data secara kronologis...")
        df_latih, df_val, df_uji = bagi_kronologis(df_fitur)
        verifikasi_pembagian(df_latih, df_val, df_uji)

        if df_latih.empty or df_val.empty:
            print("  [X] Blok latih atau validasi kosong.")
            sys.exit(1)

        # 4. Siapkan X, y
        fitur = kolom_fitur()
        fitur_ada = [f for f in fitur if f in df_latih.columns]

        X_latih = df_latih[fitur_ada]
        y_latih = df_latih["label"].values
        X_val = df_val[fitur_ada]
        y_val = df_val["label"].values

        # 5. Latih dan pilih hiperparameter
        print("\n[5/6] Melatih model...")
        hasil = latih_dan_pilih(X_latih, y_latih, X_val, y_val)

        # Tambahkan tanggal potong ke metadata
        hasil["tanggal_potong"] = {
            "latih_mulai": str(TANGGAL_LATIH_MULAI),
            "latih_selesai": str(TANGGAL_LATIH_SELESAI),
            "validasi_mulai": str(TANGGAL_VALIDASI_MULAI),
            "validasi_selesai": str(TANGGAL_VALIDASI_SELESAI),
        }

        # 6. Evaluasi pada validasi
        print("\n[6/6] Evaluasi pada blok validasi...")

        # Baseline
        print("\n-- Baseline --")
        m_maj = baseline_mayoritas(y_val)
        cetak_metrik("Baseline: Mayoritas", m_maj)

        rata_ruang = hitung_rata_per_ruang(df_latih)
        m_ruang = baseline_rata_historis_ruang(
            y_val, df_val["room_id"].values, rata_ruang
        )
        cetak_metrik("Baseline: Rata-rata historis per ruang", m_ruang)

        rata_jenis = hitung_rata_per_jenis_hari(df_latih)
        m_jenis = baseline_rata_historis_jenis_hari(
            y_val, df_val["jenis_hari"].values, rata_jenis
        )
        cetak_metrik("Baseline: Rata-rata historis per jenis hari", m_jenis)

        # Model
        print("\n-- Model --")
        for nama_model, key in [("Decision Tree", "tree"), ("Logistic Regression", "logreg")]:
            pipe = hasil[key]["pipeline"]
            ambang = hasil[key]["ambang"]
            y_proba = pipe.predict_proba(X_val)[:, 1]

            # Dengan ambang optimal
            y_pred_opt = (y_proba >= ambang).astype(int)
            m_opt = hitung_metrik(y_val, y_pred_opt, y_proba)
            cetak_metrik(f"{nama_model} (ambang={ambang})", m_opt)

            # Dengan ambang 0.5
            y_pred_05 = (y_proba >= 0.5).astype(int)
            m_05 = hitung_metrik(y_val, y_pred_05, y_proba)
            cetak_metrik(f"{nama_model} (ambang=0.5)", m_05)

        # Analisis kesalahan
        print("\n-- Analisis Kesalahan (Logistic Regression) --")
        pipe_lr = hasil["logreg"]["pipeline"]
        ambang_lr = hasil["logreg"]["ambang"]
        y_proba_lr = pipe_lr.predict_proba(X_val)[:, 1]
        y_pred_lr = (y_proba_lr >= ambang_lr).astype(int)
        err = analisis_kesalahan(df_val, y_val, y_pred_lr)
        for key_err, df_err in err.items():
            print(f"\n  {key_err}:")
            print(df_err.to_string(index=False))

        # Feature importance
        print("\n-- Feature Importance (Decision Tree) --")
        fi = pentingnya_fitur_tree(hasil["tree"]["pipeline"], fitur_ada)
        print(fi.head(15).to_string(index=False))

        print("\n-- Koefisien (Logistic Regression) --")
        coef = koefisien_logreg(hasil["logreg"]["pipeline"], fitur_ada)
        print(coef.to_string(index=False))

        # 7. Simpan model
        simpan_model(hasil, MODEL_PATH)

    finally:
        session.close()


def cmd_evaluasi_akhir(args: argparse.Namespace) -> None:
    """Evaluasi akhir pada set test — HANYA SEKALI."""
    from app.ml.dataset import muat_calendar_exceptions, muat_sesi_terjadwal

    nama_set = args.set
    print("====================================================")
    print(f"  ML Risiko Sesi Kosong - Evaluasi Akhir (set: {nama_set})")
    print("====================================================")
    print()
    print("  [!] PERINGATAN: Set test hanya boleh dievaluasi SEKALI.")
    print("  Jangan mengubah apa pun setelah melihat hasil ini.")
    print()

    if nama_set != "test":
        print(f"  [X] Evaluasi akhir hanya untuk set test.")
        sys.exit(1)

    # Periksa model tersimpan
    if not (MODEL_PATH / "metadata.json").exists():
        print("  [X] Model belum dilatih. Latih model terlebih dahulu:")
        print("    python -m app.ml latih --set dev")
        sys.exit(1)

    session = _buat_session(nama_set)

    try:
        # Muat data test
        print("[1/4] Memuat data sesi terjadwal dari set test...")
        df_sesi = muat_sesi_terjadwal(session)
        print(f"  Jumlah sesi: {len(df_sesi)}")

        if df_sesi.empty:
            print("  [X] Tidak ada data sesi di set test.")
            print("    Jalankan runner terlebih dahulu:")
            print("    python -m app.classification --set test")
            sys.exit(1)

        print("\n[2/4] Memuat calendar_exceptions...")
        cal_exc = muat_calendar_exceptions(session)

        # Bangun fitur — riwayat dihitung dari data set test pada pekan sebelumnya
        print("\n[3/4] Membangun fitur...")
        df_fitur = bangun_fitur(df_sesi, cal_exc)

        # Filter hanya blok uji
        from datetime import date as date_type
        tanggal = df_fitur["tanggal"].apply(
            lambda d: d if isinstance(d, date_type) else date_type.fromisoformat(str(d))
        )
        mask_uji = (tanggal >= TANGGAL_UJI_MULAI) & (tanggal <= TANGGAL_UJI_SELESAI)
        df_uji = df_fitur.loc[mask_uji].copy()

        print(f"  Blok uji: {len(df_uji)} sesi")
        if "label" in df_uji.columns:
            distribusi = df_uji["label"].value_counts().to_dict()
            positif = distribusi.get(1, 0)
            print(f"  Positif={positif}, Negatif={distribusi.get(0, 0)}")
            if positif < 20:
                print(f"  [!] Kurang dari 20 sampel positif di blok uji!")

        if df_uji.empty:
            print("  [X] Blok uji kosong.")
            sys.exit(1)

        # Muat model
        fitur = kolom_fitur()
        fitur_ada = [f for f in fitur if f in df_uji.columns]
        X_uji = df_uji[fitur_ada]
        y_uji = df_uji["label"].values

        print("\n[4/4] Evaluasi akhir...")

        # Baseline dari set latih (perlu muat set dev)
        session_dev = _buat_session("dev")
        try:
            df_sesi_dev = muat_sesi_terjadwal(session_dev)
            cal_exc_dev = muat_calendar_exceptions(session_dev)
            df_fitur_dev = bangun_fitur(df_sesi_dev, cal_exc_dev)
            tanggal_dev = df_fitur_dev["tanggal"].apply(
                lambda d: d if isinstance(d, date_type) else date_type.fromisoformat(str(d))
            )
            mask_latih = (tanggal_dev >= TANGGAL_LATIH_MULAI) & (tanggal_dev <= TANGGAL_LATIH_SELESAI)
            df_latih = df_fitur_dev.loc[mask_latih].copy()
        finally:
            session_dev.close()

        # Baseline
        print("\n-- Baseline --")
        m_maj = baseline_mayoritas(y_uji)
        cetak_metrik("Baseline: Mayoritas", m_maj)

        rata_ruang = hitung_rata_per_ruang(df_latih)
        m_ruang = baseline_rata_historis_ruang(
            y_uji, df_uji["room_id"].values, rata_ruang
        )
        cetak_metrik("Baseline: Rata-rata historis per ruang", m_ruang)

        rata_jenis = hitung_rata_per_jenis_hari(df_latih)
        m_jenis = baseline_rata_historis_jenis_hari(
            y_uji, df_uji["jenis_hari"].values, rata_jenis
        )
        cetak_metrik("Baseline: Rata-rata historis per jenis hari", m_jenis)

        # Model
        print("\n-- Model --")
        import json
        with open(MODEL_PATH / "metadata.json", encoding="utf-8") as f:
            metadata = json.load(f)

        for nama_model, key in [("Decision Tree", "tree"), ("Logistic Regression", "logreg")]:
            pipe, _ = muat_model(MODEL_PATH, key)
            ambang = metadata[key]["ambang"]

            y_proba = pipe.predict_proba(X_uji)[:, 1]
            y_pred_opt = (y_proba >= ambang).astype(int)
            m_opt = hitung_metrik(y_uji, y_pred_opt, y_proba)
            ci = bootstrap_ci(y_uji, y_pred_opt, y_proba)
            cetak_metrik(f"{nama_model} (ambang={ambang})", m_opt, ci)

            # Juga ambang 0.5
            y_pred_05 = (y_proba >= 0.5).astype(int)
            m_05 = hitung_metrik(y_uji, y_pred_05, y_proba)
            cetak_metrik(f"{nama_model} (ambang=0.5)", m_05)

        # Irisan
        print("\n-- Irisan Blok Uji --")
        pipe_lr, _ = muat_model(MODEL_PATH, "logreg")
        ambang_lr = metadata["logreg"]["ambang"]
        y_proba_lr = pipe_lr.predict_proba(X_uji)[:, 1]
        y_pred_lr = (y_proba_lr >= ambang_lr).astype(int)
        cetak_irisan_uji(df_uji, y_uji, y_pred_lr, y_proba_lr, cal_exc)

        # Analisis kesalahan
        print("\n-- Analisis Kesalahan (Logistic Regression, blok uji) --")
        err = analisis_kesalahan(df_uji, y_uji, y_pred_lr)
        for key_err, df_err in err.items():
            print(f"\n  {key_err}:")
            print(df_err.to_string(index=False))

        print("\n====================================================")
        print("  Evaluasi akhir selesai. JANGAN mengubah model atau")
        print("  hiperparameter setelah melihat hasil ini.")
        print("====================================================")

    finally:
        session.close()


def main(argv: list[str] | None = None) -> None:
    """Entry point CLI."""
    parser = argparse.ArgumentParser(
        prog="python -m app.ml",
        description="ML Risiko Sesi Kosong (SS1-14)",
    )
    subparsers = parser.add_subparsers(dest="perintah", required=True)

    # Subcommand: latih
    parser_latih = subparsers.add_parser(
        "latih",
        help="Latih model dan pilih hiperparameter pada set dev.",
    )
    parser_latih.add_argument(
        "--set",
        required=True,
        choices=["dev"],
        help="Nama set data (hanya 'dev' untuk pelatihan).",
    )
    parser_latih.set_defaults(func=cmd_latih)

    # Subcommand: evaluasi-akhir
    parser_eval = subparsers.add_parser(
        "evaluasi-akhir",
        help="Evaluasi akhir pada set test (SEKALI SAJA).",
    )
    parser_eval.add_argument(
        "--set",
        required=True,
        choices=["test"],
        help="Nama set data (hanya 'test' untuk evaluasi akhir).",
    )
    parser_eval.set_defaults(func=cmd_evaluasi_akhir)

    args = parser.parse_args(argv)
    args.func(args)
