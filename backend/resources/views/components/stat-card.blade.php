@props([
    'title',
    'value',
    'subtitle' => null,
    'icon' => null,
    'trend' => null, // ['label' => '+4%', 'positive' => true/false]
])

<div {{ $attributes->merge(['class' => 'rounded-[12px] border border-line bg-surface p-5 shadow-sm transition hover:shadow-md']) }}>
    <div class="flex items-start justify-between gap-3">
        <p class="text-xs font-medium uppercase tracking-wider text-primary/80">{{ $title }}</p>
        @if ($icon)
            <div class="rounded-[8px] bg-paper p-2 text-primary" aria-hidden="true">
                {!! $icon !!}
            </div>
        @endif
    </div>

    <div class="mt-3 flex items-baseline gap-2">
        <p class="font-display text-3xl font-semibold text-ink tabular-nums tracking-tight">{{ $value }}</p>
        @if ($trend)
            <span class="inline-flex items-center text-xs font-semibold {{ ($trend['positive'] ?? true) ? 'text-ok-text' : 'text-bad-text' }}">
                {{ $trend['label'] ?? '' }}
            </span>
        @endif
    </div>

    @if ($subtitle)
        <p class="mt-1 text-xs text-primary/70">{{ $subtitle }}</p>
    @endif
</div>
