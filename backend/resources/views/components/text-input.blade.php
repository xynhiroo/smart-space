@props([
    'label',
    'name',
    'type' => 'text',
    'value' => null,
    'showError' => true,
])

@php
    $inputId = $attributes->get('id', $name);
    $hasError = $errors->has($name);
    $inputClasses = implode(' ', array_filter([
        'mt-2 block w-full rounded-md border bg-white px-3 py-2 text-royal shadow-sm transition placeholder:text-sapphire/70 focus:border-royal focus:outline-none focus:ring-2 focus:ring-royal',
        $hasError ? 'border-danger' : 'border-shellstone',
    ]));
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
        {{ $attributes->except(['id'])->merge(['class' => $inputClasses, 'aria-invalid' => $hasError ? 'true' : 'false']) }}
    >

    @if ($showError)
        @error($name)
            <p class="mt-2 text-sm text-danger">{{ $message }}</p>
        @enderror
    @endif
</div>
