@extends('layouts.admin', ['title' => 'Dashboard'])

@section('content')
    <div class="space-y-6">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
                <h1 class="text-2xl font-bold font-display text-ink tracking-tight">Dashboard Admin</h1>
                <p class="text-sm text-ink/70 mt-1">Selamat datang, <span class="font-semibold text-ink">{{ auth('admin')->user()->nama }}</span>. Pantau pemanfaatan ruang kampus secara real-time.</p>
            </div>
            <div class="flex items-center gap-3">
                <a href="{{ route('admin.rooms.index') }}" class="inline-flex items-center justify-center gap-2 rounded-kontrol bg-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-ink focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    Data Ruangan
                </a>
            </div>
        </div>

        <!-- Metric Cards Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <x-stat-card
                title="Sesuai Jadwal"
                value="-"
                description="Ruangan aktif terpakai perkuliahan"
                trend="Normal"
                trendType="up"
            />
            <x-stat-card
                title="Kosong Terjadwal"
                value="-"
                description="Potensi anomali ruang kosong"
                trend="Perhatian"
                trendType="down"
            />
            <x-stat-card
                title="Pakai Luar Jadwal"
                value="-"
                description="Ruang dipakai tanpa jadwal aktif"
                trend="Perlu cek"
                trendType="down"
            />
            <x-stat-card
                title="Total Ruangan"
                value="-"
                description="Ruangan terdaftar di sistem"
            />
        </div>

        <!-- Quick Access Section -->
        <div class="rounded-panel border border-line bg-surface p-6 shadow-xs">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-base font-semibold text-ink">Ringkasan Sistem</h2>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-chip text-xs font-medium bg-ok-bg text-ok-text">
                    <span class="w-1.5 h-1.5 rounded-full bg-ok-text mr-1.5 animate-pulse"></span>
                    Sistem Aktif
                </span>
            </div>
            <p class="text-sm text-ink/70">
                Sistem Smart Space memonitor okupansi dan jadwal ruangan tanpa menggunakan perangkat IoT, kamera, atau kontrol fisik. Seluruh anomali dihitung berdasarkan perbandingan estimasi okupansi terhadap jadwal akademik resmi.
            </p>
            <div class="mt-4 pt-4 border-t border-line flex flex-wrap gap-4">
                <a href="{{ route('admin.rooms.index') }}" class="text-sm font-medium text-primary hover:text-ink focus:outline-none focus:underline flex items-center gap-1 min-h-[44px]">
                    Kelola Ruangan &rarr;
                </a>
            </div>
        </div>
    </div>
@endsection
