@props([
    'name',
    'status' => 'tersedia',
    'capacity' => null,
    'location' => null,
    'schedule' => null,
    'role' => 'mahasiswa', // mahasiswa | admin
    'actionUrl' => null,
])

<article {{ $attributes->merge(['class' => 'rounded-[12px] border border-line bg-surface p-5 shadow-sm transition hover:border-primary/40 hover:shadow-md flex flex-col justify-between gap-4']) }}>
    <div class="space-y-3">
        <div class="flex items-start justify-between gap-3">
            <h3 class="font-display text-lg font-semibold text-ink">{{ $name }}</h3>
            <x-status-badge :status="$status" :role="$role" size="sm" />
        </div>

        <div class="space-y-1.5 text-xs text-primary/80">
            @if ($location)
                <div class="flex items-center gap-2">
                    <svg class="h-4 w-4 shrink-0 text-primary/60" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                    <span>{{ $location }}</span>
                </div>
            @endif

            @if ($capacity)
                <div class="flex items-center gap-2">
                    <svg class="h-4 w-4 shrink-0 text-primary/60" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                    </svg>
                    <span>Kapasitas: <strong class="text-ink tabular-nums">{{ $capacity }}</strong> orang</span>
                </div>
            @endif

            @if ($schedule)
                <div class="mt-2 rounded-[6px] bg-paper p-2.5 text-xs text-ink/90 border border-line/60">
                    <p class="font-medium text-primary">Sesi Terjadwal:</p>
                    <p class="mt-0.5">{{ $schedule }}</p>
                </div>
            @endif
        </div>
    </div>

    @if ($actionUrl)
        <div class="pt-2 border-t border-line/50">
            <a href="{{ $actionUrl }}" class="inline-flex w-full items-center justify-center rounded-[8px] bg-paper px-3 py-2 text-xs font-semibold text-primary hover:bg-line/40 transition">
                Lihat Detail & Jadwal →
            </a>
        </div>
    @endif
</article>
