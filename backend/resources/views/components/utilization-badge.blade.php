@props([
    'kategori', // rendah | sedang | tinggi
    'pct' => null,
])

@php
    $key = strtolower(trim((string)$kategori));

    $config = match($key) {
        'rendah' => [
            'label' => 'Rendah',
            'bg' => 'bg-bad-bg text-bad-text border border-bad-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"/></svg>',
        ],
        'sedang' => [
            'label' => 'Sedang',
            'bg' => 'bg-warn-bg text-warn-text border border-warn-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>',
        ],
        'tinggi' => [
            'label' => 'Tinggi',
            'bg' => 'bg-ok-bg text-ok-text border border-ok-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>',
        ],
        default => [
            'label' => ucfirst($key),
            'bg' => 'bg-surface text-ink border border-line',
            'icon' => '<span class="w-2 h-2 rounded-full bg-primary/50"></span>',
        ],
    };
@endphp

<span {{ $attributes->merge(['class' => "inline-flex items-center gap-1.5 rounded-[4px] px-2.5 py-1 text-xs font-medium {$config['bg']}"]) }}>
    <span class="shrink-0" aria-hidden="true">{!! $config['icon'] !!}</span>
    <span>{{ $config['label'] }}</span>
    @if ($pct !== null)
        <span class="tabular-nums font-semibold">({{ number_format($pct, 1) }}%)</span>
    @endif
</span>
