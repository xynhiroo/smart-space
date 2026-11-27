<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full bg-paper">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ $title ?? 'Ketersediaan Ruang' }} | {{ config('app.name', 'Smart Space') }}</title>

        <!-- Google Fonts: Bricolage Grotesque & Hanken Grotesk -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-full flex flex-col bg-paper font-sans text-ink antialiased">
        {{-- Header Mobile-First --}}
        <header class="sticky top-0 z-30 border-b border-line bg-surface/95 px-4 backdrop-blur-xs sm:px-6 lg:px-8">
            <div class="mx-auto flex max-w-5xl items-center justify-between gap-4 py-3 sm:py-4">
                <a href="{{ route('mahasiswa.home') }}" class="flex items-center gap-2.5">
                    <span class="flex h-9 w-9 items-center justify-center rounded-[8px] bg-primary text-surface font-display text-base font-bold shadow-xs">
                        S
                    </span>
                    <div>
                        <span class="font-display text-base font-bold text-ink block leading-none">Smart Space</span>
                        <span class="text-[11px] font-medium text-primary/70">Ketersediaan Ruangan</span>
                    </div>
                </a>

                <div class="flex items-center gap-3">
                    @auth('mahasiswa')
                        <div class="hidden sm:flex items-center gap-2 rounded-[8px] bg-paper px-3 py-1.5 border border-line text-xs font-medium text-ink">
                            <span class="text-primary/70">NIM:</span>
                            <span class="font-semibold tabular-nums">{{ auth('mahasiswa')->user()->nim }}</span>
                        </div>

                        <form method="POST" action="{{ route('mahasiswa.logout') }}">
                            @csrf
                            <x-button type="submit" variant="secondary" size="sm">
                                Keluar
                            </x-button>
                        </form>
                    @else
                        <a href="{{ route('mahasiswa.login') }}">
                            <x-button variant="primary" size="sm">
                                Masuk
                            </x-button>
                        </a>
                    @endauth
                </div>
            </div>
        </header>

        {{-- Main Container (Mobile-first 360px up to desktop) --}}
        <main class="flex-1 mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 lg:px-8">
            @yield('content')
        </main>

        {{-- Simple footer --}}
        <footer class="border-t border-line bg-surface/60 py-6 text-center text-xs text-primary/70">
            <div class="mx-auto max-w-5xl px-4">
                <p>Smart Space Analytics Platform &bull; Teknik Informatika Politeknik Negeri Batam</p>
            </div>
        </footer>

        <x-toast />

        <script>
            window.addEventListener('pageshow', function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });
        </script>
    </body>
</html>
