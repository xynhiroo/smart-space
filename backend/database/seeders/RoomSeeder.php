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
            $catatan = isset($row[1]) ? trim($row[1]) : null;

            // Tentukan lokasi dari catatan atau inferensi nama ruangan
            $lokasi = !empty($catatan) ? $catatan : $this->inferLocation($namaRuangan);

            Room::updateOrCreate(
                ['nama_ruangan' => $namaRuangan],
                [
                    'kapasitas' => 30,
                    'lokasi' => $lokasi,
                    'status' => 'tersedia',
                ]
            );
        }

        fclose($fileHandle);
        $this->command->info('Data ruangan berhasil diimpor dari CSV.');
    }

    /**
     * Infer descriptive room location from room code.
     */
    private function inferLocation(string $namaRuangan): string
    {
        if (str_starts_with($namaRuangan, 'GU')) {
            $parts = explode(' ', $namaRuangan);
            $number = $parts[1] ?? '';
            $floor = strlen($number) >= 3 ? substr($number, 0, 1) : '';
            return $floor ? "Gedung Utama Lantai {$floor}" : 'Gedung Utama';
        }

        if (str_starts_with($namaRuangan, 'TA')) {
            return 'Tower A';
        }

        return 'Gedung Perkuliahan Polibatam';
    }
}
