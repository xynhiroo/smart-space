<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Migration ini merupakan pengganti migrasi bawaan Laravel "create_users_table".
 *
 * Tabel `users` TIDAK dibuat karena proyek ini menggunakan dua akun terpisah:
 *   - admin_accounts  (guard 'admin')
 *   - mahasiswa_accounts (guard 'mahasiswa')
 *
 * Tabel `password_reset_tokens` dan `sessions` dipertahankan karena:
 *   - password_reset_tokens: dirujuk oleh config/auth.php bagian 'passwords'
 *     untuk broker 'admins' dan 'mahasiswas'.
 *   - sessions: dibutuhkan oleh SESSION_DRIVER=database (lihat .env).
 */
return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('password_reset_tokens', function (Blueprint $table) {
            $table->string('email')->primary();
            $table->string('token');
            $table->timestamp('created_at')->nullable();
        });

        Schema::create('sessions', function (Blueprint $table) {
            $table->string('id')->primary();
            $table->foreignId('user_id')->nullable()->index();
            $table->string('ip_address', 45)->nullable();
            $table->text('user_agent')->nullable();
            $table->longText('payload');
            $table->integer('last_activity')->index();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('password_reset_tokens');
        Schema::dropIfExists('sessions');
    }
};
