<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full bg-paper">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Smart Space &bull; Platform Analitik Pemanfaatan Ruang Bersama</title>

        <!-- Google Fonts: Bricolage Grotesque & Hanken Grotesk -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-full flex flex-col bg-paper font-sans text-ink antialiased">
        {{-- Navigation Bar --}}
        <header class="sticky top-0 z-40 border-b border-line bg-surface/90 px-4 backdrop-blur-md sm:px-6 lg:px-8">
            <div class="mx-auto flex max-w-6xl items-center justify-between py-4">
                <a href="{{ url('/') }}" class="flex items-center gap-3">
                    <span class="flex h-10 w-10 items-center justify-center rounded-[8px] bg-ink text-surface font-display text-lg font-bold shadow-xs">
                        S
                    </span>
                    <div>
                        <span class="font-display text-lg font-bold tracking-tight text-ink block leading-none">Smart Space</span>
                        <span class="text-[11px] font-medium text-primary/70">Politeknik Negeri Batam</span>
                    </div>
                </a>

                <nav class="flex items-center gap-3 sm:gap-4">
                    <a href="{{ route('mahasiswa.login') }}">
                        <x-button variant="secondary" size="md">
                            Masuk Mahasiswa
                        </x-button>
                    </a>
                    <a href="{{ route('admin.login') }}">
                        <x-button variant="primary" size="md">
                            Portal Admin
                        </x-button>
                    </a>
                </nav>
            </div>
        </header>

        {{-- Hero Section --}}
        <main class="flex-1">
            <section class="relative overflow-hidden px-4 pt-12 pb-20 sm:px-6 lg:px-8 lg:pt-20 lg:pb-28">
                <div class="mx-auto max-w-6xl">
                    <div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:items-center">
                        <div class="lg:col-span-7 space-y-6 text-center lg:text-left">
                            <div class="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1 text-xs font-semibold text-primary shadow-xs">
                                <span class="h-2 w-2 rounded-full bg-ok-text"></span>
                                <span>Platform Analitik Pemanfaatan Ruang Kampus</span>
                            </div>

                            <h1 class="font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl lg:text-6xl leading-[1.1]">
                                Pantau Ketersediaan &amp; Utilisasi Ruang Bersama
                            </h1>

                            <p class="text-base text-primary/80 sm:text-lg max-w-2xl mx-auto lg:mx-0">
                                Smart Space menghubungkan data jadwal resmi dengan sensor kehadiran ruangan. Menghadirkan transparansi pemakaian ruang, deteksi sesi kosong, dan analisis efisiensi fasilitas secara objektif.
                            </p>

                            <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
                                <a href="{{ route('mahasiswa.login') }}" class="w-full sm:w-auto">
                                    <x-button variant="primary" size="lg" class="w-full sm:w-auto">
                                        Cek Ruangan Mahasiswa &rarr;
                                    </x-button>
                                </a>
                                <a href="{{ route('admin.login') }}" class="w-full sm:w-auto">
                                    <x-button variant="secondary" size="lg" class="w-full sm:w-auto">
                                        Masuk sebagai Admin Fasilitas
                                    </x-button>
                                </a>
                            </div>

                            <div class="flex items-center justify-center lg:justify-start gap-6 pt-4 text-xs text-primary/70">
                                <span class="flex items-center gap-1.5">
                                    <svg class="h-4 w-4 text-ok-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                    </svg>
                                    Berbasis Hybrid AI
                                </span>
                                <span class="flex items-center gap-1.5">
                                    <svg class="h-4 w-4 text-ok-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                    </svg>
                                    Audit Terbuka &amp; Terukur
                                </span>
                                <span class="flex items-center gap-1.5">
                                    <svg class="h-4 w-4 text-ok-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                    </svg>
                                    Pencegahan Pemborosan Ruang
                                </span>
                            </div>
                        </div>

                        {{-- Mockup Visual Cards --}}
                        <div class="lg:col-span-5">
                            <div class="relative rounded-[16px] border border-line bg-surface p-6 shadow-[var(--shadow-modal)] space-y-4">
                                <div class="flex items-center justify-between border-b border-line pb-3">
                                    <span class="font-display text-sm font-semibold text-ink">Status Ruangan Terkini</span>
                                    <span class="rounded-[4px] bg-ok-bg px-2 py-0.5 text-xs font-medium text-ok-text">Live Monitoring</span>
                                </div>

                                <div class="space-y-3">
                                    <div class="rounded-[8px] border border-line bg-paper/60 p-3.5 flex items-center justify-between">
                                        <div>
                                            <p class="font-semibold text-sm text-ink">Lab RPL (TA 201)</p>
                                            <p class="text-xs text-primary/70">08.00 - 11.40 &bull; Pemrograman Web</p>
                                        </div>
                                        <x-status-badge status="sesuai_jadwal" size="sm" />
                                    </div>

                                    <div class="rounded-[8px] border border-line bg-paper/60 p-3.5 flex items-center justify-between">
                                        <div>
                                            <p class="font-semibold text-sm text-ink">Lab Jaringan (TA 202)</p>
                                            <p class="text-xs text-primary/70">13.00 - 16.40 &bull; Jaringan Komputer</p>
                                        </div>
                                        <x-status-badge status="kosong_meski_terjadwal" size="sm" />
                                    </div>

                                    <div class="rounded-[8px] border border-line bg-paper/60 p-3.5 flex items-center justify-between">
                                        <div>
                                            <p class="font-semibold text-sm text-ink">Open Space Lantai 2</p>
                                            <p class="text-xs text-primary/70">Di luar jam kuliah resmi</p>
                                        </div>
                                        <x-status-badge status="dipakai_di_luar_jadwal" size="sm" />
                                    </div>
                                </div>

                                <div class="pt-2 border-t border-line flex items-center justify-between text-xs text-primary/80">
                                    <span>Tingkat Utilisasi Rata-rata</span>
                                    <x-utilization-badge kategori="sedang" :pct="76.5" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {{-- 3 Pillars Feature Section --}}
            <section class="border-t border-line bg-surface py-16 sm:py-20">
                <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-12">
                    <div class="text-center max-w-2xl mx-auto space-y-3">
                        <p class="text-xs font-semibold uppercase tracking-wider text-primary">Fitur Utama</p>
                        <h2 class="font-display text-3xl font-semibold text-ink sm:text-4xl">Solusi Terpadu Pengelolaan Ruang</h2>
                        <p class="text-sm text-primary/80">Mendukung keputusan berbasis bukti (*evidence-based decision*) bagi pengelola fasilitas kampus dan kenyamanan mahasiswa.</p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="rounded-[12px] border border-line bg-paper/50 p-6 space-y-3">
                            <div class="rounded-[8px] bg-ok-bg p-3 text-ok-text w-fit">
                                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <h3 class="font-display text-lg font-semibold text-ink">Sistem Pakar Otomatis</h3>
                            <p class="text-xs text-primary/80 leading-relaxed">
                                Logika inferensi deterministik mengelompokkan status pemakaian ruang ke dalam 3 kelas standar dengan penjelasan logis (*explanation facility*).
                            </p>
                        </div>

                        <div class="rounded-[12px] border border-line bg-paper/50 p-6 space-y-3">
                            <div class="rounded-[8px] bg-warn-bg p-3 text-warn-text w-fit">
                                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                                </svg>
                            </div>
                            <h3 class="font-display text-lg font-semibold text-ink">Prediksi Risiko Kosong</h3>
                            <p class="text-xs text-primary/80 leading-relaxed">
                                Model Machine Learning memberikan peringatan dini sesi berisiko tidak digunakan, memungkinkan pengalihan ruangan secara cepat.
                            </p>
                        </div>

                        <div class="rounded-[12px] border border-line bg-paper/50 p-6 space-y-3">
                            <div class="rounded-[8px] bg-surface p-3 text-primary w-fit border border-line">
                                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                                </svg>
                            </div>
                            <h3 class="font-display text-lg font-semibold text-ink">Portal Mobile Mahasiswa</h3>
                            <p class="text-xs text-primary/80 leading-relaxed">
                                Cek ketersediaan ruang kelas dan open space secara mudah dari gawai tanpa perlu berkeliling gedung kampus.
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        {{-- Footer --}}
        <footer class="border-t border-line bg-surface py-8 text-xs text-primary/70">
            <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
                <p>&copy; 2026 Smart Space Analytics Platform &bull; PBLIF3-PD08</p>
                <p>Teknik Informatika &bull; Politeknik Negeri Batam</p>
            </div>
        </footer>
    </body>
</html>
