<?php

namespace Database\Seeders;

use App\Models\CalendarException;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\File;

class CalendarExceptionSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $filePath = $this->resolveFilePath('calendar_exceptions_ganjil2627.csv');

        if (!File::exists($filePath)) {
            $this->command->error("File CSV tidak ditemukan: {$filePath}");
            return;
        }

        $fileHandle = fopen($filePath, 'r');
        $header = fgetcsv($fileHandle);

        $insertedCount = 0;

        while (($row = fgetcsv($fileHandle)) !== false) {
            if (empty($row) || count($row) < 4) {
                continue;
            }

            // CSV Columns: tanggal_mulai,tanggal_selesai,tipe,keterangan
            $tanggalMulai = trim($row[0]);
            $tanggalSelesai = trim($row[1]);
            $tipe = trim($row[2]);
            $keterangan = trim($row[3]);

            if (empty($tanggalMulai) || empty($tanggalSelesai)) {
                continue;
            }

            CalendarException::create([
                'tanggal_mulai' => $tanggalMulai,
                'tanggal_selesai' => $tanggalSelesai,
                'tipe' => $tipe,
                'keterangan' => $keterangan,
            ]);

            $insertedCount++;
        }

        fclose($fileHandle);
        $this->command->info("Data kalender akademik berhasil diimpor: {$insertedCount} baris.");
    }

    /**
     * Resolve path to the CSV file across different environments.
     */
    private function resolveFilePath(string $filename): string
    {
        $backendPath = database_path("seed-data/{$filename}");
        if (File::exists($backendPath)) {
            return $backendPath;
        }

        return base_path("../database/seed-data/{$filename}");
    }
}
