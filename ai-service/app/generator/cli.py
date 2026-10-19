"""Antarmuka baris perintah (CLI) untuk generator data dummy okupansi (SS1-08)."""

from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

from app.generator.calendar_kind import resolve_day_kind
from app.generator.ground_truth import GroundTruthRow, write_ground_truth_csv
from app.generator.params import (
    DEV_SEED,
    SEMESTER_END_DATE,
    SEMESTER_START_DATE,
    TEST_SEED,
    GeneratorParams,
)
from app.generator.repository import (
    create_db_session_factory,
    load_master_data,
    resolve_database_url,
    save_occupancy_logs_idempotent,
)
from app.generator.simulator import DayResult, ObservedSlot, simulate_room_day


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Mengonfigurasi dan mem-parse argumen baris perintah."""
    parser = argparse.ArgumentParser(
        description="Generator data dummy okupansi historis dan ground truth (SS1-08)."
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
        help=f"Tanggal mulai simulasi (YYYY-MM-DD), default: {SEMESTER_START_DATE} (awal semester aktif).",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=str(SEMESTER_END_DATE),
        help=f"Tanggal selesai simulasi (YYYY-MM-DD), default: {SEMESTER_END_DATE} (akhir semester aktif).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed bilangan acak. Default: 1001 untuk dev, 2002 untuk test.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Hanya simulasikan dan tampilkan ringkasan tanpa menulis ke database atau berkas CSV.",
    )
    parser.add_argument(
        "--allow-any-database",
        action="store_true",
        help="Izinkan penulisan ke database di luar daftar dev/test (bypass pengaman aktif).",
    )

    return parser.parse_args(args)


def run_generator(args: argparse.Namespace) -> int:
    """Menjalankan proses pembangkitan data dummy secara lengkap."""
    start_time = time.perf_counter()

    start_date = date.fromisoformat(args.start)
    end_date = date.fromisoformat(args.end)

    if start_date > end_date:
        print(f"Error: Tanggal mulai ({start_date}) tidak boleh melebihi tanggal selesai ({end_date}).", file=sys.stderr)
        return 1

    # Tentukan seed
    if args.seed is not None:
        seed = args.seed
    else:
        seed = DEV_SEED if args.set == "dev" else TEST_SEED

    params = GeneratorParams()

    # Dapatkan URL database dan validasi pengaman nama DB
    try:
        db_url, active_db = resolve_database_url(
            target_set=args.set,
            allow_any_database=args.allow_any_database,
        )
    except ValueError as e:
        print(f"Error Konfigurasi Database: {e}", file=sys.stderr)
        return 1

    print("================================================================================")
    print(" Smart Space Analytics - Generator Data Dummy Okupansi Historis (SS1-08)")
    print("================================================================================")
    print(" Peringatan        : Data adalah simulasi untuk rentang yang sudah/belum berlalu.")
    print(f" Target Set        : {args.set.upper()}")
    print(f" Target Database   : {active_db}")
    print(f" Rentang Tanggal   : {start_date} s.d. {end_date} ({(end_date - start_date).days + 1} hari)")
    print(f" Seed Acak         : {seed}")
    print(f" Mode Dry-Run      : {'YA (tidak menulis DB/CSV)' if args.dry_run else 'TIDAK (menulis DB & CSV)'}")
    print("--------------------------------------------------------------------------------")

    engine, SessionFactory = create_db_session_factory(db_url)
    session = SessionFactory()

    try:
        rooms, schedules, exceptions = load_master_data(session)
        if not rooms:
            print("Error: Tabel 'rooms' kosong. Pastikan migrasi dan seeder sudah dijalankan.", file=sys.stderr)
            return 1
        if not schedules:
            print("Error: Tabel 'schedules' kosong. Pastikan migrasi dan seeder sudah dijalankan.", file=sys.stderr)
            return 1

        print(f" Dimuat Data Master: {len(rooms)} ruangan, {len(schedules)} jadwal, {len(exceptions)} pengecualian kalender.")
        print(" Menjalankan simulasi harian...")

        all_observed_slots: list[ObservedSlot] = []
        all_ground_truth: list[GroundTruthRow] = []

        # Iterasi tanggal
        current_date = start_date
        total_simulated_days = 0

        while current_date <= end_date:
            # Hanya proses Senin-Jumat
            if current_date.weekday() < 5:
                day_kind = resolve_day_kind(current_date, exceptions)
                total_simulated_days += 1

                for room in rooms:
                    day_res = simulate_room_day(
                        room=room,
                        schedules=schedules,
                        tanggal=current_date,
                        day_kind=day_kind,
                        params=params,
                        seed=seed,
                    )
                    all_observed_slots.extend(day_res.observed_slots)
                    all_ground_truth.extend(day_res.ground_truth_rows)

            current_date += timedelta(days=1)

        print(f" Simulasi selesai: {total_simulated_days} hari kerja diproses.")
        print(f" Total slot terobservasi: {len(all_observed_slots):,} baris.")
        print(f" Total baris ground truth : {len(all_ground_truth):,} baris.")
        print("--------------------------------------------------------------------------------")

        # Cetak statistik ringkasan per ruangan
        room_stats: dict[int, dict[str, Any]] = {
            r.id: {
                "name": r.nama_ruangan,
                "is_open": params.is_open_space(r.nama_ruangan),
                "total_slots": 0,
                "occupied_slots": 0,
            }
            for r in rooms
        }

        for slot in all_observed_slots:
            if slot.room_id in room_stats:
                room_stats[slot.room_id]["total_slots"] += 1
                if slot.is_occupied:
                    room_stats[slot.room_id]["occupied_slots"] += 1

        print(" RINGKASAN OKUPANSI PER RUANGAN:")
        print(f" {'ID':<4} | {'Nama Ruangan':<12} | {'Tipe':<10} | {'Total Slot':<10} | {'Slot Terisi':<11} | {'Okupansi (%)':<12}")
        print(" " + "-" * 73)

        total_slots_all = 0
        total_occupied_all = 0

        for r_id, stats in sorted(room_stats.items(), key=lambda x: x[0]):
            tot = stats["total_slots"]
            occ = stats["occupied_slots"]
            pct = (occ * 100.0 / tot) if tot > 0 else 0.0
            r_type = "Open-Space" if stats["is_open"] else "Reguler"
            total_slots_all += tot
            total_occupied_all += occ
            print(f" {r_id:<4} | {stats['name']:<12} | {r_type:<10} | {tot:<10,} | {occ:<11,} | {pct:10.2f}%")

        overall_pct = (total_occupied_all * 100.0 / total_slots_all) if total_slots_all > 0 else 0.0
        print(" " + "-" * 73)
        print(f" {'TOTAL':<30} | {total_slots_all:<10,} | {total_occupied_all:<11,} | {overall_pct:10.2f}%\n")

        # Distribusi ground truth
        status_counter = Counter(r.status_benar for r in all_ground_truth)
        penyebab_counter = Counter(r.penyebab for r in all_ground_truth)
        total_gt = len(all_ground_truth)

        print(" DISTRIBUSI GROUND TRUTH - STATUS BENAR:")
        for status, count in status_counter.most_common():
            pct = (count * 100.0 / total_gt) if total_gt > 0 else 0.0
            print(f"   - {status:<24}: {count:>6,} ({pct:6.2f}%)")

        print("\n DISTRIBUSI GROUND TRUTH - PENYEBAB:")
        for penyebab, count in penyebab_counter.most_common():
            pct = (count * 100.0 / total_gt) if total_gt > 0 else 0.0
            print(f"   - {penyebab:<24}: {count:>6,} ({pct:6.2f}%)")
        print("--------------------------------------------------------------------------------")

        if not args.dry_run:
            # 1. Tulis ke Database secara idempoten
            room_ids = [r.id for r in rooms]
            min_dt = datetime.combine(start_date, datetime.min.time())
            max_dt = datetime.combine(end_date, datetime.max.time())

            print(" Menyimpan data ke database MySQL...")
            inserted = save_occupancy_logs_idempotent(
                session=session,
                observed_slots=all_observed_slots,
                room_ids=room_ids,
                min_dt=min_dt,
                max_dt=max_dt,
                batch_size=5000,
            )
            print(f" Sukses menyimpan {inserted:,} baris ke tabel occupancy_logs ({active_db}).")

            # 2. Tulis berkas Ground Truth CSV
            base_dir = Path(__file__).resolve().parent.parent.parent
            gt_csv_path = base_dir / "data" / "ground_truth" / f"ground_truth_{args.set}.csv"
            print(f" Menulis berkas ground truth ke: {gt_csv_path}")
            write_ground_truth_csv(all_ground_truth, gt_csv_path)
            print(" Berkas ground truth CSV berhasil disimpan.")
        else:
            print(" [DRY-RUN] Penulisan database dan pembuatan CSV dilewati.")

        elapsed = time.perf_counter() - start_time
        print(f" Selesai dalam {elapsed:.2f} detik.")
        print("================================================================================")
        return 0

    finally:
        session.close()
        engine.dispose()
