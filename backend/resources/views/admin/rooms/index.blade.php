@extends('layouts.admin', ['title' => 'Data Ruangan'])

@section('content')
    <div class="flex items-center justify-between gap-4">
        <h1 class="text-2xl font-semibold">Data Ruangan</h1>
        <a href="{{ route('admin.rooms.create') }}" class="rounded-md bg-royal px-4 py-2 text-sm font-semibold text-swan hover:opacity-90">
            Tambah ruangan
        </a>
    </div>

    @if (session('status'))
        <div role="status" class="mt-4 rounded-md border border-shellstone bg-white px-4 py-3 text-sm">
            {{ session('status') }}
        </div>
    @endif

    @if ($errors->any())
        <div class="mt-4">
            <x-alert>
                <ul class="space-y-1">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </x-alert>
        </div>
    @endif

    <div class="mt-6 overflow-x-auto rounded-md border border-shellstone bg-white">
        <table class="min-w-full text-left text-sm">
            <thead class="border-b border-shellstone bg-swan">
                <tr>
                    <th class="px-4 py-3 font-semibold">Nama ruangan</th>
                    <th class="px-4 py-3 font-semibold">Kapasitas</th>
                    <th class="px-4 py-3 font-semibold">Lokasi</th>
                    <th class="px-4 py-3 font-semibold">Status</th>
                    <th class="px-4 py-3 font-semibold">Aksi</th>
                </tr>
            </thead>
            <tbody>
                @forelse ($rooms as $room)
                    <tr class="border-b border-shellstone last:border-0">
                        <td class="px-4 py-3 font-semibold">{{ $room->nama_ruangan }}</td>
                        <td class="px-4 py-3">{{ $room->kapasitas ?? '-' }}</td>
                        <td class="px-4 py-3">{{ $room->lokasi ?? '-' }}</td>
                        <td class="px-4 py-3">{{ $room->status }}</td>
                        <td class="px-4 py-3">
                            <div class="flex items-center gap-4">
                                <a href="{{ route('admin.rooms.edit', $room) }}" class="font-semibold text-sapphire hover:text-royal">Ubah</a>
                                <form method="POST" action="{{ route('admin.rooms.destroy', $room) }}"
                                      onsubmit="return confirm({{ Illuminate\Support\Js::from('Hapus ruangan '.$room->nama_ruangan.'?') }})">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="font-semibold text-sapphire hover:text-royal">Hapus</button>
                                </form>
                            </div>
                        </td>
                    </tr>
                @empty
                    <tr>
                        <td colspan="5" class="px-4 py-6 text-center">Belum ada ruangan.</td>
                    </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    <div class="mt-4">
        {{ $rooms->links() }}
    </div>
@endsection