<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <title>Dashboard Admin</title>
</head>
<body>
    <h1>Dashboard Admin</h1>
    <p>Selamat datang, {{ auth('admin')->user()->nama }}.</p>

    <form method="POST" action="{{ route('admin.logout') }}">
        @csrf
        <button type="submit">Keluar</button>
    </form>
</body>
</html>