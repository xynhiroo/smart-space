<?php

namespace Database\Seeders;

use App\Models\Room;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\File;

class RoomSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $filePath = database_path('seed-data/rooms_if.csv');

        if (!File::exists($filePath)) {
            $this->command->error("File CSV tidak ditemukan: {$filePath}");
            return;
        }

        $fileHandle = fopen($filePath, 'r');
        $header = fgetcsv($fileHandle);

        while (($row = fgetcsv($fileHandle)) !== false) {
            if (empty($row) || empty(trim($row[0]))) {
                continue;
            }

            $namaRuangan = trim($row[0]);
            $catatan = isset($row[1]) && trim($row[1]) !== '' ? trim($row[1]) : null;

            // Hindari data karangan: kapasitas & lokasi diisi NULL bila tidak disediakan di sumber CSV
            Room::updateOrCreate(
                ['nama_ruangan' => $namaRuangan],
                [
                    'kapasitas' => null,
                    'lokasi' => $catatan,
                    'status' => 'tersedia', // Default sistem, bukan data dari sumber CSV
                ]
            );
        }

        fclose($fileHandle);
        $this->command->info('Data ruangan berhasil diimpor dari CSV.');
    }
}
