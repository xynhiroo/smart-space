<?php

namespace Tests\Feature;

use App\Models\Room;
use App\Models\Schedule;
use App\Models\ThresholdSetting;
use App\Services\AnalitikService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

/**
 * Pengujian kesetaraan (equivalence test):
 * Memastikan hasil perhitungan AnalitikService di Laravel menghasilkan angka,
 * utilisasi terbobot, selisih menit, dan kategori yang identik persis dengan logika
 * yang ada di ai-service (FastAPI /utilization & utilization.py) pada dataset yang sama.
 */
class AnalitikServiceEquivalenceTest extends TestCase
{
    use RefreshDatabase;

    public function test_utilisasi_setara_dengan_logika_fastapi_utilization(): void
    {
        // 1. Setup threshold settings (sama seperti default ai-service)
        ThresholdSetting::create([
            'key' => 'utilization_low_max',
            'value' => '40',
            'keterangan' => 'Batas bawah',
        ]);
        ThresholdSetting::create([
            'key' => 'utilization_medium_max',
            'value' => '80',
            'keterangan' => 'Batas tengah',
        ]);

        // 2. Setup master rooms
        $room701 = Room::create(['nama_ruangan' => 'GU 701', 'status' => 'tersedia']);
        $room702 = Room::create(['nama_ruangan' => 'GU 702', 'status' => 'tersedia']);
        $room703 = Room::create(['nama_ruangan' => 'GU 703', 'status' => 'tersedia']);

        $sched1 = Schedule::create([
            'room_id' => $room701->id,
            'hari' => 'Senin',
            'jam_mulai' => '08:00',
            'jam_selesai' => '10:00',
            'mata_kuliah' => 'Algoritma',
            'kelas' => 'IF-1',
            'dosen' => 'Dosen A',
        ]);
        $sched2 = Schedule::create([
            'room_id' => $room702->id,
            'hari' => 'Senin',
            'jam_mulai' => '10:00',
            'jam_selesai' => '12:00',
            'mata_kuliah' => 'Basis Data',
            'kelas' => 'IF-2',
            'dosen' => 'Dosen B',
        ]);

        // 3. Masukkan dataset sesi dan episode
        DB::table('classification_results')->insert([
            // GU 701 - Hari 1: 120 menit terjadwal, 40 menit terpakai (33.33%)
            [
                'room_id' => $room701->id,
                'schedule_id' => $sched1->id,
                'tanggal' => '2026-10-05',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '10:00:00',
                'status' => 'sesuai_jadwal',
                'menit_terjadwal' => 120,
                'menit_terpakai' => 40,
                'utilisasi_pct' => 33.33,
                'rule_id' => 'R01',
                'penjelasan' => 'Sesuai',
                'computed_at' => '2026-10-05 10:10:00',
            ],
            // GU 701 - Hari 2: 120 menit terjadwal, 100 menit terpakai (83.33%)
            // Total GU 701: terjadwal = 240, terpakai = 140. Terbobot = 140/240 * 100 = 58.33% (Sedang)
            [
                'room_id' => $room701->id,
                'schedule_id' => $sched1->id,
                'tanggal' => '2026-10-06',
                'waktu_mulai' => '08:00:00',
                'waktu_selesai' => '10:00:00',
                'status' => 'sesuai_jadwal',
                'menit_terjadwal' => 120,
                'menit_terpakai' => 100,
                'utilisasi_pct' => 83.33,
                'rule_id' => 'R01',
                'penjelasan' => 'Sesuai',
                'computed_at' => '2026-10-06 10:10:00',
            ],
            // GU 702 - Hari 1: 120 menit terjadwal, 110 menit terpakai (91.67%) -> Kategori Tinggi
            [
                'room_id' => $room702->id,
                'schedule_id' => $sched2->id,
                'tanggal' => '2026-10-05',
                'waktu_mulai' => '10:00:00',
                'waktu_selesai' => '12:00:00',
                'status' => 'sesuai_jadwal',
                'menit_terjadwal' => 120,
                'menit_terpakai' => 110,
                'utilisasi_pct' => 91.67,
                'rule_id' => 'R01',
                'penjelasan' => 'Sesuai',
                'computed_at' => '2026-10-05 12:10:00',
            ],
            // Episode di luar jadwal pada GU 701 (tidak boleh masuk hitungan)
            [
                'room_id' => $room701->id,
                'schedule_id' => null,
                'tanggal' => '2026-10-05',
                'waktu_mulai' => '14:00:00',
                'waktu_selesai' => '16:00:00',
                'status' => 'dipakai_di_luar_jadwal',
                'menit_terjadwal' => 0,
                'menit_terpakai' => 120,
                'utilisasi_pct' => null,
                'rule_id' => 'R03',
                'penjelasan' => 'Luar jadwal',
                'computed_at' => '2026-10-05 16:10:00',
            ],
        ]);

        $service = new AnalitikService();
        $hasil = $service->utilisasiPerRuang('2026-10-05', '2026-10-06');

        // Verifikasi Ruang 1 (GU 701)
        $r1 = $hasil->get($room701->id);
        $this->assertEquals(240, $r1['menit_terjadwal']);
        $this->assertEquals(140, $r1['menit_terpakai']);
        $this->assertEquals(100, $r1['selisih_menit']);
        // 140 / 240 * 100 = 58.3333... dibulatkan 2 desimal = 58.33
        $this->assertEquals(58.33, $r1['utilisasi_pct']);
        $this->assertEquals('sedang', $r1['kategori']);
        // Harian: Hari 1 = 33.33%, Hari 2 = 83.33% -> rata-rata = 58.33%, min = 33.33%, max = 83.33%
        $this->assertEquals(58.33, $r1['rata_rata_harian_pct']);
        $this->assertEquals(33.33, $r1['min_harian_pct']);
        $this->assertEquals(83.33, $r1['max_harian_pct']);

        // Verifikasi Ruang 2 (GU 702)
        $r2 = $hasil->get($room702->id);
        $this->assertEquals(120, $r2['menit_terjadwal']);
        $this->assertEquals(110, $r2['menit_terpakai']);
        $this->assertEquals(10, $r2['selisih_menit']);
        // 110 / 120 * 100 = 91.666... dibulatkan 2 desimal = 91.67
        $this->assertEquals(91.67, $r2['utilisasi_pct']);
        $this->assertEquals('tinggi', $r2['kategori']);

        // Verifikasi Ruang 3 (GU 703) tanpa sesi
        $r3 = $hasil->get($room703->id);
        $this->assertEquals(0, $r3['menit_terjadwal']);
        $this->assertEquals(0, $r3['menit_terpakai']);
        $this->assertEquals(0, $r3['selisih_menit']);
        $this->assertNull($r3['utilisasi_pct']);
        $this->assertNull($r3['kategori']);
    }
}
