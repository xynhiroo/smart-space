<?php

namespace Database\Seeders;

use App\Models\AdminAccount;
use App\Models\MahasiswaAccount;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AccountSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Seed initial Admin Account
        AdminAccount::updateOrCreate(
            ['email' => 'admin@smartspace.polibatam.ac.id'],
            [
                'nama' => 'Admin Fasilitas IF',
                'password_hash' => Hash::make('admin12345'),
            ]
        );

        // Seed initial Mahasiswa Dummy Accounts (Simulasi Learning)
        $mahasiswaList = [
            '3312501036', // Rangga Surya Saputra
            '3312501059', // Muradika Laksamana Putra
            '3312501001', // Mahasiswa Simulasi 1
        ];

        foreach ($mahasiswaList as $nim) {
            MahasiswaAccount::updateOrCreate(
                ['nim' => $nim],
                [
                    'password_hash' => Hash::make('password123'),
                ]
            );
        }

        $this->command->info('Data akun Admin dan Mahasiswa awal berhasil dibuat.');
    }
}
