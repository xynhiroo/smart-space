"""Utilitas kalender dan penanganan nama hari Bahasa Indonesia."""

from __future__ import annotations

HARI_TO_WEEKDAY: dict[str, int] = {
    "senin": 0,
    "selasa": 1,
    "rabu": 2,
    "kamis": 3,
    "jumat": 4,
}

WEEKDAY_TO_CANONICAL_HARI: dict[int, str] = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
}


def normalize_hari(nama_hari: str | None) -> str | None:
    """Menormalkan nama hari Bahasa Indonesia ke bentuk kanonikal (Senin..Jumat).

    Menangani:
    - Variasi penulisan 'Jum'at' dan 'Jumat'
    - Variasi huruf besar/kecil (mis. 'SENIN', 'jum\'at')
    - Spasi di awal/akhir
    - Mengembalikan None untuk nama hari di luar hari kerja (Sabtu, Minggu) atau nilai tak dikenal.
    """
    if not nama_hari or not isinstance(nama_hari, str):
        return None

    cleaned = nama_hari.replace("'", "").strip().lower()
    weekday = HARI_TO_WEEKDAY.get(cleaned)
    if weekday is None:
        return None
    return WEEKDAY_TO_CANONICAL_HARI[weekday]


def hari_to_weekday(nama_hari: str | None) -> int | None:
    """Mengubah nama hari Bahasa Indonesia ke indeks weekday Python (0=Senin s.d. 4=Jumat).

    Mengembalikan None jika tidak dikenal atau akhir pekan.
    """
    if not nama_hari or not isinstance(nama_hari, str):
        return None
    cleaned = nama_hari.replace("'", "").strip().lower()
    return HARI_TO_WEEKDAY.get(cleaned)


def matches_day_of_week(hari_str: str | None, weekday_int: int) -> bool:
    """Memeriksa apakah string nama hari cocok dengan indeks weekday Python (0=Senin s.d. 4=Jumat).

    Mendukung 'Jum'at' maupun 'Jumat', variasi casing, dan spasi.
    """
    w = hari_to_weekday(hari_str)
    if w is None:
        return False
    return w == weekday_int
