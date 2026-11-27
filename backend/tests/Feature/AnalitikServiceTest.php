<?php

namespace Tests\Feature;

use App\Models\Room;
use App\Models\Schedule;
use App\Models\ThresholdSetting;
use App\Services\AnalitikService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class AnalitikServiceTest extends TestCase
{
    use RefreshDatabase;

    protected AnalitikService $service;

    protected function setUp(): void
    {
        parent::setUp();
        $this->service = new AnalitikService();
    }

    public function test_ambil_ambang_batas_membaca_threshold_settings(): void
    {
        ThresholdSetting::create([
            'key' => 'utilization_low_max',
            'value' => '35',
            'keterangan' => 'Batas bawah',
        ]);
        ThresholdSetting::create([
            'key' => 'utilization_medium_max',
            'value' => '75',
            'keterangan' => 'Batas tengah',
        ]);

        $ambang = $this->service->ambilAmbangBatas();

        $this->assertEquals(35.0, $ambang['batas_rendah']);
        $this->assertEquals(75.0, $ambang['batas_sedang']);
    }

    public function test_tentukan_kategori_sesuai_aturan_inklusif(): void
    {
        $this->assertNull($this->service->tentukanKategori(null, 40.0, 80.0));
        $this->assertEquals('rendah', $this->service->tentukanKategori(0.0, 40.0, 80.0));
        $this->assertEquals('rendah', $this->service->tentukanKategori(40.0, 40.0, 80.0));
        $this->assertEquals('sedang', $this->service->tentukanKategori(40.1, 40.0, 80.0));
        $this->assertEquals('sedang', $this->service->tentukanKategori(80.0, 40.0, 80.0));
        $this->assertEquals('tinggi', $this->service->tentukanKategori(80.01, 40.0, 80.0));
        $this->assertEquals('tinggi', $this->service->tentukanKategori(100.0, 40.0, 80.0));
    }

    public function test_ringkasan_status_menghitung_tiga_status_dengan_benar(): void
    {
        $room = Room::create(['nama_ruangan' => 'Lab 1', 'status' => 'tersedia']);
        $schedule = Schedule::create([
            'room_id' => $room->id,
            'hari' => 'Senin',
            'jam_mulai' => '08:00',
            'jam_selesai' => '10:00',
            'mata_kuliah' => 'AI',
            'kelas' => 'IF-1',
            'dosen' => 'Dosen 1',
        ]);

        DB::table('classification_results')->insert([
            [
                'room_id' => $room->id,
                'schedule_id' => $schedule->id,
                'tanggal' => '2026-10-05',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '10:00:00',
                'status' => 'sesuai_jadwal',
                'menit_terjadwal' => 120,
                'menit_terpakai' => 100,
                'utilisasi_pct' => 83.33,
                'rule_id' => 'R01',
                'penjelasan' => 'Sesuai jadwal',
                'computed_at' => '2026-10-05 10:10:00',
            ],
            [
                'room_id' => $room->id,
                'schedule_id' => $schedule->id,
                'tanggal' => '2026-10-06',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '10:00:00',
                'status' => 'kosong_meski_terjadwal',
                'menit_terjadwal' => 120,
                'menit_terpakai' => 0,
                'utilisasi_pct' => 0.0,
                'rule_id' => 'R02',
                'penjelasan' => 'Kosong terjadwal',
                'computed_at' => '2026-10-06 10:10:00',
            ],
            [
                'room_id' => $room->id,
                'schedule_id' => null,
                'tanggal' => '2026-10-07',
                'waktu_mulai' => '13:00:00',
                'waktu_selesai' => '14:00:00',
                'status' => 'dipakai_di_luar_jadwal',
                'menit_terjadwal' => 0,
                'menit_terpakai' => 60,
                'utilisasi_pct' => null,
                'rule_id' => 'R03',
                'penjelasan' => 'Luar jadwal',
                'computed_at' => '2026-10-07 14:10:00',
            ],
        ]);

        $ringkasan = $this->service->ringkasanStatus('2026-10-05', '2026-10-07');

        $this->assertEquals(1, $ringkasan['sesuai_jadwal']);
        $this->assertEquals(1, $ringkasan['kosong_meski_terjadwal']);
        $this->assertEquals(1, $ringkasan['dipakai_di_luar_jadwal']);
        $this->assertEquals(3, $ringkasan['total_sesi']);
    }

    public function test_utilisasi_per_ruang_rumus_terbobot_dan_mengecualikan_luar_jadwal(): void
    {
        ThresholdSetting::create(['key' => 'utilization_low_max', 'value' => '40', 'keterangan' => '']);
        ThresholdSetting::create(['key' => 'utilization_medium_max', 'value' => '80', 'keterangan' => '']);

        $room1 = Room::create(['nama_ruangan' => 'Lab 1', 'status' => 'tersedia']);
        $room2 = Room::create(['nama_ruangan' => 'Lab 2', 'status' => 'tersedia']);

        $sched1 = Schedule::create([
            'room_id' => $room1->id,
            'hari' => 'Senin',
            'jam_mulai' => '08:00',
            'jam_selesai' => '10:00',
            'mata_kuliah' => 'Matkul A',
            'kelas' => 'IF-1',
            'dosen' => 'Dosen A',
        ]);

        // Room 1: dua sesi terjadwal (total terjadwal = 120 + 60 = 180, total terpakai = 60 + 30 = 90) -> 50%
        // dan 1 baris di luar jadwal (harus diabaikan)
        DB::table('classification_results')->insert([
            [
                'room_id' => $room1->id,
                'schedule_id' => $sched1->id,
                'tanggal' => '2026-10-05',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '10:00:00',
                'status' => 'sesuai_jadwal',
                'menit_terjadwal' => 120,
                'menit_terpakai' => 60,
                'utilisasi_pct' => 50.0,
                'rule_id' => 'R01',
                'penjelasan' => 'Sesi 1',
                'computed_at' => '2026-10-05 10:10:00',
            ],
            [
                'room_id' => $room1->id,
                'schedule_id' => $sched1->id,
                'tanggal' => '2026-10-06',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '09:00:00',
                'status' => 'sesuai_jadwal',
                'menit_terjadwal' => 60,
                'menit_terpakai' => 30,
                'utilisasi_pct' => 50.0,
                'rule_id' => 'R01',
                'penjelasan' => 'Sesi 2',
                'computed_at' => '2026-10-06 09:10:00',
            ],
            [
                'room_id' => $room1->id,
                'schedule_id' => null,
                'tanggal' => '2026-10-06',
                'waktu_mulai' => '13:00:00',
                'waktu_selesai' => '15:00:00',
                'status' => 'dipakai_di_luar_jadwal',
                'menit_terjadwal' => 0,
                'menit_terpakai' => 120,
                'utilisasi_pct' => null,
                'rule_id' => 'R03',
                'penjelasan' => 'Episode luar jadwal harus diabaikan',
                'computed_at' => '2026-10-06 15:10:00',
            ],
        ]);

        $hasil = $this->service->utilisasiPerRuang('2026-10-05', '2026-10-06');

        $this->assertCount(2, $hasil);

        // Room 1: 90 / 180 * 100 = 50.0% -> kategori sedang
        $statsRoom1 = $hasil->get($room1->id);
        $this->assertEquals(180, $statsRoom1['menit_terjadwal']);
        $this->assertEquals(90, $statsRoom1['menit_terpakai']);
        $this->assertEquals(90, $statsRoom1['selisih_menit']);
        $this->assertEquals(50.0, $statsRoom1['utilisasi_pct']);
        $this->assertEquals('sedang', $statsRoom1['kategori']);

        // Room 2: tanpa jadwal -> menit_terjadwal = 0, utilisasi_pct = null, kategori = null
        $statsRoom2 = $hasil->get($room2->id);
        $this->assertEquals(0, $statsRoom2['menit_terjadwal']);
        $this->assertEquals(0, $statsRoom2['menit_terpakai']);
        $this->assertNull($statsRoom2['utilisasi_pct']);
        $this->assertNull($statsRoom2['kategori']);
    }
}
