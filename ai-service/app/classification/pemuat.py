"""Pemuat data dari database untuk klasifikasi (SS1-11)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.classification.ambang import bentuk_ambang
from app.expert_system.tipe import Ambang
from app.models import ThresholdSetting


def muat_ambang(session: Session) -> Ambang:
    """Membaca threshold_settings dan membentuk Ambang.

    Raises:
        ValueError: kunci wajib hilang atau nilainya tidak valid.
    """
    nilai = {baris.key: baris.value for baris in session.query(ThresholdSetting)}
    return bentuk_ambang(nilai)
