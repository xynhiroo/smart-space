<?php

namespace Tests\Feature;

use App\Models\Room;
use App\Models\Schedule;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Tests\TestCase;

class AiTablesSchemaTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed();
    }

    /**
     * Test that both AI tables exist in the database.
     */
    public function test_ai_tables_exist(): void
    {
        $this->assertTrue(Schema::hasTable('occupancy_logs'), "Tabel 'occupancy_logs' tidak ditemukan.");
        $this->assertTrue(Schema::hasTable('classification_results'), "Tabel 'classification_results' tidak ditemukan.");
    }

    /**
     * Test occupancy_logs columns and their nullability according to DATA_CONTRACT.md.
     */
    public function test_occupancy_logs_columns_and_nullability(): void
    {
        $columns = Schema::getColumns('occupancy_logs');
        $columnMap = collect($columns)->keyBy('name');

        $expectedColumns = [
            'id' => false,
            'room_id' => false,
            'slot_mulai' => false,
            'is_occupied' => false,
            'source' => false,
            'created_at' => true,
            'updated_at' => true,
        ];

        $this->assertCount(count($expectedColumns), $columns, 'Jumlah kolom occupancy_logs tidak sesuai kontrak.');

        foreach ($expectedColumns as $colName => $nullable) {
            $this->assertTrue($columnMap->has($colName), "Kolom '{$colName}' tidak ditemukan pada occupancy_logs.");
            $this->assertEquals(
                $nullable,
                (bool) $columnMap->get($colName)['nullable'],
                "Nullability kolom '{$colName}' pada occupancy_logs tidak sesuai."
            );
        }
    }

    /**
     * Test classification_results columns and nullability according to DATA_CONTRACT.md.
     */
    public function test_classification_results_columns_and_nullability(): void
    {
        $columns = Schema::getColumns('classification_results');
        $columnMap = collect($columns)->keyBy('name');

        $expectedColumns = [
            'id' => false,
            'room_id' => false,
            'schedule_id' => true,
            'tanggal' => false,
            'waktu_mulai' => false,
            'waktu_selesai' => false,
            'status' => false,
            'menit_terjadwal' => false,
            'menit_terpakai' => false,
            'utilisasi_pct' => true,
            'rule_id' => false,
            'penjelasan' => false,
            'computed_at' => false,
        ];

        $this->assertCount(count($expectedColumns), $columns, 'Jumlah kolom classification_results tidak sesuai kontrak.');

        foreach ($expectedColumns as $colName => $nullable) {
            $this->assertTrue($columnMap->has($colName), "Kolom '{$colName}' tidak ditemukan pada classification_results.");
            $this->assertEquals(
                $nullable,
                (bool) $columnMap->get($colName)['nullable'],
                "Nullability kolom '{$colName}' pada classification_results tidak sesuai."
            );
        }
    }

    /**
     * Test unique constraint on occupancy_logs(room_id, slot_mulai).
     */
    public function test_occupancy_logs_rejects_duplicate_room_and_slot(): void
    {
        $room = Room::firstOrFail();

        DB::table('occupancy_logs')->insert([
            'room_id' => $room->id,
            'slot_mulai' => '2026-10-16 08:00:00',
            'is_occupied' => true,
            'source' => 'dummy',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $this->expectException(QueryException::class);

        DB::table('occupancy_logs')->insert([
            'room_id' => $room->id,
            'slot_mulai' => '2026-10-16 08:00:00',
            'is_occupied' => false,
            'source' => 'dummy',
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }

    /**
     * Test unique constraint on classification_results(room_id, tanggal, waktu_mulai).
     */
    public function test_classification_results_rejects_duplicate_room_date_and_start_time(): void
    {
        $room = Room::firstOrFail();

        DB::table('classification_results')->insert([
            'room_id' => $room->id,
            'schedule_id' => null,
            'tanggal' => '2026-10-16',
            'waktu_mulai' => '08:00:00',
            'waktu_selesai' => '09:40:00',
            'status' => 'dipakai_di_luar_jadwal',
            'menit_terjadwal' => 0,
            'menit_terpakai' => 100,
            'utilisasi_pct' => null,
            'rule_id' => 'R03',
            'penjelasan' => 'Ruang dipakai di luar jadwal',
            'computed_at' => '2026-10-16 10:00:00',
        ]);

        $this->expectException(QueryException::class);

        DB::table('classification_results')->insert([
            'room_id' => $room->id,
            'schedule_id' => null,
            'tanggal' => '2026-10-16',
            'waktu_mulai' => '08:00:00',
            'waktu_selesai' => '10:00:00',
            'status' => 'dipakai_di_luar_jadwal',
            'menit_terjadwal' => 0,
            'menit_terpakai' => 120,
            'utilisasi_pct' => null,
            'rule_id' => 'R03',
            'penjelasan' => 'Duplikasi slot',
            'computed_at' => '2026-10-16 10:30:00',
        ]);
    }

    /**
     * Test foreign key constraint rejects non-existent room_id.
     */
    public function test_foreign_key_rejects_nonexistent_room(): void
    {
        $nonExistentRoomId = 999999;

        try {
            DB::table('occupancy_logs')->insert([
                'room_id' => $nonExistentRoomId,
                'slot_mulai' => '2026-10-16 08:00:00',
                'is_occupied' => true,
                'source' => 'dummy',
            ]);
            $this->fail('Seharusnya QueryException dilemparkan ketika room_id tidak ada pada occupancy_logs.');
        } catch (QueryException $e) {
            $this->assertTrue(true);
        }

        try {
            DB::table('classification_results')->insert([
                'room_id' => $nonExistentRoomId,
                'schedule_id' => null,
                'tanggal' => '2026-10-16',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '09:40:00',
                'status' => 'dipakai_di_luar_jadwal',
                'menit_terjadwal' => 0,
                'menit_terpakai' => 100,
                'utilisasi_pct' => null,
                'rule_id' => 'R03',
                'penjelasan' => 'Ruang tidak ada',
                'computed_at' => '2026-10-16 10:00:00',
            ]);
            $this->fail('Seharusnya QueryException dilemparkan ketika room_id tidak ada pada classification_results.');
        } catch (QueryException $e) {
            $this->assertTrue(true);
        }
    }

    /**
     * Test foreign key cascade on delete when a room is deleted.
     */
    public function test_foreign_key_cascade_on_delete(): void
    {
        $testRoom = Room::create([
            'nama_ruangan' => 'TEST_CASCADE_ROOM',
            'kapasitas' => 20,
            'lokasi' => 'Test Floor',
        ]);

        DB::table('occupancy_logs')->insert([
            'room_id' => $testRoom->id,
            'slot_mulai' => '2026-10-16 08:00:00',
            'is_occupied' => true,
            'source' => 'dummy',
        ]);

        DB::table('classification_results')->insert([
            'room_id' => $testRoom->id,
            'schedule_id' => null,
            'tanggal' => '2026-10-16',
            'waktu_mulai' => '08:00:00',
            'waktu_selesai' => '09:40:00',
            'status' => 'dipakai_di_luar_jadwal',
            'menit_terjadwal' => 0,
            'menit_terpakai' => 100,
            'utilisasi_pct' => null,
            'rule_id' => 'R03',
            'penjelasan' => 'Uji cascade',
            'computed_at' => '2026-10-16 10:00:00',
        ]);

        $this->assertEquals(1, DB::table('occupancy_logs')->where('room_id', $testRoom->id)->count());
        $this->assertEquals(1, DB::table('classification_results')->where('room_id', $testRoom->id)->count());

        $testRoom->delete();

        $this->assertEquals(0, DB::table('occupancy_logs')->where('room_id', $testRoom->id)->count());
        $this->assertEquals(0, DB::table('classification_results')->where('room_id', $testRoom->id)->count());
    }

    /**
     * Test that all 102 schedules are 10-minute multiples and have no overlaps.
     */
    public function test_all_102_schedules_are_10_minute_multiples_and_have_no_overlaps(): void
    {
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
