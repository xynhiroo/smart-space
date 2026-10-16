@extends('layouts.admin', ['title' => 'Ubah Ruangan'])

@section('content')
    <h1 class="text-2xl font-semibold">Ubah Ruangan</h1>

    <form method="POST" action="{{ route('admin.rooms.update', $room) }}" class="mt-6 max-w-xl space-y-5">
        @csrf
        @method('PUT')
        @include('admin.rooms._form', ['room' => $room, 'submitLabel' => 'Simpan perubahan'])
    </form>
@endsection