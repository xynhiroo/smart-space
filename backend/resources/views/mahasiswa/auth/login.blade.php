@extends('layouts.guest', ['title' => 'Masuk Mahasiswa'])

@section('content')
    <form method="POST" action="{{ route('mahasiswa.login.store') }}" class="space-y-5" x-data="{ showPassword: false, submitting: false }" x-on:submit="submitting = true">
        @csrf

        @if ($errors->any())
            <x-alert>
                <ul class="space-y-1">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </x-alert>
        @endif

        <x-text-input
            label="NIM"
            name="nim"
            value="{{ old('nim') }}"
            autocomplete="username"
            autofocus
            inputmode="numeric"
            maxlength="10"
            placeholder="Masukkan NIM"
        />

        <div class="space-y-2">
            <div class="relative">
                <x-text-input
                    label="Password"
                    name="password"
                    type="password"
                    autocomplete="current-password"
                    placeholder="Masukkan password"
                    x-bind:type="showPassword ? 'text' : 'password'"
                    class="pr-28"
                />

                <button
                    type="button"
                    class="absolute bottom-2 right-2 rounded-md px-3 py-1 text-sm font-semibold text-sapphire transition hover:text-royal focus:outline-none focus:ring-2 focus:ring-royal"
                    x-on:click="showPassword = ! showPassword"
                    x-bind:aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'"
                >
                    <span x-text="showPassword ? 'Sembunyikan' : 'Tampilkan'">Tampilkan</span>
                </button>
            </div>
        </div>

        <x-primary-button type="submit" class="w-full" x-bind:disabled="submitting">
            <span x-text="submitting ? 'Memproses...' : 'Masuk'">Masuk</span>
        </x-primary-button>
    </form>
@endsection
