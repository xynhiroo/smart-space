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
Pengujian otomatis menggunakan `pytest` untuk memverifikasi integritas model SQLAlchemy terhadap skema basis data:

```bash
# Dari root repo:
python -m pytest ai-service/tests

# Atau dari folder ai-service:
cd ai-service
pytest
# atau
python -m pytest
```

Hasil pengujian memastikan model `OccupancyLog`, `ClassificationResult`, `Room`, `Schedule`, dan `ThresholdSetting` dapat melakukan query ke basis data bersama tanpa kesalahan skema.
