<?php

namespace App\Http\Controllers\Admin\Auth;

use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\LoginRequest;
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
        return view('admin.auth.login');
    }

    public function store(LoginRequest $request): RedirectResponse
    {
        $credentials = $request->only('email', 'password');
        $rateLimitKey = $this->rateLimitKey($request->string('email')->toString(), $request->ip());

        if (RateLimiter::tooManyAttempts($rateLimitKey, 5)) {
            $seconds = RateLimiter::availableIn($rateLimitKey);

            $request->session()->flash('retry_after', $seconds);

            throw ValidationException::withMessages([
                'email' => "Terlalu banyak percobaan masuk. Coba lagi dalam {$seconds} detik.",
            ]);
        }

        if (! Auth::guard('admin')->attempt($credentials)) {
            RateLimiter::hit($rateLimitKey, 60);

            throw ValidationException::withMessages([
                'email' => 'Email atau password salah',
            ]);
        }

        RateLimiter::clear($rateLimitKey);
        $request->session()->regenerate();

        return redirect()->intended(route('admin.dashboard'));
    }

    public function destroy(): RedirectResponse
    {
        Auth::guard('admin')->logout();

        request()->session()->invalidate();
        request()->session()->regenerateToken();

        return redirect()->route('admin.login');
    }

    private function rateLimitKey(string $email, ?string $ipAddress): string
    {
        return 'admin-login:'.Str::lower(trim($email)).'|'.$ipAddress;
    }
}