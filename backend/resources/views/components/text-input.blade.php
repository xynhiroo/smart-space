@props([
    'label',
    'name',
    'type' => 'text',
    'value' => null,
])

@php
    $inputId = $attributes->get('id', $name);
    $hasError = $errors->has($name);
@endphp

<div>
    <label for="{{ $inputId }}" class="block text-sm font-medium text-royal">
        {{ $label }}
    </label>

    <input
        id="{{ $inputId }}"
        name="{{ $name }}"
        type="{{ $type }}"
        value="{{ $value }}"
        @class([
            'mt-2 block w-full rounded-md border bg-white px-3 py-2 text-royal shadow-sm transition placeholder:text-sapphire/70 focus:border-royal focus:outline-none focus:ring-2 focus:ring-royal',
            'border-danger' => $hasError,
            'border-shellstone' => ! $hasError,
        ])
        {{ $attributes->except(['id'])->merge(['aria-invalid' => $hasError ? 'true' : 'false']) }}
    >

    @error($name)
        <p class="mt-2 text-sm text-danger">{{ $message }}</p>
    @enderror
</div>
