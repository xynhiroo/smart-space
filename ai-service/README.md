# Smart Space AI Service

Layanan AI dan analitik untuk Smart Space Analytics Platform (PBLIF3-PD08, Politeknik Negeri Batam).

## Peran dan Batasan
- Layanan AI dibangun dengan FastAPI dan SQLAlchemy.
- **Larangan Skema**: Laravel adalah satu-satunya pengelola skema basis data melalui migrasi. Python hanya membaca dan menulis ke tabel yang ditentukan, tidak pernah membuat (`create_all`) atau mengubah skema (`drop_all`).
- Model SQLAlchemy di `app/models.py` mencerminkan tabel basis data bersama MySQL (`smart_space`).

## Persyaratan
- Python 3.11+ (atau Python 3.13)
- MySQL / MariaDB (XAMPP) yang sudah dimigrasi oleh Laravel

## Instalasi Dependensi
```bash
cd ai-service
pip install -r requirements.txt
```

## Konfigurasi Lingkungan (.env)
Pastikan berkas `.env` ada di direktori `ai-service/` dengan konfigurasi kredensial basis data bersama:
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=smart_space
DB_USERNAME=root
DB_PASSWORD=
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/smart_space
```

## Menjalankan Pengujian (pytest)

### 1. Menyiapkan Basis Data Pengujian (`smart_space_test`)
Pengujian otomatis di `ai-service` **selalu menggunakan basis data terisolasi `smart_space_test`**, bukan database development `smart_space`.

Pastikan database `smart_space_test` sudah dibuat di MySQL dan skema tabel dimigrasi oleh Laravel:
```bash
# Buat database jika belum ada (lewat MySQL client / phpMyAdmin):
mysql -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_test;"

# Jalankan migrasi skema Laravel ke database test:
# Dari direktori backend/ (PowerShell / Windows):
$env:DB_DATABASE="smart_space_test"; php artisan migrate

# Atau dari direktori backend/ (Bash / Linux / macOS):
DB_DATABASE=smart_space_test php artisan migrate
```

> **Catatan Pengaman Database:**
> Pengujian dilengkapi pengaman aktif di `conftest.py`. Pengujian akan langsung dibatalkan jika nama basis data target tidak berakhiran `_test`, sehingga mencegah risiko manipulasi atau penghapusan data pada database pengembangan/produksi.

### 2. Menjalankan Pengujian
Jalankan `pytest` dari root direktori repository atau langsung dari folder `ai-service`:

```bash
# Dari root repo:
python -m pytest ai-service/tests

# Atau dari folder ai-service/:
cd ai-service
pytest -v
# atau
python -m pytest -v
```

Hasil pengujian memverifikasi bahwa model `OccupancyLog`, `ClassificationResult`, `Room`, `Schedule`, dan `ThresholdSetting` berinteraksi dengan basis data bersama secara benar dan terisolasi dalam transaksi tanpa meninggalkan data sisa.

## Generator Data Dummy (SS1-08)

Modul generator berada di `app/generator/` dan digunakan untuk membangkitkan data dummy okupansi historis (`occupancy_logs`) beserta label kebenaran (*ground truth* CSV) untuk dataset `dev` dan `test`.

### 1. Persiapan Basis Data (`smart_space_ai_dev` & `smart_space_ai_test`)

Generator memerlukan basis data terpisah agar data simulasi tidak bercampur dengan database operasional Laravel (`smart_space`).

Buat database di MySQL (XAMPP):
```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_ai_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_ai_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Migrasikan skema dan isi data master (rooms, schedules, calendar_exceptions, threshold_settings) **SATU KALI SAJA** per database dari direktori `backend/`:

**Versi PowerShell (Windows):**
```powershell
# Migrasi dan seeding smart_space_ai_dev
$env:DB_DATABASE="smart_space_ai_dev"; php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE

# Migrasi dan seeding smart_space_ai_test
$env:DB_DATABASE="smart_space_ai_test"; php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE
```

**Versi Bash (Linux / macOS):**
```bash
# Migrasi dan seeding smart_space_ai_dev
DB_DATABASE=smart_space_ai_dev php artisan migrate:fresh --seed

# Migrasi dan seeding smart_space_ai_test
DB_DATABASE=smart_space_ai_test php artisan migrate:fresh --seed
```

> **Penting:** Pastikan environment variable `DB_DATABASE` dihapus atau tidak menetap agar perintah Laravel berikutnya tidak salah menimpa database target.

### 2. Menjalankan Generator

Jalankan generator dari folder `ai-service/` atau root direktori:

```bash
# Uji coba simulasi tanpa menulis ke DB maupun CSV (dry-run):
python -m app.generator --set dev --dry-run

# Pembangkitan data dev (menulis ke smart_space_ai_dev dan data/ground_truth/ground_truth_dev.csv):
python -m app.generator --set dev

# Pembangkitan data test (menulis ke smart_space_ai_test dan data/ground_truth/ground_truth_test.csv):
python -m app.generator --set test
```

**Opsi CLI Tambahan:**
- `--start YYYY-MM-DD`: Tanggal awal simulasi (default: `2026-09-07`).
- `--end YYYY-MM-DD`: Tanggal akhir simulasi (default: kemarin WIB).
- `--seed N`: Menentukan seed acak kustom (default: `1001` untuk dev, `2002` untuk test).
- `--dry-run`: Hanya mencetak ringkasan distribusi tanpa menyentuh DB atau membuat berkas CSV.
- `--allow-any-database`: Mengizinkan penulisan ke database di luar daftar resmi (`smart_space_ai_dev` dan `smart_space_ai_test`). Database aplikasi `smart_space` dilindungi secara default.
