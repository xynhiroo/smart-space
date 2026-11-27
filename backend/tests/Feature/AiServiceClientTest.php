<?php

namespace Tests\Feature;

use App\Services\AiServiceClient;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class AiServiceClientTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        Config::set('services.ai_service.url', 'http://127.0.0.1:8001');
        Config::set('services.ai_service.token', 'test-secret-token');
        Config::set('services.ai_service.timeout', 2);
    }

    public function test_classify_berhasil_mengembalikan_data(): void
    {
        Http::fake([
            'http://127.0.0.1:8001/classify' => Http::response([
                'status' => 'success',
                'total_terklasifikasi' => 45,
            ], 200),
        ]);

        $client = new AiServiceClient();
        $hasil = $client->classify('2026-10-05', '2026-10-09');

        $this->assertTrue($hasil['sukses']);
        $this->assertEquals(200, $hasil['status_code']);
        $this->assertEquals(45, $hasil['data']['total_terklasifikasi']);

        Http::assertSent(function ($request) {
            return $request->url() === 'http://127.0.0.1:8001/classify'
                && $request->hasHeader('X-Internal-Token', 'test-secret-token')
                && $request['tanggal_mulai'] === '2026-10-05'
                && $request['tanggal_selesai'] === '2026-10-09';
        });
    }

    public function test_classify_gagal_atau_error_500_mengembalikan_pesan_ramah(): void
    {
        Http::fake([
            'http://127.0.0.1:8001/classify' => Http::response([
                'detail' => 'Database connection failed',
            ], 500),
        ]);

        $client = new AiServiceClient();
        $hasil = $client->classify('2026-10-05', '2026-10-09');

        $this->assertFalse($hasil['sukses']);
        $this->assertEquals(500, $hasil['status_code']);
        $this->assertEquals(AiServiceClient::PESAN_LAYANAN_TIDAK_TERSEDIA, $hasil['pesan']);
        $this->assertNull($hasil['data']);
    }

    public function test_classify_saat_layanan_mati_atau_timeout_mengembalikan_pesan_ramah(): void
    {
        Http::fake([
            'http://127.0.0.1:8001/classify' => function () {
                throw new ConnectionException('Connection refused');
            },
        ]);

        $client = new AiServiceClient();
        $hasil = $client->classify('2026-10-05', '2026-10-09');

        $this->assertFalse($hasil['sukses']);
        $this->assertNull($hasil['status_code']);
        $this->assertEquals(AiServiceClient::PESAN_LAYANAN_TIDAK_TERSEDIA, $hasil['pesan']);
        $this->assertNull($hasil['data']);
    }

    public function test_perintah_artisan_analitik_klasifikasi(): void
    {
        Http::fake([
            'http://127.0.0.1:8001/classify' => Http::response([
                'total_terklasifikasi' => 10,
            ], 200),
        ]);

        $exitCode = Artisan::call('analitik:klasifikasi', [
            'mulai' => '2026-10-05',
            'selesai' => '2026-10-09',
        ]);

        $this->assertEquals(0, $exitCode);
        $output = Artisan::output();
        $this->assertStringContainsString('Klasifikasi berhasil dijalankan.', $output);
    }
}
