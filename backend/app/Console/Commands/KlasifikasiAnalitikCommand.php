<?php

namespace App\Console\Commands;

use App\Services\AiServiceClient;
use Illuminate\Console\Command;

class KlasifikasiAnalitikCommand extends Command
{
    /**
     * Nama dan tanda tangan perintah console.
     *
     * @var string
     */
    protected $signature = 'analitik:klasifikasi
                            {mulai : Tanggal awal dalam format YYYY-MM-DD}
                            {selesai : Tanggal akhir dalam format YYYY-MM-DD}
                            {--room= : Filter opsional ID ruang}';

    /**
     * Deskripsi perintah console.
     *
     * @var string
     */
    protected $description = 'Menjalankan klasifikasi sistem pakar via AiServiceClient ke AI Service';

    /**
     * Eksekusi perintah console.
     */
    public function handle(AiServiceClient $client): int
    {
        $mulai = (string) $this->argument('mulai');
        $selesai = (string) $this->argument('selesai');
        $roomId = $this->option('room') ? (int) $this->option('room') : null;

        $this->info("Menjalankan klasifikasi analitik untuk rentang {$mulai} s.d. {$selesai}...");

        $hasil = $client->classify($mulai, $selesai, $roomId);

        if ($hasil['sukses']) {
            $this->info($hasil['pesan']);
            if (!empty($hasil['data'])) {
                $this->line(json_encode($hasil['data'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
            }
            return self::SUCCESS;
        }

        $this->warn($hasil['pesan']);
        return self::FAILURE;
    }
}
