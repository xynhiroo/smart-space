<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('landing');
})->name('landing');

require __DIR__.'/mahasiswa.php';
require __DIR__.'/admin.php';
