<?php

namespace Tests\Feature;

use App\Models\AdminAccount;
use App\Models\MahasiswaAccount;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\RateLimiter;
use Tests\TestCase;

class MahasiswaAuthenticationTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->seed();
        RateLimiter::clear($this->rateLimitKey('3312501036'));
        RateLimiter::clear($this->rateLimitKey('3312501999'));
    }

    public function test_login_page_can_be_accessed_by_guest(): void
    {
        $this->get(route('mahasiswa.login'))
            ->assertOk()
            ->assertSee('Masuk Mahasiswa');
    }

    public function test_mahasiswa_can_login_with_valid_credentials(): void
    {
        $this->post(route('mahasiswa.login.store'), [
            'nim' => '3312501036',
            'password' => 'password123',
        ])->assertRedirect(route('mahasiswa.home'));

        $this->assertAuthenticatedAs(
            MahasiswaAccount::where('nim', '3312501036')->first(),
            'mahasiswa'
        );
    }

    public function test_wrong_password_fails_with_generic_message(): void
    {
        $this->from(route('mahasiswa.login'))->post(route('mahasiswa.login.store'), [
            'nim' => '3312501036',
            'password' => 'password-salah',
        ])
            ->assertRedirect(route('mahasiswa.login'))
            ->assertSessionHasErrors(['nim' => 'NIM atau password salah'])
            ->assertSessionHasInput('nim', '3312501036');

        $this->assertGuest('mahasiswa');
    }

    public function test_unknown_nim_fails_with_same_generic_message(): void
    {
        $this->from(route('mahasiswa.login'))->post(route('mahasiswa.login.store'), [
            'nim' => '3312501999',
            'password' => 'password123',
        ])
            ->assertRedirect(route('mahasiswa.login'))
            ->assertSessionHasErrors(['nim' => 'NIM atau password salah'])
            ->assertSessionHasInput('nim', '3312501999');

        $this->assertGuest('mahasiswa');
    }

    public function test_login_validation_errors_are_returned(): void
    {
        $this->from(route('mahasiswa.login'))->post(route('mahasiswa.login.store'), [
            'nim' => '',
            'password' => '',
        ])
            ->assertRedirect(route('mahasiswa.login'))
            ->assertSessionHasErrors([
                'nim' => 'NIM wajib diisi.',
                'password' => 'Password wajib diisi.',
            ]);

        $this->from(route('mahasiswa.login'))->post(route('mahasiswa.login.store'), [
            'nim' => 'abc123',
            'password' => 'password123',
        ])
            ->assertRedirect(route('mahasiswa.login'))
            ->assertSessionHasErrors(['nim' => 'NIM harus terdiri dari tepat 10 digit angka.']);
    }

    public function test_guest_accessing_mahasiswa_home_is_redirected_to_login(): void
    {
        $this->get(route('mahasiswa.home'))
            ->assertRedirect(route('mahasiswa.login'));
    }

    public function test_logout_ends_session_and_protects_mahasiswa_home(): void
    {
        $mahasiswa = MahasiswaAccount::where('nim', '3312501036')->firstOrFail();

        $this->actingAs($mahasiswa, 'mahasiswa')
            ->post(route('mahasiswa.logout'))
            ->assertRedirect(route('mahasiswa.login'));

        $this->assertGuest('mahasiswa');

        $this->get(route('mahasiswa.home'))
            ->assertRedirect(route('mahasiswa.login'));
    }

    public function test_authenticated_mahasiswa_opening_login_is_redirected_to_home(): void
    {
        $mahasiswa = MahasiswaAccount::where('nim', '3312501036')->firstOrFail();

        $this->actingAs($mahasiswa, 'mahasiswa')
            ->get(route('mahasiswa.login'))
            ->assertRedirect(route('mahasiswa.home'));
    }

    public function test_rate_limiting_starts_after_repeated_failed_attempts(): void
    {
        for ($attempt = 0; $attempt < 5; $attempt++) {
            $this->post(route('mahasiswa.login.store'), [
                'nim' => '3312501036',
                'password' => 'password-salah',
            ]);
        }

        $response = $this->from(route('mahasiswa.login'))->post(route('mahasiswa.login.store'), [
            'nim' => '3312501036',
            'password' => 'password-salah',
        ]);

        $response->assertRedirect(route('mahasiswa.login'))
            ->assertSessionHasErrors('nim');

        $this->assertStringContainsString(
            'Terlalu banyak percobaan masuk.',
            session('errors')->first('nim')
        );
    }

    public function test_mahasiswa_login_does_not_authenticate_admin_guard(): void
    {
        $this->post(route('mahasiswa.login.store'), [
            'nim' => '3312501036',
            'password' => 'password123',
        ])->assertRedirect(route('mahasiswa.home'));

        $this->assertAuthenticated('mahasiswa');
        $this->assertFalse(Auth::guard('admin')->check());
        $this->assertNotEquals(
            AdminAccount::where('email', 'admin@smartspace.polibatam.ac.id')->first()->getAuthIdentifier(),
            Auth::guard('mahasiswa')->id()
        );
    }

    private function rateLimitKey(string $nim): string
    {
        return 'mahasiswa-login:'.$nim.'|127.0.0.1';
    }
}
