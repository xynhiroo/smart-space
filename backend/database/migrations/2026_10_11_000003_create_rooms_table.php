<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('rooms', function (Blueprint $table) {
            $table->id();
            $table->string('nama_ruangan', 50)->unique();
            $table->integer('kapasitas')->nullable();
            $table->string('lokasi', 100)->nullable();
            $table->string('status', 50)->default('tersedia'); // Default sistem, bukan data dari sumber CSV
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('rooms');
    }
};
