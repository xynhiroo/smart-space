import pytest

from app.classification.pemuat import muat_ambang
from app.expert_system.tipe import Ambang
from app.models import ThresholdSetting


def _isi_threshold(db_session, nilai):
    # Dalam transaksi test: semua perubahan dibatalkan oleh rollback di akhir.
    db_session.query(ThresholdSetting).delete()
    for key, value in nilai.items():
        db_session.add(ThresholdSetting(key=key, value=value))
    db_session.flush()


def test_muat_ambang_dari_threshold_settings(db_session):
    _isi_threshold(
        db_session,
        {
            "empty_min_occupied_minutes": "10",
            "outside_schedule_min_minutes": "30",
            "utilization_low_max": "40",
            "utilization_medium_max": "80",
            "empty_status_evaluation_timing": "after_schedule_finished",
        },
    )

    assert muat_ambang(db_session) == Ambang(
        empty_min_occupied_minutes=10,
        outside_schedule_min_minutes=30,
        batas_rendah=40.0,
        batas_sedang=80.0,
    )


def test_muat_ambang_menolak_kunci_yang_hilang(db_session):
    _isi_threshold(db_session, {"empty_min_occupied_minutes": "10"})

    with pytest.raises(ValueError, match="utilization_low_max"):
        muat_ambang(db_session)
