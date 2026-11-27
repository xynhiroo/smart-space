@extends('errors.layout')

@section('code', '403')
@section('title', 'Akses Ditolak')

@section('illustration')
    <svg class="w-16 h-16 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m0 0v2m0-2h2m-2 0H10m4-11a4 4 0 00-8 0v4h8V6zM6 10h12a2 2 0 012 2v7a2 2 0 01-2 2H6a2 2 0 01-2-2v-7a2 2 0 012-2z" />
    </svg>
@endsection

@section('heading', 'Akses Ditolak')
@section('message', 'Anda tidak memiliki hak akses atau izin yang memadai untuk membuka halaman ini. Silakan periksa akun Anda atau hubungi Administrator sistem.')

@section('action')
    <a href="{{ url('/') }}" class="inline-flex items-center justify-center px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-kontrol hover:bg-ink focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
        Kembali ke Beranda
    </a>
@endsection
