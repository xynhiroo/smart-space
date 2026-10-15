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

            // Auth redirects per area: admin.* dan mahasiswa.*
        $middleware->redirectGuestsTo(function (Request $request): ?string {
            if ($request->routeIs('admin.*')) {
                return route('admin.login');
            }

            return $request->routeIs('mahasiswa.*') ? route('mahasiswa.login') : null;
        });

        $middleware->redirectUsersTo(function (Request $request): ?string {
            if ($request->routeIs('admin.*')) {
                return route('admin.dashboard');
            }

            return Auth::guard('mahasiswa')->check() ? route('mahasiswa.home') : null;
    });
        })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
