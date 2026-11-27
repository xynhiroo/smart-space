@props([
    'type' => 'card', // card | table-row | text
    'count' => 1,
])

@if ($type === 'card')
    <div {{ $attributes->merge(['class' => 'rounded-[12px] border border-line bg-surface p-5 shadow-sm animate-pulse space-y-4']) }}>
        <div class="flex items-center justify-between">
            <div class="h-4 w-28 bg-line/60 rounded-[4px]"></div>
            <div class="h-6 w-16 bg-line/60 rounded-[4px]"></div>
        </div>
        <div class="space-y-2">
            <div class="h-3 w-3/4 bg-line/50 rounded-[4px]"></div>
            <div class="h-3 w-1/2 bg-line/50 rounded-[4px]"></div>
        </div>
    </div>
@elseif ($type === 'table-row')
    @for ($i = 0; $i < $count; $i++)
        <tr class="animate-pulse border-b border-line/60">
            <td class="px-5 py-4"><div class="h-4 w-24 bg-line/60 rounded-[4px]"></div></td>
            <td class="px-5 py-4"><div class="h-4 w-12 bg-line/50 rounded-[4px]"></div></td>
            <td class="px-5 py-4"><div class="h-4 w-32 bg-line/50 rounded-[4px]"></div></td>
            <td class="px-5 py-4"><div class="h-6 w-24 bg-line/60 rounded-[4px]"></div></td>
            <td class="px-5 py-4"><div class="h-4 w-16 bg-line/50 rounded-[4px]"></div></td>
        </tr>
    @endfor
@else
    <div {{ $attributes->merge(['class' => 'space-y-2 animate-pulse']) }}>
        <div class="h-4 w-3/4 bg-line/60 rounded-[4px]"></div>
        <div class="h-4 w-1/2 bg-line/50 rounded-[4px]"></div>
    </div>
@endif
