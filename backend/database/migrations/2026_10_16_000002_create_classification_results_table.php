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
        Schema::create('classification_results', function (Blueprint $table) {
            $table->id();
            $table->foreignId('room_id')->constrained('rooms')->cascadeOnDelete();
            $table->foreignId('schedule_id')->nullable()->constrained('schedules')->cascadeOnDelete();
            $table->date('tanggal');
            $table->time('waktu_mulai');
            $table->time('waktu_selesai');
            $table->string('status', 30);
            $table->unsignedSmallInteger('menit_terjadwal');
            $table->unsignedSmallInteger('menit_terpakai');
            $table->decimal('utilisasi_pct', 5, 2)->nullable();
            $table->string('rule_id', 10);
            $table->text('penjelasan');
            $table->dateTime('computed_at');

            $table->unique(['room_id', 'tanggal', 'waktu_mulai']);
            $table->index(['tanggal', 'room_id']);
            $table->index('status');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('classification_results');
    }
};
