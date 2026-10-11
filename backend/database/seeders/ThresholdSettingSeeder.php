<?php

namespace Database\Seeders;

use App\Models\ThresholdSetting;
use Illuminate\Database\Seeder;

class ThresholdSettingSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $settings = [
            [
                'key' => 'utilization_low_min',
                'value' => '0',
                'keterangan' => 'Batas minimum persentase utilisasi kategori rendah (%)',
            ],
            [
                'key' => 'utilization_low_max',
                'value' => '40',
                'keterangan' => 'Batas maksimum persentase utilisasi kategori rendah (%)',
            ],
            [
                'key' => 'utilization_medium_min',
                'value' => '41',
                'keterangan' => 'Batas minimum persentase utilisasi kategori sedang (%)',
            ],
            [
                'key' => 'utilization_medium_max',
                'value' => '80',
                'keterangan' => 'Batas maksimum persentase utilisasi kategori sedang (%)',
            ],
            [
                'key' => 'utilization_high_min',
                'value' => '81',
                'keterangan' => 'Batas minimum persentase utilisasi kategori tinggi (%)',
            ],
            [
                'key' => 'utilization_high_max',
                'value' => '100',
                'keterangan' => 'Batas maksimum persentase utilisasi kategori tinggi (%)',
            ],
            [
                'key' => 'empty_status_evaluation_timing',
                'value' => 'after_schedule_finished',
                'keterangan' => 'Kebijakan evaluasi status ruang kosong: dievaluasi setelah jam terjadwal selesai, bukan durasi toleransi awal slot',
            ],
            [
                'key' => 'empty_status_use_start_tolerance',
                'value' => 'false',
                'keterangan' => 'Flag toleransi durasi di awal slot (false = dievaluasi setelah slot selesai)',
            ],
        ];

        foreach ($settings as $setting) {
            ThresholdSetting::updateOrCreate(
                ['key' => $setting['key']],
                [
                    'value' => $setting['value'],
                    'keterangan' => $setting['keterangan'],
                ]
            );
        }

        $this->command->info('Data pengaturan threshold berhasil dikonfigurasi.');
    }
}
