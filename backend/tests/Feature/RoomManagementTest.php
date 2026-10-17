<?php

namespace Tests\Feature;

use App\Models\AdminAccount;
use App\Models\MahasiswaAccount;
use App\Models\Room;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class RoomManagementTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->withoutVite();
    }

    public function test_guest_is_redirected_to_admin_login_for_every_room_route(): void
    {
        $room = $this->room();

        $this->get(route('admin.rooms.index'))->assertRedirect(route('admin.login'));
        $this->get(route('admin.rooms.create'))->assertRedirect(route('admin.login'));
        $this->post(route('admin.rooms.store'), ['nama_ruangan' => 'GU 900', 'status' => 'tersedia'])
            ->assertRedirect(route('admin.login'));
        $this->get(route('admin.rooms.edit', $room))->assertRedirect(route('admin.login'));
        $this->put(route('admin.rooms.update', $room), ['nama_ruangan' => 'GU 900', 'status' => 'tersedia'])
            ->assertRedirect(route('admin.login'));
        $this->delete(route('admin.rooms.destroy', $room))->assertRedirect(route('admin.login'));

        $this->assertDatabaseCount('rooms', 1);
        $this->assertDatabaseHas('rooms', ['nama_ruangan' => 'GU 101']);
    }

    public function test_mahasiswa_cannot_open_admin_room_pages(): void
    {
        $mahasiswa = MahasiswaAccount::create([
            'nim' => '3312501001',
            'password_hash' => Hash::make('password-uji-123'),
        ]);

        $this->actingAs($mahasiswa, 'mahasiswa')
            ->get(route('admin.rooms.index'))
            ->assertRedirect(route('admin.login'));
    }

    public function test_admin_sees_room_list(): void
    {
        $this->room(['nama_ruangan' => 'GU 101']);
        $this->room(['nama_ruangan' => 'TA 202']);

        $this->actingAs($this->admin(), 'admin')
            ->get(route('admin.rooms.index'))
            ->assertOk()
            ->assertSee('Data Ruangan')
            ->assertSee('GU 101')
            ->assertSee('TA 202');
    }

    public function test_admin_sees_empty_state_when_there_are_no_rooms(): void
    {
        $this->actingAs($this->admin(), 'admin')
            ->get(route('admin.rooms.index'))
            ->assertOk()
            ->assertSee('Belum ada ruangan.');
    }

    public function test_admin_can_open_create_and_edit_forms(): void
    {
        $room = $this->room();

        $this->actingAs($this->admin(), 'admin')
            ->get(route('admin.rooms.create'))
            ->assertOk()
            ->assertSee('Tambah Ruangan');

        $this->get(route('admin.rooms.edit', $room))
            ->assertOk()
            ->assertSee('Ubah Ruangan')
            ->assertSee('GU 101');
    }

    public function test_admin_can_create_room(): void
    {
        $this->actingAs($this->admin(), 'admin')
            ->post(route('admin.rooms.store'), [
                'nama_ruangan' => 'GU 900',
                'kapasitas' => 40,
                'lokasi' => 'Gedung Uji Lantai 9',
                'status' => 'tersedia',
            ])
            ->assertRedirect(route('admin.rooms.index'))
            ->assertSessionHas('status', 'Ruangan berhasil ditambahkan.');

        $this->assertDatabaseHas('rooms', [
            'nama_ruangan' => 'GU 900',
            'kapasitas' => 40,
            'lokasi' => 'Gedung Uji Lantai 9',
            'status' => 'tersedia',
        ]);
    }

    public function test_capacity_and_location_are_optional_when_creating_room(): void
    {
        $this->actingAs($this->admin(), 'admin')
            ->post(route('admin.rooms.store'), [
                'nama_ruangan' => 'GU 901',
                'status' => 'tersedia',
            ])
            ->assertRedirect(route('admin.rooms.index'));

        $this->assertDatabaseHas('rooms', [
            'nama_ruangan' => 'GU 901',
            'kapasitas' => null,
            'lokasi' => null,
        ]);
    }

    public function test_create_room_validation_errors_are_returned(): void
    {
        $this->room(['nama_ruangan' => 'GU 101']);

        $this->actingAs($this->admin(), 'admin')
            ->from(route('admin.rooms.create'))
            ->post(route('admin.rooms.store'), [
                'nama_ruangan' => '',
                'status' => '',
            ])
            ->assertRedirect(route('admin.rooms.create'))
            ->assertSessionHasErrors([
                'nama_ruangan' => 'Nama ruangan wajib diisi',
                'status' => 'Status wajib dipilih',
            ]);

        $this->from(route('admin.rooms.create'))
            ->post(route('admin.rooms.store'), [
                'nama_ruangan' => 'GU 101',
                'status' => 'tersedia',
            ])
            ->assertSessionHasErrors(['nama_ruangan' => 'Nama ruangan sudah dipakai']);

        $this->from(route('admin.rooms.create'))
            ->post(route('admin.rooms.store'), [
                'nama_ruangan' => 'GU 902',
                'status' => 'rusak',
            ])
            ->assertSessionHasErrors(['status' => 'Status tidak valid']);

        $this->from(route('admin.rooms.create'))
            ->post(route('admin.rooms.store'), [
                'nama_ruangan' => 'GU 902',
                'kapasitas' => 'banyak',
                'status' => 'tersedia',
            ])
            ->assertSessionHasErrors(['kapasitas' => 'Kapasitas harus berupa angka']);

        $this->assertDatabaseCount('rooms', 1);
    }

    public function test_admin_can_update_room(): void
    {
        $room = $this->room();

        $this->actingAs($this->admin(), 'admin')
            ->put(route('admin.rooms.update', $room), [
                'nama_ruangan' => 'GU 101',
                'kapasitas' => 50,
                'lokasi' => 'Lantai 1',
                'status' => 'tidak tersedia',
            ])
            ->assertRedirect(route('admin.rooms.index'))
            ->assertSessionHas('status', 'Ruangan berhasil diperbarui.');

        $this->assertDatabaseHas('rooms', [
            'id' => $room->id,
            'nama_ruangan' => 'GU 101',
            'kapasitas' => 50,
            'status' => 'tidak tersedia',
        ]);
    }

    public function test_update_cannot_use_name_of_another_room(): void
    {
        $this->room(['nama_ruangan' => 'GU 101']);
        $other = $this->room(['nama_ruangan' => 'TA 202']);

        $this->actingAs($this->admin(), 'admin')
            ->from(route('admin.rooms.edit', $other))
            ->put(route('admin.rooms.update', $other), [
                'nama_ruangan' => 'GU 101',
                'status' => 'tersedia',
            ])
            ->assertRedirect(route('admin.rooms.edit', $other))
            ->assertSessionHasErrors(['nama_ruangan' => 'Nama ruangan sudah dipakai']);

        $this->assertDatabaseHas('rooms', ['id' => $other->id, 'nama_ruangan' => 'TA 202']);
    }

    public function test_admin_can_delete_room_without_schedules(): void
    {
        $room = $this->room();

        $this->actingAs($this->admin(), 'admin')
            ->delete(route('admin.rooms.destroy', $room))
            ->assertRedirect(route('admin.rooms.index'))
            ->assertSessionHas('status', 'Ruangan berhasil dihapus.');

        $this->assertDatabaseMissing('rooms', ['id' => $room->id]);
    }

    public function test_room_with_schedules_cannot_be_deleted(): void
    {
        $room = $this->room();

        DB::table('schedules')->insert([
            [
                'room_id' => $room->id,
                'hari' => 'Senin',
                'jam_mulai' => '08:00:00',
                'jam_selesai' => '10:00:00',
                'mata_kuliah' => 'Mata Kuliah Uji 1',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'room_id' => $room->id,
                'hari' => 'Selasa',
                'jam_mulai' => '10:00:00',
                'jam_selesai' => '12:00:00',
                'mata_kuliah' => 'Mata Kuliah Uji 2',
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);

        $this->actingAs($this->admin(), 'admin')
            ->delete(route('admin.rooms.destroy', $room))
            ->assertRedirect(route('admin.rooms.index'))
            ->assertSessionHasErrors([
                'room' => "Ruangan {$room->nama_ruangan} tidak dapat dihapus karena masih memiliki 2 jadwal dan 0 data riwayat. Data ruangan yang sudah memiliki jadwal atau riwayat dipertahankan agar analitik tidak hilang.",
            ]);

        $this->assertDatabaseHas('rooms', ['id' => $room->id]);
        $this->assertEquals(2, DB::table('schedules')->where('room_id', $room->id)->count());
    }

    public function test_room_with_occupancy_logs_cannot_be_deleted(): void
    {
        $room = $this->room();

        DB::table('occupancy_logs')->insert([
            'room_id' => $room->id,
            'slot_mulai' => '2026-10-17 08:00:00',
            'is_occupied' => true,
            'source' => 'dummy',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $this->actingAs($this->admin(), 'admin')
            ->delete(route('admin.rooms.destroy', $room))
            ->assertRedirect(route('admin.rooms.index'))
            ->assertSessionHasErrors([
                'room' => "Ruangan {$room->nama_ruangan} tidak dapat dihapus karena masih memiliki 0 jadwal dan 1 data riwayat. Data ruangan yang sudah memiliki jadwal atau riwayat dipertahankan agar analitik tidak hilang.",
            ]);

        $this->assertDatabaseHas('rooms', ['id' => $room->id]);
        $this->assertEquals(1, DB::table('occupancy_logs')->where('room_id', $room->id)->count());
    }

    public function test_room_with_classification_results_cannot_be_deleted(): void
    {
        $room = $this->room();

        DB::table('classification_results')->insert([
            'room_id' => $room->id,
            'schedule_id' => null,
            'tanggal' => '2026-10-17',
            'waktu_mulai' => '08:00:00',
            'waktu_selesai' => '09:40:00',
            'status' => 'dipakai_di_luar_jadwal',
            'menit_terjadwal' => 0,
            'menit_terpakai' => 100,
            'utilisasi_pct' => null,
            'rule_id' => 'R03',
            'penjelasan' => 'Ruang dipakai di luar jadwal',
            'computed_at' => now(),
        ]);

        $this->actingAs($this->admin(), 'admin')
            ->delete(route('admin.rooms.destroy', $room))
            ->assertRedirect(route('admin.rooms.index'))
            ->assertSessionHasErrors([
                'room' => "Ruangan {$room->nama_ruangan} tidak dapat dihapus karena masih memiliki 0 jadwal dan 1 data riwayat. Data ruangan yang sudah memiliki jadwal atau riwayat dipertahankan agar analitik tidak hilang.",
            ]);

        $this->assertDatabaseHas('rooms', ['id' => $room->id]);
        $this->assertEquals(1, DB::table('classification_results')->where('room_id', $room->id)->count());
    }

    public function test_room_form_and_index_display_kondisi_ruangan_label_and_help_text(): void
    {
        $room = $this->room();

        $this->actingAs($this->admin(), 'admin')
            ->get(route('admin.rooms.index'))
            ->assertOk()
            ->assertSee('Kondisi ruangan');

        $this->get(route('admin.rooms.create'))
            ->assertOk()
            ->assertSee('Kondisi ruangan')
            ->assertSee('Kondisi master ruangan (mis. sedang diperbaiki). Bukan status pemakaian kosong/terisi, karena itu dihitung otomatis oleh sistem dari data okupansi dan jadwal.');

        $this->get(route('admin.rooms.edit', $room))
            ->assertOk()
            ->assertSee('Kondisi ruangan')
            ->assertSee('Kondisi master ruangan (mis. sedang diperbaiki). Bukan status pemakaian kosong/terisi, karena itu dihitung otomatis oleh sistem dari data okupansi dan jadwal.');
    }

    private function admin(): AdminAccount
    {
        return AdminAccount::create([
            'nama' => 'Admin Uji',
            'email' => 'admin.uji@smartspace.polibatam.ac.id',
            'password_hash' => Hash::make('rahasia-uji-123'),
        ]);
    }

    private function room(array $attributes = []): Room
    {
        return Room::create(array_merge([
            'nama_ruangan' => 'GU 101',
            'kapasitas' => 30,
            'lokasi' => 'Gedung Uji Lantai 1',
            'status' => 'tersedia',
        ], $attributes));
    }
}