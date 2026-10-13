# Smart Space Analytics Platform (PBLIF3-PD08)

Platform analitik pemanfaatan dan utilisasi ruang kelas/lab berbasis arsitektur **Hybrid**:
- **Backend Utama**: Laravel (REST API, CRUD Master Data Ruangan, Jadwal, Threshold, dan Autentikasi Multi-Guard).
- **AI & Analytics Engine**: Python FastAPI (Rule engine klasifikasi okupansi, generator data dummy sensor, analisis utilisasi).
- **Database**: MySQL (Shared database untuk kedua service).

---

## 🚀 Prasyarat Sistem

1. **PHP**: >= 8.2 (ekstensi `pdo_mysql`, `mbstring`, `openssl`, `curl`)
2. **Composer**: >= 2.x
3. **Node.js dan npm**: gunakan versi aktif proyek untuk asset frontend Vite/Tailwind
4. **Python**: >= 3.10
5. **MySQL / MariaDB**: v10.4+ (misal via XAMPP di port 3306)

---

## ⚙️ Panduan Setup & Menjalankan Service

### 1. Persiapan Database (MySQL)
Pastikan MySQL service telah aktif (misal melalui XAMPP Control Panel), lalu buat database:
```sql
CREATE DATABASE smart_space CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### 2. Backend Service (Laravel)

1. Masuk ke direktori `backend/`:
   ```bash
   cd backend
   ```
2. Pastikan file `.env` sudah terkonfigurasi:
   ```env
   DB_CONNECTION=mysql
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_DATABASE=smart_space
   DB_USERNAME=root
   DB_PASSWORD=
   ```
3. Install dependensi dan generate application key (jika baru di-clone):
   ```bash
   composer install
   npm install
   php artisan key:generate
   ```
4. Jalankan migrasi dan seeder:
   ```bash
   php artisan migrate:fresh --seed
   ```
   > **Catatan Seeder**:
   > - Mengimpor 10 ruangan fisik dari `backend/database/seed-data/rooms_if.csv`.
   > - Mengimpor 102 blok jadwal kuliah dari `backend/database/seed-data/schedules_if_gabungan.csv` (terhubung ke tabel `rooms`).
   > - Mengimpor 8 kalender akademik/pengecualian dari `backend/database/seed-data/calendar_exceptions_ganjil2627.csv`.
   > - Mengonfigurasi ambang batas final pada `threshold_settings` (rendah 0-40%, sedang 41-80%, tinggi 81-100%, evaluasi status kosong setelah slot jadwal selesai).
   > - Menginisialisasi akun awal untuk guard `admin` dan `mahasiswa`.
5. Jalankan server lokal:
   ```bash
   php artisan serve
   ```
   Aplikasi backend berjalan di: `http://127.0.0.1:8000`

6. Jalankan asset frontend untuk pengembangan:
   ```bash
   npm run dev
   ```
   Untuk build produksi:
   ```bash
   npm run build
   ```

7. Menjalankan pengujian otomatis:
   ```bash
   php artisan test
   ```

---

### 3. AI & Analytics Engine (Python FastAPI)

1. Masuk ke direktori `ai-service/`:
   ```bash
   cd ai-service
   ```
2. Buat virtual environment dan aktifkan:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Pastikan file `.env` sudah sesuai:
   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_DATABASE=smart_space
   DB_USERNAME=root
   DB_PASSWORD=
   DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/smart_space
   ```
5. Uji koneksi shared database & query tabel `rooms`:
   ```bash
   python test_db_connection.py
   ```
6. Jalankan API server FastAPI:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
   AI service berjalan di: `http://127.0.0.1:8001` (Dokumentasi Swagger di: `http://127.0.0.1:8001/docs`)

---

## 🔐 Akun Default untuk Pengujian Guard Autentikasi

> Akun dummy mahasiswa hanya disediakan untuk kebutuhan pengembangan dan pengujian lokal.

| Guard | Identifier | Password Default | Keterangan |
|---|---|---|---|
| **Admin** | `admin@smartspace.polibatam.ac.id` | `admin12345` | Guard `admin`, provider `admin_accounts` |
| **Mahasiswa** | `3312501036` | `password123` | Guard `mahasiswa`, provider `mahasiswa_accounts` |
| **Mahasiswa** | `3312501059` | `password123` | Guard `mahasiswa`, provider `mahasiswa_accounts` |
| **Mahasiswa** | `3312501001` | `password123` | Guard `mahasiswa`, provider `mahasiswa_accounts` |

---

## 🗄️ Skema Tabel Basis Data (Sprint 1)

1. `admin_accounts`: Akun administrator (`id`, `nama`, `email`, `password_hash`, timestamps).
2. `mahasiswa_accounts`: Akun simulasi mahasiswa (`id`, `nim`, `password_hash`, timestamps).
3. `rooms`: Master data ruangan (`id`, `nama_ruangan`, `kapasitas`, `lokasi`, `status`, timestamps).
4. `schedules`: Jadwal kuliah terhubung ke ruangan (`id`, `room_id`, `hari`, `jam_mulai`, `jam_selesai`, `mata_kuliah`, `kelas`, `dosen`, `shift`, timestamps).
5. `threshold_settings`: Konfigurasi ambang batas analitik (`id`, `key`, `value`, `keterangan`, timestamps).
6. `calendar_exceptions`: Pengecualian kalender akademik (`id`, `tanggal_mulai`, `tanggal_selesai`, `tipe`, `keterangan`, timestamps).
