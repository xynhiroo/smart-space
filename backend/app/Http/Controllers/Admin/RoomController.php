<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\RoomRequest;
use App\Models\Room;
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
        if ($reason = $room->getDeletionBlockReason()) {
            return redirect()
                ->route('admin.rooms.index')
                ->withErrors(['room' => $reason]);
        }

        $room->delete();

        return redirect()
            ->route('admin.rooms.index')
            ->with('status', 'Ruangan berhasil dihapus.');
    }
}