@extends('layouts.admin', ['title' => 'Tambah Ruangan'])

@section('content')
    <div class="max-w-2xl">
        <div class="mb-6">
            <nav class="flex items-center gap-2 text-xs text-ink/60 mb-2">
                <a href="{{ route('admin.rooms.index') }}" class="hover:text-primary">Data Ruangan</a>
                <span>/</span>
                <span class="text-ink font-medium">Tambah</span>
            </nav>
            <h1 class="text-2xl font-bold font-display text-ink tracking-tight">Tambah Ruangan</h1>
            <p class="text-sm text-ink/70 mt-1">Daftarkan data ruangan baru ke dalam sistem pemantauan.</p>
        </div>

        <div class="rounded-panel border border-line bg-surface p-6 shadow-xs">
            <form method="POST" action="{{ route('admin.rooms.store') }}">
                @csrf
                @include('admin.rooms._form', ['room' => null, 'submitLabel' => 'Simpan'])
            </form>
        </div>
    </div>
@endsection
