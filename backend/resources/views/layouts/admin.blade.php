<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ $title ?? 'Admin' }} | {{ config('app.name', 'Smart Space') }}</title>

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-screen bg-swan font-sans text-royal">
        <div class="min-h-screen">
            <header class="border-b border-shellstone bg-royal text-swan">
                <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
                    <nav class="flex items-center gap-6">
                        <a href="{{ route('admin.dashboard') }}" class="text-lg font-semibold">
                            Smart Space Admin
                        </a>
                        <a href="{{ route('admin.rooms.index') }}" class="text-sm font-semibold hover:underline">
                            Ruangan
                        </a>
                    </nav>

                    <form method="POST" action="{{ route('admin.logout') }}">
                        @csrf
                        <x-primary-button type="submit" variant="dark">
                            Keluar
                        </x-primary-button>
                    </form>
                </div>
            </header>

            <main class="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
                @yield('content')
            </main>
        </div>

        <script>
            window.addEventListener('pageshow', function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });
        </script>
    </body>
</html>