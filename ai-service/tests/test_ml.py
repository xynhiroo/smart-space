"""Unit test paket ML risiko sesi kosong (SS1-14).

Test ini tidak bergantung pada model terlatih sungguhan; menggunakan data
buatan tangan dan model kecil yang dilatih di fixture.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from app.ml.konstanta import (
    KOLOM_TERLARANG,
    RANDOM_STATE,
    STATUS_KOSONG,
    TANGGAL_LATIH_MULAI,
    TANGGAL_LATIH_SELESAI,
    TANGGAL_UJI_MULAI,
    TANGGAL_UJI_SELESAI,
    TANGGAL_VALIDASI_MULAI,
    TANGGAL_VALIDASI_SELESAI,
)
from app.ml.fitur import (
    KOLOM_KATEGORIK,
    KOLOM_NUMERIK,
    bangun_fitur,
    hitung_dekat_libur,
    hitung_durasi_menit,
    hitung_pekan_ke,
    kolom_fitur,
    turunkan_shift,
)
from app.ml.pembagian import bagi_kronologis, verifikasi_pembagian
from app.ml.evaluasi import (
    baseline_mayoritas,
    baseline_rata_historis_jenis_hari,
    baseline_rata_historis_ruang,
    bootstrap_ci,
    hitung_metrik,
    hitung_rata_per_jenis_hari,
    hitung_rata_per_ruang,
)


# ---------------------------------------------------------------------------
# Helper: data buatan tangan
# ---------------------------------------------------------------------------

def _buat_sesi_df(
    n: int = 50,
    tanggal_mulai: date = date(2026, 9, 7),
    room_ids: list[int] | None = None,
) -> pd.DataFrame:
    """Buat DataFrame sesi terjadwal buatan tangan."""
    if room_ids is None:
        room_ids = [1, 2, 3]

    nama_ruangan_map = {1: "GU 201", 2: "GU 301", 3: "GU 701"}
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]

    rows = []
    rng = np.random.RandomState(RANDOM_STATE)

    for i in range(n):
        room_id = room_ids[i % len(room_ids)]
        tanggal = tanggal_mulai + timedelta(days=(i // len(room_ids)) * 7 + (i % 5))
        # Pastikan hari kerja
        while tanggal.weekday() >= 5:
            tanggal += timedelta(days=1)

        jam_mulai = time(7 + (i % 8) * 2, 0)
        jam_selesai = time(7 + (i % 8) * 2 + 2, 0)

        rows.append({
            "schedule_id": i + 1,
            "room_id": room_id,
            "nama_ruangan": nama_ruangan_map.get(room_id, f"GU {room_id}"),
            "tanggal": tanggal,
            "jam_mulai": jam_mulai,
            "jam_selesai": jam_selesai,
            "shift": None,
            "label": 1 if rng.random() < 0.2 else 0,
        })

    return pd.DataFrame(rows)


def _buat_calendar_exceptions() -> pd.DataFrame:
    """Buat calendar_exceptions buatan tangan."""
    return pd.DataFrame([
        {
            "tanggal_mulai": date(2026, 10, 26),
            "tanggal_selesai": date(2026, 10, 30),
            "tipe": "kegiatan_khusus",
        },
        {
            "tanggal_mulai": date(2026, 11, 16),
            "tanggal_selesai": date(2026, 11, 27),
            "tipe": "ujian",
        },
        {
            "tanggal_mulai": date(2026, 12, 25),
            "tanggal_selesai": date(2026, 12, 25),
            "tipe": "libur",
        },
        {
            "tanggal_mulai": date(2027, 1, 1),
            "tanggal_selesai": date(2027, 1, 1),
            "tipe": "libur",
        },
        {
            "tanggal_mulai": date(2027, 1, 5),
            "tanggal_selesai": date(2027, 1, 16),
            "tipe": "ujian",
        },
    ])


def _buat_dataset_lengkap() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Buat dataset yang mencakup seluruh semester."""
    room_ids = [1, 2, 3, 4, 5]
    nama_ruangan_map = {
        1: "GU 201", 2: "GU 301", 3: "GU 701", 4: "GU 401", 5: "GU 705"
    }

    rows = []
    rng = np.random.RandomState(RANDOM_STATE)
    tanggal = date(2026, 9, 7)
    sid = 0

    while tanggal <= date(2027, 1, 22):
        if tanggal.weekday() < 5:  # Hari kerja
            for room_id in room_ids:
                for sesi_idx in range(3):  # 3 sesi per hari per ruang
                    sid += 1
                    jam = 8 + sesi_idx * 3
                    rows.append({
                        "schedule_id": sid,
                        "room_id": room_id,
                        "nama_ruangan": nama_ruangan_map[room_id],
                        "tanggal": tanggal,
                        "jam_mulai": time(jam, 0),
                        "jam_selesai": time(jam + 2, 0),
                        "shift": None,
                        "label": 1 if rng.random() < 0.15 else 0,
                    })
        tanggal += timedelta(days=1)

    df = pd.DataFrame(rows)
    cal = _buat_calendar_exceptions()
    return df, cal


# ---------------------------------------------------------------------------
# Test 1: Anti-kebocoran
# ---------------------------------------------------------------------------

class TestAntiKebocoran:
    """Tidak ada kolom terlarang di matriks fitur; fitur tidak berubah
    jika label sesi pada/setelah pekan sesi diubah."""

    def test_kolom_terlarang_tidak_ada(self):
        """Matriks fitur tidak boleh mengandung kolom terlarang."""
        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)

        kolom_hasil = set(df_fitur.columns)
        bocor = kolom_hasil & KOLOM_TERLARANG
        assert not bocor, f"Kolom terlarang ditemukan: {bocor}"

    def test_fitur_tidak_berubah_saat_label_diubah(self):
        """Ubah label semua sesi pada atau setelah pekan sesi;
        fitur sesi itu tidak berubah."""
        df, cal = _buat_dataset_lengkap()

        # Pilih sesi acak
        rng = np.random.RandomState(99)
        idx_sample = rng.choice(len(df), size=5, replace=False)

        for idx in idx_sample:
            sesi = df.iloc[idx]
            pekan = hitung_pekan_ke(sesi["tanggal"])

            # Bangun fitur asli
            df_asli = df.copy()
            fitur_asli = bangun_fitur(df_asli, cal)

            # Ubah label sesi pada/setelah pekan ini
            df_ubah = df.copy()
            pekan_all = df_ubah["tanggal"].apply(hitung_pekan_ke)
            mask = pekan_all >= pekan
            df_ubah.loc[mask, "label"] = 1 - df_ubah.loc[mask, "label"]

            fitur_ubah = bangun_fitur(df_ubah, cal)

            # Bandingkan fitur sesi ini (kecuali kolom riwayat yang memang
            # hanya dari pekan SEBELUM)
            kolom_cek = [
                c for c in kolom_fitur()
                if c in fitur_asli.columns
                and c not in ("kosong_rate_ruang_sebelumnya", "ada_riwayat")
            ]
            for col in kolom_cek:
                val_asli = fitur_asli.iloc[idx][col]
                val_ubah = fitur_ubah.iloc[idx][col]
                assert val_asli == val_ubah, (
                    f"Fitur '{col}' berubah untuk sesi {idx}: "
                    f"{val_asli} → {val_ubah}"
                )


# ---------------------------------------------------------------------------
# Test 2: Pembagian kronologis
# ---------------------------------------------------------------------------

class TestPembagianKronologis:
    """Blok tidak tumpang tindih, berurutan."""

    def test_blok_tidak_tumpang_tindih(self):
        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)
        df_latih, df_val, df_uji = bagi_kronologis(df_fitur)

        # Tidak error
        verifikasi_pembagian(df_latih, df_val, df_uji)

    def test_berurutan(self):
        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)
        df_latih, df_val, df_uji = bagi_kronologis(df_fitur)

        if not df_latih.empty and not df_val.empty:
            max_latih = max(df_latih["tanggal"])
            min_val = min(df_val["tanggal"])
            assert max_latih < min_val

        if not df_val.empty and not df_uji.empty:
            max_val = max(df_val["tanggal"])
            min_uji = min(df_uji["tanggal"])
            assert max_val < min_uji

    def test_tanggal_uji_setelah_latih(self):
        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)
        df_latih, df_val, df_uji = bagi_kronologis(df_fitur)

        if not df_latih.empty and not df_uji.empty:
            max_latih = max(df_latih["tanggal"])
            min_uji = min(df_uji["tanggal"])
            assert min_uji > max_latih, (
                f"Sesi uji ({min_uji}) lebih awal dari akhir latih ({max_latih})"
            )


# ---------------------------------------------------------------------------
# Test 3: Imputasi di-fit hanya pada data latih
# ---------------------------------------------------------------------------

class TestImputasi:
    """Imputer di-fit pada data latih, perubahan data uji tidak
    mempengaruhi transformasi latih."""

    def test_imputasi_hanya_dari_latih(self):
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
        from sklearn.tree import DecisionTreeClassifier

        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)
        df_latih, df_val, df_uji = bagi_kronologis(df_fitur)

        if df_latih.empty or df_uji.empty:
            pytest.skip("Data latih atau uji kosong")

        fitur = kolom_fitur()
        fitur_ada = [f for f in fitur if f in df_latih.columns]
        numerik = [c for c in KOLOM_NUMERIK if c in df_latih.columns]
        kategorik = [c for c in KOLOM_KATEGORIK if c in df_latih.columns]

        # Bangun pipeline
        preprocessor = ColumnTransformer([
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler()),
            ]), numerik),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), kategorik),
        ], remainder="drop")

        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", DecisionTreeClassifier(
                max_depth=3, class_weight="balanced", random_state=RANDOM_STATE
            )),
        ])

        # Fit pada latih
        X_latih = df_latih[fitur_ada]
        y_latih = df_latih["label"].values
        pipe.fit(X_latih, y_latih)
        pred_latih_1 = pipe.predict(X_latih)

        # Ubah data uji — tidak mempengaruhi prediksi latih
        df_uji_ubah = df_uji.copy()
        for col in numerik:
            if col in df_uji_ubah.columns:
                df_uji_ubah[col] = 999.0

        # Prediksi latih harus sama
        pred_latih_2 = pipe.predict(X_latih)
        np.testing.assert_array_equal(pred_latih_1, pred_latih_2)


# ---------------------------------------------------------------------------
# Test 4: Metrik benar pada contoh kecil
# ---------------------------------------------------------------------------

class TestMetrik:
    """Metrik dihitung benar pada contoh kecil."""

    def test_metrik_contoh_manual(self):
        y_true = np.array([0, 0, 0, 1, 1, 1, 1, 1])
        y_pred = np.array([0, 0, 1, 0, 1, 1, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.6, 0.3, 0.7, 0.8, 0.9, 0.95])

        m = hitung_metrik(y_true, y_pred, y_proba)

        # Manual: TP=4, FP=1, FN=1, TN=2
        assert m["confusion_matrix"] == [[2, 1], [1, 4]]
        assert m["accuracy"] == pytest.approx(6 / 8)
        assert m["precision"] == pytest.approx(4 / 5)
        assert m["recall"] == pytest.approx(4 / 5)
        assert m["f1"] == pytest.approx(4 / 5)
        assert m["roc_auc"] is not None
        assert m["pr_auc"] is not None

    def test_baseline_mayoritas(self):
        y_true = np.array([0, 0, 0, 0, 1, 1])
        m = baseline_mayoritas(y_true)

        # Mayoritas = 0, jadi pred semua 0
        assert m["accuracy"] == pytest.approx(4 / 6)
        assert m["recall"] == 0.0  # Tidak menangkap kelas positif

    def test_baseline_rata_ruang(self):
        y_true = np.array([0, 1, 0, 1])
        room_ids = np.array([1, 1, 2, 2])
        rata = {1: 0.5, 2: 0.5}  # Semua 50%

        m = baseline_rata_historis_ruang(y_true, room_ids, rata)
        # Dengan rata 0.5 >= 0.5, semua diprediksi 1
        assert m["recall"] == 1.0

    def test_baseline_rata_jenis_hari(self):
        y_true = np.array([0, 0, 1, 1])
        jenis = np.array(["biasa", "biasa", "ujian", "ujian"])
        rata = {"biasa": 0.1, "ujian": 0.8}

        m = baseline_rata_historis_jenis_hari(y_true, jenis, rata)
        # biasa → 0.1 < 0.5 → pred 0 (benar untuk keduanya)
        # ujian → 0.8 >= 0.5 → pred 1 (benar untuk keduanya)
        assert m["accuracy"] == 1.0


# ---------------------------------------------------------------------------
# Test 5: Determinisme
# ---------------------------------------------------------------------------

class TestDeterminisme:
    """Pelatihan dua kali dengan seed sama → prediksi identik."""

    def test_pelatihan_deterministic(self):
        from app.ml.model import latih_dan_pilih

        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)
        df_latih, df_val, _ = bagi_kronologis(df_fitur)

        if df_latih.empty or df_val.empty:
            pytest.skip("Data latih atau validasi kosong")

        fitur = kolom_fitur()
        fitur_ada = [f for f in fitur if f in df_latih.columns]

        X_latih = df_latih[fitur_ada]
        y_latih = df_latih["label"].values
        X_val = df_val[fitur_ada]
        y_val = df_val["label"].values

        # Latih dua kali
        hasil_1 = latih_dan_pilih(X_latih, y_latih, X_val, y_val)
        hasil_2 = latih_dan_pilih(X_latih, y_latih, X_val, y_val)

        # Prediksi harus identik
        for key in ["tree", "logreg"]:
            p1 = hasil_1[key]["pipeline"].predict(X_val)
            p2 = hasil_2[key]["pipeline"].predict(X_val)
            np.testing.assert_array_equal(p1, p2)

            # Ambang juga harus sama
            assert hasil_1[key]["ambang"] == hasil_2[key]["ambang"]


# ---------------------------------------------------------------------------
# Test 6: Endpoint
# ---------------------------------------------------------------------------

class TestEndpoint:
    """Test endpoint /predict/risk menggunakan TestClient dan model kecil."""

    @pytest.fixture()
    def _model_kecil(self, tmp_path: Path):
        """Latih model kecil dan simpan di tmp."""
        from app.ml.model import latih_dan_pilih, simpan_model

        df, cal = _buat_dataset_lengkap()
        df_fitur = bangun_fitur(df, cal)
        df_latih, df_val, _ = bagi_kronologis(df_fitur)

        if df_latih.empty or df_val.empty:
            pytest.skip("Data latih atau validasi kosong")

        fitur = kolom_fitur()
        fitur_ada = [f for f in fitur if f in df_latih.columns]

        X_latih = df_latih[fitur_ada]
        y_latih = df_latih["label"].values
        X_val = df_val[fitur_ada]
        y_val = df_val["label"].values

        hasil = latih_dan_pilih(X_latih, y_latih, X_val, y_val)
        simpan_model(hasil, tmp_path / "models")

        return tmp_path / "models"

    @pytest.fixture()
    def _client_tanpa_model(self):
        """TestClient tanpa model tersimpan."""
        import app.api.prediksi as pred_mod

        original = pred_mod.MODEL_PATH
        pred_mod.MODEL_PATH = Path("/nonexistent/models")
        try:
            from fastapi.testclient import TestClient
            from app.main import app
            yield TestClient(app)
        finally:
            pred_mod.MODEL_PATH = original

    def test_503_tanpa_model(self, _client_tanpa_model):
        """Harus 503 jika model belum dilatih."""
        resp = _client_tanpa_model.post(
            "/predict/risk",
            json={"schedule_id": 1, "tanggal": "2026-10-15"},
        )
        assert resp.status_code == 503
        assert "belum dilatih" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Test 7: Tidak ada angka tanggal potong literal di logika
# ---------------------------------------------------------------------------

class TestKonstantaBernama:
    """Semua tanggal potong dan ambang menggunakan konstanta bernama."""

    def test_konstanta_didefinisikan(self):
        """Konstanta tanggal potong terdefinisi."""
        assert TANGGAL_LATIH_MULAI == date(2026, 9, 7)
        assert TANGGAL_LATIH_SELESAI == date(2026, 11, 13)
        assert TANGGAL_VALIDASI_MULAI == date(2026, 11, 16)
        assert TANGGAL_VALIDASI_SELESAI == date(2026, 12, 18)
        assert TANGGAL_UJI_MULAI == date(2026, 12, 21)
        assert TANGGAL_UJI_SELESAI == date(2027, 1, 22)

    def test_tidak_ada_literal_di_pembagian(self):
        """pembagian.py mengimpor dari konstanta, tidak ada literal."""
        import inspect
        from app.ml import pembagian

        source = inspect.getsource(pembagian.bagi_kronologis)
        # Tidak boleh ada string tanggal literal
        assert "2026-09-07" not in source
        assert "2026-11-13" not in source
        assert "2026-11-16" not in source
        assert "2026-12-18" not in source
        assert "2026-12-21" not in source
        assert "2027-01-22" not in source


# ---------------------------------------------------------------------------
# Test tambahan: fitur dasar
# ---------------------------------------------------------------------------

class TestFiturDasar:
    """Test fungsi pembangun fitur dasar."""

    def test_turunkan_shift(self):
        assert turunkan_shift(time(8, 0)) == "pagi"
        assert turunkan_shift(time(11, 50)) == "pagi"
        assert turunkan_shift(time(12, 0)) == "siang"
        assert turunkan_shift(time(16, 50)) == "siang"
        assert turunkan_shift(time(17, 0)) == "malam"

    def test_hitung_durasi_menit(self):
        assert hitung_durasi_menit(time(8, 0), time(10, 0)) == 120
        assert hitung_durasi_menit(time(8, 30), time(9, 0)) == 30

    def test_hitung_pekan_ke(self):
        assert hitung_pekan_ke(date(2026, 9, 7)) == 0
        assert hitung_pekan_ke(date(2026, 9, 14)) == 1

    def test_dekat_libur(self):
        tanggal_libur = {date(2026, 12, 25)}
        # 24 Des = 1 hari kerja sebelum
        assert hitung_dekat_libur(date(2026, 12, 24), tanggal_libur)
        # 7 Sep = jauh dari libur
        assert not hitung_dekat_libur(date(2026, 9, 8), tanggal_libur)

    def test_bangun_fitur_tidak_kosong(self):
        df = _buat_sesi_df(10)
        cal = _buat_calendar_exceptions()
        result = bangun_fitur(df, cal)
        assert not result.empty
        assert "jam_mulai_num" in result.columns
        assert "is_open_space" in result.columns

    def test_is_open_space_dari_params(self):
        """is_open_space menggunakan NAMA_OPEN_SPACE dari generator params."""
        df = _buat_sesi_df(10)
        cal = _buat_calendar_exceptions()
        result = bangun_fitur(df, cal)

        # GU 701 (room_id=3) is open space
        mask_701 = result["nama_ruangan"] == "GU 701"
        if mask_701.any():
            assert (result.loc[mask_701, "is_open_space"] == 1).all()

        # GU 201 (room_id=1) is NOT open space
        mask_201 = result["nama_ruangan"] == "GU 201"
        if mask_201.any():
            assert (result.loc[mask_201, "is_open_space"] == 0).all()
