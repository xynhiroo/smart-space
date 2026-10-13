@props([
    'type' => 'error',
])

@php
    $classes = [
        'error' => 'border-danger bg-danger-soft text-danger',
    ][$type] ?? 'border-shellstone bg-white text-royal';
@endphp

<div {{ $attributes->merge(['class' => 'rounded-md border px-4 py-3 text-sm '.$classes, 'role' => 'alert']) }}>
    {{ $slot }}
</div>
