@props([
    'title' => 'Terjadi Kendala',
    'message' => 'Sistem tidak dapat memuat data. Silakan periksa koneksi Anda dan coba lagi.',
    'retryUrl' => null,
    'retryLabel' => 'Muat Ulang',
])

<div {{ $attributes->merge(['class' => 'rounded-[12px] border border-bad-text/30 bg-bad-bg/60 p-6 sm:p-8 text-center text-ink flex flex-col items-center justify-center']) }} role="alert">
    <div class="rounded-full bg-bad-bg p-3 text-bad-text" aria-hidden="true">
        <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
    </div>

    <h3 class="mt-3 font-display text-lg font-semibold text-bad-text">
        {{ $title }}
    </h3>

    <p class="mt-1.5 max-w-md text-sm text-ink/90">
        {{ $message }}
    </p>

    @if ($retryUrl)
        <div class="mt-5">
            <a href="{{ $retryUrl }}">
                <x-button variant="danger" size="md">
                    {{ $retryLabel }}
                </x-button>
            </a>
        </div>
    @elseif (isset($action))
        <div class="mt-5">
            {{ $action }}
        </div>
    @endif
</div>
