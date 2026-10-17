<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Facades\DB;

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

    /**
     * Get the count of schedules associated with this room.
     */
    public function schedulesCount(): int
    {
        return $this->schedules()->count();
    }

    /**
     * Get the count of analytics history records (occupancy logs and classification results).
     */
    public function historyCount(): int
    {
        $occupancyCount = DB::table('occupancy_logs')->where('room_id', $this->id)->count();
        $classificationCount = DB::table('classification_results')->where('room_id', $this->id)->count();

        return $occupancyCount + $classificationCount;
    }

    /**
     * Determine whether the room has any associated schedules or analytics history.
     */
    public function hasAssociatedData(): bool
    {
        return $this->schedulesCount() > 0 || $this->historyCount() > 0;
    }

    /**
     * Get the deletion block reason message if room cannot be deleted, or null if it can.
     */
    public function getDeletionBlockReason(): ?string
    {
        $schedulesCount = $this->schedulesCount();
        $historyCount = $this->historyCount();

        if ($schedulesCount > 0 || $historyCount > 0) {
            return "Ruangan {$this->nama_ruangan} tidak dapat dihapus karena masih memiliki {$schedulesCount} jadwal dan {$historyCount} data riwayat. Data ruangan yang sudah memiliki jadwal atau riwayat dipertahankan agar analitik tidak hilang.";
        }

        return null;
    }
}
