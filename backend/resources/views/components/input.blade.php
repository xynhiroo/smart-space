@props([
    'label' => null,
    'name',
    'type' => 'text',
    'value' => null,
    'helper' => null,
    'required' => false,
    'disabled' => false,
    'showError' => true,
    'placeholder' => null,
    'id' => null,
])

@php
    $inputId = $id ?? $name;
    $hasError = $errors->has($name);
    $errorId = "{$inputId}-error";
    $helperId = "{$inputId}-helper";

    $describedBy = [];
    if ($hasError && $showError) $describedBy[] = $errorId;
    if ($helper) $describedBy[] = $helperId;
    $ariaDescribedBy = !empty($describedBy) ? implode(' ', $describedBy) : null;

    $baseClasses = 'block w-full min-h-[44px] rounded-[8px] border bg-surface px-3.5 py-2.5 text-sm text-ink placeholder:text-primary/50 transition duration-150 focus:outline-none focus:ring-2 disabled:bg-paper disabled:text-ink/50 disabled:cursor-not-allowed';
    $stateClasses = $hasError
        ? 'border-error text-error focus:border-error focus:ring-error/20'
        : 'border-line focus:border-primary focus:ring-primary/20';

    $inputClasses = "{$baseClasses} {$stateClasses}";
@endphp

<div class="space-y-1.5">
    @if ($label)
        <label for="{{ $inputId }}" class="block text-sm font-medium text-ink">
            {{ $label }}
            @if ($required)
                <span class="text-error" aria-hidden="true">*</span>
                <span class="sr-only">(wajib diisi)</span>
            @endif
        </label>
    @endif

    <div class="relative">
        <input
            id="{{ $inputId }}"
            name="{{ $name }}"
            type="{{ $type }}"
            value="{{ $value }}"
            @if ($placeholder) placeholder="{{ $placeholder }}" @endif
            @if ($required) required @endif
            @if ($disabled) disabled @endif
            @if ($ariaDescribedBy) aria-describedby="{{ $ariaDescribedBy }}" @endif
            aria-invalid="{{ $hasError ? 'true' : 'false' }}"
            {{ $attributes->merge(['class' => $inputClasses]) }}
        >
    </div>

    @if ($helper)
        <p id="{{ $helperId }}" class="text-xs text-primary/80">{{ $helper }}</p>
    @endif

    @if ($showError && $hasError)
        <p id="{{ $errorId }}" class="text-xs font-medium text-error flex items-center gap-1" role="alert">
            <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <span>{{ $errors->first($name) }}</span>
        </p>
    @endif
</div>
