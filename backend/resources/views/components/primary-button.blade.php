@props([
    'variant' => 'default',
])

@php
    $classes = [
        'default' => 'bg-royal text-swan hover:bg-sapphire focus:ring-royal',
        'dark' => 'bg-quicksand text-royal hover:bg-swan focus:ring-quicksand',
    ][$variant] ?? 'bg-royal text-swan hover:bg-sapphire focus:ring-royal';
@endphp

<button {{ $attributes->merge(['class' => 'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-swan disabled:cursor-not-allowed disabled:opacity-70 '.$classes]) }}>
    {{ $slot }}
</button>
