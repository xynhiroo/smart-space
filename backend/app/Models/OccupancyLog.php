<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use LogicException;

/**
 * Model hanya-baca untuk tabel occupancy_logs (DATA_CONTRACT Bagian 3 & 4).
 *
 * Tabel ini hanya ditulis oleh komponen AI (Python / ai-service).
 * Laravel dilarang keras melakukan operasi tulis ke tabel ini.
 */
class OccupancyLog extends Model
{
    use HasFactory;

    /**
     * Nama tabel terkait.
     *
     * @var string
     */
    protected $table = 'occupancy_logs';

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
        'slot_mulai' => 'datetime',
        'is_occupied' => 'boolean',
    ];

    /**
     * Relasi ke model Room.
     */
    public function room(): BelongsTo
    {
        return $this->belongsTo(Room::class, 'room_id');
    }

    /**
     * Larang operasi simpan (save/insert/update) dari Laravel.
     */
    public function save(array $options = []): bool
    {
        throw new LogicException('Tabel occupancy_logs bersifat hanya-baca (read-only) untuk Laravel.');
    }

    /**
     * Larang operasi perbarui (update) dari Laravel.
     */
    public function update(array $attributes = [], array $options = []): bool
    {
        throw new LogicException('Tabel occupancy_logs bersifat hanya-baca (read-only) untuk Laravel.');
    }

    /**
     * Larang operasi hapus (delete) dari Laravel.
     */
    public function delete(): ?bool
    {
        throw new LogicException('Tabel occupancy_logs bersifat hanya-baca (read-only) untuk Laravel.');
    }
}
