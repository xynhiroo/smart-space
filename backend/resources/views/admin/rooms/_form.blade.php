<div class="space-y-5">
    <x-input
        label="Nama ruangan"
        name="nama_ruangan"
        value="{{ old('nama_ruangan', $room?->nama_ruangan) }}"
        maxlength="50"
        required
        autofocus
        placeholder="Contoh: Lab Komputer 1 / Ruang Teori 302"
    />

    <x-input
        label="Kapasitas"
        name="kapasitas"
        type="number"
        value="{{ old('kapasitas', $room?->kapasitas) }}"
        min="1"
        max="1000"
        placeholder="Kapasitas kursi ruangan"
        helper="Jumlah kapasitas maksimal mahasiswa di dalam ruangan"
    />

    <x-input
        label="Lokasi"
        name="lokasi"
        value="{{ old('lokasi', $room?->lokasi) }}"
        maxlength="100"
        placeholder="Contoh: Gedung Utama Lantai 2"
        helper="Informasi letak gedung atau lantai"
    />

    <div class="space-y-1.5">
        <label for="status" class="block text-sm font-semibold text-ink">Kondisi ruangan</label>
        <select id="status" name="status" required class="w-full rounded-kontrol border border-line bg-surface px-3 py-2.5 text-ink text-sm min-h-[44px] focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-colors">
            @foreach (['tersedia', 'tidak tersedia'] as $option)
                <option value="{{ $option }}" @selected(old('status', $room?->status ?? 'tersedia') === $option)>{{ $option }}</option>
            @endforeach
        </select>
        <p class="text-xs text-ink/70">Kondisi master ruangan (mis. sedang diperbaiki). Bukan status pemakaian kosong/terisi, karena itu dihitung otomatis oleh sistem dari data okupansi dan jadwal.</p>
        @error('status')
            <p class="text-xs text-error font-medium" role="alert">{{ $message }}</p>
        @enderror
    </div>

    <div class="flex items-center gap-3 pt-4 border-t border-line">
        <x-button type="submit" variant="primary">
            {{ $submitLabel }}
        </x-button>
        <a href="{{ route('admin.rooms.index') }}" class="inline-flex items-center justify-center rounded-kontrol border border-line bg-surface px-4 py-2.5 text-sm font-medium text-ink hover:bg-paper focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors min-h-[44px]">
            Batal
        </a>
    </div>
</div>
