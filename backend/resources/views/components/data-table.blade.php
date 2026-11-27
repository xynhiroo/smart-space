@props([
    'headers' => [],
    'pagination' => null,
])

<div {{ $attributes->merge(['class' => 'overflow-hidden rounded-[12px] border border-line bg-surface shadow-sm']) }}>
    <div class="overflow-x-auto">
        <table class="min-w-full text-left text-sm text-ink divide-y divide-line">
            @if (!empty($headers))
                <thead class="bg-paper text-xs font-semibold uppercase tracking-wider text-primary/90">
                    <tr>
                        @foreach ($headers as $header)
                            <th scope="col" class="px-5 py-3.5">{{ $header }}</th>
                        @endforeach
                    </tr>
                </thead>
            @endif
            <tbody class="divide-y divide-line/70 bg-surface">
                {{ $slot }}
            </tbody>
        </table>
    </div>

    @if ($pagination)
        <div class="border-t border-line bg-paper px-5 py-3.5">
            {{ $pagination }}
        </div>
    @endif
</div>
