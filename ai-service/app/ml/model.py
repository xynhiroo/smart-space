"""Pelatihan dan penyimpanan model ML risiko sesi kosong (SS1-14).

Model: Decision Tree dan Logistic Regression dengan scikit-learn Pipeline.
Hiperparameter dipilih di blok validasi (memaksimalkan F1).
Ambang keputusan dipilih di blok validasi, lalu dipakai tanpa diubah
pada blok uji.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from app.ml.fitur import KOLOM_KATEGORIK, KOLOM_NUMERIK, kolom_fitur
from app.ml.konstanta import (
    C_VALUES,
    KEDALAMAN_POHON_RANGE,
    MODEL_DIR_NAME,
    RANDOM_STATE,
)


def _buat_preprocessor(df_latih: pd.DataFrame) -> ColumnTransformer:
    """Buat preprocessor kolom: imputer + scaler untuk numerik, one-hot untuk kategorik."""
    kategorik_ada = [c for c in KOLOM_KATEGORIK if c in df_latih.columns]
    numerik_ada = [c for c in KOLOM_NUMERIK if c in df_latih.columns]

    transformers = []

    if numerik_ada:
        transformers.append((
            "num",
            Pipeline([
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler()),
            ]),
            numerik_ada,
        ))

    if kategorik_ada:
        transformers.append((
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]),
            kategorik_ada,
        ))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def _pilih_ambang_optimal(
    y_true: np.ndarray, y_proba: np.ndarray
) -> float:
    """Pilih ambang keputusan yang memaksimalkan F1 pada data validasi."""
    ambang_candidates = np.arange(0.05, 0.96, 0.01)
    best_f1 = -1.0
    best_threshold = 0.5

    for threshold in ambang_candidates:
        y_pred = (y_proba >= threshold).astype(int)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)

    return round(best_threshold, 2)


def latih_dan_pilih(
    X_latih: pd.DataFrame,
    y_latih: np.ndarray,
    X_val: pd.DataFrame,
    y_val: np.ndarray,
) -> dict[str, Any]:
    """Latih Decision Tree dan Logistic Regression, pilih hiperparameter terbaik.

    Returns:
        Dict berisi:
        - 'tree': dict dengan 'pipeline', 'best_depth', 'ambang', 'tabel_overfitting'
        - 'logreg': dict dengan 'pipeline', 'best_C', 'ambang', 'tabel_overfitting'
        - 'preprocessor_fitur': daftar fitur
    """
    fitur = kolom_fitur()
    fitur_ada = [f for f in fitur if f in X_latih.columns]

    X_tr = X_latih[fitur_ada].copy()
    X_v = X_val[fitur_ada].copy()

    # ===== Decision Tree =====
    print("\n=== Pemilihan hiperparameter Decision Tree ===")
    tabel_dt: list[dict] = []
    best_tree_f1 = -1.0
    best_tree_depth = 1
    best_tree_pipeline = None

    for depth in KEDALAMAN_POHON_RANGE:
        preprocessor = _buat_preprocessor(X_tr)
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", DecisionTreeClassifier(
                max_depth=depth,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )),
        ])
        pipe.fit(X_tr, y_latih)

        y_pred_train = pipe.predict(X_tr)
        y_pred_val = pipe.predict(X_v)

        f1_train = f1_score(y_latih, y_pred_train, zero_division=0)
        f1_val = f1_score(y_val, y_pred_val, zero_division=0)

        tabel_dt.append({
            "depth": depth,
            "f1_latih": round(f1_train, 4),
            "f1_validasi": round(f1_val, 4),
            "gap": round(f1_train - f1_val, 4),
        })
        print(
            f"  depth={depth:2d}  F1_latih={f1_train:.4f}  "
            f"F1_val={f1_val:.4f}  gap={f1_train - f1_val:.4f}"
        )

        if f1_val > best_tree_f1:
            best_tree_f1 = f1_val
            best_tree_depth = depth
            best_tree_pipeline = pipe

    print(f"  → Terbaik: depth={best_tree_depth}, F1_val={best_tree_f1:.4f}")

    # Ambang optimal Decision Tree
    y_proba_tree_val = best_tree_pipeline.predict_proba(X_v)[:, 1]
    ambang_tree = _pilih_ambang_optimal(y_val, y_proba_tree_val)
    print(f"  → Ambang optimal: {ambang_tree}")

    # ===== Logistic Regression =====
    print("\n=== Pemilihan hiperparameter Logistic Regression ===")
    tabel_lr: list[dict] = []
    best_lr_f1 = -1.0
    best_lr_C = 1.0
    best_lr_pipeline = None

    for C in C_VALUES:
        preprocessor = _buat_preprocessor(X_tr)
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(
                C=C,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                max_iter=1000,
                solver="lbfgs",
            )),
        ])
        pipe.fit(X_tr, y_latih)

        y_pred_train = pipe.predict(X_tr)
        y_pred_val = pipe.predict(X_v)

        f1_train = f1_score(y_latih, y_pred_train, zero_division=0)
        f1_val = f1_score(y_val, y_pred_val, zero_division=0)

        tabel_lr.append({
            "C": C,
            "f1_latih": round(f1_train, 4),
            "f1_validasi": round(f1_val, 4),
            "gap": round(f1_train - f1_val, 4),
        })
        print(
            f"  C={C:8.3f}  F1_latih={f1_train:.4f}  "
            f"F1_val={f1_val:.4f}  gap={f1_train - f1_val:.4f}"
        )

        if f1_val > best_lr_f1:
            best_lr_f1 = f1_val
            best_lr_C = C
            best_lr_pipeline = pipe

    print(f"  → Terbaik: C={best_lr_C}, F1_val={best_lr_f1:.4f}")

    # Ambang optimal Logistic Regression
    y_proba_lr_val = best_lr_pipeline.predict_proba(X_v)[:, 1]
    ambang_lr = _pilih_ambang_optimal(y_val, y_proba_lr_val)
    print(f"  → Ambang optimal: {ambang_lr}")

    return {
        "tree": {
            "pipeline": best_tree_pipeline,
            "best_depth": best_tree_depth,
            "ambang": ambang_tree,
            "tabel_overfitting": tabel_dt,
        },
        "logreg": {
            "pipeline": best_lr_pipeline,
            "best_C": best_lr_C,
            "ambang": ambang_lr,
            "tabel_overfitting": tabel_lr,
        },
        "fitur": fitur_ada,
    }


def simpan_model(
    hasil: dict[str, Any],
    model_dir: Path,
) -> Path:
    """Simpan model, metadata, dan ambang ke direktori model.

    Returns:
        Path direktori model yang dibuat.
    """
    model_dir.mkdir(parents=True, exist_ok=True)

    # Simpan pipeline
    joblib.dump(
        hasil["tree"]["pipeline"],
        model_dir / "tree_pipeline.joblib",
    )
    joblib.dump(
        hasil["logreg"]["pipeline"],
        model_dir / "logreg_pipeline.joblib",
    )

    # Metadata
    metadata = {
        "created_at": datetime.now().isoformat(),
        "sklearn_version": sklearn.__version__,
        "random_state": RANDOM_STATE,
        "fitur": hasil["fitur"],
        "tree": {
            "best_depth": hasil["tree"]["best_depth"],
            "ambang": hasil["tree"]["ambang"],
        },
        "logreg": {
            "best_C": hasil["logreg"]["best_C"],
            "ambang": hasil["logreg"]["ambang"],
        },
        "tanggal_potong": {
            "latih_mulai": str(hasil.get("tanggal_potong", {}).get("latih_mulai", "")),
            "latih_selesai": str(hasil.get("tanggal_potong", {}).get("latih_selesai", "")),
            "validasi_mulai": str(hasil.get("tanggal_potong", {}).get("validasi_mulai", "")),
            "validasi_selesai": str(hasil.get("tanggal_potong", {}).get("validasi_selesai", "")),
        },
    }
    with open(model_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Model disimpan di: {model_dir}")
    return model_dir


def muat_model(
    model_dir: Path,
    nama_model: str = "logreg",
) -> tuple[Pipeline, dict[str, Any]]:
    """Muat model dan metadata dari direktori.

    Args:
        model_dir: Path ke direktori model.
        nama_model: 'tree' atau 'logreg'.

    Returns:
        (pipeline, metadata)

    Raises:
        FileNotFoundError: Jika model belum dilatih.
    """
    if nama_model == "tree":
        pipeline_path = model_dir / "tree_pipeline.joblib"
    else:
        pipeline_path = model_dir / "logreg_pipeline.joblib"

    metadata_path = model_dir / "metadata.json"

    if not pipeline_path.exists():
        raise FileNotFoundError(
            f"Model '{nama_model}' belum ditemukan di {model_dir}. "
            f"Latih model terlebih dahulu dengan: python -m app.ml latih --set dev"
        )

    pipeline = joblib.load(pipeline_path)

    metadata: dict[str, Any] = {}
    if metadata_path.exists():
        with open(metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)

    return pipeline, metadata
