"""Runner klasifikasi untuk set data simulasi: python -m app.classification --set dev (SS1-11).

Hanya database di daftar putih generator (smart_space_ai_dev dan smart_space_ai_test)
yang boleh dipilih. Database aplikasi smart_space ditolak.
"""

from __future__ import annotations

import argparse
from datetime import date

from app.classification.pelaksana import jalankan_klasifikasi
from app.generator.repository import create_db_session_factory, resolve_database_url

TANGGAL_AWAL_SEMESTER = date(2026, 9, 7)
TANGGAL_AKHIR_SEMESTER = date(2027, 1, 22)


def _baca_argumen(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m app.classification",
        description="Klasifikasikan sesi dan episode untuk set data simulasi lalu simpan ke classification_results.",
    )
    parser.add_argument("--set", dest="set_data", choices=("dev", "test"), required=True)
    parser.add_argument("--start", type=date.fromisoformat, default=TANGGAL_AWAL_SEMESTER,
                        help="Tanggal awal YYYY-MM-DD (default awal semester).")
    parser.add_argument("--end", type=date.fromisoformat, default=TANGGAL_AKHIR_SEMESTER,
                        help="Tanggal akhir YYYY-MM-DD (default akhir semester).")
    parser.add_argument("--room-id", type=int, default=None, help="Batasi pada satu ruang.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Hitung dan cetak ringkasan, lalu batalkan (tidak ada yang tersimpan).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    argumen = _baca_argumen(argv)

    try:
        url, nama_db = resolve_database_url(target_set=argumen.set_data)
    except ValueError as galat:
        print(f"[GAGAL] {galat}")
        return 2

    engine, fabrik_session = create_db_session_factory(url)
    session = fabrik_session()
    try:
        ringkasan = jalankan_klasifikasi(
            session,
            argumen.start,
            argumen.end,
            room_ids=[argumen.room_id] if argumen.room_id is not None else None,
        )
        if argumen.dry_run:
            session.rollback()
        else:
            session.commit()
    except ValueError as galat:
        session.rollback()
        print(f"[GAGAL] {galat}")
        return 3
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()

    print(f"Database : {nama_db}")
    print(f"Rentang  : {ringkasan.tanggal_mulai} sampai {ringkasan.tanggal_selesai}")
    print(f"Ruang    : {ringkasan.jumlah_ruang}")
    print(f"Baris    : {ringkasan.jumlah_baris}")
    for status, jumlah in sorted(ringkasan.per_status.items()):
        print(f"  {status}: {jumlah}")
    print("[DRY-RUN] Tidak ada yang disimpan." if argumen.dry_run else "[SELESAI] Hasil disimpan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
