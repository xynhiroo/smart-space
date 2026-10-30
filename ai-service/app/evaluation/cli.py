"""Antarmuka baris perintah evaluasi sistem pakar (SS1-12). Hanya membaca database."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from sqlalchemy import text

from app.evaluation.laporan import format_laporan, muat_penyebab_csv, susun_laporan
from app.evaluation.pencocokan import baris_dari_hasil_klasifikasi, muat_ground_truth_csv
from app.generator.repository import create_db_session_factory, resolve_database_url

FOLDER_GROUND_TRUTH = Path(__file__).resolve().parents[2] / "data" / "ground_truth"


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluasi hasil klasifikasi sistem pakar terhadap ground truth (SS1-12)."
    )
    parser.add_argument(
        "--set",
        choices=["dev", "test"],
        required=True,
        help="Target dataset: 'dev' (smart_space_ai_dev) atau 'test' (smart_space_ai_test).",
    )
    parser.add_argument(
        "--ground-truth",
        type=str,
        default=None,
        dest="ground_truth",
        help="Jalur CSV ground truth. Default: data/ground_truth/ground_truth_<set>.csv.",
    )
    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    opsi = parse_args(args)
    jalur = (
        Path(opsi.ground_truth)
        if opsi.ground_truth
        else FOLDER_GROUND_TRUTH / f"ground_truth_{opsi.set}.csv"
    )
    if not jalur.exists():
        print(f"Berkas ground truth tidak ditemukan: {jalur}", file=sys.stderr)
        return 1

    try:
        db_url, nama_db = resolve_database_url(target_set=opsi.set, allow_any_database=False)
    except ValueError as e:
        print(f"Error Konfigurasi Database: {e}", file=sys.stderr)
        return 1

    engine, session_factory = create_db_session_factory(db_url)
    session = session_factory()
    try:
        baris = session.execute(
            text(
                "SELECT tanggal, room_id, schedule_id, waktu_mulai, waktu_selesai, status "
                "FROM classification_results"
            )
        ).mappings().all()
        hasil = baris_dari_hasil_klasifikasi([dict(r) for r in baris])
        laporan = susun_laporan(
            muat_ground_truth_csv(jalur), hasil, muat_penyebab_csv(jalur)
        )
        print(format_laporan(laporan, opsi.set, nama_db))
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"Terjadi kesalahan selama evaluasi: {e}", file=sys.stderr)
        return 1
    finally:
        session.close()
        engine.dispose()
