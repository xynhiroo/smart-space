@extends('layouts.guest', ['title' => 'Masuk Mahasiswa'])

@section('content')
    @php
        $retryAfter = (int) session('retry_after', 0);
    @endphp

    <form
        method="POST"
        action="{{ route('mahasiswa.login.store') }}"
        class="space-y-5"
        x-data="{
            showPassword: false,
            submitting: false,
            retryAfter: {{ $retryAfter }},
            remaining: {{ $retryAfter }},
            deadline: 0,
            timer: null,
            statusMessage: '',
            statusTimeout: null,

            init() {
                if (this.retryAfter > 0) {
                    this.deadline = Date.now() + (this.retryAfter * 1000);
                    this.updateCountdown();
                    this.timer = setInterval(() => {
                        this.updateCountdown();
                    }, 1000);
                }
            },

            updateCountdown() {
                const diff = Math.max(0, Math.ceil((this.deadline - Date.now()) / 1000));
                this.remaining = diff;

                if (diff <= 0) {
                    this.clearTimer();
                    this.statusMessage = 'Silakan coba lagi.';
                    this.$nextTick(() => {
                        document.getElementById('password')?.focus();
                    });
                    this.statusTimeout = setTimeout(() => {
                        this.statusMessage = '';
                    }, 4000);
                }
            },

            clearTimer() {
                if (this.timer) {
                    clearInterval(this.timer);
                    this.timer = null;
                }
            },

            destroy() {
                this.clearTimer();
                if (this.statusTimeout) {
                    clearTimeout(this.statusTimeout);
                }
            }
        }"
        x-on:submit="submitting = true"
    >
        @csrf

        <div
            x-show="statusMessage"
            x-transition
            role="status"
            class="rounded-md border border-shellstone bg-white px-4 py-3 text-sm text-royal"
            style="display: none;"
        >
            <span x-text="statusMessage"></span>
        </div>

        @if ($errors->any())
            @if ($retryAfter > 0)
                <div x-show="remaining > 0">
                    <x-alert>
                        <p>
                            <span>Terlalu banyak percobaan. Coba lagi dalam </span><span aria-hidden="true" x-text="remaining">{{ $retryAfter }}</span><span class="sr-only">{{ $retryAfter }}</span><span> detik.</span>
                        </p>
                    </x-alert>
                </div>
            @else
                <x-alert>
                    <ul class="space-y-1">
                        @foreach ($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </x-alert>
            @endif
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
                    id="password"
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

        <x-primary-button type="submit" class="w-full" x-bind:disabled="submitting || remaining > 0">
            <span x-text="submitting ? 'Memproses...' : 'Masuk'">Masuk</span>
        </x-primary-button>
    </form>
@endsection
