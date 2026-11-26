@extends('errors.layout')

@section('code', '500')
@section('title', 'Terjadi Kendala Server')

@section('illustration')
    <svg class="w-16 h-16 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
@endsection

@section('heading', 'Terjadi Kendala Server')
@section('message', 'Sistem kami sedang mengalami gangguan internal tak terduga. Tim pengelola sedang menelusuri kendala ini. Silakan coba kembali dalam beberapa saat.')

@section('action')
    <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
        <button onclick="window.location.reload()" class="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-kontrol hover:bg-ink focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
            Coba Lagi
        </button>
        <a href="{{ url('/') }}" class="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2.5 border border-line text-ink bg-white text-sm font-medium rounded-kontrol hover:bg-paper focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
            Ke Beranda
        </a>
    </div>
@endsection
