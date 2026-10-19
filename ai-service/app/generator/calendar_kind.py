"""Penentuan jenis hari dari kalender akademik (SS1-08).

Prioritas: libur > ujian > kegiatan_khusus > biasa.
"""

from datetime import date
from typing import Any, Iterable

PRIORITY_MAP: dict[str, int] = {
    "libur": 3,
    "ujian": 2,
    "kegiatan_khusus": 1,
}


def parse_date(d: Any) -> date:
    """Mengubah nilai tanggal ke objek datetime.date jika berupa string."""
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        return date.fromisoformat(d)
    raise TypeError(f"Tidak dapat mengubah {type(d)} ke datetime.date")


def resolve_day_kind(tanggal: date | str, exceptions: Iterable[Any]) -> str:
    """Menentukan jenis hari berdasarkan daftar pengecualian kalender.

    Aturan prioritas:
    1. libur (tertinggi)
    2. ujian
    3. kegiatan_khusus
    4. biasa (default jika tidak ada pengecualian atau tipe di luar prioritas seperti 'info')
    """
    target_date = parse_date(tanggal)
    best_priority = 0
    best_kind = "biasa"

    for exc in exceptions:
        start_date = parse_date(exc.tanggal_mulai)
        end_date = parse_date(exc.tanggal_selesai)

        if start_date <= target_date <= end_date:
            tip = getattr(exc, "tipe", None)
            if tip in PRIORITY_MAP:
                priority = PRIORITY_MAP[tip]
                if priority > best_priority:
                    best_priority = priority
                    best_kind = tip

    return best_kind
