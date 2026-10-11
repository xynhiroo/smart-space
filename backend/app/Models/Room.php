<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Room extends Model
{
    use HasFactory;

    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'rooms';

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'nama_ruangan',
        'kapasitas',
        'lokasi',
        'status',
    ];

    /**
     * Get all schedules associated with the room.
     */
    public function schedules(): HasMany
    {
        return $this->hasMany(Schedule::class, 'room_id');
    }
}
