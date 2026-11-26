@props([
    'label' => null,
    'name',
    'type' => 'text',
    'value' => null,
    'showError' => true,
    'helper' => null,
    'required' => false,
])

<x-input
    :label="$label"
    :name="$name"
    :type="$type"
    :value="$value"
    :show-error="$showError"
    :helper="$helper"
    :required="$required"
    {{ $attributes }}
/>
