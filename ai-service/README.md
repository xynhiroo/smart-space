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
