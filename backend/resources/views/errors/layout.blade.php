<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full bg-paper">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@yield('title') &bull; {{ config('app.name', 'Smart Space') }}</title>

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-full flex flex-col items-center justify-center bg-paper px-4 py-12 text-ink font-sans antialiased sm:px-6 lg:px-8">
        <div class="w-full max-w-lg text-center space-y-6">
            <div class="inline-flex items-center gap-2 mb-2">
                <span class="flex h-10 w-10 items-center justify-center rounded-[8px] bg-ink text-surface font-display text-lg font-bold shadow-xs">
                    S
                </span>
                <span class="font-display text-xl font-bold tracking-tight text-ink">Smart Space</span>
            </div>

            <div class="rounded-[16px] border border-line bg-surface p-8 shadow-[var(--shadow-modal)] sm:p-10 space-y-5">
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-paper border border-line text-primary" aria-hidden="true">
                    @yield('icon')
                </div>

                <div class="space-y-2">
                    <p class="font-display text-4xl font-bold text-primary tabular-nums">@yield('code')</p>
                    <h1 class="font-display text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
                        @yield('message')
                    </h1>
                </div>

                <p class="text-sm text-primary/80 leading-relaxed max-w-md mx-auto">
                    @yield('description')
                </p>

                <div class="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                    @yield('actions')
                </div>
            </div>

            <p class="text-xs text-primary/70">
                &copy; {{ date('Y') }} Smart Space Analytics Platform &bull; Politeknik Negeri Batam
            </p>
        </div>
    </body>
</html>
