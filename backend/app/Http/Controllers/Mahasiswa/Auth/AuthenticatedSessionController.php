<?php

namespace App\Http\Controllers\Mahasiswa\Auth;

use App\Http\Controllers\Controller;
use App\Http\Requests\Mahasiswa\LoginRequest;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;
use Illuminate\View\View;

class AuthenticatedSessionController extends Controller
{
    public function create(): View
    {
        return view('mahasiswa.auth.login');
    }

    public function store(LoginRequest $request): RedirectResponse
    {
        $credentials = $request->only('nim', 'password');
        $rateLimitKey = $this->rateLimitKey($request->string('nim')->toString(), $request->ip());

        if (RateLimiter::tooManyAttempts($rateLimitKey, 5)) {
            $seconds = RateLimiter::availableIn($rateLimitKey);

            throw ValidationException::withMessages([
                'nim' => "Terlalu banyak percobaan masuk. Coba lagi dalam {$seconds} detik.",
            ]);
        }

        if (! Auth::guard('mahasiswa')->attempt($credentials)) {
            RateLimiter::hit($rateLimitKey, 60);

            throw ValidationException::withMessages([
                'nim' => 'NIM atau password salah',
            ]);
        }

        RateLimiter::clear($rateLimitKey);
        $request->session()->regenerate();

        return redirect()->intended(route('mahasiswa.home'));
    }

    public function destroy(): RedirectResponse
    {
        Auth::guard('mahasiswa')->logout();

        request()->session()->invalidate();
        request()->session()->regenerateToken();

        return redirect()->route('mahasiswa.login');
    }

    private function rateLimitKey(string $nim, ?string $ipAddress): string
    {
        return 'mahasiswa-login:'.Str::lower($nim).'|'.$ipAddress;
    }
}
