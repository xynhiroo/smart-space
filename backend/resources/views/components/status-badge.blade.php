@props([
    'status', // sesuai_jadwal | kosong_meski_terjadwal | dipakai_di_luar_jadwal | kosong | terisi | tersedia | tidak_tersedia
    'role' => 'admin', // admin | mahasiswa
    'size' => 'md',    // sm | md
])

@php
    $key = strtolower(trim((string)$status));
    $sizeClasses = $size === 'sm' ? 'px-2 py-0.5 text-xs gap-1' : 'px-2.5 py-1 text-xs font-medium gap-1.5';

    // Standar Admin: SS1-11 & Data Contract
    // Standar Mahasiswa: Kosong / Terisi / Tidak Tersedia
    $config = match($key) {
        'sesuai_jadwal' => [
            'label' => 'Sesuai Jadwal',
            'bg' => 'bg-ok-bg text-ok-text border border-ok-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>',
        ],
        'kosong_meski_terjadwal' => [
            'label' => 'Kosong Meski Terjadwal',
            'bg' => 'bg-warn-bg text-warn-text border border-warn-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" /></svg>',
        ],
        'dipakai_di_luar_jadwal' => [
            'label' => 'Dipakai di Luar Jadwal',
            'bg' => 'bg-bad-bg text-bad-text border border-bad-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clip-rule="evenodd" /></svg>',
        ],
        'kosong', 'tersedia' => [
            'label' => ($role === 'mahasiswa' && $key === 'kosong') ? 'Kosong' : 'Tersedia',
            'bg' => 'bg-ok-bg text-ok-text border border-ok-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd" /></svg>',
        ],
        'terisi' => [
            'label' => 'Terisi',
            'bg' => 'bg-warn-bg text-warn-text border border-warn-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor"><path d="M10 8a3 3 0 100-6 3 3 0 000 6zM3.465 14.493a1.23 1.23 0 00.41 1.412A9.957 9.957 0 0010 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 00-13.074.003z" /></svg>',
        ],
        'tidak_tersedia', 'tidak tersedia' => [
            'label' => 'Tidak Tersedia',
            'bg' => 'bg-bad-bg text-bad-text border border-bad-text/20',
            'icon' => '<svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" /></svg>',
        ],
        default => [
            'label' => ucfirst(str_replace('_', ' ', $key)),
            'bg' => 'bg-surface text-ink border border-line',
            'icon' => '<span class="inline-block w-2 h-2 rounded-full bg-primary/60"></span>',
        ],
    };
@endphp

<span {{ $attributes->merge(['class' => "inline-flex items-center rounded-[4px] {$sizeClasses} {$config['bg']}"]) }}>
    <span class="shrink-0" aria-hidden="true">{!! $config['icon'] !!}</span>
    <span>{{ $config['label'] }}</span>
</span>
