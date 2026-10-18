"""Parameter generator data dummy okupansi dan ground truth (SS1-08)."""

from dataclasses import dataclass
from typing import Mapping, Sequence

DEV_SEED: int = 1001
TEST_SEED: int = 2002

DEFAULT_START_DATE: str = "2026-09-07"

SCENARIO_NAMES: tuple[str, ...] = (
    "tepat_waktu",
    "terlambat",
    "selesai_awal",
    "tidak_hadir",
    "dipinjam_kegiatan_lain",
)

SCENARIO_PENYEBAB: Mapping[str, str] = {
    "tepat_waktu": "kelas_berlangsung",
    "terlambat": "terlambat",
    "selesai_awal": "selesai_awal",
    "tidak_hadir": "tidak_hadir",
    "dipinjam_kegiatan_lain": "dipinjam_kegiatan_lain",
}

STATUS_SESUAI_JADWAL = "sesuai_jadwal"
STATUS_KOSONG_TERJADWAL = "kosong_meski_terjadwal"
STATUS_LUAR_JADWAL = "dipakai_di_luar_jadwal"

PENYEBAB_LUAR_JADWAL = "pemakaian_luar_jadwal"


@dataclass(frozen=True)
class GeneratorParams:
    """Dataclass frozen yang memuat semua parameter dan asumsi generator dummy."""

    # Peluang skenario per jenis hari (urutan: tepat_waktu, terlambat, selesai_awal, tidak_hadir, dipinjam_kegiatan_lain)
    weights_biasa: tuple[float, ...] = (0.78, 0.08, 0.06, 0.06, 0.02)
    weights_ujian: tuple[float, ...] = (0.58, 0.05, 0.15, 0.20, 0.02)
    weights_kegiatan_khusus: tuple[float, ...] = (0.40, 0.04, 0.04, 0.50, 0.02)

    # Pemakaian di luar jadwal (episode panjang >= 30 menit)
    prob_outside_regular: float = 0.03
    prob_outside_openspace: float = 0.10
    holiday_outside_multiplier: float = 0.3
    min_outside_duration: int = 30
    max_outside_duration: int = 180

    # Episode pendek (10-20 menit, tidak masuk ground truth)
    prob_short_outside: float = 0.05
    short_outside_durations: tuple[int, ...] = (10, 20)

    # Noise sensor simulasi
    prob_detection_error: float = 0.01  # 1% per slot (flip boolean)
    prob_missing_slot: float = 0.02     # 2% per slot (baris ditiadakan)

    # Ambang batas evaluasi ground truth
    empty_min_occupied_minutes: int = 10
    outside_schedule_min_minutes: int = 30

    # Jam operasional & grid
    operational_start_hour: int = 7
    operational_end_hour: int = 23
    slot_minutes: int = 10
    break_hour: int = 17
    break_minute: int = 0

    # Ruang open-space
    open_space_room_names: tuple[str, ...] = ("GU 701", "GU 705", "GU 707")

    def is_open_space(self, room_name: str) -> bool:
        """Memeriksa apakah ruangan tergolong open-space berdasarkan namanya."""
        return room_name in self.open_space_room_names

    def get_scenario_weights(self, day_kind: str) -> tuple[float, ...] | None:
        """Mengembalikan bobot skenario untuk jenis hari yang diberikan.
        
        Untuk 'libur', mengembalikan None karena tidak ada sesi terjadwal.
        """
        if day_kind == "biasa":
            return self.weights_biasa
        elif day_kind == "ujian":
            return self.weights_ujian
        elif day_kind == "kegiatan_khusus":
            return self.weights_kegiatan_khusus
        elif day_kind == "libur":
            return None
        return self.weights_biasa
