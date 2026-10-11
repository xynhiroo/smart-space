<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ config('app.name', 'Smart Space') }}</title>

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-screen bg-swan font-sans text-royal">
        <main class="flex min-h-screen items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
            <div class="w-full max-w-md">
                <div class="mb-8 text-center">
                    <p class="text-sm font-semibold uppercase tracking-[0.24em] text-sapphire">Smart Space</p>
                    <h1 class="mt-3 text-2xl font-semibold text-royal sm:text-3xl">{{ $title ?? 'Masuk Mahasiswa' }}</h1>
                </div>

                <section class="rounded-lg border border-shellstone bg-white p-6 shadow-sm sm:p-8">
                    {{ $slot }}
                </section>
            </div>
        </main>
    </body>
</html>
