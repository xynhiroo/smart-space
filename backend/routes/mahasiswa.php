<?php

use App\Http\Controllers\Mahasiswa\Auth\AuthenticatedSessionController;
use Illuminate\Support\Facades\Route;

Route::middleware('guest:mahasiswa')->group(function (): void {
    Route::get('/login', [AuthenticatedSessionController::class, 'create'])->name('mahasiswa.login');
    Route::post('/login', [AuthenticatedSessionController::class, 'store'])->name('mahasiswa.login.store');
});

Route::middleware(['auth:mahasiswa', 'prevent-back-history'])->group(function (): void {
    Route::get('/ruangan', function () {
        return view('mahasiswa.home');
    })->name('mahasiswa.home');

    Route::post('/logout', [AuthenticatedSessionController::class, 'destroy'])->name('mahasiswa.logout');
});
