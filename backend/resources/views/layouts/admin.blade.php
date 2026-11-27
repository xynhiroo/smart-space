<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full bg-paper">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ $title ?? 'Admin' }} | {{ config('app.name', 'Smart Space') }}</title>

        <!-- Google Fonts: Bricolage Grotesque (SemiBold) & Hanken Grotesk per Modern Web Guidance -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600&family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body
        class="h-full bg-paper font-sans text-ink antialiased"
        x-data="{ sidebarOpen: false }"
        @keydown.escape.window="sidebarOpen = false"
    >
        <div class="min-h-full flex flex-col lg:flex-row">
            {{-- Mobile Sidebar Backdrop --}}
            <div
                x-show="sidebarOpen"
                x-transition:enter="transition-opacity ease-linear duration-200"
                x-transition:enter-start="opacity-0"
                x-transition:enter-end="opacity-100"
                x-transition:leave="transition-opacity ease-linear duration-200"
                x-transition:leave-start="opacity-100"
                x-transition:leave-end="opacity-0"
                class="fixed inset-0 z-40 bg-ink/50 backdrop-blur-xs lg:hidden"
                @click="sidebarOpen = false"
                style="display: none;"
                aria-hidden="true"
            ></div>

            {{-- Sidebar --}}
            <aside
                :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
                class="fixed inset-y-0 left-0 z-50 w-72 flex-col justify-between border-r border-line bg-surface p-6 shadow-md transition-transform duration-200 ease-in-out lg:static lg:flex lg:shadow-none shrink-0"
                aria-label="Navigasi Utama Admin"
            >
                <div class="space-y-6">
                    {{-- Logo & Brand --}}
                    <div class="flex items-center justify-between border-b border-line pb-4">
                        <a href="{{ route('admin.dashboard') }}" class="flex items-center gap-3">
                            <span class="flex h-10 w-10 items-center justify-center rounded-[8px] bg-ink text-surface font-display text-lg font-bold shadow-xs">
                                S
                            </span>
                            <div>
                                <span class="font-display text-lg font-bold tracking-tight text-ink block leading-none">Smart Space</span>
                                <span class="text-[11px] font-medium tracking-wider uppercase text-primary/70">Panel Admin</span>
                            </div>
                        </a>
                        <button
                            type="button"
                            class="rounded-[8px] p-2 text-primary lg:hidden hover:bg-paper focus:outline-none focus:ring-2 focus:ring-primary min-h-[44px] min-w-[44px] flex items-center justify-center"
                            @click="sidebarOpen = false"
                            aria-label="Tutup menu navigasi"
                        >
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>

                    {{-- 6 Menu Sidebar Sesuai Kartu SS3-01 --}}
                    <nav class="space-y-1.5" aria-label="Menu Admin">
                        @php
                            $currentRoute = request()->route()?->getName();
                            $menus = [
                                [
                                    'name' => 'Dashboard',
                                    'route' => 'admin.dashboard',
                                    'url' => route('admin.dashboard'),
                                    'active' => request()->routeIs('admin.dashboard*'),
                                    'icon' => '<svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>',
                                ],
                                [
                                    'name' => 'Kelola Ruangan',
                                    'route' => 'admin.rooms.index',
                                    'url' => route('admin.rooms.index'),
                                    'active' => request()->routeIs('admin.rooms*'),
                                    'icon' => '<svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>',
                                ],
                                [
                                    'name' => 'Kelola Jadwal',
                                    'route' => 'admin.schedules.index',
                                    'url' => Route::has('admin.schedules.index') ? route('admin.schedules.index') : '#',
                                    'active' => request()->routeIs('admin.schedules*'),
                                    'badge' => 'Sprint 2',
                                    'icon' => '<svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
                                ],
                                [
                                    'name' => 'Ambang Batas',
                                    'route' => 'admin.thresholds.index',
                                    'url' => Route::has('admin.thresholds.index') ? route('admin.thresholds.index') : '#',
                                    'active' => request()->routeIs('admin.thresholds*'),
                                    'badge' => 'Sprint 2',
                                    'icon' => '<svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>',
                                ],
                                [
                                    'name' => 'Laporan',
                                    'route' => 'admin.reports.index',
                                    'url' => Route::has('admin.reports.index') ? route('admin.reports.index') : '#',
                                    'active' => request()->routeIs('admin.reports*'),
                                    'badge' => 'Sprint 2',
                                    'icon' => '<svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
                                ],
                                [
                                    'name' => 'Akun',
                                    'route' => 'admin.accounts.index',
                                    'url' => Route::has('admin.accounts.index') ? route('admin.accounts.index') : '#',
                                    'active' => request()->routeIs('admin.accounts*'),
                                    'badge' => 'Sprint 2',
                                    'icon' => '<svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>',
                                ],
                            ];
                        @endphp

                        @foreach ($menus as $item)
                            <a
                                href="{{ $item['url'] }}"
                                class="flex items-center justify-between rounded-[8px] px-3.5 py-2.5 text-sm font-medium transition min-h-[44px] {{ $item['active'] ? 'bg-primary text-surface font-semibold shadow-xs' : 'text-ink/80 hover:bg-paper hover:text-ink' }}"
                                @if($item['active']) aria-current="page" @endif
                            >
                                <div class="flex items-center gap-3">
                                    {!! $item['icon'] !!}
                                    <span>{{ $item['name'] }}</span>
                                </div>
                                @if (isset($item['badge']) && !$item['active'])
                                    <span class="rounded-[4px] bg-paper px-2 py-0.5 text-[10px] font-medium text-primary/70 border border-line/60">
                                        {{ $item['badge'] }}
                                    </span>
                                @endif
                            </a>
                        @endforeach
                    </nav>
                </div>

                {{-- Admin Profile & Logout --}}
                <div class="border-t border-line pt-4 space-y-3">
                    <div class="flex items-center gap-3 px-2">
                        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-paper font-semibold text-primary border border-line">
                            {{ substr(auth('admin')->user()->name ?? 'A', 0, 1) }}
                        </div>
                        <div class="min-w-0 flex-1">
                            <p class="truncate text-xs font-semibold text-ink">{{ auth('admin')->user()->name ?? 'Administrator' }}</p>
                            <p class="truncate text-[11px] text-primary/70">{{ auth('admin')->user()->email ?? 'admin@smartspace' }}</p>
                        </div>
                    </div>

                    <form method="POST" action="{{ route('admin.logout') }}">
                        @csrf
                        <x-button type="submit" variant="secondary" size="md" class="w-full justify-center">
                            Keluar
                        </x-button>
                    </form>
                </div>
            </aside>

            {{-- Main Content Column --}}
            <div class="flex-1 flex flex-col min-w-0">
                {{-- Top Bar --}}
                <header class="sticky top-0 z-30 flex min-h-[64px] items-center justify-between border-b border-line bg-surface/95 px-4 backdrop-blur-xs sm:px-6 lg:px-8">
                    <div class="flex items-center gap-4">
                        <button
                            type="button"
                            class="rounded-[8px] p-2 text-primary lg:hidden hover:bg-paper focus:outline-none focus:ring-2 focus:ring-primary min-h-[44px] min-w-[44px] flex items-center justify-center"
                            @click="sidebarOpen = true"
                            aria-label="Buka menu navigasi"
                        >
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                            </svg>
                        </button>
                        <h1 class="font-display text-xl font-semibold text-ink sm:text-2xl">
                            {{ $title ?? 'Smart Space Admin' }}
                        </h1>
                    </div>

                    <div class="flex items-center gap-3">
                        <span class="hidden sm:inline-flex items-center rounded-[4px] bg-paper px-2.5 py-1 text-xs font-medium text-primary border border-line">
                            <span class="mr-1.5 h-2 w-2 rounded-full bg-ok-text"></span>
                            Sistem Aktif
                        </span>
                    </div>
                </header>

                {{-- Page Main Content --}}
                <main class="flex-1 p-4 sm:p-6 lg:p-8">
                    <div class="mx-auto max-w-7xl space-y-6">
                        @yield('content')
                    </div>
                </main>
            </div>
        </div>

        {{-- Toast notification flash --}}
        <x-toast />

        {{-- Prevent-back-history page reload script --}}
        <script>
            window.addEventListener('pageshow', function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });
        </script>
    </body>
</html>
