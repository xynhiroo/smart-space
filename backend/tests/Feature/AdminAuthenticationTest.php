<?php

namespace Tests\Feature;

use App\Models\AdminAccount;
use App\Models\MahasiswaAccount;
use Database\Seeders\AccountSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\RateLimiter;
use Tests\TestCase;

class AdminAuthenticationTest extends TestCase
{
    use RefreshDatabase;

    private const EMAIL = 'admin@smartspace.polibatam.ac.id';

    protected function setUp(): void
    {
        parent::setUp();

        $this->withoutVite();
        $this->seed(AccountSeeder::class);

        RateLimiter::clear($this->rateLimitKey(self::EMAIL));
        RateLimiter::clear($this->rateLimitKey('tidak.ada@smartspace.polibatam.ac.id'));
    }

    public function test_login_page_can_be_accessed_by_guest(): void
    {
        $this->get(route('admin.login'))
            ->assertOk()
            ->assertSee('Masuk Admin');
    }

    public function test_admin_can_login_with_valid_credentials(): void
    {
        $this->post(route('admin.login.store'), [
            'email' => self::EMAIL,
            'password' => 'admin12345',
        ])->assertRedirect(route('admin.dashboard'));

        $this->assertAuthenticatedAs(
            AdminAccount::where('email', self::EMAIL)->first(),
            'admin'
        );
    }

    public function test_wrong_password_fails_with_generic_message(): void
    {
        $this->from(route('admin.login'))->post(route('admin.login.store'), [
            'email' => self::EMAIL,
            'password' => 'password-salah',
        ])
            ->assertRedirect(route('admin.login'))
            ->assertSessionHasErrors(['email' => 'Email atau password salah'])
            ->assertSessionHasInput('email', self::EMAIL);

        $this->assertGuest('admin');
    }

    public function test_unknown_email_fails_with_same_generic_message(): void
    {
        $this->from(route('admin.login'))->post(route('admin.login.store'), [
            'email' => 'tidak.ada@smartspace.polibatam.ac.id',
            'password' => 'admin12345',
        ])
            ->assertRedirect(route('admin.login'))
            ->assertSessionHasErrors(['email' => 'Email atau password salah']);

        $this->assertGuest('admin');
    }

    public function test_login_validation_errors_are_returned(): void
    {
        $this->from(route('admin.login'))->post(route('admin.login.store'), [
            'email' => '',
            'password' => '',
        ])
            ->assertRedirect(route('admin.login'))
            ->assertSessionHasErrors([
                'email' => 'Email wajib diisi',
                'password' => 'Password wajib diisi',
            ]);

        $this->from(route('admin.login'))->post(route('admin.login.store'), [
            'email' => 'bukan-email',
            'password' => 'admin12345',
        ])
            ->assertRedirect(route('admin.login'))
            ->assertSessionHasErrors(['email' => 'Format email tidak valid']);
    }

    public function test_guest_accessing_admin_dashboard_is_redirected_to_login(): void
    {
        $this->get(route('admin.dashboard'))
            ->assertRedirect(route('admin.login'));
    }

    public function test_authenticated_admin_can_open_dashboard(): void
    {
        $admin = AdminAccount::where('email', self::EMAIL)->firstOrFail();

        $this->actingAs($admin, 'admin')
            ->get(route('admin.dashboard'))
            ->assertOk()
            ->assertSee('Dashboard Admin')
            ->assertSee('Admin Fasilitas IF');
    }

    public function test_logout_ends_session_and_protects_admin_dashboard(): void
    {
        $admin = AdminAccount::where('email', self::EMAIL)->firstOrFail();

        $this->actingAs($admin, 'admin')
            ->post(route('admin.logout'))
            ->assertRedirect(route('admin.login'));

        $this->assertGuest('admin');

        $this->get(route('admin.dashboard'))
            ->assertRedirect(route('admin.login'));
    }

    public function test_authenticated_admin_opening_login_is_redirected_to_dashboard(): void
    {
        $admin = AdminAccount::where('email', self::EMAIL)->firstOrFail();

        $this->actingAs($admin, 'admin')
            ->get(route('admin.login'))
            ->assertRedirect(route('admin.dashboard'));
    }

    public function test_rate_limiting_starts_after_repeated_failed_attempts(): void
    {
        for ($attempt = 0; $attempt < 5; $attempt++) {
            $this->post(route('admin.login.store'), [
                'email' => self::EMAIL,
                'password' => 'password-salah',
            ]);
        }

        $response = $this->from(route('admin.login'))->post(route('admin.login.store'), [
            'email' => self::EMAIL,
            'password' => 'password-salah',
        ]);

        $response->assertRedirect(route('admin.login'))
            ->assertSessionHasErrors('email')
            ->assertSessionHas('retry_after', function (mixed $value): bool {
                return is_numeric($value) && (int) $value > 0;
            });

        $this->assertStringContainsString(
            'Terlalu banyak percobaan masuk.',
            session('errors')->first('email')
        );

        $this->get(route('admin.login'))
            ->assertOk()
            ->assertSee('Terlalu banyak percobaan. Coba lagi dalam');
    }

    public function test_admin_login_does_not_authenticate_mahasiswa_guard(): void
    {
        $this->post(route('admin.login.store'), [
            'email' => self::EMAIL,
            'password' => 'admin12345',
        ])->assertRedirect(route('admin.dashboard'));

        $this->assertAuthenticated('admin');
        $this->assertFalse(Auth::guard('mahasiswa')->check());
    }

    public function test_mahasiswa_cannot_open_admin_dashboard(): void
    {
        $mahasiswa = MahasiswaAccount::where('nim', '3312501036')->firstOrFail();

        $this->actingAs($mahasiswa, 'mahasiswa')
            ->get(route('admin.dashboard'))
            ->assertRedirect(route('admin.login'));
    }

    public function test_protected_admin_dashboard_has_prevent_back_cache_headers(): void
    {
        $admin = AdminAccount::where('email', self::EMAIL)->firstOrFail();

        $response = $this->actingAs($admin, 'admin')
            ->get(route('admin.dashboard'));

        $response->assertOk();
        $cacheControl = (string) $response->headers->get('Cache-Control');
        $this->assertTrue(str_contains($cacheControl, 'no-store'));
        $this->assertSame('no-cache', $response->headers->get('Pragma'));
        $this->assertSame('0', $response->headers->get('Expires'));
    }

    private function rateLimitKey(string $email): string
    {
        return 'admin-login:'.strtolower(trim($email)).'|127.0.0.1';
    }
}