@props([
    'id',
    'title',
    'maxWidth' => 'md', // sm | md | lg | xl
])

@php
    $maxWidthClass = [
        'sm' => 'max-w-sm',
        'md' => 'max-w-md',
        'lg' => 'max-w-lg',
        'xl' => 'max-w-xl',
    ][$maxWidth] ?? 'max-w-md';
@endphp

{{-- Native dialog element per Modern Web Guidance --}}
<dialog
    id="{{ $id }}"
    aria-labelledby="{{ $id }}-title"
    {{ $attributes->merge(['class' => "w-full {$maxWidthClass} p-0 rounded-[12px] border border-line bg-surface text-ink shadow-[var(--shadow-modal)] focus:outline-none"]) }}
    x-data="{
        openModal() {
            this.$el.showModal();
        },
        closeModal() {
            this.$el.close();
        }
    }"
    @open-modal.window="if ($event.detail === '{{ $id }}') openModal()"
    @close-modal.window="if ($event.detail === '{{ $id }}') closeModal()"
>
    <div class="p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-line pb-3">
            <h2 id="{{ $id }}-title" class="font-display text-lg font-semibold text-ink">
                {{ $title }}
            </h2>
            <button
                type="button"
                class="rounded-[6px] p-1.5 text-primary/70 hover:bg-paper hover:text-ink focus:outline-none focus:ring-2 focus:ring-primary"
                onclick="document.getElementById('{{ $id }}').close()"
                aria-label="Tutup dialog"
            >
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </button>
        </div>

        <div class="text-sm text-ink/90">
            {{ $slot }}
        </div>

        @if (isset($footer))
            <div class="flex items-center justify-end gap-3 pt-3 border-t border-line">
                {{ $footer }}
            </div>
        @endif
    </div>
</dialog>
