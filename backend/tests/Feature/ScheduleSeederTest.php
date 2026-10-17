<?php

namespace Tests\Feature;

use App\Models\Room;
use App\Models\Schedule;
use Database\Seeders\RoomSeeder;
use Database\Seeders\ScheduleSeeder;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ScheduleSeederTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(RoomSeeder::class);
    }

    /**
     * Test running ScheduleSeeder twice preserves total count and per-room count.
     */
    public function test_schedule_seeder_is_idempotent_and_preserves_room_schedule_counts(): void
    {
        $this->seed(ScheduleSeeder::class);

        $this->assertEquals(10, Room::count(), 'Jumlah ruangan harus 10.');
        $this->assertEquals(102, Schedule::count(), 'Jumlah jadwal seeder pertama harus 102.');

        $countsFirstRun = Schedule::query()
            ->selectRaw('room_id, count(*) as total')
            ->groupBy('room_id')
            ->orderBy('room_id')
            ->pluck('total', 'room_id')
            ->toArray();

        // Jalankan ScheduleSeeder kedua kali
        $this->seed(ScheduleSeeder::class);

        $this->assertEquals(10, Room::count(), 'Jumlah ruangan tetap 10 setelah seeder kedua.');
        $this->assertEquals(102, Schedule::count(), 'Jumlah jadwal tetap 102 setelah seeder kedua.');

        $countsSecondRun = Schedule::query()
            ->selectRaw('room_id, count(*) as total')
            ->groupBy('room_id')
            ->orderBy('room_id')
            ->pluck('total', 'room_id')
            ->toArray();

        $this->assertEquals($countsFirstRun, $countsSecondRun, 'Distribusi jadwal per ruang harus sama persis.');
    }

    /**
     * Test manual insert with existing (room_id, hari, jam_mulai) is rejected by database.
     */
    public function test_database_rejects_duplicate_slot_with_same_room_day_and_start_time(): void
    {
        $this->seed(ScheduleSeeder::class);

        $existing = Schedule::firstOrFail();

        $this->expectException(QueryException::class);

        Schedule::create([
            'room_id' => $existing->room_id,
            'hari' => $existing->hari,
            'jam_mulai' => $existing->jam_mulai,
            'jam_selesai' => '23:50:00',
            'mata_kuliah' => 'Mata Kuliah Duplikat Uji',
            'kelas' => 'IF-TEST',
            'dosen' => 'Dosen Penguji',
            'shift' => null,
        ]);
    }

    /**
     * Test all 102 schedules satisfy 10-minute slot multiple and no overlaps.
     */
    public function test_all_102_schedules_are_10_minute_multiples_and_have_no_overlaps(): void
    {
        $this->seed(ScheduleSeeder::class);

        $schedules = Schedule::all();
        $this->assertEquals(102, $schedules->count(), 'Jumlah total jadwal hasil seeder harus 102.');

        $violations10Min = [];
        $schedulesByRoomDay = [];

        foreach ($schedules as $sched) {
            $startParts = explode(':', $sched->jam_mulai);
            $startMin = (int) $startParts[1];
            $startSec = isset($startParts[2]) ? (int) $startParts[2] : 0;

            $endParts = explode(':', $sched->jam_selesai);
            $endMin = (int) $endParts[1];
            $endSec = isset($endParts[2]) ? (int) $endParts[2] : 0;

            if ($startMin % 10 !== 0 || $startSec !== 0) {
                $violations10Min[] = "Jadwal #{$sched->id} ({$sched->mata_kuliah}) jam_mulai={$sched->jam_mulai} bukan kelipatan 10 menit.";
            }

            if ($endMin % 10 !== 0 || $endSec !== 0) {
                $violations10Min[] = "Jadwal #{$sched->id} ({$sched->mata_kuliah}) jam_selesai={$sched->jam_selesai} bukan kelipatan 10 menit.";
            }

            $startMinutes = ((int) $startParts[0]) * 60 + $startMin;
            $endMinutes = ((int) $endParts[0]) * 60 + $endMin;

            $key = $sched->room_id . '-' . $sched->hari;
            $schedulesByRoomDay[$key][] = [
                'id' => $sched->id,
                'mata_kuliah' => $sched->mata_kuliah,
                'start' => $startMinutes,
                'end' => $endMinutes,
                'start_str' => $sched->jam_mulai,
                'end_str' => $sched->jam_selesai,
            ];
        }

        $this->assertEmpty($violations10Min, 'Ditemukan jadwal yang bukan kelipatan 10 menit: ' . implode('; ', $violations10Min));

        $overlapViolations = [];
        foreach ($schedulesByRoomDay as $groupKey => $groupScheds) {
            $count = count($groupScheds);
            for ($i = 0; $i < $count; $i++) {
                for ($j = $i + 1; $j < $count; $j++) {
                    $s1 = $groupScheds[$i];
                    $s2 = $groupScheds[$j];

                    $latestStart = max($s1['start'], $s2['start']);
                    $earliestEnd = min($s1['end'], $s2['end']);

                    if ($latestStart < $earliestEnd) {
                        $overlapViolations[] = "Tumpang tindih antara Jadwal #{$s1['id']} ({$s1['mata_kuliah']} {$s1['start_str']}-{$s1['end_str']}) dan Jadwal #{$s2['id']} ({$s2['mata_kuliah']} {$s2['start_str']}-{$s2['end_str']}) pada grup {$groupKey}.";
                    }
                }
            }
        }

        $this->assertEmpty($overlapViolations, 'Ditemukan jadwal yang saling tumpang tindih: ' . implode('; ', $overlapViolations));
    }
}
