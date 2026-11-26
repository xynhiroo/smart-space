@props([
    'type' => 'error',
])

@php
    $classes = [
        'error' => 'border-error/30 bg-bad-bg text-bad-text',
        'warning' => 'border-warn-text/30 bg-warn-bg text-warn-text',
        'success' => 'border-ok-text/30 bg-ok-bg text-ok-text',
        'info' => 'border-primary/30 bg-primary/5 text-ink',
    ][$type] ?? 'border-line bg-white text-ink';
@endphp

<div {{ $attributes->merge(['class' => 'rounded-kontrol border px-4 py-3 text-sm flex items-start gap-3 '.$classes, 'role' => 'alert']) }}>
    @if ($type === 'error')
        <svg class="w-5 h-5 flex-shrink-0 text-error mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
    @endif
    <div class="flex-1">
        {{ $slot }}
    </div>
</div>
