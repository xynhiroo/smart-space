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
        <div class="min-h-screen">
            <header class="border-b border-shellstone bg-royal text-swan">
                <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
                    <a href="{{ Route::has('mahasiswa.home') ? route('mahasiswa.home') : url('/') }}" class="text-lg font-semibold">
                        Smart Space
                    </a>

                    @if (Route::has('mahasiswa.logout'))
                        <form method="POST" action="{{ route('mahasiswa.logout') }}">
                            @csrf
                            <x-primary-button type="submit" variant="dark">
                                Keluar
                            </x-primary-button>
                        </form>
                    @endif
                </div>
            </header>

            <main class="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
                {{ $slot }}
            </main>
        </div>
    </body>
</html>
