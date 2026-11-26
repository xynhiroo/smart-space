@extends('layouts.admin', ['title' => 'Data Ruangan'])

@section('content')
    <div class="space-y-6">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
                <h1 class="text-2xl font-bold font-display text-ink tracking-tight">Data Ruangan</h1>
                <p class="text-sm text-ink/70 mt-1">Kelola daftar master ruangan fisik perkuliahan dan laboratorium.</p>
            </div>
            <a href="{{ route('admin.rooms.create') }}" class="inline-flex items-center justify-center gap-2 rounded-kontrol bg-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-ink focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Tambah ruangan
            </a>
        </div>

        @if (session('status'))
            <div role="status" class="rounded-kontrol border border-ok-text/30 bg-ok-bg px-4 py-3 text-sm text-ok-text flex items-center gap-3">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <span>{{ session('status') }}</span>
            </div>
        @endif

        @if ($errors->any())
            <div>
                <x-alert>
                    <ul class="space-y-1">
                        @foreach ($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </x-alert>
            </div>
        @endif

        <!-- Table Card -->
        <div class="overflow-hidden rounded-panel border border-line bg-surface shadow-xs">
            <div class="overflow-x-auto">
                <table class="min-w-full text-left text-sm divide-y divide-line">
                    <thead class="bg-paper text-ink">
                        <tr>
                            <th scope="col" class="px-5 py-3.5 font-semibold text-xs uppercase tracking-wider">Nama ruangan</th>
                            <th scope="col" class="px-5 py-3.5 font-semibold text-xs uppercase tracking-wider">Kapasitas</th>
                            <th scope="col" class="px-5 py-3.5 font-semibold text-xs uppercase tracking-wider">Lokasi</th>
                            <th scope="col" class="px-5 py-3.5 font-semibold text-xs uppercase tracking-wider">Kondisi ruangan</th>
                            <th scope="col" class="px-5 py-3.5 font-semibold text-xs uppercase tracking-wider text-right">Aksi</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-line bg-white">
                        @forelse ($rooms as $room)
                            <tr class="hover:bg-paper/50 transition-colors">
                                <td class="px-5 py-4 font-semibold text-ink">
                                    {{ $room->nama_ruangan }}
                                </td>
                                <td class="px-5 py-4 text-ink/80 tabular-nums">
                                    {{ $room->kapasitas ? $room->kapasitas . ' Kursi' : '-' }}
                                </td>
                                <td class="px-5 py-4 text-ink/80">
                                    {{ $room->lokasi ?? '-' }}
                                </td>
                                <td class="px-5 py-4">
                                    <x-status-badge :status="$room->status" />
                                </td>
                                <td class="px-5 py-4 text-right">
                                    <div class="inline-flex items-center justify-end gap-3">
                                        <a href="{{ route('admin.rooms.edit', $room) }}" class="inline-flex items-center text-sm font-medium text-primary hover:text-ink focus:outline-none focus:underline p-1 min-h-[44px] min-w-[44px] justify-center">
                                            Ubah
                                        </a>
                                        <form method="POST" action="{{ route('admin.rooms.destroy', $room) }}"
                                              onsubmit="return confirm({{ Illuminate\Support\Js::from('Hapus ruangan '.$room->nama_ruangan.'?') }})"
                                              class="inline-block">
                                            @csrf
                                            @method('DELETE')
                                            <button type="submit" class="inline-flex items-center text-sm font-medium text-error hover:text-bad-text focus:outline-none focus:underline p-1 min-h-[44px] min-w-[44px] justify-center">
                                                Hapus
                                            </button>
                                        </form>
                                    </div>
                                </td>
                            </tr>
                        @empty
                            <tr>
                                <td colspan="5" class="px-5 py-12 text-center">
                                    <div class="flex flex-col items-center justify-center">
                                        <svg class="w-12 h-12 text-ink/30 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                        </svg>
                                        <p class="text-sm font-medium text-ink">Belum ada ruangan.</p>
                                        <p class="text-xs text-ink/60 mt-1">Mulai tambahkan ruangan baru untuk mengaktifkan pemantauan.</p>
                                    </div>
                                </td>
                            </tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>

        @if ($rooms->hasPages())
            <div class="mt-4">
                {{ $rooms->links() }}
            </div>
        @endif
    </div>
@endsection
