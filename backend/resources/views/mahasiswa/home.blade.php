<x-layouts.app>
    <div class="space-y-4">
        <div>
            <p class="text-sm font-medium text-sapphire">NIM: {{ auth('mahasiswa')->user()->nim }}</p>
            <h1 class="mt-2 text-2xl font-semibold text-royal">Status Ruangan</h1>
        </div>

        <div class="rounded-lg border border-shellstone bg-white p-6 shadow-sm">
            <p>Status ketersediaan ruangan akan tampil di sini</p>
        </div>
    </div>
</x-layouts.app>
