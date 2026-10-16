@extends('layouts.admin', ['title' => 'Tambah Ruangan'])

@section('content')
    <h1 class="text-2xl font-semibold">Tambah Ruangan</h1>

    <form method="POST" action="{{ route('admin.rooms.store') }}" class="mt-6 max-w-xl space-y-5">
        @csrf
        @include('admin.rooms._form', ['room' => null, 'submitLabel' => 'Simpan'])
    </form>
@endsection