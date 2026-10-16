<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\RoomRequest;
use App\Models\Room;
use App\Models\Schedule;
use Illuminate\Http\RedirectResponse;
use Illuminate\View\View;

class RoomController extends Controller
{
    public function index(): View
    {
        $rooms = Room::orderBy('nama_ruangan')->paginate(15);

        return view('admin.rooms.index', compact('rooms'));
    }

    public function create(): View
    {
        return view('admin.rooms.create');
    }

    public function store(RoomRequest $request): RedirectResponse
    {
        Room::create($request->validated());

        return redirect()
            ->route('admin.rooms.index')
            ->with('status', 'Ruangan berhasil ditambahkan.');
    }

    public function edit(Room $room): View
    {
        return view('admin.rooms.edit', compact('room'));
    }

    public function update(RoomRequest $request, Room $room): RedirectResponse
    {
        $room->update($request->validated());

        return redirect()
            ->route('admin.rooms.index')
            ->with('status', 'Ruangan berhasil diperbarui.');
    }

    public function destroy(Room $room): RedirectResponse
    {
        // Jadwal ikut terhapus kalau ruangan dihapus (cascadeOnDelete), jadi dicegah.
        if (Schedule::where('room_id', $room->id)->exists()) {
            return redirect()
                ->route('admin.rooms.index')
                ->withErrors(['room' => "Ruangan {$room->nama_ruangan} masih punya jadwal, jadi tidak bisa dihapus."]);
        }

        $room->delete();

        return redirect()
            ->route('admin.rooms.index')
            ->with('status', 'Ruangan berhasil dihapus.');
    }
}