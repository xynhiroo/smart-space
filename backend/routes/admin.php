<?php

use App\Http\Controllers\Admin\Auth\AuthenticatedSessionController;
use App\Http\Controllers\Admin\RoomController;
use Illuminate\Support\Facades\Route;

Route::prefix('admin')->group(function (): void {
    Route::middleware('guest:admin')->group(function (): void {
        Route::get('/login', [AuthenticatedSessionController::class, 'create'])->name('admin.login');
        Route::post('/login', [AuthenticatedSessionController::class, 'store'])->name('admin.login.store');
    });

    Route::middleware(['auth:admin', 'prevent-back-history'])->group(function (): void {
        Route::get('/dashboard', function () {
            return view('admin.dashboard');
        })->name('admin.dashboard');

        Route::post('/logout', [AuthenticatedSessionController::class, 'destroy'])->name('admin.logout');

        Route::resource('rooms', RoomController::class)
            ->except('show')
            ->names('admin.rooms');
    });
});