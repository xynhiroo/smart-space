<?php

namespace App\Services;

use Exception;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\RequestException;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class AiServiceClient
{
    protected string $baseUrl;
    protected string $token;
    protected int $timeout;

    public const PESAN_LAYANAN_TIDAK_TERSEDIA = 'Layanan analitik sedang tidak tersedia, menampilkan data terakhir.';

    public function __construct(
        ?string $baseUrl = null,
        ?string $token = null,
        ?int $timeout = null
    ) {
        $this->baseUrl = rtrim($baseUrl ?? (string) Config::get('services.ai_service.url', 'http://127.0.0.1:8001'), '/');
        $this->token = $token ?? (string) Config::get('services.ai_service.token', '');
        $this->timeout = $timeout ?? (int) Config::get('services.ai_service.timeout', 10);
    }

    /**
     * Memanggil POST /classify ke layanan FastAPI AI Service.
     *
     * - Timeout 10 detik.
     * - Retry 1 kali otomatis dengan jeda 100ms.
     * - Header Authorization/X-Internal-Token untuk otentikasi internal.
     * - Menangkap kegagalan jaringan atau respons error dan mengembalikan status ramah.
     *
     * @param string $tanggalMulai Format YYYY-MM-DD
     * @param string $tanggalSelesai Format YYYY-MM-DD
     * @param int|null $roomId Batasi ke room_id tertentu bila diberikan
     * @return array{
     *     sukses: bool,
     *     pesan: string,
     *     data: array<string, mixed>|null,
     *     status_code: int|null
     * }
     */
    public function classify(string $tanggalMulai, string $tanggalSelesai, ?int $roomId = null): array
    {
        $url = "{$this->baseUrl}/classify";
        $payload = [
            'tanggal_mulai' => $tanggalMulai,
            'tanggal_selesai' => $tanggalSelesai,
        ];
        if ($roomId !== null) {
            $payload['room_id'] = $roomId;
        }

        try {
            $response = Http::timeout($this->timeout)
                ->retry(1, 100, throw: false)
                ->withHeaders([
                    'X-Internal-Token' => $this->token,
                    'Authorization' => "Bearer {$this->token}",
                    'Accept' => 'application/json',
                ])
                ->post($url, $payload);

            if ($response->successful()) {
                return [
                    'sukses' => true,
                    'pesan' => 'Klasifikasi berhasil dijalankan.',
                    'data' => $response->json(),
                    'status_code' => $response->status(),
                ];
            }

            Log::warning('AI Service merespons dengan status gagal', [
                'url' => $url,
                'status' => $response->status(),
                'body' => $response->body(),
            ]);

            return [
                'sukses' => false,
                'pesan' => self::PESAN_LAYANAN_TIDAK_TERSEDIA,
                'data' => null,
                'status_code' => $response->status(),
            ];
        } catch (ConnectionException | RequestException $e) {
            Log::warning('Koneksi ke AI Service gagal atau timeout', [
                'url' => $url,
                'error' => $e->getMessage(),
            ]);

            return [
                'sukses' => false,
                'pesan' => self::PESAN_LAYANAN_TIDAK_TERSEDIA,
                'data' => null,
                'status_code' => null,
            ];
        } catch (Exception $e) {
            Log::error('Kesalahan tak terduga saat menghubungi AI Service', [
                'url' => $url,
                'error' => $e->getMessage(),
            ]);

            return [
                'sukses' => false,
                'pesan' => self::PESAN_LAYANAN_TIDAK_TERSEDIA,
                'data' => null,
                'status_code' => null,
            ];
        }
    }
}
