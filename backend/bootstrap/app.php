<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->alias([
            'prevent-back-history' => \App\Http\Middleware\PreventBackHistory::class,
        ]);

        // Mahasiswa auth redirects. Keep this block isolated so Admin auth can add its own rules.
        $middleware->redirectGuestsTo(function (Request $request): ?string {
            return $request->routeIs('mahasiswa.*') ? route('mahasiswa.login') : null;
        });

        $middleware->redirectUsersTo(function (Request $request): ?string {
            return Auth::guard('mahasiswa')->check() ? route('mahasiswa.home') : null;
        });
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
