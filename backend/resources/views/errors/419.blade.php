@extends('errors.layout')

@section('code', '419')
@section('title', 'Sesi Telah Kedaluwarsa')

@section('illustration')
    <svg class="w-16 h-16 text-warn-text" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
@endsection

@section('heading', 'Sesi Telah Kedaluwarsa')
@section('message', 'Halaman ini telah terbuka terlalu lama sehingga token keamanan atau sesi Anda telah berakhir. Silakan muat ulang halaman atau masuk kembali.')

@section('action')
    <button onclick="window.location.reload()" class="inline-flex items-center justify-center px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-kontrol hover:bg-ink focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
        Muat Ulang Halaman
    </button>
@endsection
