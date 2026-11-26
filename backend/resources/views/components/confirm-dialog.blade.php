@props([
    'id',
    'title' => 'Konfirmasi Tindakan',
    'message' => 'Apakah Anda yakin ingin melanjutkan tindakan ini?',
    'type' => 'normal', // normal | danger | blocked
    'confirmLabel' => 'Lanjutkan',
    'cancelLabel' => 'Batal',
    'action' => '#',
    'method' => 'POST',
])

{{-- Native modal dialog per Modern Web Guidance --}}
<dialog
    id="{{ $id }}"
    aria-labelledby="{{ $id }}-title"
    aria-describedby="{{ $id }}-desc"
    class="w-full max-w-md p-0 rounded-[12px] border border-line bg-surface text-ink shadow-[var(--shadow-modal)] focus:outline-none"
>
    <div class="p-6 space-y-4">
        <div class="flex items-start gap-4">
            @if ($type === 'danger')
                <div class="rounded-full bg-bad-bg p-2 text-bad-text shrink-0" aria-hidden="true">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                    </svg>
                </div>
            @elseif ($type === 'blocked')
                <div class="rounded-full bg-warn-bg p-2 text-warn-text shrink-0" aria-hidden="true">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
                    </svg>
                </div>
            @else
                <div class="rounded-full bg-ok-bg p-2 text-ok-text shrink-0" aria-hidden="true">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
            @endif

            <div class="space-y-1">
                <h3 id="{{ $id }}-title" class="font-display text-lg font-semibold text-ink">
                    {{ $title }}
                </h3>
                <p id="{{ $id }}-desc" class="text-sm text-primary/80">
                    {{ $message }}
                </p>
            </div>
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-line">
            @if ($type === 'blocked')
                {{-- Blocked warning: user only needs an acknowledgement button --}}
                <x-button
                    type="button"
                    variant="primary"
                    size="md"
                    autofocus
                    onclick="document.getElementById('{{ $id }}').close()"
                >
                    Saya Mengerti
                </x-button>
            @else
                {{-- Modern Web Guidance: Autofocus on safe action (Cancel) in destructive dialogs --}}
                <x-button
                    type="button"
                    variant="secondary"
                    size="md"
                    autofocus
                    onclick="document.getElementById('{{ $id }}').close()"
                >
                    {{ $cancelLabel }}
                </x-button>

                <form method="POST" action="{{ $action }}" class="inline">
                    @csrf
                    @if (in_array(strtoupper($method), ['PUT', 'PATCH', 'DELETE']))
                        @method($method)
                    @endif
                    <x-button
                        type="submit"
                        :variant="$type === 'danger' ? 'danger' : 'primary'"
                        size="md"
                    >
                        {{ $confirmLabel }}
                    </x-button>
                </form>
            @endif
        </div>
    </div>
</dialog>
