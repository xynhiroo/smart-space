@extends('layouts.guest', ['title' => 'Masuk Admin', 'subtitle' => 'Portal Pengelola Fasilitas & Analitik Ruang'])

@section('content')
    @php
        $retryAfter = (int) session('retry_after', 0);
    @endphp

    <form
        method="POST"
        action="{{ route('admin.login.store') }}"
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

        {{-- Rate limit countdown status message --}}
        <div
            x-show="statusMessage"
            x-transition
            role="status"
            class="rounded-[8px] border border-ok-text/30 bg-ok-bg px-4 py-3 text-sm font-medium text-ok-text"
            style="display: none;"
        >
            <span x-text="statusMessage"></span>
        </div>

        @if ($errors->any())
            @if ($retryAfter > 0)
                <div x-show="remaining > 0">
                    <x-alert>
                        <p class="flex items-center gap-2">
                            <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <span>Terlalu banyak percobaan. Coba lagi dalam </span><span aria-hidden="true" x-text="remaining">{{ $retryAfter }}</span><span class="sr-only">{{ $retryAfter }}</span><span> detik.</span>
                        </p>
                    </x-alert>
                </div>
            @else
                <x-alert>
                    <ul class="space-y-1">
                        @foreach ($errors->all() as $error)
                            <li class="flex items-center gap-1.5">
                                <span class="h-1.5 w-1.5 rounded-full bg-error shrink-0"></span>
                                <span>{{ $error }}</span>
                            </li>
                        @endforeach
                    </ul>
                </x-alert>
            @endif
        @endif

        <x-text-input
            label="Email"
            name="email"
            type="email"
            value="{{ old('email') }}"
            autocomplete="username"
            placeholder="admin@smartspace.polibatam.ac.id"
            required
            autofocus
        />

        <div class="space-y-1.5">
            <div class="flex items-center justify-between">
                <label for="password" class="block text-sm font-medium text-ink">
                    Password
                    <span class="text-error" aria-hidden="true">*</span>
                    <span class="sr-only">(wajib diisi)</span>
                </label>
            </div>

            <div class="relative">
                <input
                    id="password"
                    name="password"
                    :type="showPassword ? 'text' : 'password'"
                    autocomplete="current-password"
                    required
                    placeholder="Masukkan password admin"
                    aria-invalid="{{ $errors->has('password') ? 'true' : 'false' }}"
                    class="block w-full min-h-[44px] rounded-[8px] border bg-surface px-3.5 py-2.5 pr-11 text-sm text-ink placeholder:text-primary/50 transition duration-150 focus:outline-none focus:ring-2 disabled:bg-paper disabled:text-ink/50 {{ $errors->has('password') ? 'border-error text-error focus:ring-error/20' : 'border-line focus:border-primary focus:ring-primary/20' }}"
                >

                <button
                    type="button"
                    class="absolute inset-y-0 right-0 flex items-center px-3 text-primary/70 hover:text-ink focus:outline-none focus:ring-2 focus:ring-primary rounded-r-[8px] min-h-[44px]"
                    @click="showPassword = !showPassword"
                    :aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'"
                >
                    <svg x-show="!showPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg x-show="showPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display: none;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                    </svg>
                </button>
            </div>

            @error('password')
                <p class="text-xs font-medium text-error mt-1">{{ $message }}</p>
            @enderror
        </div>

        <div class="pt-2">
            <x-button
                type="submit"
                variant="primary"
                size="md"
                class="w-full justify-center text-base"
                ::loading="submitting"
            >
                Masuk ke Panel Admin
            </x-button>
        </div>
    </form>
@endsection
