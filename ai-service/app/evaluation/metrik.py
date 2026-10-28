"""Metrik klasifikasi: confusion matrix, precision, recall, F1, dan accuracy (SS1-12).

Fungsi murni tanpa database. Label benar dan label prediksi dikirim sebagai daftar
sama panjang, sehingga fungsi ini dapat dites dengan data buatan tangan.

Aturan nilai yang tidak terdefinisi:
- precision kosong (None) bila tidak ada prediksi untuk kelas itu.
- recall kosong (None) bila kelas itu tidak punya contoh benar (support 0).
- f1 kosong (None) bila support 0. Bila support > 0 tetapi tidak ada prediksi
  yang tepat, f1 bernilai 0.0.
- macro_f1 adalah rata-rata f1 pada kelas yang punya support > 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

STATUS = ("sesuai_jadwal", "kosong_meski_terjadwal", "dipakai_di_luar_jadwal")


@dataclass(frozen=True)
class MetrikKelas:
    """Metrik satu kelas."""

    precision: float | None
    recall: float | None
    f1: float | None
    support: int


@dataclass(frozen=True)
class HasilEvaluasi:
    """Hasil evaluasi. Kunci matriks adalah (label_benar, label_prediksi)."""

    jumlah: int
    accuracy: float
    macro_f1: float | None
    matriks: dict[tuple[str, str], int]
    per_kelas: dict[str, MetrikKelas]


def _bagi(pembilang: int, penyebut: int) -> float | None:
    return pembilang / penyebut if penyebut else None


def hitung_evaluasi(
    benar: Sequence[str],
    prediksi: Sequence[str],
    kelas: Iterable[str] = STATUS,
) -> HasilEvaluasi:
    """Menghitung confusion matrix dan metrik per kelas.

    Raises:
        ValueError: panjang berbeda, data kosong, atau ada label di luar daftar kelas.
    """
    if len(benar) != len(prediksi):
        raise ValueError("Jumlah label benar dan label prediksi harus sama.")
    if not benar:
        raise ValueError("Data evaluasi tidak boleh kosong.")

    daftar_kelas = tuple(kelas)
    tak_dikenal = (set(benar) | set(prediksi)) - set(daftar_kelas)
    if tak_dikenal:
        raise ValueError(f"Label tidak dikenal: {sorted(tak_dikenal)}")

    matriks = {(b, p): 0 for b in daftar_kelas for p in daftar_kelas}
    for label_benar, label_prediksi in zip(benar, prediksi):
        matriks[(label_benar, label_prediksi)] += 1

    per_kelas: dict[str, MetrikKelas] = {}
    for k in daftar_kelas:
        tp = matriks[(k, k)]
        fp = sum(matriks[(b, k)] for b in daftar_kelas if b != k)
        fn = sum(matriks[(k, p)] for p in daftar_kelas if p != k)
        support = tp + fn

        precision = _bagi(tp, tp + fp)
        recall = _bagi(tp, support)
        if support == 0:
            f1 = None
        elif precision is None or precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)
        per_kelas[k] = MetrikKelas(precision, recall, f1, support)

    accuracy = sum(matriks[(k, k)] for k in daftar_kelas) / len(benar)
    f1_tersedia = [m.f1 for m in per_kelas.values() if m.f1 is not None]
    macro_f1 = sum(f1_tersedia) / len(f1_tersedia) if f1_tersedia else None

    return HasilEvaluasi(
        jumlah=len(benar),
        accuracy=accuracy,
        macro_f1=macro_f1,
        matriks=matriks,
        per_kelas=per_kelas,
    )
