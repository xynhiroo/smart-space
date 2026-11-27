<?php

namespace App\Services;

use App\Models\ClassificationResult;
use App\Models\Room;
use App\Models\ThresholdSetting;
use Carbon\CarbonInterface;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;

class AnalitikService
{
    public const KATEGORI_RENDAH = 'rendah';
    public const KATEGORI_SEDANG = 'sedang';
    public const KATEGORI_TINGGI = 'tinggi';

    /**
     * Mengambil ambang batas utilisasi (utilization_low_max dan utilization_medium_max)
     * dari tabel threshold_settings secara dinamis.
     *
     * @return array{batas_rendah: float, batas_sedang: float}
     */
    public function ambilAmbangBatas(): array
    {
        $settings = ThresholdSetting::whereIn('key', [
            'utilization_low_max',
            'utilization_medium_max',
        ])->pluck('value', 'key');

        $batasRendah = isset($settings['utilization_low_max'])
            ? (float) $settings['utilization_low_max']
            : 40.0;

        $batasSedang = isset($settings['utilization_medium_max'])
            ? (float) $settings['utilization_medium_max']
            : 80.0;

        if ($batasRendah >= $batasSedang) {
            throw new InvalidArgumentException('Ambang batas_rendah harus lebih kecil dari batas_sedang.');
        }

        return [
            'batas_rendah' => $batasRendah,
            'batas_sedang' => $batasSedang,
        ];
    }

    /**
     * Menentukan kategori utilisasi berdasarkan ambang dinamis (DATA_CONTRACT Bagian 10).
     * <= batas_rendah -> rendah, <= batas_sedang -> sedang, selebihnya -> tinggi.
     */
    public function tentukanKategori(?float $utilisasiPct, float $batasRendah, float $batasSedang): ?string
    {
        if ($utilisasiPct === null) {
            return null;
        }

        if ($utilisasiPct <= $batasRendah) {
            return self::KATEGORI_RENDAH;
        }

        if ($utilisasiPct <= $batasSedang) {
            return self::KATEGORI_SEDANG;
        }

        return self::KATEGORI_TINGGI;
    }

    /**
     * Menghitung ringkasan jumlah sesi per status dalam rentang tanggal (inklusif).
     *
     * @param string|CarbonInterface $tanggalMulai Format Y-m-d atau Carbon instance
     * @param string|CarbonInterface $tanggalSelesai Format Y-m-d atau Carbon instance
     * @param int|null $roomId Filter opsional ID ruang
     * @return array{
     *     sesuai_jadwal: int,
     *     kosong_meski_terjadwal: int,
     *     dipakai_di_luar_jadwal: int,
     *     total_sesi: int
     * }
     */
    public function ringkasanStatus(
        string|CarbonInterface $tanggalMulai,
        string|CarbonInterface $tanggalSelesai,
        ?int $roomId = null
    ): array {
        $mulai = is_string($tanggalMulai) ? $tanggalMulai : $tanggalMulai->format('Y-m-d');
        $selesai = is_string($tanggalSelesai) ? $tanggalSelesai : $tanggalSelesai->format('Y-m-d');

        $query = DB::table('classification_results')
            ->whereBetween('tanggal', [$mulai, $selesai]);

        if ($roomId !== null) {
            $query->where('room_id', $roomId);
        }

        $counts = $query->select('status', DB::raw('count(*) as total'))
            ->groupBy('status')
            ->pluck('total', 'status')
            ->all();

        $sesuaiJadwal = (int) ($counts['sesuai_jadwal'] ?? 0);
        $kosongMeskiTerjadwal = (int) ($counts['kosong_meski_terjadwal'] ?? 0);
        $dipakaiDiLuarJadwal = (int) ($counts['dipakai_di_luar_jadwal'] ?? 0);

        return [
            'sesuai_jadwal' => $sesuaiJadwal,
            'kosong_meski_terjadwal' => $kosongMeskiTerjadwal,
            'dipakai_di_luar_jadwal' => $dipakaiDiLuarJadwal,
            'total_sesi' => $sesuaiJadwal + $kosongMeskiTerjadwal + $dipakaiDiLuarJadwal,
        ];
    }

    /**
     * Menghitung utilisasi terbobot per ruang dalam rentang tanggal (inklusif).
     *
     * Rumus (DATA_CONTRACT Bagian 10):
     * sum(menit_terpakai) / sum(menit_terjadwal) x 100
     * Hanya baris sesi yang memiliki schedule_id IS NOT NULL.
     * Bila sum(menit_terjadwal) == 0: hasil null, kategori null.
     *
     * @param string|CarbonInterface $tanggalMulai
     * @param string|CarbonInterface $tanggalSelesai
     * @param int|null $roomId
     * @return Collection<int, array{
     *     room_id: int,
     *     nama_ruangan: string,
     *     menit_terjadwal: int,
     *     menit_terpakai: int,
     *     selisih_menit: int,
     *     utilisasi_pct: float|null,
     *     kategori: string|null,
     *     rata_rata_harian_pct: float|null,
     *     min_harian_pct: float|null,
     *     max_harian_pct: float|null
     * }>
     */
    public function utilisasiPerRuang(
        string|CarbonInterface $tanggalMulai,
        string|CarbonInterface $tanggalSelesai,
        ?int $roomId = null
    ): Collection {
        $mulai = is_string($tanggalMulai) ? $tanggalMulai : $tanggalMulai->format('Y-m-d');
        $selesai = is_string($tanggalSelesai) ? $tanggalSelesai : $tanggalSelesai->format('Y-m-d');

        $ambang = $this->ambilAmbangBatas();
        $batasRendah = $ambang['batas_rendah'];
        $batasSedang = $ambang['batas_sedang'];

        // Ambil daftar ruang target
        $roomQuery = Room::orderBy('id');
        if ($roomId !== null) {
            $roomQuery->where('id', $roomId);
        }
        $rooms = $roomQuery->get();

        if ($rooms->isEmpty()) {
            return collect();
        }

        // Ambil baris sesi resmi (schedule_id IS NOT NULL)
        $sessionQuery = DB::table('classification_results')
            ->select('room_id', 'tanggal', 'menit_terjadwal', 'menit_terpakai')
            ->whereNotNull('schedule_id')
            ->whereBetween('tanggal', [$mulai, $selesai]);

        if ($roomId !== null) {
            $sessionQuery->where('room_id', $roomId);
        }

        $sessions = $sessionQuery->get();

        // Kelompokkan sesi berdasarkan room_id
        $sessionsByRoom = $sessions->groupBy('room_id');

        return $rooms->map(function (Room $room) use ($sessionsByRoom, $batasRendah, $batasSedang) {
            $roomSessions = $sessionsByRoom->get($room->id, collect());

            $totalTerjadwal = (int) $roomSessions->sum('menit_terjadwal');
            $totalTerpakai = (int) $roomSessions->sum('menit_terpakai');
            $selisihMenit = $totalTerjadwal - $totalTerpakai;

            $utilisasiPct = null;
            $kategori = null;

            if ($totalTerjadwal > 0) {
                $rawPct = ($totalTerpakai * 100) / $totalTerjadwal;
                $utilisasiPct = round($rawPct, 2);
                $kategori = $this->tentukanKategori($rawPct, $batasRendah, $batasSedang);
            }

            // Hitung statistik harian (rata-rata, min, max harian)
            $dailyStats = $roomSessions->groupBy('tanggal')->map(function (Collection $daySessions) {
                $dayTerjadwal = (int) $daySessions->sum('menit_terjadwal');
                $dayTerpakai = (int) $daySessions->sum('menit_terpakai');
                if ($dayTerjadwal === 0) {
                    return null;
                }
                return ($dayTerpakai * 100) / $dayTerjadwal;
            })->filter(fn ($pct) => $pct !== null);

            $rataRataHarian = null;
            $minHarian = null;
            $maxHarian = null;

            if ($dailyStats->isNotEmpty()) {
                $rataRataHarian = round($dailyStats->average(), 2);
                $minHarian = round($dailyStats->min(), 2);
                $maxHarian = round($dailyStats->max(), 2);
            }

            return [
                'room_id' => $room->id,
                'nama_ruangan' => $room->nama_ruangan,
                'menit_terjadwal' => $totalTerjadwal,
                'menit_terpakai' => $totalTerpakai,
                'selisih_menit' => $selisihMenit,
                'utilisasi_pct' => $utilisasiPct,
                'kategori' => $kategori,
                'rata_rata_harian_pct' => $rataRataHarian,
                'min_harian_pct' => $minHarian,
                'max_harian_pct' => $maxHarian,
            ];
        })->keyBy('room_id');
    }

    /**
     * Mengambil tanggal komputasi klasifikasi terakhir yang ada di database.
     */
    public function tanggalKomputasiTerakhir(): ?string
    {
        return DB::table('classification_results')
            ->max('computed_at');
    }
}
