"""Simulasi okupansi harian per ruangan (SS1-08).

Fungsi murni simulate_room_day tanpa akses database.
Menghasilkan DayResult yang memuat observed_slots (setelah noise) dan
ground_truth_rows (dihitung dari okupansi sebenarnya sebelum noise).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any, Iterable, Sequence

from app.generator.ground_truth import (
    GroundTruthRow,
    create_outside_episode_ground_truth,
    evaluate_session_ground_truth,
)
from app.calendar_utils import matches_day_of_week
from app.generator.params import (
    SCENARIO_NAMES,
    SCENARIO_PENYEBAB,
    GeneratorParams,
)


@dataclass(frozen=True)
class ObservedSlot:
    """Representasi satu baris pada tabel occupancy_logs."""

    room_id: int
    slot_mulai: datetime
    is_occupied: bool
    source: str = "dummy"


@dataclass(frozen=True)
class DayResult:
    """Hasil simulasi satu ruang pada satu hari."""

    room_id: int
    tanggal: date
    day_kind: str
    observed_slots: list[ObservedSlot]
    ground_truth_rows: list[GroundTruthRow]
    actual_slots: list[ObservedSlot] = field(default_factory=list)


def add_minutes_to_time(t: time, minutes: int) -> time:
    """Menambahkan menit ke objek datetime.time."""
    dt = datetime.combine(date(2000, 1, 1), t) + timedelta(minutes=minutes)
    return dt.time()


def build_operational_slots(
    start_hour: int = 7,
    end_hour: int = 23,
    step_minutes: int = 10,
    break_hour: int = 17,
    break_minute: int = 0,
) -> list[time]:
    """Membangun daftar slot operasional 10 menit (07.00 - 22.50), mengecualikan slot 17.00."""
    slots: list[time] = []
    current_dt = datetime(2000, 1, 1, start_hour, 0)
    end_dt = datetime(2000, 1, 1, end_hour, 0)
    step = timedelta(minutes=step_minutes)

    while current_dt < end_dt:
        t = current_dt.time()
        if not (t.hour == break_hour and t.minute == break_minute):
            slots.append(t)
        current_dt += step

    return slots


def simulate_room_day(
    room: Any,
    schedules: Iterable[Any],
    tanggal: date,
    day_kind: str,
    params: GeneratorParams,
    seed: int,
) -> DayResult:
    """Fungsi murni simulasi satu ruang pada satu hari.

    Aturan:
    - RNG deterministik per (seed, room_id, tanggal).
    - Hanya Senin-Jumat. Sabtu/Minggu mengembalikan DayResult kosong.
    - Slot 17.00 selalu ditiadakan (tidak pernah dibuat).
    - Pada hari libur: tidak ada sesi jadwal; hanya episode di luar jadwal.
    - Ground truth dihitung sebelum noise sensor diaplikasikan.
    """
    room_id = int(getattr(room, "id", None) or getattr(room, "room_id"))
    room_name = str(getattr(room, "nama_ruangan", ""))

    # Hanya Senin (0) sampai Jumat (4)
    if tanggal.weekday() >= 5:
        return DayResult(
            room_id=room_id,
            tanggal=tanggal,
            day_kind=day_kind,
            observed_slots=[],
            ground_truth_rows=[],
            actual_slots=[],
        )

    # Inisialisasi RNG deterministik
    rng_key = f"{seed}:{room_id}:{tanggal.isoformat()}"
    rng = random.Random(rng_key)

    operational_slots = build_operational_slots(
        start_hour=params.operational_start_hour,
        end_hour=params.operational_end_hour,
        step_minutes=params.slot_minutes,
        break_hour=params.break_hour,
        break_minute=params.break_minute,
    )

    actual_occupied: dict[time, bool] = {t: False for t in operational_slots}
    ground_truth_rows: list[GroundTruthRow] = []

    # 1. Filter jadwal untuk ruang ini pada hari ini
    active_schedules: list[Any] = []
    if day_kind != "libur":
        for sched in schedules:
            sched_room_id = int(getattr(sched, "room_id"))
            if sched_room_id == room_id and matches_day_of_week(getattr(sched, "hari"), tanggal.weekday()):
                active_schedules.append(sched)

    # Urutkan jadwal berdasarkan jam mulai
    active_schedules.sort(key=lambda s: getattr(s, "jam_mulai"))

    # Kumpulkan slot yang masuk dalam sesi jadwal
    scheduled_slot_set: set[time] = set()

    scenario_weights = params.get_scenario_weights(day_kind)

    for sched in active_schedules:
        sched_id = int(getattr(sched, "id"))
        jam_mulai = getattr(sched, "jam_mulai")
        jam_selesai = getattr(sched, "jam_selesai")

        # Slot dalam jendela jadwal
        session_slots = [
            t for t in operational_slots if jam_mulai <= t < jam_selesai
        ]
        scheduled_slot_set.update(session_slots)

        if not session_slots:
            continue

        n_slots = len(session_slots)
        total_duration = n_slots * params.slot_minutes

        # Pilih skenario
        scenario = rng.choices(SCENARIO_NAMES, weights=scenario_weights, k=1)[0]
        penyebab = SCENARIO_PENYEBAB[scenario]

        if scenario == "tepat_waktu":
            for t in session_slots:
                actual_occupied[t] = True

        elif scenario == "terlambat":
            # Offset 10-40 menit setelah jam mulai
            candidate_offsets = [10, 20, 30, 40]
            valid_offsets = [o for o in candidate_offsets if o < total_duration]
            offset = rng.choice(valid_offsets) if valid_offsets else total_duration
            empty_slots_count = offset // params.slot_minutes
            for idx, t in enumerate(session_slots):
                actual_occupied[t] = (idx >= empty_slots_count)

        elif scenario == "selesai_awal":
            # Berhenti 10-40 menit sebelum jam selesai
            candidate_early = [10, 20, 30, 40]
            valid_early = [e for e in candidate_early if e < total_duration]
            early = rng.choice(valid_early) if valid_early else total_duration
            active_slots_count = max(0, n_slots - (early // params.slot_minutes))
            for idx, t in enumerate(session_slots):
                actual_occupied[t] = (idx < active_slots_count)

        elif scenario == "tidak_hadir":
            for t in session_slots:
                actual_occupied[t] = False

        elif scenario == "dipinjam_kegiatan_lain":
            # Terisi pada porsi 60-100% jendela oleh kegiatan lain
            portion = rng.uniform(0.60, 1.00)
            k_slots = max(1, min(n_slots, round(portion * n_slots)))
            start_idx = rng.randint(0, n_slots - k_slots)
            for idx, t in enumerate(session_slots):
                actual_occupied[t] = (start_idx <= idx < start_idx + k_slots)

        # Hitung menit terpakai untuk evaluasi ground truth
        menit_terpakai = sum(
            params.slot_minutes for t in session_slots if actual_occupied[t]
        )

        gt_session = evaluate_session_ground_truth(
            tanggal=tanggal,
            room_id=room_id,
            schedule_id=sched_id,
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai,
            menit_terpakai=menit_terpakai,
            penyebab=penyebab,
            empty_threshold_minutes=params.empty_min_occupied_minutes,
        )
        ground_truth_rows.append(gt_session)

    # 2. Episode pemakaian di luar jadwal
    # Kumpulkan slot di luar semua jendela jadwal
    outside_slots = [t for t in operational_slots if t not in scheduled_slot_set]

    # Bentuk rangkaian celah (gaps) yang berurutan
    gaps: list[list[time]] = []
    current_gap: list[time] = []
    step = timedelta(minutes=params.slot_minutes)

    for t in outside_slots:
        if not current_gap:
            current_gap.append(t)
        else:
            prev_t = current_gap[-1]
            if add_minutes_to_time(prev_t, params.slot_minutes) == t:
                current_gap.append(t)
            else:
                gaps.append(current_gap)
                current_gap = [t]
    if current_gap:
        gaps.append(current_gap)

    # 2a. Episode panjang (durasi 30-180 menit)
    is_open = params.is_open_space(room_name)
    prob_long = params.prob_outside_openspace if is_open else params.prob_outside_regular
    if day_kind == "libur":
        prob_long *= params.holiday_outside_multiplier

    if rng.random() < prob_long:
        max_gap_duration = max((len(g) * params.slot_minutes for g in gaps), default=0)
        if max_gap_duration >= params.min_outside_duration:
            possible_durations = [
                d
                for d in range(
                    params.min_outside_duration,
                    min(params.max_outside_duration, max_gap_duration) + 1,
                    params.slot_minutes,
                )
            ]
            dur = rng.choice(possible_durations)
            k_slots = dur // params.slot_minutes

            valid_placements: list[tuple[list[time], int]] = []
            for g in gaps:
                if len(g) >= k_slots:
                    for i in range(0, len(g) - k_slots + 1):
                        valid_placements.append((g, i))

            if valid_placements:
                chosen_gap, start_i = rng.choice(valid_placements)
                placed_slots = chosen_gap[start_i : start_i + k_slots]
                for t in placed_slots:
                    actual_occupied[t] = True

                waktu_mulai = placed_slots[0]
                waktu_selesai = add_minutes_to_time(placed_slots[-1], params.slot_minutes)

                gt_episode = create_outside_episode_ground_truth(
                    tanggal=tanggal,
                    room_id=room_id,
                    waktu_mulai=waktu_mulai,
                    waktu_selesai=waktu_selesai,
                )
                ground_truth_rows.append(gt_episode)

    # 2b. Episode pendek (durasi 10-20 menit, TIDAK dimasukkan ke ground truth)
    if rng.random() < params.prob_short_outside:
        short_candidates: list[tuple[list[time], int, int]] = []
        for d in params.short_outside_durations:
            k_slots = d // params.slot_minutes
            for g in gaps:
                if len(g) >= k_slots:
                    for i in range(0, len(g) - k_slots + 1):
                        segment = g[i : i + k_slots]
                        # Pastikan slot kosong dan terpisah agar tidak memperbesar episode panjang
                        if all(not actual_occupied[t] for t in segment):
                            touch_left = (i > 0 and actual_occupied[g[i - 1]])
                            touch_right = (i + k_slots < len(g) and actual_occupied[g[i + k_slots]])
                            if not (touch_left or touch_right):
                                short_candidates.append((g, i, k_slots))

        if short_candidates:
            chosen_gap, start_i, k_slots = rng.choice(short_candidates)
            for t in chosen_gap[start_i : start_i + k_slots]:
                actual_occupied[t] = True

    # 3. Bentuk actual_slots (sebelum noise) dan observed_slots (setelah noise)
    actual_slots: list[ObservedSlot] = []
    observed_slots: list[ObservedSlot] = []

    for t in operational_slots:
        slot_dt = datetime.combine(tanggal, t)
        is_occ = actual_occupied[t]

        actual_slots.append(
            ObservedSlot(
                room_id=room_id,
                slot_mulai=slot_dt,
                is_occupied=is_occ,
                source="dummy",
            )
        )

        # Terapkan noise:
        # a. Slot hilang (missing slot)
        if rng.random() < params.prob_missing_slot:
            continue

        # b. Salah deteksi (flip boolean)
        observed_occ = is_occ
        if rng.random() < params.prob_detection_error:
            observed_occ = not observed_occ

        observed_slots.append(
            ObservedSlot(
                room_id=room_id,
                slot_mulai=slot_dt,
                is_occupied=observed_occ,
                source="dummy",
            )
        )

    # Urutkan ground_truth_rows berdasarkan waktu mulai
    ground_truth_rows.sort(key=lambda r: (r.waktu_mulai, r.schedule_id if r.schedule_id is not None else -1))

    return DayResult(
        room_id=room_id,
        tanggal=tanggal,
        day_kind=day_kind,
        observed_slots=observed_slots,
        ground_truth_rows=ground_truth_rows,
        actual_slots=actual_slots,
    )
