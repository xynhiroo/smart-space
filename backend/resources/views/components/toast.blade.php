@props([
    'type' => 'success', // success | error | info
    'message' => null,
])

@php
    $type = session('status_type', $type);
    $text = $message ?? session('status') ?? session('success') ?? session('error');

    $isError = $type === 'error' || session()->has('error') || $errors->any();
    $config = $isError ? [
        'bg' => 'bg-surface border-error/40 text-ink shadow-[var(--shadow-toast)]',
        'icon' => '<div class="rounded-full bg-bad-bg p-1 text-bad-text"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></div>',
        'role' => 'alert',
    ] : [
        'bg' => 'bg-surface border-ok-text/40 text-ink shadow-[var(--shadow-toast)]',
        'icon' => '<div class="rounded-full bg-ok-bg p-1 text-ok-text"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg></div>',
        'role' => 'status',
    ];
@endphp

@if ($text)
    <div
        x-data="{ show: true }"
        x-show="show"
        x-transition:enter="transition ease-out duration-300 transform"
        x-transition:enter-start="opacity-0 translate-y-2 sm:translate-y-0 sm:translate-x-2"
        x-transition:enter-end="opacity-100 translate-y-0 sm:translate-x-0"
        x-transition:leave="transition ease-in duration-200"
        x-transition:leave-start="opacity-100"
        x-transition:leave-end="opacity-0"
        x-init="setTimeout(() => show = false, 5000)"
        role="{{ $config['role'] }}"
        aria-live="polite"
        class="fixed bottom-5 right-5 z-50 flex max-w-sm items-center gap-3 rounded-[8px] border p-4 {{ $config['bg'] }}"
    >
        <span class="shrink-0">{!! $config['icon'] !!}</span>
        <div class="text-sm font-medium flex-1">
            {{ $text }}
        </div>
        <button
            type="button"
            class="rounded-[4px] p-1 text-primary/70 hover:bg-paper hover:text-ink focus:outline-none focus:ring-2 focus:ring-primary"
            @click="show = false"
            aria-label="Tutup notifikasi"
        >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>
    </div>
@endif
