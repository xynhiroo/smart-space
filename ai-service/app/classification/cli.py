"""Antarmuka baris perintah (CLI) untuk runner klasifikasi status ruangan (SS1-11)."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime, time as dt_time, timedelta
from typing import Sequence

from app.classification.runner import jalankan_klasifikasi
from app.generator.params import SEMESTER_END_DATE, SEMESTER_START_DATE
from app.generator.repository import create_db_session_factory, resolve_database_url


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Mengonfigurasi dan mem-parse argumen baris perintah."""
    parser = argparse.ArgumentParser(
        description="Runner klasifikasi status ruangan berbasis sistem pakar (SS1-11)."
    )
    parser.add_argument(
        "--set",
        choices=["dev", "test"],
        required=True,
        help="Target dataset: 'dev' (database smart_space_ai_dev) atau 'test' (smart_space_ai_test).",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=str(SEMESTER_START_DATE),
        help=f"Tanggal mulai evaluasi (YYYY-MM-DD), default: {SEMESTER_START_DATE} (awal semester aktif).",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=str(SEMESTER_END_DATE),
        help=f"Tanggal selesai evaluasi (YYYY-MM-DD), default: {SEMESTER_END_DATE} (akhir semester aktif).",
    )
    parser.add_argument(
        "--waktu-evaluasi",
        type=str,
        default=None,
        dest="waktu_evaluasi",
        help="Waktu evaluasi (ISO-8601 YYYY-MM-DD[THH:MM:SS]). Default: hari sesudah --end pukul 00.00.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Hanya jalankan evaluasi dan tampilkan ringkasan tanpa menulis ke database.",
    )
    parser.add_argument(
        "--allow-any-database",
        action="store_true",
        help="Izinkan penulisan ke database di luar daftar dev/test (bypass pengaman aktif).",
    )

    return parser.parse_args(args)


def run_classification_cli(args: argparse.Namespace) -> int:
    """Menjalankan proses klasifikasi lengkap melalui CLI."""
    start_time = time.perf_counter()

    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as e:
        print(f"Format tanggal salah: {e}", file=sys.stderr)
        return 1

    if start_date > end_date:
        print(
            f"Error: Tanggal mulai ({start_date}) tidak boleh melebihi tanggal selesai ({end_date}).",
            file=sys.stderr,
        )
        return 1

    if args.waktu_evaluasi:
        try:
            waktu_evaluasi = datetime.fromisoformat(args.waktu_evaluasi)
        except ValueError as e:
            print(f"Format --waktu-evaluasi salah: {e}", file=sys.stderr)
            return 1
    else:
        # Default: hari sesudah --end pukul 00.00 WIB
        waktu_evaluasi = datetime.combine(end_date + timedelta(days=1), dt_time(0, 0, 0))

    try:
        db_url, active_db = resolve_database_url(
            target_set=args.set,
            allow_any_database=args.allow_any_database,
        )
    except ValueError as e:
        print(f"Error Konfigurasi Database: {e}", file=sys.stderr)
        return 1

    print("================================================================================")
    print(" Smart Space Analytics - Runner Klasifikasi Status Ruangan (SS1-11)")
    print("================================================================================")
    print(f" Target Set        : {args.set.upper()}")
    print(f" Target Database   : {active_db}")
    print(f" Rentang Tanggal   : {start_date} s.d. {end_date} ({(end_date - start_date).days + 1} hari)")
    print(f" Waktu Evaluasi    : {waktu_evaluasi.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Mode Dry-Run      : {'YA (tidak menulis database)' if args.dry_run else 'TIDAK (menulis ke database)'}")
    print("================================================================================")

    engine, session_factory = create_db_session_factory(db_url)
    session = session_factory()

    try:
        print(" Memulai proses klasifikasi...")
        ringkasan = jalankan_klasifikasi(
            session=session,
            tanggal_mulai=start_date,
            tanggal_selesai=end_date,
            waktu_evaluasi=waktu_evaluasi,
            simpan=not args.dry_run,
        )

        print("\n--------------------------------------------------------------------------------")
        print(" RINGKASAN HASIL KLASIFIKASI")
        print("--------------------------------------------------------------------------------")
        print(f" Total Ruang Dievaluasi  : {ringkasan.jumlah_ruang}")
        print(f" Total Baris Klasifikasi : {ringkasan.total_baris:,}")
        print(" Distribusi Status:")
        for status, count in sorted(ringkasan.jumlah_baris_per_status.items()):
            pct = (count / ringkasan.total_baris * 100) if ringkasan.total_baris > 0 else 0.0
            print(f"   - {status:<24}: {count:>6,} ({pct:6.2f}%)")
        print("--------------------------------------------------------------------------------")

        if not args.dry_run:
            session.commit()
            print(f" Berhasil menyimpan {ringkasan.total_baris:,} baris ke classification_results ({active_db}).")
        else:
            session.rollback()
            print(" [DRY-RUN] Transaksi dibatalkan (rollback), tidak ada perubahan disimpan ke database.")

        elapsed = time.perf_counter() - start_time
        print(f" Selesai dalam {elapsed:.2f} detik.")
        print("================================================================================")
        return 0

    except Exception as e:
        session.rollback()
        print(f"\nTerjadi kesalahan selama proses klasifikasi: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    finally:
        session.close()
        engine.dispose()


def main() -> None:
    """Fungsi entri utama CLI."""
    args = parse_args()
    sys.exit(run_classification_cli(args))


if __name__ == "__main__":
    main()
