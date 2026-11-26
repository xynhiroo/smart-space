<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full bg-paper">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ $title ?? 'Masuk' }} | {{ config('app.name', 'Smart Space') }}</title>

        <!-- Google Fonts: Bricolage Grotesque & Hanken Grotesk -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-full flex flex-col bg-paper font-sans text-ink antialiased">
        <main class="flex flex-1 items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
            <div class="w-full max-w-md space-y-6">
                <div class="text-center space-y-2">
                    <a href="{{ url('/') }}" class="inline-flex items-center gap-2 mb-2 focus:outline-none focus:ring-2 focus:ring-primary rounded-[8px] p-1">
                        <span class="flex h-10 w-10 items-center justify-center rounded-[8px] bg-ink text-surface font-display text-lg font-bold shadow-xs">
                            S
                        </span>
                        <span class="font-display text-xl font-bold tracking-tight text-ink">Smart Space</span>
                    </a>
                    <h1 class="font-display text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
                        {{ $title ?? 'Masuk' }}
                    </h1>
                    @if (isset($subtitle))
                        <p class="text-sm text-primary/80">{{ $subtitle }}</p>
                    @endif
                </div>

                <section class="rounded-[12px] border border-line bg-surface p-6 shadow-[var(--shadow-modal)] sm:p-8">
                    @yield('content')
                </section>

                <div class="text-center text-xs text-primary/70">
                    <a href="{{ url('/') }}" class="hover:text-ink hover:underline">
                        &larr; Kembali ke Beranda
                    </a>
                </div>
            </div>
        </main>

        <x-toast />
    </body>
</html>
