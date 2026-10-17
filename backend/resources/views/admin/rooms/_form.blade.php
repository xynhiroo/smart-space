<x-text-input
    label="Nama ruangan"
    name="nama_ruangan"
    value="{{ old('nama_ruangan', $room?->nama_ruangan) }}"
    maxlength="50"
    required
    autofocus
/>

<x-text-input
    label="Kapasitas"
    name="kapasitas"
    type="number"
    value="{{ old('kapasitas', $room?->kapasitas) }}"
    min="1"
    max="1000"
/>

<x-text-input
    label="Lokasi"
    name="lokasi"
    value="{{ old('lokasi', $room?->lokasi) }}"
    maxlength="100"
/>

<div class="space-y-2">
    <label for="status" class="block text-sm font-semibold">Kondisi ruangan</label>
    <select id="status" name="status" required class="w-full rounded-md border border-shellstone bg-white px-4 py-3 text-royal focus:outline-none focus:ring-2 focus:ring-royal">
        @foreach (['tersedia', 'tidak tersedia'] as $option)
            <option value="{{ $option }}" @selected(old('status', $room?->status ?? 'tersedia') === $option)>{{ $option }}</option>
        @endforeach
    </select>
    <p class="text-xs text-sapphire">Kondisi master ruangan (mis. sedang diperbaiki). Bukan status pemakaian kosong/terisi, karena itu dihitung otomatis oleh sistem dari data okupansi dan jadwal.</p>
    @error('status')
        <p class="text-sm text-red-700">{{ $message }}</p>
    @enderror
</div>

<div class="flex items-center gap-4">
    <x-primary-button type="submit">{{ $submitLabel }}</x-primary-button>
    <a href="{{ route('admin.rooms.index') }}" class="text-sm font-semibold text-sapphire hover:text-royal">Batal</a>
</div>