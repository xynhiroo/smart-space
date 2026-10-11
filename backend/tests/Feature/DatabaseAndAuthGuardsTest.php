<?php

namespace Tests\Feature;

use App\Models\AdminAccount;
use App\Models\CalendarException;
use App\Models\MahasiswaAccount;
use App\Models\Room;
use App\Models\Schedule;
use App\Models\ThresholdSetting;
use Illuminate\Support\Facades\Auth;
use Tests\TestCase;

class DatabaseAndAuthGuardsTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        $this->artisan('migrate');
        $this->artisan('db:seed');
    }

    /**
     * Test admin authentication guard.
     */
    public function test_admin_guard_can_authenticate_valid_admin(): void
    {
        $credentials = [
            'email' => 'admin@smartspace.polibatam.ac.id',
            'password' => 'admin12345',
        ];

        $authenticated = Auth::guard('admin')->attempt($credentials);

        $this->assertTrue($authenticated, 'Admin guard failed to authenticate valid credentials.');
        $this->assertNotNull(Auth::guard('admin')->user());
        $this->assertEquals('Admin Fasilitas IF', Auth::guard('admin')->user()->nama);
    }

    /**
     * Test mahasiswa authentication guard.
     */
    public function test_mahasiswa_guard_can_authenticate_valid_mahasiswa(): void
    {
        $credentials = [
            'nim' => '3312501036',
            'password' => 'password123',
        ];

        $authenticated = Auth::guard('mahasiswa')->attempt($credentials);

        $this->assertTrue($authenticated, 'Mahasiswa guard failed to authenticate valid credentials.');
        $this->assertNotNull(Auth::guard('mahasiswa')->user());
        $this->assertEquals('3312501036', Auth::guard('mahasiswa')->user()->nim);
    }

    /**
     * Test rooms table seeded properly.
     */
    public function test_rooms_table_is_seeded_with_expected_rooms(): void
    {
        $this->assertGreaterThanOrEqual(10, Room::count());
        $this->assertNotNull(Room::where('nama_ruangan', 'GU 702')->first());
        $this->assertNotNull(Room::where('nama_ruangan', 'TA 10.3')->first());
    }

    /**
     * Test schedules table is linked properly to rooms.
     */
    public function test_schedules_table_is_linked_to_rooms(): void
    {
        $this->assertGreaterThanOrEqual(100, Schedule::count());
        $firstSchedule = Schedule::with('room')->first();

        $this->assertNotNull($firstSchedule);
        $this->assertNotNull($firstSchedule->room);
        $this->assertNotEmpty($firstSchedule->room->nama_ruangan);
    }

    /**
     * Test calendar exceptions table is seeded properly.
     */
    public function test_calendar_exceptions_is_seeded(): void
    {
        $this->assertGreaterThanOrEqual(8, CalendarException::count());
    }

    /**
     * Test threshold settings seeded with required final default values.
     */
    public function test_threshold_settings_contain_required_defaults(): void
    {
        $lowMin = ThresholdSetting::where('key', 'utilization_low_min')->first();
        $lowMax = ThresholdSetting::where('key', 'utilization_low_max')->first();
        $medMin = ThresholdSetting::where('key', 'utilization_medium_min')->first();
        $medMax = ThresholdSetting::where('key', 'utilization_medium_max')->first();
        $highMin = ThresholdSetting::where('key', 'utilization_high_min')->first();
        $highMax = ThresholdSetting::where('key', 'utilization_high_max')->first();
        $emptyTiming = ThresholdSetting::where('key', 'empty_status_evaluation_timing')->first();
        $emptyTolerance = ThresholdSetting::where('key', 'empty_status_use_start_tolerance')->first();

        $this->assertNotNull($lowMin);
        $this->assertEquals('0', $lowMin->value);
        $this->assertEquals('40', $lowMax->value);
        $this->assertEquals('41', $medMin->value);
        $this->assertEquals('80', $medMax->value);
        $this->assertEquals('81', $highMin->value);
        $this->assertEquals('100', $highMax->value);
        $this->assertEquals('after_schedule_finished', $emptyTiming->value);
        $this->assertEquals('false', $emptyTolerance->value);
    }
}
