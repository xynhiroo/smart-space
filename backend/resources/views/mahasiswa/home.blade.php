@extends('layouts.app')

@section('content')
    <div class="space-y-6">
        <!-- Student Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-line">
            <div>
                <div class="inline-flex items-center px-2.5 py-1 rounded-chip text-xs font-semibold bg-primary/10 text-primary mb-2">
                    NIM: {{ auth('mahasiswa')->user()->nim }}
                </div>
                <h1 class="text-2xl font-bold font-display text-ink tracking-tight">Status Ruangan</h1>
                <p class="text-sm text-ink/70 mt-0.5">Cek ketersediaan ruang belajar, ruang kelas, dan laboratorium secara real-time.</p>
            </div>
            <div>
                <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-kontrol text-xs font-medium bg-ok-bg text-ok-text">
                    <span class="w-2 h-2 rounded-full bg-ok-text"></span>
                    Data Diperbarui Terus-Menerus
                </span>
            </div>
        </div>

        <!-- Room Status Placeholder / Stream Container -->
        <div class="rounded-panel border border-line bg-surface p-6 shadow-xs text-center">
            <div class="max-w-md mx-auto py-8">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-paper flex items-center justify-center text-primary">
                    <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-ink font-display">Status Ketersediaan Ruangan</h3>
                <p class="text-sm text-ink/70 mt-2">
                    Status ketersediaan ruangan akan tampil di sini secara real-time saat modul jadwal dan estimasi okupansi terhubung.
                </p>
                <div class="mt-6 flex items-center justify-center gap-3">
                    <x-status-badge status="kosong" />
                    <x-status-badge status="terisi" />
                    <x-status-badge status="tidak_tersedia" />
                </div>
            </div>
        </div>
    </div>
@endsection
