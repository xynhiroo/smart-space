<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use LogicException;

/**
 * Model hanya-baca untuk tabel classification_results (DATA_CONTRACT Bagian 3 & 5).
 *
 * Tabel ini hanya ditulis oleh komponen AI (Python / ai-service).
 * Laravel dilarang keras melakukan operasi tulis ke tabel ini.
 */
class ClassificationResult extends Model
{
    use HasFactory;

    /**
     * Nama tabel terkait.
     *
     * @var string
     */
    protected $table = 'classification_results';

    /**
     * Tabel tidak menggunakan timestamp Laravel created_at dan updated_at.
     *
     * @var bool
     */
    public $timestamps = false;

    /**
     * Atribut yang boleh diisi (mass assignable).
     *
     * @var array<int, string>
     */
    protected $fillable = [];

    /**
     * Konversi tipe atribut (casting).
     *
     * @var array<string, string>
     */
    protected $casts = [
        'tanggal' => 'date',
        'menit_terjadwal' => 'integer',
        'menit_terpakai' => 'integer',
        'utilisasi_pct' => 'float',
        'computed_at' => 'datetime',
    ];

    /**
     * Relasi ke model Room.
     */
    public function room(): BelongsTo
    {
        return $this->belongsTo(Room::class, 'room_id');
    }

    /**
     * Relasi ke model Schedule (nullable untuk episode di luar jadwal).
     */
    public function schedule(): BelongsTo
    {
        return $this->belongsTo(Schedule::class, 'schedule_id');
    }

    /**
     * Larang operasi simpan (save/insert/update) dari Laravel.
     */
    public function save(array $options = []): bool
    {
        throw new LogicException('Tabel classification_results bersifat hanya-baca (read-only) untuk Laravel.');
    }

    /**
     * Larang operasi perbarui (update) dari Laravel.
     */
    public function update(array $attributes = [], array $options = []): bool
    {
        throw new LogicException('Tabel classification_results bersifat hanya-baca (read-only) untuk Laravel.');
    }

    /**
     * Larang operasi hapus (delete) dari Laravel.
     */
    public function delete(): ?bool
    {
        throw new LogicException('Tabel classification_results bersifat hanya-baca (read-only) untuk Laravel.');
    }
}
