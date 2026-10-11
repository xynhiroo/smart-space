<?php

namespace Database\Seeders;

use App\Models\Room;
use App\Models\Schedule;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\File;

class ScheduleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $filePath = database_path('seed-data/schedules_if_gabungan.csv');

        if (!File::exists($filePath)) {
            $this->command->error("File CSV tidak ditemukan: {$filePath}");
            return;
        }

        $fileHandle = fopen($filePath, 'r');
        $header = fgetcsv($fileHandle);

        $insertedCount = 0;
        $skippedCount = 0;

        while (($row = fgetcsv($fileHandle)) !== false) {
            if (empty($row) || count($row) < 7) {
                continue;
            }

            // CSV Columns: hari,jam_mulai,jam_selesai,kelas,mata_kuliah,dosen,ruangan,shift
            $hari = trim($row[0]);
            $jamMulai = trim($row[1]);
            $jamSelesai = trim($row[2]);
            $kelas = trim($row[3]);
            $mataKuliah = trim($row[4]);
            $dosen = trim($row[5]);
            $namaRuangan = trim($row[6]);
            $shift = isset($row[7]) ? trim($row[7]) : null;

            if (empty($namaRuangan) || empty($mataKuliah)) {
                $skippedCount++;
                continue;
            }

            // Hubungkan dengan room_id berdasarkan nama_ruangan
            $room = Room::where('nama_ruangan', $namaRuangan)->first();

            if (!$room) {
                // Jika ruangan belum terdaftar, buat record ruangan otomatis
                $room = Room::create([
                    'nama_ruangan' => $namaRuangan,
                    'kapasitas' => null,
                    'status' => 'tersedia', // Default sistem, bukan data dari sumber CSV
                ]);
            }

            Schedule::create([
                'room_id' => $room->id,
                'hari' => $hari,
                'jam_mulai' => $jamMulai,
                'jam_selesai' => $jamSelesai,
                'mata_kuliah' => $mataKuliah,
                'kelas' => $kelas,
                'dosen' => $dosen,
                'shift' => $shift,
            ]);

            $insertedCount++;
        }

        fclose($fileHandle);
        $this->command->info("Data jadwal berhasil diimpor: {$insertedCount} baris, {$skippedCount} diabaikan.");
    }
}
