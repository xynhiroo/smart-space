@extends('errors.layout')

@section('code', '404')
@section('title', 'Halaman Tidak Ditemukan')

@section('illustration')
    <svg class="w-16 h-16 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
@endsection

@section('heading', 'Halaman Tidak Ditemukan')
@section('message', 'Alamat atau halaman yang Anda cari mungkin telah dipindahkan, dihapus, atau tautan yang Anda masukkan keliru. Silakan periksa kembali URL yang Anda tuju.')

@section('action')
    <a href="{{ url('/') }}" class="inline-flex items-center justify-center px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-kontrol hover:bg-ink focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
        Kembali ke Beranda
    </a>
@endsection
