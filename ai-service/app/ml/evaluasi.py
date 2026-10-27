"""Evaluasi model ML risiko sesi kosong (SS1-14).

Metrik: confusion matrix, accuracy, precision, recall, F1, ROC-AUC, PR-AUC.
Bootstrap 95% CI untuk F1 dan ROC-AUC pada blok uji.
Baseline: mayoritas, rata-rata historis per ruang, rata-rata per jenis hari.
Analisis kesalahan: per jenis hari dan ruang.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from app.ml.konstanta import BOOTSTRAP_N_RESAMPLE, BOOTSTRAP_SEED


def hitung_metrik(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> dict[str, Any]:
    """Hitung metrik evaluasi lengkap.

    Returns:
        Dict berisi: confusion_matrix, accuracy, precision, recall, f1,
        roc_auc, pr_auc (average_precision).
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    hasil: dict[str, Any] = {
        "confusion_matrix": cm.tolist(),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    if y_proba is not None and len(np.unique(y_true)) > 1:
        hasil["roc_auc"] = float(roc_auc_score(y_true, y_proba))
        hasil["pr_auc"] = float(average_precision_score(y_true, y_proba))
    else:
        hasil["roc_auc"] = None
        hasil["pr_auc"] = None

    return hasil


def bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None,
    n_resamples: int = BOOTSTRAP_N_RESAMPLE,
    seed: int = BOOTSTRAP_SEED,
    alpha: float = 0.05,
) -> dict[str, dict[str, float]]:
    """Interval kepercayaan bootstrap 95% untuk F1 dan ROC-AUC.

    Returns:
        Dict: {'f1': {'lower': ..., 'upper': ..., 'mean': ...},
               'roc_auc': {'lower': ..., 'upper': ..., 'mean': ...}}
    """
    rng = np.random.RandomState(seed)
    n = len(y_true)

    f1_scores = []
    roc_scores = []

    for _ in range(n_resamples):
        idx = rng.choice(n, size=n, replace=True)
        yt = y_true[idx]
        yp = y_pred[idx]

        f1_val = f1_score(yt, yp, zero_division=0)
        f1_scores.append(f1_val)

        if y_proba is not None and len(np.unique(yt)) > 1:
            roc_val = roc_auc_score(yt, y_proba[idx])
            roc_scores.append(roc_val)

    result: dict[str, dict[str, float]] = {}

    f1_arr = np.array(f1_scores)
    result["f1"] = {
        "lower": float(np.percentile(f1_arr, 100 * alpha / 2)),
        "upper": float(np.percentile(f1_arr, 100 * (1 - alpha / 2))),
        "mean": float(np.mean(f1_arr)),
    }

    if roc_scores:
        roc_arr = np.array(roc_scores)
        result["roc_auc"] = {
            "lower": float(np.percentile(roc_arr, 100 * alpha / 2)),
            "upper": float(np.percentile(roc_arr, 100 * (1 - alpha / 2))),
            "mean": float(np.mean(roc_arr)),
        }
    else:
        result["roc_auc"] = {"lower": 0.0, "upper": 0.0, "mean": 0.0}

    return result


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def baseline_mayoritas(y_true: np.ndarray) -> dict[str, Any]:
    """Baseline: selalu menebak kelas mayoritas."""
    kelas_mayoritas = int(np.bincount(y_true).argmax())
    y_pred = np.full_like(y_true, kelas_mayoritas)
    y_proba = np.full(len(y_true), 1.0 - kelas_mayoritas, dtype=float)
    return hitung_metrik(y_true, y_pred, y_proba)


def baseline_rata_historis_ruang(
    y_true: np.ndarray,
    room_ids_eval: np.ndarray,
    rata_per_ruang: dict[int, float],
) -> dict[str, Any]:
    """Baseline: rata-rata historis kosong per ruang sebagai skor.

    Args:
        y_true: label sebenarnya.
        room_ids_eval: room_id untuk setiap sampel.
        rata_per_ruang: {room_id: rata-rata kosong pada set latih}.

    Returns:
        Metrik evaluasi. Prediksi biner pada ambang 0.5.
    """
    y_proba = np.array([
        rata_per_ruang.get(rid, 0.0) for rid in room_ids_eval
    ])
    y_pred = (y_proba >= 0.5).astype(int)
    return hitung_metrik(y_true, y_pred, y_proba)


def baseline_rata_historis_jenis_hari(
    y_true: np.ndarray,
    jenis_hari_eval: np.ndarray,
    rata_per_jenis: dict[str, float],
) -> dict[str, Any]:
    """Baseline: rata-rata historis kosong per jenis hari sebagai skor.

    Args:
        y_true: label sebenarnya.
        jenis_hari_eval: jenis_hari untuk setiap sampel.
        rata_per_jenis: {jenis_hari: rata-rata kosong pada set latih}.

    Returns:
        Metrik evaluasi.
    """
    y_proba = np.array([
        rata_per_jenis.get(jh, 0.0) for jh in jenis_hari_eval
    ])
    y_pred = (y_proba >= 0.5).astype(int)
    return hitung_metrik(y_true, y_pred, y_proba)


def hitung_rata_per_ruang(
    df_latih: pd.DataFrame,
) -> dict[int, float]:
    """Hitung rata-rata label kosong per ruang dari set latih."""
    if df_latih.empty:
        return {}
    grouped = df_latih.groupby("room_id")["label"].mean()
    return grouped.to_dict()


def hitung_rata_per_jenis_hari(
    df_latih: pd.DataFrame,
) -> dict[str, float]:
    """Hitung rata-rata label kosong per jenis hari dari set latih."""
    if df_latih.empty:
        return {}
    if "jenis_hari" not in df_latih.columns:
        return {}
    grouped = df_latih.groupby("jenis_hari")["label"].mean()
    return grouped.to_dict()


# ---------------------------------------------------------------------------
# Analisis kesalahan
# ---------------------------------------------------------------------------

def analisis_kesalahan(
    df: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, pd.DataFrame]:
    """Analisis kesalahan menurut jenis hari dan ruang.

    Returns:
        Dict dengan key 'per_jenis_hari' dan 'per_ruang', masing-masing
        DataFrame berisi jumlah FP, FN, total, dan error rate.
    """
    df_err = df.copy()
    df_err["y_true"] = y_true
    df_err["y_pred"] = y_pred
    df_err["fp"] = ((y_pred == 1) & (y_true == 0)).astype(int)
    df_err["fn"] = ((y_pred == 0) & (y_true == 1)).astype(int)
    df_err["error"] = (y_pred != y_true).astype(int)

    result: dict[str, pd.DataFrame] = {}

    if "jenis_hari" in df_err.columns:
        per_jh = df_err.groupby("jenis_hari").agg(
            total=("error", "count"),
            fp=("fp", "sum"),
            fn=("fn", "sum"),
            errors=("error", "sum"),
        ).reset_index()
        per_jh["error_rate"] = per_jh["errors"] / per_jh["total"]
        result["per_jenis_hari"] = per_jh

    if "nama_ruangan" in df_err.columns:
        per_ruang = df_err.groupby("nama_ruangan").agg(
            total=("error", "count"),
            fp=("fp", "sum"),
            fn=("fn", "sum"),
            errors=("error", "sum"),
        ).reset_index()
        per_ruang["error_rate"] = per_ruang["errors"] / per_ruang["total"]
        result["per_ruang"] = per_ruang

    return result


def cetak_metrik(
    nama: str,
    metrik: dict[str, Any],
    ci: dict[str, dict[str, float]] | None = None,
) -> None:
    """Cetak metrik evaluasi dengan format rapi."""
    cm = metrik.get("confusion_matrix", [[0, 0], [0, 0]])
    print(f"\n--- {nama} ---")
    print(f"  Confusion Matrix:")
    print(f"    TN={cm[0][0]:4d}  FP={cm[0][1]:4d}")
    print(f"    FN={cm[1][0]:4d}  TP={cm[1][1]:4d}")
    print(f"  Accuracy:  {metrik['accuracy']:.4f}")
    print(f"  Precision: {metrik['precision']:.4f}")
    print(f"  Recall:    {metrik['recall']:.4f}")
    print(f"  F1:        {metrik['f1']:.4f}")
    roc = metrik.get("roc_auc")
    pr = metrik.get("pr_auc")
    print(f"  ROC-AUC:   {roc:.4f}" if roc is not None else "  ROC-AUC:   N/A")
    print(f"  PR-AUC:    {pr:.4f}" if pr is not None else "  PR-AUC:    N/A")

    if ci:
        f1_ci = ci.get("f1", {})
        roc_ci = ci.get("roc_auc", {})
        print(f"  Bootstrap 95% CI:")
        print(
            f"    F1:      [{f1_ci.get('lower', 0):.4f}, "
            f"{f1_ci.get('upper', 0):.4f}] (mean={f1_ci.get('mean', 0):.4f})"
        )
        print(
            f"    ROC-AUC: [{roc_ci.get('lower', 0):.4f}, "
            f"{roc_ci.get('upper', 0):.4f}] (mean={roc_ci.get('mean', 0):.4f})"
        )


def cetak_irisan_uji(
    df_uji: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None,
    calendar_exceptions: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    """Laporkan metrik pada irisan blok uji: ujian, kegiatan_khusus, pekan libur.

    Returns:
        Dict {nama_irisan: metrik}.
    """
    from datetime import date, timedelta

    from app.ml.fitur import _kumpulkan_tanggal_libur, _resolve_jenis_hari

    tanggal_libur = _kumpulkan_tanggal_libur(calendar_exceptions)

    df_eval = df_uji.copy()
    df_eval["y_true"] = y_true
    df_eval["y_pred"] = y_pred
    if y_proba is not None:
        df_eval["y_proba"] = y_proba

    # Resolve jenis hari
    if "jenis_hari" not in df_eval.columns:
        df_eval["jenis_hari"] = df_eval["tanggal"].apply(
            lambda d: _resolve_jenis_hari(d, calendar_exceptions)
        )

    # Dekat libur
    if "dekat_libur" not in df_eval.columns:
        from app.ml.fitur import hitung_dekat_libur
        df_eval["dekat_libur"] = df_eval["tanggal"].apply(
            lambda d: int(hitung_dekat_libur(d, tanggal_libur))
        )

    result: dict[str, dict[str, Any]] = {}
    irisan_def = {
        "masa_ujian_AAS": df_eval["jenis_hari"] == "ujian",
        "kegiatan_khusus": df_eval["jenis_hari"] == "kegiatan_khusus",
        "pekan_libur": df_eval["dekat_libur"] == 1,
    }

    for nama, mask in irisan_def.items():
        subset = df_eval.loc[mask]
        n = len(subset)
        n_positif = int(subset["y_true"].sum())

        print(f"\n  Irisan '{nama}': {n} sampel, {n_positif} positif")

        if n_positif < 20:
            print(f"    [!] Kurang dari 20 sampel positif, metrik tidak stabil.")

        if n > 0:
            yt = subset["y_true"].values
            yp = subset["y_pred"].values
            ypr = subset["y_proba"].values if "y_proba" in subset.columns else None
            metrik = hitung_metrik(yt, yp, ypr)
            result[nama] = metrik
            cetak_metrik(f"  {nama}", metrik)
        else:
            result[nama] = {}

    return result


def pentingnya_fitur_tree(pipeline, fitur_names: list[str]) -> pd.DataFrame:
    """Ambil feature importance dari Decision Tree."""
    clf = pipeline.named_steps["classifier"]
    preprocessor = pipeline.named_steps["preprocessor"]

    # Dapatkan nama fitur setelah preprocessing
    try:
        feature_names_out = preprocessor.get_feature_names_out()
    except AttributeError:
        feature_names_out = [f"fitur_{i}" for i in range(len(clf.feature_importances_))]

    importances = clf.feature_importances_
    df = pd.DataFrame({
        "fitur": feature_names_out,
        "importance": importances,
    }).sort_values("importance", ascending=False)

    return df


def koefisien_logreg(pipeline, fitur_names: list[str]) -> pd.DataFrame:
    """Ambil koefisien dari Logistic Regression."""
    clf = pipeline.named_steps["classifier"]
    preprocessor = pipeline.named_steps["preprocessor"]

    try:
        feature_names_out = preprocessor.get_feature_names_out()
    except AttributeError:
        feature_names_out = [f"fitur_{i}" for i in range(len(clf.coef_[0]))]

    coef = clf.coef_[0]
    df = pd.DataFrame({
        "fitur": feature_names_out,
        "koefisien": coef,
    }).sort_values("koefisien", ascending=False)

    return df
