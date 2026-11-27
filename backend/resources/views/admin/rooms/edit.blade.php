@extends('layouts.admin', ['title' => 'Ubah Ruangan'])

@section('content')
    <div class="max-w-2xl">
        <div class="mb-6">
            <nav class="flex items-center gap-2 text-xs text-ink/60 mb-2">
                <a href="{{ route('admin.rooms.index') }}" class="hover:text-primary">Data Ruangan</a>
                <span>/</span>
                <span class="text-ink font-medium">Ubah</span>
            </nav>
            <h1 class="text-2xl font-bold font-display text-ink tracking-tight">Ubah Ruangan</h1>
            <p class="text-sm text-ink/70 mt-1">Perbarui informasi kapasitas, lokasi, atau kondisi master ruangan.</p>
        </div>

        <div class="rounded-panel border border-line bg-surface p-6 shadow-xs">
            <form method="POST" action="{{ route('admin.rooms.update', $room) }}">
                @csrf
                @method('PUT')
                @include('admin.rooms._form', ['room' => $room, 'submitLabel' => 'Simpan perubahan'])
            </form>
        </div>
    </div>
@endsection
