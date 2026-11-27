@props([
    'variant' => 'primary',
    'size' => 'md',
    'type' => 'submit',
    'loading' => false,
])

<x-button
    :variant="$variant"
    :size="$size"
    :type="$type"
    :loading="$loading"
    {{ $attributes }}
>
    {{ $slot }}
</x-button>
