@extends('layouts.admin', ['title' => 'Dashboard'])

@section('content')
    <h1 class="text-2xl font-semibold">Dashboard Admin</h1>
    <p class="mt-2">Selamat datang, {{ auth('admin')->user()->nama }}.</p>

    <div class="mt-6">
        <a href="{{ route('admin.rooms.index') }}" class="inline-block rounded-md border border-shellstone bg-white px-4 py-3 font-semibold hover:bg-swan">
            Data Ruangan
        </a>
    </div>
@endsection