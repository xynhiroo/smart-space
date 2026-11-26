@props([
    'title' => 'Belum ada data',
    'description' => 'Data untuk tampilan ini belum tersedia saat ini.',
    'actionLabel' => null,
    'actionUrl' => null,
])

<div {{ $attributes->merge(['class' => 'flex flex-col items-center justify-center rounded-[12px] border border-dashed border-line bg-surface/80 p-8 text-center sm:p-12']) }}>
    <div class="rounded-full bg-paper p-4 text-primary" aria-hidden="true">
        @if (isset($icon))
            {{ $icon }}
        @else
            <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
        @endif
    </div>

    <h3 class="mt-4 font-display text-lg font-semibold text-ink">
        {{ $title }}
    </h3>

    <p class="mt-1.5 max-w-sm text-sm text-primary/80">
        {{ $description }}
    </p>

    @if ($actionLabel && $actionUrl)
        <div class="mt-6">
            <a href="{{ $actionUrl }}">
                <x-button variant="primary" size="md">
                    {{ $actionLabel }}
                </x-button>
            </a>
        </div>
    @elseif (isset($action))
        <div class="mt-6">
            {{ $action }}
        </div>
    @endif
</div>
