@props([
    'variant' => 'primary', // primary | secondary | danger | ghost
    'size' => 'md',        // sm | md | lg
    'type' => 'button',
    'loading' => false,
    'icon' => null,
])

@php
    $baseClasses = 'inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-[8px] focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary focus-visible:ring-offset-paper disabled:opacity-50 disabled:cursor-not-allowed select-none';

    $sizeClasses = [
        'sm' => 'min-h-[36px] px-3 py-1.5 text-xs gap-1.5',
        'md' => 'min-h-[44px] px-4 py-2 text-sm gap-2', // Target sentuh minimal 44px (IMK/WCAG)
        'lg' => 'min-h-[48px] px-6 py-2.5 text-base gap-2.5',
    ][$size] ?? 'min-h-[44px] px-4 py-2 text-sm gap-2';

    // Map legacy variants for backward compatibility
    $normalizedVariant = match($variant) {
        'default', 'primary' => 'primary',
        'dark', 'secondary' => 'secondary',
        'danger' => 'danger',
        'ghost' => 'ghost',
        default => 'primary',
    };

    $variantClasses = [
        'primary' => 'bg-primary text-surface hover:bg-ink active:bg-ink shadow-sm',
        'secondary' => 'bg-surface text-ink border border-line hover:bg-paper active:bg-line/40 shadow-sm',
        'danger' => 'bg-error text-surface hover:bg-bad-text active:bg-bad-text shadow-sm',
        'ghost' => 'bg-transparent text-primary hover:bg-line/30 active:bg-line/50',
    ][$normalizedVariant];

    $classes = "{$baseClasses} {$sizeClasses} {$variantClasses}";
@endphp

<button
    type="{{ $type }}"
    {{ $attributes->merge(['class' => $classes]) }}
    @if($loading) disabled aria-busy="true" @endif
>
    @if ($loading)
        <svg class="animate-spin -ml-0.5 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    @elseif ($icon)
        <span class="inline-flex shrink-0 items-center justify-center text-current" aria-hidden="true">
            {!! $icon !!}
        </span>
    @endif

    <span>{{ $slot }}</span>
</button>
