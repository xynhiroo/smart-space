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
- `--start YYYY-MM-DD`: Tanggal awal simulasi (default: `2026-09-07`, awal semester aktif).
- `--end YYYY-MM-DD`: Tanggal akhir simulasi (default: `2027-01-22`, akhir semester aktif).
- `--seed N`: Menentukan seed acak kustom (default: `1001` untuk dev, `2002` untuk test).
- `--dry-run`: Hanya mencetak ringkasan distribusi tanpa menyentuh DB atau membuat berkas CSV.
- `--allow-any-database`: Mengizinkan penulisan ke database di luar daftar resmi (`smart_space_ai_dev` dan `smart_space_ai_test`). Database aplikasi `smart_space` dilindungi secara default.

## Menjalankan Klasifikasi (SS1-11)

Modul runner klasifikasi berada di `app/classification/` dan digunakan untuk mengorkestrasi evaluasi status ruangan harian menggunakan sistem pakar Tier 1 secara idempoten dan menyimpannya ke tabel `classification_results`.

Jalankan klasifikasi dari folder `ai-service/` atau root direktori:

```bash
# Uji coba evaluasi tanpa menulis ke database (dry-run):
python -m app.classification --set dev --dry-run

# Menjalankan klasifikasi untuk dataset dev (semester penuh ke smart_space_ai_dev):
python -m app.classification --set dev

# Menjalankan klasifikasi untuk dataset test (semester penuh ke smart_space_ai_test):
python -m app.classification --set test
```

**Opsi CLI Tambahan:**
- `--start YYYY-MM-DD`: Tanggal awal evaluasi (default: `2026-09-07`, awal semester aktif).
- `--end YYYY-MM-DD`: Tanggal akhir evaluasi (default: `2027-01-22`, akhir semester aktif).
- `--waktu-evaluasi YYYY-MM-DDTHH:MM:SS`: Batas waktu evaluasi (default: hari sesudah `--end` pukul 00.00 WIB, agar seluruh sesi dalam rentang dinilai).
- `--dry-run`: Hanya mencetak ringkasan distribusi status tanpa menulis ke database (transaksi dibatalkan/rollback).
- `--allow-any-database`: Mengizinkan penulisan ke database di luar daftar dev/test (`smart_space_ai_dev` dan `smart_space_ai_test`). Database operasional `smart_space` terlindungi secara default.

## Menjalankan API (SS1-11)

API dijalankan dengan Uvicorn dari folder `ai-service/`:

```bash
python -m uvicorn app.main:app --port 8001
```

Dokumentasi interaktif (Swagger) ada di `http://127.0.0.1:8001/docs`.

API membaca database dari `ai-service/.env` (`smart_space` secara default). Database itu harus sudah dimigrasi dan di-seed lebih dulu, termasuk kunci `empty_min_occupied_minutes` dan `outside_schedule_min_minutes` di `threshold_settings`. Bila belum, `GET /utilization` menjawab 500 dengan pesan kunci yang hilang. Dari folder `backend/`:

```bash
php artisan migrate:fresh --seed
```

> `migrate:fresh` menghapus seluruh tabel di database tujuan. Pastikan variabel `DB_DATABASE` tidak tertinggal di terminal (`$env:DB_DATABASE` harus kosong).

### Endpoint

| Endpoint | Fungsi |
|---|---|
| `GET /health` | Status layanan |
| `GET /results` | Hasil klasifikasi pada rentang tanggal. Filter opsional: `room_id`, `status`, `limit` (maksimal 1000), `offset` |
| `GET /utilization` | Utilisasi dan statistik efisiensi per ruang pada rentang tanggal. Filter opsional: `room_id`. Episode di luar jadwal tidak ikut dihitung |

Tabel `classification_results` terisi setelah klasifikasi dijalankan. Sebelum itu, `/results` mengembalikan `total: 0` dan `/utilization` mengembalikan nilai kosong untuk semua ruang.

## Evaluasi Sistem Pakar terhadap Ground Truth (SS1-12)

Modul `app/evaluation/` mencocokkan hasil klasifikasi (`classification_results`) dengan ground truth generator (CSV) dan mencetak accuracy, precision, recall, F1 per kelas, matriks kebingungan, serta rincian galat. Modul ini hanya membaca database.

```bash
python -m app.generator --set dev
python -m app.classification --set dev
python -m app.evaluation --set dev
```

Opsi: `--set dev|test`, `--ground-truth JALUR`. Berkas CSV ground truth ada di `data/ground_truth/` dan tidak ikut ke git. Sesi dicocokkan lewat (`tanggal`, `room_id`, `schedule_id`). Episode di luar jadwal dicocokkan lewat irisan waktu. Hasil dan analisisnya ada di `docs/EVALUASI_AI.md`.

Set test hanya boleh dievaluasi setelah ambang final ditetapkan dari set dev.

## Evaluasi Sistem Pakar terhadap Ground Truth (SS1-12)

Modul `app/evaluation/` mencocokkan hasil klasifikasi (`classification_results`) dengan ground truth generator (CSV) dan mencetak accuracy, precision, recall, F1 per kelas, matriks kebingungan, serta rincian galat. Modul ini hanya membaca database.

```bash
python -m app.generator --set dev
python -m app.classification --set dev
python -m app.evaluation --set dev
```

Opsi: `--set dev|test`, `--ground-truth JALUR`. Berkas CSV ground truth ada di `data/ground_truth/` dan tidak ikut ke git. Sesi dicocokkan lewat (`tanggal`, `room_id`, `schedule_id`). Episode di luar jadwal dicocokkan lewat irisan waktu. Hasil dan analisisnya ada di `docs/EVALUASI_AI.md`.

Set test hanya boleh dievaluasi setelah ambang final ditetapkan dari set dev.
