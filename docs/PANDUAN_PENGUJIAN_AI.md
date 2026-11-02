# Panduan Pengujian Menyeluruh: Sisi AI Smart Space Analytics Platform (PBLIF3-PD08)

| | |
|---|---|
| **Versi** | 1.0, 28 Oktober 2026 |
| **Pemilik** | Rangga Surya Saputra (reviewer: Muradika Laksamana Putra) |
| **Berlaku untuk** | `main` setelah PR #63 (runner klasifikasi) dan branch `feature/ss1-14-model-risiko-sesi-kosong` (belum ter-merge) |
| **Acuan** | `docs/DATA_CONTRACT.md`, `docs/DATA_CARD.md`, `docs/BACKLOG.md`, `ai-service/README.md`, `ai-service/app/ml/README.md` |
| **Lingkup** | Seluruh komponen AI/analitik: skema data AI, generator dummy, sistem pakar, utilisasi, runner klasifikasi, API FastAPI, model ML, serta regresi Laravel yang berbagi database |

Panduan ini membuktikan bahwa kode AI berjalan benar, aman, dan reprodusibel dari awal sampai akhir. Seluruh perintah ditulis untuk Windows PowerShell dengan XAMPP.

---

## 0. Cara memakai dokumen ini

**Aturan emas (baca sebelum mulai):**

1. Kerjakan berurutan dari Tahap A sampai L. Tahap berikutnya memakai hasil tahap sebelumnya.
2. Jangan menjalankan `php artisan test` dan `pytest` bersamaan. Keduanya memakai database `smart_space_test`.
3. MySQL hanya boleh dinyalakan dari **XAMPP Control Panel**. Jangan menyalakan `mysqld` manual dan jangan memakai `--skip-grant-tables`.
4. Database set **test** (`smart_space_ai_test`) hanya dibaca untuk pengecekan jumlah dan konsistensi. **Jangan menjalankan `python -m app.ml evaluasi-akhir` lagi** (sudah dijalankan; hasilnya tercatat di Bagian 17).
5. Jangan mengubah kode, aturan, atau ambang berdasarkan hasil pengujian di set test.
6. Setiap uji punya ID (A1, B3, dan seterusnya). Catat hasilnya di lembar catat (Bagian 15). Uji yang gagal: simpan pesan error lengkap dan jangan lanjut ke tahap yang bergantung padanya.

**Penanda status komponen:**

| Penanda | Arti |
|---|---|
| `[MAIN]` | Sudah ada di `main` |
| `[BRANCH SS1-14]` | Hanya ada di branch SS1-14 (checkout dulu; belum ter-merge) |
| `[BELUM]` | Belum dibangun; hanya kerangka uji untuk nanti |

**Angka acuan** di dokumen ini berasal dari laporan pengerjaan dan `DATA_CARD.md`. Bila kartu lain (mis. SS1-12) mengubah data, angka bisa bergeser; catat selisihnya, jangan memaksa angkanya sama.

---

## 1. Peta komponen dan status

| Komponen | Kartu | Lokasi kode | Cara menjalankan | Status |
|---|---|---|---|---|
| Skema data AI (`occupancy_logs`, `classification_results`) | SS1-07 | `backend/database/migrations/` | `php artisan migrate` | `[MAIN]` |
| Seeder jadwal idempoten | SS1-05 | `backend/database/seeders/` | `php artisan db:seed` | `[MAIN]` |
| Generator data dummy | SS1-08 | `ai-service/app/generator/` | `python -m app.generator --set dev|test` | `[MAIN]` |
| Sistem pakar (Tier 1) | SS1-09 | `ai-service/app/expert_system/` | Fungsi `klasifikasikan_hari(...)` | `[MAIN]` |
| Utilisasi dan statistik | SS1-10 | `ai-service/app/analytics/utilization.py` | Fungsi murni | `[MAIN]` |
| Runner klasifikasi | SS1-11 (bagian) | `ai-service/app/classification/runner.py` | `python -m app.classification --set dev|test` | `[MAIN]` |
| API `GET /health`, `/results`, `/utilization` | SS1-11 | `ai-service/app/api/` | `uvicorn app.main:app --port 8001` | `[MAIN]` |
| API `POST /classify` | SS1-11 | belum ada | | `[BELUM]` |
| Validasi akurasi sistem pakar | SS1-12 | notebook dan `docs/EVALUASI_AI.md` | | `[BELUM]` (sedang dikerjakan) |
| Model ML risiko sesi kosong | SS1-14 | `ai-service/app/ml/` | `python -m app.ml latih --set dev` | `[BRANCH SS1-14]` |
| API `POST /predict/risk` | SS1-14 | `ai-service/app/api/prediksi.py` | `uvicorn` | `[BRANCH SS1-14]` |

---

## 2. Persiapan lingkungan

### 2.1 Perangkat yang diperlukan
- Windows PowerShell, XAMPP (MySQL/MariaDB), PHP, Composer, Python 3.11 atau lebih baru, Git.
- Repository ada di `d:\xampp\htdocs\Smart-Space`.

### 2.2 Variabel bantu (jalankan sekali di tiap jendela PowerShell)
```powershell
$MYSQL = "d:\xampp\mysql\bin\mysql.exe"
$REPO  = "d:\xampp\htdocs\Smart-Space"
Set-Location $REPO
```
Untuk query SQL yang panjang, buka klien interaktif lalu tempel query-nya (menghindari masalah tanda kutip PowerShell):
```powershell
& $MYSQL -u root smart_space_ai_dev
# ketik exit; untuk keluar
```

### 2.3 Pemeriksaan MySQL (wajib)
Nyalakan MySQL dari XAMPP Control Panel, lalu:
```powershell
Get-CimInstance Win32_Process -Filter "Name='mysqld.exe' OR Name='mariadbd.exe'" | Select-Object ProcessId, Name, CommandLine
netstat -ano | findstr :3306
```
**Harapan:** tepat satu proses dari `d:\xampp\mysql\bin\`, dan `CommandLine` tidak memuat `--skip-grant-tables`. Jika ada proses lain atau flag itu, matikan lewat `& d:\xampp\mysql\bin\mysqladmin.exe -u root shutdown`, lalu nyalakan ulang dari XAMPP.

### 2.4 Python dan dependensi
```powershell
Set-Location $REPO\ai-service
python --version            # 3.11 atau lebih baru
pip install -r requirements.txt
pip check                   # harus: No broken requirements found.
```
Setelah checkout branch SS1-14, jalankan `pip install -r requirements.txt` lagi (menambah scikit-learn, pandas, numpy, joblib). Untuk notebook: `pip install -r requirements-notebook.txt`.

### 2.5 File `.env`
`ai-service/.env` harus ada (lihat `ai-service/README.md`). Jangan pernah di-commit:
```powershell
Set-Location $REPO
git ls-files | findstr /i "\.env"        # hanya .env.example yang boleh muncul
```

### 2.6 Empat database
| Database | Fungsi | Diisi oleh |
|---|---|---|
| `smart_space` | Aplikasi Laravel (dev harian) | Laravel |
| `smart_space_test` | PHPUnit dan pytest (terisolasi) | Test otomatis |
| `smart_space_ai_dev` | Set dev: merancang dan menyetel | Generator, runner, ML latih |
| `smart_space_ai_test` | Set test: evaluasi akhir sekali | Generator, runner |

Buat dan siapkan bila belum ada (lihat `ai-service/README.md`):
```powershell
& $MYSQL -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_ai_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
& $MYSQL -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_ai_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
& $MYSQL -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
Set-Location $REPO\backend
$env:DB_DATABASE="smart_space_ai_dev";  php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE
$env:DB_DATABASE="smart_space_ai_test"; php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE
$env:DB_DATABASE="smart_space_test";    php artisan migrate; Remove-Item Env:DB_DATABASE
```
**Peringatan:** `migrate:fresh` menghapus seluruh tabel di database tujuan. Pastikan `echo $env:DB_DATABASE` kosong setelahnya.

### 2.7 Folder skrip uji
Skrip di panduan ini disimpan di luar repository supaya tidak ikut ter-commit:
```powershell
New-Item -ItemType Directory -Force C:\temp\uji_ai | Out-Null
```
Menjalankan skrip dari folder `ai-service` agar `import app...` berhasil:
```powershell
Set-Location $REPO\ai-service
$env:PYTHONPATH = (Get-Location).Path
python C:\temp\uji_ai\nama_skrip.py
```

---

## 3. Tahap A: Smoke test cepat (sekitar 5 menit)

| ID | Perintah | Harapan |
|---|---|---|
| A1 | `Set-Location $REPO\ai-service; python -m pytest -q` | Semua lulus. `[MAIN]`: sekitar 119 test (atau lebih bila ada PR lain). `[BRANCH SS1-14]`: 143 test. Tidak ada `failed` atau `error`. Jika muncul pesan "PENGAMAN AKTIF", cek nama database test. |
| A2 | `Set-Location $REPO\backend; php artisan test` | 58 test lulus (295 assertions), atau lebih bila ada PR lain. |

Jalankan A1 dan A2 **bergantian**, tidak bersamaan.

---

## 4. Tahap B: Database, seeder, dan skema

Gunakan klien interaktif di `smart_space_ai_dev` kecuali dinyatakan lain.

| ID | Uji | Cara | Harapan |
|---|---|---|---|
| B1 | Empat database ada | `& $MYSQL -u root -e "SHOW DATABASES LIKE 'smart_space%';"` | `smart_space`, `smart_space_ai_dev`, `smart_space_ai_test`, `smart_space_test` |
| B2 | Data master | `SELECT COUNT(*) FROM rooms; SELECT COUNT(*) FROM schedules; SELECT COUNT(*) FROM threshold_settings;` (di dev dan test) | rooms 10, schedules 102, threshold_settings 9 |
| B3 | Kunci threshold | `SELECT * FROM threshold_settings;` | Ada `empty_min_occupied_minutes` = 10, `outside_schedule_min_minutes` = 30, `utilization_low_max` = 40, `utilization_medium_max` = 80. **Tidak ada** `empty_status_use_start_tolerance`. |
| B4 | Seeder idempoten | Di `backend`: `php artisan db:seed` dua kali (pada `smart_space`), lalu hitung rooms dan schedules | Tetap 10 dan 102, tanpa error |
| B5 | Batasan skema | Lihat blok SQL di bawah | Tiga percobaan terakhir **harus error** |
| B6 | Zona waktu | `Set-Location $REPO\backend; php artisan tinker --execute="echo config('app.timezone').' '.now();"` | `Asia/Jakarta` dan jam sama dengan jam di komputer |
| B7 | Integritas jadwal | Lihat blok SQL di bawah | Kedua query menghasilkan 0 |

**B5 (di klien interaktif, database `smart_space_ai_dev`; gunakan transaksi agar bersih):**
```sql
START TRANSACTION;
INSERT INTO occupancy_logs (room_id, slot_mulai, is_occupied) VALUES ((SELECT MIN(id) FROM rooms), '2026-09-07 07:00:00', 1);
INSERT INTO occupancy_logs (room_id, slot_mulai, is_occupied) VALUES ((SELECT MIN(id) FROM rooms), '2026-09-07 07:00:00', 0);   -- harus ERROR 1062 (duplikat)
INSERT INTO occupancy_logs (room_id, slot_mulai, is_occupied) VALUES (999999, '2026-09-07 07:10:00', 1);                          -- harus ERROR 1452 (FK)
ROLLBACK;
```
Setelah `ROLLBACK`, uji kunci unik `classification_results` (harus error pada percobaan kedua, lalu rollback):
```sql
START TRANSACTION;
INSERT INTO classification_results (room_id, schedule_id, tanggal, waktu_mulai, waktu_selesai, status, menit_terjadwal, menit_terpakai, utilisasi_pct, rule_id, penjelasan, computed_at)
VALUES ((SELECT MIN(id) FROM rooms), NULL, '2099-01-01', '10:00:00', '10:30:00', 'dipakai_di_luar_jadwal', 0, 30, NULL, 'R03', 'uji', NOW());
INSERT INTO classification_results (room_id, schedule_id, tanggal, waktu_mulai, waktu_selesai, status, menit_terjadwal, menit_terpakai, utilisasi_pct, rule_id, penjelasan, computed_at)
VALUES ((SELECT MIN(id) FROM rooms), NULL, '2099-01-01', '10:00:00', '10:40:00', 'dipakai_di_luar_jadwal', 0, 40, NULL, 'R03', 'uji', NOW());   -- harus ERROR 1062
ROLLBACK;
```
Pastikan tidak ada sisa data: `SELECT COUNT(*) FROM classification_results WHERE tanggal = '2099-01-01';` harus 0.

**B7:**
```sql
-- jam jadwal bukan kelipatan 10 menit
SELECT COUNT(*) FROM schedules WHERE MINUTE(jam_mulai) % 10 <> 0 OR MINUTE(jam_selesai) % 10 <> 0;
-- jadwal tumpang tindih pada ruang dan hari yang sama
SELECT a.id, b.id FROM schedules a JOIN schedules b
  ON a.room_id = b.room_id AND a.hari = b.hari AND a.id < b.id
 AND a.jam_mulai < b.jam_selesai AND b.jam_mulai < a.jam_selesai;
```

---

## 5. Tahap C: Generator data dummy (SS1-08) `[MAIN]`

Jalankan dari `ai-service`.

| ID | Uji | Perintah / cara | Harapan |
|---|---|---|---|
| C1 | Uji coba tanpa menulis | `python -m app.generator --set dev --dry-run` | Ringkasan tercetak; tidak ada perubahan di DB. Banner menyatakan data simulasi. |
| C2 | Bangkitkan set dev dan test | `python -m app.generator --set dev` lalu `python -m app.generator --set test` | Selesai tanpa error (beberapa menit) |
| C3 | Jumlah baris | `SELECT COUNT(*) FROM occupancy_logs;` di dev dan test | Dev **93.063**, test **93.112** |
| C4 | Aturan grid waktu | Blok SQL C4 di bawah | Hasil sesuai komentar |
| C5 | Okupansi per ruang (dev) | Blok SQL C5 | Mendekati tabel acuan di Lampiran 17.2 |
| C6 | Determinisme | Skrip `cek_hash.py` (Bagian 5.1); jalankan dua kali | Jumlah dan hash sama pada kedua run |
| C7 | Ground truth CSV | Bagian 5.2 | Dev 2.010 baris, test 2.007 baris, distribusi sesuai |
| C8 | Argumen tidak sah | `python -m app.generator --set prod` | Ditolak oleh argparse (pesan "invalid choice"), tidak menyentuh DB |

**Blok SQL C4 (di dev):**
```sql
SELECT COUNT(*) FROM occupancy_logs WHERE TIME(slot_mulai) = '17:00:00';                         -- harus 0 (jeda 17.00)
SELECT COUNT(*) FROM occupancy_logs WHERE MINUTE(slot_mulai) % 10 <> 0 OR SECOND(slot_mulai) <> 0; -- harus 0
SELECT MIN(TIME(slot_mulai)), MAX(TIME(slot_mulai)) FROM occupancy_logs;                         -- 07:00:00 dan 22:50:00
SELECT MIN(DATE(slot_mulai)), MAX(DATE(slot_mulai)) FROM occupancy_logs;                         -- 2026-09-07 dan 2027-01-22
SELECT COUNT(*) FROM occupancy_logs WHERE DAYOFWEEK(slot_mulai) IN (1, 7);                       -- harus 0 (hanya Senin sampai Jumat)
SELECT DISTINCT source FROM occupancy_logs;                                                      -- hanya 'dummy'
```

**Blok SQL C5:**
```sql
SELECT room_id, COUNT(*) AS total_slot, SUM(is_occupied) AS terisi,
       ROUND(100 * SUM(is_occupied) / COUNT(*), 2) AS okupansi_pct
FROM occupancy_logs GROUP BY room_id ORDER BY room_id;
```

### 5.1 Skrip `C:\temp\uji_ai\cek_hash.py`
```python
"""Hash occupancy_logs dan classification_results untuk set dev atau test (baca saja)."""
import hashlib
import sys
from datetime import datetime

from app.generator.repository import create_db_session_factory, resolve_database_url
from app.models import ClassificationResult, OccupancyLog

nama_set = sys.argv[1] if len(sys.argv) > 1 else "dev"
url, nama_db = resolve_database_url(target_set=nama_set)
mesin, Sesi = create_db_session_factory(url)
sesi = Sesi()
print("Database:", nama_db)


def hash_okupansi(batas=None):
    kueri = sesi.query(OccupancyLog.room_id, OccupancyLog.slot_mulai, OccupancyLog.is_occupied)
    if batas is not None:
        kueri = kueri.filter(OccupancyLog.slot_mulai < batas)
    baris = kueri.order_by(OccupancyLog.room_id, OccupancyLog.slot_mulai).all()
    h = hashlib.sha256()
    for r in baris:
        h.update(f"{r[0]}:{r[1].isoformat()}:{r[2]}\n".encode())
    return len(baris), h.hexdigest()


def hash_klasifikasi():
    baris = (
        sesi.query(ClassificationResult)
        .order_by(ClassificationResult.room_id, ClassificationResult.tanggal, ClassificationResult.waktu_mulai)
        .all()
    )
    h = hashlib.sha256()
    for r in baris:
        h.update(f"{r.room_id}|{r.tanggal}|{r.waktu_mulai}|{r.status}|{r.menit_terpakai}\n".encode())
    return len(baris), h.hexdigest()


print("okupansi (semua)         :", *hash_okupansi())
print("okupansi (< 2026-10-17)  :", *hash_okupansi(datetime(2026, 10, 17)))
print("klasifikasi              :", *hash_klasifikasi())
sesi.close()
mesin.dispose()
```
Cara menjalankan: `python C:\temp\uji_ai\cek_hash.py dev` (setelah mengatur `PYTHONPATH`, Bagian 2.7).

**Harapan set dev** (acuan Lampiran 17.1):
- okupansi (semua): 93063 baris, hash `00e20073e875a91b1e266a9f2a6f13be8274d98d27a3c303832d94145af8eb68`
- okupansi (< 2026-10-17): 27911 baris, hash `1bd2dd2f5aa32e70ca565475944218f8bb35b833ea4be490494aeaa71e757136`
- klasifikasi: diuji pada Tahap F.

### 5.2 Ground truth CSV
```powershell
Set-Location $REPO\ai-service
(Import-Csv data\ground_truth\ground_truth_dev.csv).Count        # 2010
(Import-Csv data\ground_truth\ground_truth_test.csv).Count       # 2007
Import-Csv data\ground_truth\ground_truth_dev.csv | Group-Object status_benar | Select-Object Name, Count
Import-Csv data\ground_truth\ground_truth_dev.csv | Group-Object penyebab | Select-Object Name, Count
Import-Csv data\ground_truth\ground_truth_dev.csv | Get-Member -MemberType NoteProperty | Select-Object Name
```
**Harapan (dev):** `sesuai_jadwal` 1704, `kosong_meski_terjadwal` 255, `dipakai_di_luar_jadwal` 51. Penyebab: `kelas_berlangsung` 1402, `tidak_hadir` 255, `selesai_awal` 136, `terlambat` 122, `pemakaian_luar_jadwal` 51, `dipinjam_kegiatan_lain` 44. Kolom: `tanggal, room_id, schedule_id, waktu_mulai, waktu_selesai, status_benar, penyebab`.

Hari libur tidak boleh punya baris sesi:
```powershell
Import-Csv data\ground_truth\ground_truth_dev.csv |
  Where-Object { $_.tanggal -in @('2026-12-24','2026-12-25','2027-01-01','2027-01-05') -and $_.schedule_id } |
  Measure-Object | Select-Object Count      # harus 0
```
Pastikan folder `data/` tidak ter-track git: `git check-ignore -v ai-service/data` (harus menunjukkan aturan ignore).

---

## 6. Tahap D: Sistem pakar (SS1-09) `[MAIN]`

| ID | Uji | Cara | Harapan |
|---|---|---|---|
| D1 | Unit test sistem pakar | `python -m pytest tests/test_expert_system.py -v` | 24 test lulus (tiap aturan F.., R01 sampai R03, kasus batas, jeda 17.00, slot hilang, hari libur, determinisme, tanpa literal ambang) |
| D2 | Skrip skenario manual | Bagian 6.1 | Semua baris `[LULUS]` |
| D3 | Tidak membaca ground truth | `git grep -n ground_truth ai-service/app/expert_system` | Tidak ada hasil |
| D4 | Tidak ada angka ambang di kode | `git grep -n -E "\b(10|30)\b" ai-service/app/expert_system` | Hanya muncul di komentar, docstring, README (bukan di logika) |
| D5 | Kesesuaian dengan kontrak | Baca `docs/DATA_CONTRACT.md` Bagian 11.2 dan 12 lalu bandingkan dengan `app/expert_system/tipe.py` dan `basis_pengetahuan.py` | Nama tipe, fungsi, aturan F01 sampai F04 dan R01 sampai R03 sama |

### 6.1 Skrip `C:\temp\uji_ai\skenario_sistem_pakar.py`
Skrip ini menguji perilaku utama dengan data buatan sendiri. Bila ada error nama (impor, atribut), tempel pesannya ke chat.
```python
"""Skenario manual sistem pakar: satu ruang, jadwal Senin 08.00-10.00."""
import random
import sys
from datetime import date, datetime, time, timedelta

from app.expert_system.klasifikasi import klasifikasikan_hari
from app.expert_system.tipe import Ambang, FaktaJadwal, FaktaRuang, SlotOkupansi

SENIN = date(2026, 9, 7)
JUMAT = date(2026, 9, 11)
RUANG = FaktaRuang(room_id=1, nama_ruangan="GU 604", is_open_space=False)
AMBANG = Ambang(empty_min_occupied_minutes=10, outside_schedule_min_minutes=30,
                batas_rendah=40.0, batas_sedang=80.0)
JADWAL_SENIN = [FaktaJadwal(schedule_id=1, room_id=1, hari="Senin", jam_mulai=time(8, 0),
                            jam_selesai=time(10, 0), mata_kuliah="Kecerdasan Buatan")]


def slots(mulai, selesai, terisi, tanggal=SENIN):
    t = datetime.combine(tanggal, mulai)
    akhir = datetime.combine(tanggal, selesai)
    hasil = []
    while t < akhir:
        hasil.append(SlotOkupansi(room_id=1, slot_mulai=t, is_occupied=terisi))
        t += timedelta(minutes=10)
    return hasil


def jalankan(slot_list, ambang=AMBANG, tanggal=SENIN, waktu=None, libur=False, jadwal=JADWAL_SENIN):
    waktu = waktu or datetime.combine(tanggal, time(23, 0))
    return klasifikasikan_hari(ruang=RUANG, daftar_jadwal=jadwal, slot_list=slot_list,
                               tanggal=tanggal, waktu_evaluasi=waktu, ambang=ambang, is_holiday=libur)


gagal = 0


def cek(nama, kondisi, rinci=""):
    global gagal
    if not kondisi:
        gagal += 1
    print(f"[{'LULUS' if kondisi else 'GAGAL'}] {nama} {rinci}")


# S1: kelas terisi penuh
r = jalankan(slots(time(8, 0), time(10, 0), True))
cek("S1 sesi terisi penuh = sesuai_jadwal R01",
    len(r) == 1 and r[0].status == "sesuai_jadwal" and r[0].rule_id == "R01"
    and r[0].menit_terjadwal == 120 and r[0].menit_terpakai == 120, f"-> {[(h.status, h.rule_id) for h in r]}")

# S2: kelas kosong
r = jalankan(slots(time(8, 0), time(10, 0), False))
cek("S2 sesi kosong = kosong_meski_terjadwal R02",
    len(r) == 1 and r[0].status == "kosong_meski_terjadwal" and r[0].rule_id == "R02"
    and r[0].menit_terpakai == 0, f"-> {r[0].penjelasan if r else ''}")
cek("S2b penjelasan R02 menyebut TU (informasi saja)", bool(r) and "TU" in r[0].penjelasan)

# S3: sesi terisi + pemakaian 40 menit di luar jadwal
r = jalankan(slots(time(8, 0), time(10, 0), True) + slots(time(12, 0), time(12, 40), True))
cek("S3 episode 40 menit di luar jadwal = R03",
    len(r) == 2 and r[1].status == "dipakai_di_luar_jadwal" and r[1].rule_id == "R03"
    and r[1].schedule_id is None and r[1].menit_terpakai == 40 and r[1].menit_terjadwal == 0
    and r[1].waktu_mulai == time(12, 0) and r[1].waktu_selesai == time(12, 40),
    f"-> {r[1].penjelasan if len(r) > 1 else ''}")

# S4: batas ambang 10 menit (pembanding <, bukan <=)
s = slots(time(8, 0), time(10, 0), False)
s[5] = SlotOkupansi(room_id=1, slot_mulai=s[5].slot_mulai, is_occupied=True)
r10 = jalankan(s)
r20 = jalankan(s, ambang=Ambang(20, 30, 40.0, 80.0))
cek("S4 terisi tepat 10 menit pada ambang 10 = sesuai_jadwal",
    r10[0].menit_terpakai == 10 and r10[0].status == "sesuai_jadwal")
cek("S4b ambang dinaikkan ke 20 mengubah hasil menjadi kosong_meski_terjadwal (bukan hard-code)",
    r20[0].status == "kosong_meski_terjadwal")

# S5 dan S6: batas durasi episode 30 menit
r = jalankan(slots(time(8, 0), time(10, 0), True) + slots(time(12, 0), time(12, 20), True))
cek("S5 episode 20 menit tidak ditandai", len(r) == 1)
r = jalankan(slots(time(8, 0), time(10, 0), True) + slots(time(12, 0), time(12, 30), True))
cek("S6 episode 30 menit ditandai", len(r) == 2 and r[1].status == "dipakai_di_luar_jadwal")

# S7: slot hilang memutus episode (keterbatasan yang tercatat)
ep = [x for x in slots(time(12, 0), time(12, 40), True) if x.slot_mulai.time() != time(12, 20)]
r = jalankan(slots(time(8, 0), time(10, 0), True) + ep)
cek("S7 slot hilang di tengah episode 40 menit memecahnya sehingga tidak ditandai", len(r) == 1)

# S8: waktu evaluasi
r = jalankan(slots(time(8, 0), time(10, 0), True), waktu=datetime(2026, 9, 7, 9, 50))
cek("S8 sesi belum berakhir tidak dinilai", r == [])
r = jalankan(slots(time(8, 0), time(10, 0), True), waktu=datetime(2026, 9, 7, 10, 0))
cek("S8b sesi berakhir tepat pada waktu evaluasi dinilai", len(r) == 1 and r[0].status == "sesuai_jadwal")

# S9: hari libur
r = jalankan(slots(time(8, 0), time(10, 0), True) + slots(time(12, 0), time(12, 40), True), libur=True)
cek("S9 hari libur: tidak ada baris sesi, hanya episode di luar jadwal",
    len(r) >= 1 and all(h.schedule_id is None and h.status == "dipakai_di_luar_jadwal" for h in r),
    f"-> {len(r)} episode")

# S10: ruang tanpa jadwal pada hari itu
jadwal_selasa = [FaktaJadwal(schedule_id=2, room_id=1, hari="Selasa", jam_mulai=time(8, 0),
                             jam_selesai=time(10, 0), mata_kuliah="Lain")]
r = jalankan(slots(time(8, 0), time(10, 0), True), jadwal=jadwal_selasa)
cek("S10 jadwal hari lain tidak dievaluasi; okupansi menjadi episode di luar jadwal",
    len(r) == 1 and r[0].status == "dipakai_di_luar_jadwal" and r[0].menit_terpakai == 120)

# S11: nama hari Jum'at dan Jumat
for ejaan in ("Jum'at", "Jumat", "JUM'AT"):
    jadwal = [FaktaJadwal(schedule_id=3, room_id=1, hari=ejaan, jam_mulai=time(8, 0),
                          jam_selesai=time(10, 0), mata_kuliah="Jumat")]
    r = jalankan(slots(time(8, 0), time(10, 0), True, tanggal=JUMAT), tanggal=JUMAT, jadwal=jadwal)
    cek(f"S11 ejaan hari '{ejaan}' cocok dengan hari Jumat", len(r) == 1 and r[0].schedule_id == 3)

# S12 dan S13: determinisme, urutan masukan, dan masukan tidak berubah
data = slots(time(8, 0), time(10, 0), True) + slots(time(12, 0), time(12, 40), True)
r1 = jalankan(data)
acak = list(data)
random.Random(42).shuffle(acak)
salinan = list(acak)
r2 = jalankan(acak)
cek("S12 urutan slot diacak tidak mengubah hasil", r1 == r2)
cek("S13 masukan tidak dimutasi", acak == salinan)

print(f"\nGagal: {gagal}")
sys.exit(1 if gagal else 0)
```
Jalankan: `python C:\temp\uji_ai\skenario_sistem_pakar.py` (dengan `PYTHONPATH`, Bagian 2.7). **Harapan:** semua `[LULUS]`, `Gagal: 0`.

---

## 7. Tahap E: Utilisasi dan statistik (SS1-10) `[MAIN]`

| ID | Uji | Cara | Harapan |
|---|---|---|---|
| E1 | Unit test | `python -m pytest tests/test_utilization.py -v` | 18 test lulus |
| E2 | Skrip batas kategori dan bobot | Bagian 7.1 | Semua `[LULUS]` |
| E3 | Konsistensi dengan SQL | Lihat Tahap G (G7) | API sama dengan hitungan SQL |

### 7.1 Skrip `C:\temp\uji_ai\cek_utilisasi.py`
```python
"""Batas kategori, rumus berbobot, dan kasus tepi utilisasi."""
import sys
from datetime import date

from app.analytics.utilization import Sesi, hitung_statistik_ruang, hitung_utilisasi_pct, tentukan_kategori

gagal = 0


def cek(nama, kondisi, rinci=""):
    global gagal
    if not kondisi:
        gagal += 1
    print(f"[{'LULUS' if kondisi else 'GAGAL'}] {nama} {rinci}")


cek("rumus 60 dari 120 menit = 50.0", hitung_utilisasi_pct(120, 60) == 50.0)
cek("menit terjadwal nol = None", hitung_utilisasi_pct(0, 0) is None)
cek("40.0 = rendah", tentukan_kategori(40.0, 40.0, 80.0) == "rendah")
cek("40.01 = sedang", tentukan_kategori(40.01, 40.0, 80.0) == "sedang")
cek("80.0 = sedang", tentukan_kategori(80.0, 40.0, 80.0) == "sedang")
cek("80.01 = tinggi", tentukan_kategori(80.01, 40.0, 80.0) == "tinggi")
cek("0 = rendah", tentukan_kategori(0.0, 40.0, 80.0) == "rendah")
cek("100 = tinggi", tentukan_kategori(100.0, 40.0, 80.0) == "tinggi")
cek("None = None", tentukan_kategori(None, 40.0, 80.0) is None)

try:
    hitung_utilisasi_pct(60, 61)
    print("[INFO] menit terpakai > terjadwal tidak melempar galat")
except ValueError:
    print("[INFO] menit terpakai > terjadwal melempar ValueError (sesuai invarian)")

# Rata-rata terbobot, bukan rata-rata persentase: 60/60 (100%) dan 0/180 (0%)
sesi = [
    Sesi(room_id=1, tanggal=date(2026, 9, 7), menit_terjadwal=60, menit_terpakai=60),
    Sesi(room_id=1, tanggal=date(2026, 9, 8), menit_terjadwal=180, menit_terpakai=0),
]
hasil = hitung_statistik_ruang(sesi=sesi, tanggal_mulai=date(2026, 9, 7), tanggal_selesai=date(2026, 9, 8),
                               batas_rendah=40.0, batas_sedang=80.0)
st = hasil[1]
cek("utilisasi periode berbobot = 60/240 = 25.0 (bukan rata-rata 50.0)", st.utilisasi_pct == 25.0, f"-> {st.utilisasi_pct}")
cek("kategori periode = rendah", st.kategori == "rendah")
cek("selisih menit = 180", st.selisih_menit == 180)
cek("rata-rata harian = 50.0, min 0.0, maks 100.0",
    (st.rata_rata_harian_pct, st.min_harian_pct, st.max_harian_pct) == (50.0, 0.0, 100.0))

print(f"\nGagal: {gagal}")
sys.exit(1 if gagal else 0)
```
**Harapan:** semua `[LULUS]`, `Gagal: 0`.

---

## 8. Tahap F: Runner klasifikasi (SS1-11 bagian runner) `[MAIN]`

Prasyarat: Tahap C selesai (set dev dan test terisi). Jalankan dari `ai-service`.

| ID | Uji | Perintah / cara | Harapan |
|---|---|---|---|
| F1 | Dry-run | `python -m app.classification --set dev --dry-run` | Ringkasan status tercetak; `SELECT COUNT(*) FROM classification_results;` tetap 0 |
| F2 | Jalankan dev dan test | `python -m app.classification --set dev` lalu `--set test` | Tanpa error |
| F3 | Jumlah baris | `SELECT status, COUNT(*) FROM classification_results GROUP BY status;` | Dev: `sesuai_jadwal` 1745, `kosong_meski_terjadwal` 214, `dipakai_di_luar_jadwal` 59 (total 2018). Test: 1714, 245, 54 (total 2013). Jumlah sesi di kedua set tepat 1959. |
| F4 | Invarian data | Blok SQL F4 | Semua hitungan 0 kecuali yang dinyatakan |
| F5 | Idempoten | Jalankan `--set dev` dua kali lalu `cek_hash.py dev` (baris "klasifikasi") | Jumlah dan hash sama pada kedua run. Acuan: 2018 baris, `0eaf401c75f9a4c59cd18464b8771fca86b2281c849858846f9e48261a1a7956` |
| F6 | Dibandingkan ground truth (dev, baca saja) | Skrip Bagian 8.1 | Cocok dengan angka acuan |
| F7 | Database aplikasi tidak tersentuh | `SELECT COUNT(*) FROM classification_results;` dan `occupancy_logs` di `smart_space` | Keduanya 0 |

**Blok SQL F4 (di `smart_space_ai_dev`):**
```sql
-- status luar jadwal jika dan hanya jika schedule_id kosong (harus 0)
SELECT COUNT(*) FROM classification_results WHERE (status = 'dipakai_di_luar_jadwal') <> (schedule_id IS NULL);
-- baris sesi: menit terpakai tidak boleh melebihi terjadwal (harus 0)
SELECT COUNT(*) FROM classification_results WHERE schedule_id IS NOT NULL AND menit_terpakai > menit_terjadwal;
-- baris episode: terjadwal 0, utilisasi kosong, durasi minimal 30 menit (harus 0)
SELECT COUNT(*) FROM classification_results WHERE schedule_id IS NULL
  AND (menit_terjadwal <> 0 OR utilisasi_pct IS NOT NULL OR menit_terpakai < 30);
-- utilisasi kosong hanya bila menit terjadwal 0 (harus 0)
SELECT COUNT(*) FROM classification_results WHERE utilisasi_pct IS NULL AND menit_terjadwal <> 0;
-- utilisasi sama dengan rumus (toleransi pembulatan) (harus 0)
SELECT COUNT(*) FROM classification_results WHERE schedule_id IS NOT NULL AND menit_terjadwal > 0
  AND ABS(utilisasi_pct - 100 * menit_terpakai / menit_terjadwal) > 0.01;
-- pasangan status dan rule_id (harus tepat tiga baris: kosong-R02, luar-R03, sesuai-R01)
SELECT status, rule_id, COUNT(*) FROM classification_results GROUP BY status, rule_id;
-- penjelasan wajib terisi (harus 0)
SELECT COUNT(*) FROM classification_results WHERE penjelasan IS NULL OR penjelasan = '';
-- tidak ada sesi pada hari libur (harus 0)
SELECT COUNT(*) FROM classification_results c
JOIN calendar_exceptions e ON c.tanggal BETWEEN e.tanggal_mulai AND e.tanggal_selesai AND e.tipe = 'libur'
WHERE c.schedule_id IS NOT NULL;
-- computed_at memakai WIB: harus dekat jam komputer saat runner dijalankan, bukan terlambat 7 jam
SELECT MIN(computed_at), MAX(computed_at), NOW() FROM classification_results;
```

### 8.1 Skrip `C:\temp\uji_ai\bandingkan_gt_dev.py` (baca saja, hanya set dev)
```python
"""Membandingkan classification_results dev dengan ground_truth_dev.csv. Tidak menyetel apa pun."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

from app.generator.repository import create_db_session_factory, resolve_database_url
from app.models import ClassificationResult

CSV_GT = Path("data/ground_truth/ground_truth_dev.csv")
url, _ = resolve_database_url(target_set="dev")
mesin, Sesi = create_db_session_factory(url)
sesi = Sesi()


def hhmm(nilai):
    return str(nilai)[:5]


def tumpang_tindih(a, b):
    return a[0] < b[1] and b[0] < a[1]


prediksi = sesi.query(ClassificationResult).all()
pred_sesi = {(p.room_id, str(p.tanggal), hhmm(p.waktu_mulai)): p for p in prediksi if p.schedule_id is not None}
pred_episode = defaultdict(list)
for p in prediksi:
    if p.schedule_id is None:
        pred_episode[(p.room_id, str(p.tanggal))].append((hhmm(p.waktu_mulai), hhmm(p.waktu_selesai)))

konfusi = Counter()
gt_episode = defaultdict(list)
with CSV_GT.open(encoding="utf-8") as berkas:
    for g in csv.DictReader(berkas):
        kunci_hari = (int(g["room_id"]), g["tanggal"])
        if g["status_benar"] == "dipakai_di_luar_jadwal":
            gt_episode[kunci_hari].append((hhmm(g["waktu_mulai"]), hhmm(g["waktu_selesai"])))
            continue
        p = pred_sesi.get((int(g["room_id"]), g["tanggal"], hhmm(g["waktu_mulai"])))
        konfusi[(g["status_benar"], p.status if p else "TIDAK_ADA")] += 1

print("Sesi (ground truth -> prediksi):")
for (benar, pred), jumlah in sorted(konfusi.items()):
    print(f"  {benar:26s} -> {pred:26s} {jumlah}")
total_sesi = sum(konfusi.values())
benar_sesi = sum(j for (b, p), j in konfusi.items() if b == p)
print(f"  akurasi sesi: {benar_sesi}/{total_sesi} = {benar_sesi / total_sesi:.4f}")

jumlah_gt = sum(len(v) for v in gt_episode.values())
terdeteksi = sum(1 for k, daftar in gt_episode.items() for g in daftar
                 if any(tumpang_tindih(g, p) for p in pred_episode.get(k, [])))
jumlah_pred = sum(len(v) for v in pred_episode.values())
tanpa_pasangan = sum(1 for k, daftar in pred_episode.items() for p in daftar
                     if not any(tumpang_tindih(p, g) for g in gt_episode.get(k, [])))
print(f"Episode: ground truth {jumlah_gt}, prediksi {jumlah_pred}, ground truth terdeteksi {terdeteksi}")
print(f"  episode prediksi tanpa pasangan ground truth sama sekali: {tanpa_pasangan}")
print(f"  pecahan (prediksi lebih dari ground truth): {jumlah_pred - terdeteksi}")
sesi.close()
mesin.dispose()
```
**Harapan (set dev, acuan Lampiran 17.3):**
- `sesuai_jadwal` -> `sesuai_jadwal`: **1704** (tidak ada yang salah arah ke kosong).
- `kosong_meski_terjadwal` -> `kosong_meski_terjadwal`: **214**; -> `sesuai_jadwal`: **41** (sesi kosong yang satu slotnya terbalik oleh noise 1%).
- Akurasi sesi mendekati 0,98.
- Episode: ground truth **51**, prediksi **59**, terdeteksi **51**, tanpa pasangan **0**, pecahan **8** (episode yang terputus slot hilang 2%).
Jika angkanya berbeda jauh, kemungkinan ada bug, bukan noise.

---

## 9. Tahap G: API FastAPI `[MAIN]`

API membaca database dari `ai-service/.env` (`smart_space`). Untuk menguji dengan data hasil klasifikasi, arahkan ke set dev **hanya untuk jendela terminal ini**:

```powershell
# Terminal 1 (server)
Set-Location $REPO\ai-service
$env:DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/smart_space_ai_dev"
python -m uvicorn app.main:app --port 8001
```
```powershell
# Terminal 2 (klien) - fungsi bantu
function Panggil($url) {
  try { Invoke-RestMethod $url }
  catch { "HTTP " + [int]$_.Exception.Response.StatusCode }
}
$B = "http://127.0.0.1:8001"
$R = "tanggal_mulai=2026-09-07&tanggal_selesai=2027-01-22"
```
Setelah selesai: tutup server (Ctrl+C) dan di Terminal 1 jalankan `Remove-Item Env:DATABASE_URL`.

| ID | Uji | Perintah (Terminal 2) | Harapan |
|---|---|---|---|
| G1 | Kesehatan | `Panggil "$B/health"` | Jawaban sukses (HTTP 200) dengan status layanan |
| G2 | Hasil penuh | `$h = Panggil "$B/results?$R&limit=5"; $h.total; $h.items.Count` | `total` = 2018, 5 item, terurut tanggal lalu waktu |
| G3 | Filter status | `(Panggil "$B/results?$R&status=kosong_meski_terjadwal&limit=1").total`, dan status `dipakai_di_luar_jadwal` | 214 dan 59 |
| G4 | Filter ruang | `(Panggil "$B/results?$R&room_id=2&limit=1").total` | Sama dengan `SELECT COUNT(*) ... WHERE room_id = 2` |
| G5 | Paginasi | `$p = Panggil "$B/results?$R&limit=3&offset=2016"; $p.items.Count` | 2 item (sisa baris) |
| G6 | Validasi masukan | `Panggil "$B/results?tanggal_mulai=2027-01-22&tanggal_selesai=2026-09-07"`; `Panggil "$B/results?$R&limit=1001"`; `Panggil "$B/results?$R&status=ngawur"`; `Panggil "$B/results?$R&room_id=0"` | Masing-masing **HTTP 422** |
| G7 | Utilisasi per ruang | `$u = Panggil "$B/utilization?$R"; $u.ruang \| Select-Object nama_ruangan, menit_terjadwal, menit_terpakai, utilisasi_pct, kategori` | 10 ruang. Cocok dengan SQL di bawah (toleransi 0,01). `batas_rendah` 40, `batas_sedang` 80. Korelasi terisi (`jumlah_ruang` 10). |
| G8 | Ruang tidak ada | `Panggil "$B/utilization?$R&room_id=9999"` | **HTTP 404** |
| G9 | Periode tanpa sesi | `$u = Panggil "$B/utilization?tanggal_mulai=2026-12-25&tanggal_selesai=2026-12-25"; $u.ruang \| Select-Object -First 3` | `utilisasi_pct` dan `kategori` kosong (null) untuk ruang tanpa jadwal pada hari libur |
| G10 | Dokumentasi | Buka `http://127.0.0.1:8001/docs` di browser, coba "Try it out" pada ketiga endpoint | Swagger tampil; endpoint menjawab |
| G11 | Database aplikasi | Hentikan server, jangan atur `DATABASE_URL`, jalankan ulang, `(Panggil "$B/results?$R").total` | 0 (karena `smart_space` belum diklasifikasi) |

**SQL pembanding G7 (di `smart_space_ai_dev`):**
```sql
SELECT room_id, SUM(menit_terjadwal) AS terjadwal, SUM(menit_terpakai) AS terpakai,
       ROUND(100 * SUM(menit_terpakai) / SUM(menit_terjadwal), 2) AS utilisasi_pct
FROM classification_results WHERE schedule_id IS NOT NULL GROUP BY room_id ORDER BY room_id;
```
Kategori: `<= 40` rendah, `<= 80` sedang, selebihnya tinggi. Episode di luar jadwal tidak ikut menghitung.

**G12 `[BELUM]` `POST /classify`:** setelah endpoint ada, uji: (a) rentang valid membuat baris di `classification_results` dan menjawab ringkasan jumlah per status; (b) panggilan kedua pada rentang yang sama tidak menggandakan baris; (c) `tanggal_mulai` setelah `tanggal_selesai` menjawab 422; (d) hanya `occupancy_logs` dan `classification_results` yang berubah; (e) hasilnya sama dengan runner CLI (jumlah dan hash, Tahap F5).

**Catatan keamanan (belum teratasi):** API belum memakai autentikasi dan CORS. Jangan diekspos ke jaringan luar sebelum ada kunci antarlayanan.

---

## 10. Tahap H: Model ML (SS1-14) `[BRANCH SS1-14]`

Prasyarat: branch SS1-14 aktif (`git checkout feature/ss1-14-model-risiko-sesi-kosong`), dependensi terpasang (Bagian 2.4), Tahap F selesai untuk dev **dan** test.

| ID | Uji | Perintah / cara | Harapan |
|---|---|---|---|
| H1 | Unit test ML | `python -m pytest tests/test_ml.py -v` | 24 test lulus |
| H2 | Pelatihan di set dev | `python -m app.ml latih --set dev` | Distribusi blok: latih 1.020 sesi (119 positif), validasi 510 (25), uji-dev 429 (70). Decision Tree kedalaman 5 ambang 0,45; Logistic Regression C = 0,01 ambang 0,56. Model tersimpan di `ai-service/models/` beserta `metadata.json`. |
| H3 | Reprodusibel | Salin `ai-service\models\metadata.json`, latih ulang (H2), bandingkan | Isi `metadata.json` sama |
| H4 | Tanpa kebocoran | `git grep -n ground_truth ai-service/app/ml`; `python -m pytest tests/test_ml.py --collect-only -q` | `git grep` kosong; daftar test memuat uji anti-kebocoran, pembagian kronologis, imputasi hanya dari data latih |
| H5 | Artefak tidak ter-track | `git check-ignore -v ai-service/models` | Ada aturan ignore |
| H6 | Endpoint `POST /predict/risk` | Bagian 10.1 | Sesuai tabel kasus |
| H7 | Makna label `risiko` | Bagian 10.2 | Persentase `tinggi` mendekati 90% (Logistic Regression ambang 0,56) |

**Jangan menjalankan** `python -m app.ml evaluasi-akhir` di pengujian ini. Hasil evaluasi akhir (dijalankan dua kali dengan hasil identik, tanpa perubahan kode di antaranya) sudah tercatat di Lampiran 17.4.

### 10.1 Uji endpoint
Jalankan server seperti Tahap G (dengan `DATABASE_URL` set dev). Pilih jadwal dan tanggal yang cocok:
```powershell
& $MYSQL -u root -N -B -e "SELECT id, hari FROM schedules WHERE hari='Senin' ORDER BY id LIMIT 1;" smart_space_ai_dev
& $MYSQL -u root -N -B -e "SELECT id, hari FROM schedules WHERE hari='Jum''at' ORDER BY id LIMIT 1;" smart_space_ai_dev
```
Gunakan `ID_SENIN` dan `ID_JUMAT` dari hasil di atas. 12 Oktober 2026 adalah hari Senin biasa; 25 Desember 2026 adalah hari Jumat libur.
```powershell
function Kirim($badan) {
  try { Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8001/predict/risk" -ContentType "application/json" -Body $badan }
  catch { "HTTP " + [int]$_.Exception.Response.StatusCode }
}
Kirim '{"schedule_id": ID_SENIN, "tanggal": "2026-10-12"}'
```
| ID | Masukan | Harapan |
|---|---|---|
| H6a | jadwal Senin, tanggal 2026-10-12 | **200** dengan `skor_risiko` antara 0 dan 1, `risiko` (`tinggi` atau `rendah`), `ambang` (0,56), `nama_model`, `fitur` |
| H6b | `schedule_id` 999999 | **404** |
| H6c | jadwal Senin, tanggal 2026-10-13 (Selasa) | **422** (hari tidak cocok) |
| H6d | jadwal Jum'at, tanggal 2026-12-25 (libur) | **422** |
| H6e | badan tanpa `tanggal` | **422** (validasi) |
| H6f | model belum ada | **503** dengan pesan Bahasa Indonesia yang menyebut perintah melatih. Cara uji: hentikan server, ubah nama folder `ai-service\models` menjadi `models_off`, jalankan server, kirim H6a, lalu **kembalikan nama folder** dan hentikan server. |
| H6g | masukan sama dua kali | Skor identik (deterministik) |

### 10.2 Seberapa sering `risiko = tinggi`
Kirim permintaan untuk semua jadwal Senin pada 2026-10-12:
```powershell
$ids = & $MYSQL -u root -N -B -e "SELECT id FROM schedules WHERE hari='Senin' ORDER BY id;" smart_space_ai_dev
$jumlah = @{ tinggi = 0; rendah = 0 }
foreach ($id in $ids) {
  $r = Kirim "{`"schedule_id`": $id, `"tanggal`": `"2026-10-12`"}"
  if ($r.risiko) { $jumlah[$r.risiko]++ }
}
$jumlah
```
**Harapan:** mayoritas `tinggi` (sekitar 90% pada set uji). Ini bukan bug, melainkan konsekuensi ambang 0,56 dari validasi (proporsi positif validasi 4,9% vs uji 20,3%). Catat angkanya; label ini hanya sinyal prioritas pemantauan, bukan kepastian.

---

## 11. Tahap I: Validasi akurasi sistem pakar (SS1-12) `[BELUM]`

Sedang dikerjakan Dika. Saat selesai, tinjau:

| ID | Pemeriksaan | Harapan |
|---|---|---|
| I1 | Notebook `ai-service/notebooks/01_validasi_sistem_pakar.ipynb` dapat dijalankan dari awal sampai akhir | Menghasilkan confusion matrix 3 kelas, precision, recall, F1, accuracy |
| I2 | Penyetelan `empty_min_occupied_minutes` dan `outside_schedule_min_minutes` hanya di set dev; set test dievaluasi sekali | Dicatat di PR; angka dev dan test tidak dipertukarkan |
| I3 | `docs/EVALUASI_AI.md` | Memuat keterbatasan: noise 1% pada ambang 10 menit, episode terpecah oleh slot hilang 2%, data simulasi |

Angka dev dari Tahap F6 menjadi pembanding kasar. Jika hasil notebook pada dev sangat berbeda, selidiki sebelum menerima.

---

## 12. Tahap J: Ujung ke ujung dari nol (sekitar 15 sampai 30 menit)

Membuktikan seluruh jalur AI dapat dibangun ulang dari nol dan menghasilkan angka yang sama. Menghapus **set dev saja** (dapat dibangkitkan ulang dari seed); jangan menyentuh `smart_space` maupun `smart_space_ai_test`.

```powershell
# 1. Hapus dan siapkan ulang database dev
& $MYSQL -u root -e "DROP DATABASE IF EXISTS smart_space_ai_dev; CREATE DATABASE smart_space_ai_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
Set-Location $REPO\backend
$env:DB_DATABASE = "smart_space_ai_dev"; php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE

# 2. Hapus keluaran lama
Set-Location $REPO\ai-service
Remove-Item data\ground_truth\ground_truth_dev.csv -ErrorAction SilentlyContinue
Remove-Item models\* -Recurse -ErrorAction SilentlyContinue      # hanya bila SS1-14 sudah di branch ini

# 3. Bangkitkan, klasifikasikan, latih
python -m app.generator --set dev
python -m app.classification --set dev
python -m app.ml latih --set dev                                  # hanya [BRANCH SS1-14]

# 4. Verifikasi angka
$env:PYTHONPATH = (Get-Location).Path
python C:\temp\uji_ai\cek_hash.py dev
```

| ID | Harapan |
|---|---|
| J1 | `occupancy_logs` dev 93.063 baris dengan hash `00e20073...8eb68` (sama dengan Tahap C6) |
| J2 | `classification_results` dev 2.018 baris dengan hash `0eaf401c...7956` (sama dengan Tahap F5) |
| J3 | Model dilatih ulang dengan `metadata.json` yang sama seperti H3, dan `python -m pytest -q` serta `php artisan test` tetap hijau |

Bila hash berbeda, jangan lanjut: berarti ada langkah yang tidak deterministik atau skema/seeder berubah.

**Skenario demo ATS (urutan 5 menit):** (1) `python -m app.generator --set dev --dry-run` menunjukkan data simulasi; (2) `python -m app.classification --set dev --dry-run` menunjukkan ringkasan status; (3) jalankan `skenario_sistem_pakar.py` untuk menunjukkan penjelasan per aturan; (4) buka `/docs` pada API dan panggil `/results` dan `/utilization`; (5) bila SS1-14 sudah ter-merge, panggil `POST /predict/risk`.

---

## 13. Tahap K: Non-fungsional, keamanan, dan kebersihan

| ID | Uji | Cara | Harapan |
|---|---|---|---|
| K1 | Isolasi database | Hitung baris `rooms`, `schedules`, `threshold_settings`, `occupancy_logs`, `classification_results` di `smart_space` sebelum dan sesudah seluruh pengujian | Tidak berubah |
| K2 | Pengaman database | Pytest mencakup uji penolakan database di luar daftar; periksa `python -m pytest -q -k "database or pengaman"` | Lulus |
| K3 | Tidak ada rahasia di git | `git ls-files \| findstr /i "\.env"`; `git status` | Hanya `.env.example`; tidak ada `.env`, `data/`, atau `models/` ter-track |
| K4 | Kinerja runner | `Measure-Command { python -m app.classification --set dev }` | Catat waktu (baseline untuk dibandingkan nanti); tidak ada query per-hari yang berulang (cek kode: satu query per tabel) |
| K5 | Kinerja API | `Measure-Command { Panggil "$B/results?$R&limit=1000" }` dan `/utilization` | Catat waktu; hasil tetap benar |
| K6 | Masukan nakal API | `Panggil "$B/results?tanggal_mulai=abc&tanggal_selesai=2027-01-22"`; `Panggil "$B/results?$R&status='; DROP TABLE rooms;--"` | HTTP 422; tabel `rooms` tetap 10 baris |
| K7 | Dependensi | `pip check` | `No broken requirements found.` |
| K8 | Kualitas kode | `git grep -n "print(" ai-service/app` ; baca sekilas | `print` hanya di CLI (keluaran ringkasan); tidak ada kode mati atau debug tertinggal |
| K9 | Dokumen sesuai kode | Bandingkan nama fungsi dan tipe pada `DATA_CONTRACT.md` Bagian 11 dengan kode | Sama |
| K10 | Konstanta bernama | `git grep -n -E "random_state|seed" ai-service/app/ml ai-service/app/generator` | Seed dan tanggal potong berupa konstanta bernama, bukan angka di logika |

---

## 14. Tahap L: Regresi Laravel (database dibagi bersama)

| ID | Uji | Cara | Harapan |
|---|---|---|---|
| L1 | Test otomatis | `Set-Location $REPO\backend; php artisan test` | 58 test lulus (atau lebih) |
| L2 | Login Mahasiswa dan Admin | Jalankan `php artisan serve` dan `npm run dev`; coba `/login`, `/ruangan`, `/admin/login`, `/admin/dashboard` | Login benar masuk; salah menampilkan error; tanpa login diarahkan ke login; guard terpisah |
| L3 | CRUD ruangan dan pengaman hapus | Hapus ruangan yang punya jadwal (mis. GU 604) lewat `/admin/rooms` | Ditolak dengan pesan yang menyebut jumlah jadwal dan riwayat; jumlah jadwal tidak berubah |

---

## 15. Lembar catat hasil

Salin tabel ini ke berkas pribadi dan isi saat menguji. Status: LULUS / GAGAL / TERTUNDA.

| ID | Uji | Harapan ringkas | Hasil | Status | Catatan |
|---|---|---|---|---|---|
| A1 | pytest | semua lulus | | | |
| A2 | php artisan test | 58 lulus | | | |
| B1 | empat database | ada | | | |
| B2 | data master | 10 / 102 / 9 | | | |
| B3 | kunci threshold | dua kunci baru ada, kunci lama tidak | | | |
| B4 | seeder idempoten | tetap 10 / 102 | | | |
| B5 | batasan skema | duplikat dan FK ditolak | | | |
| B6 | zona waktu | Asia/Jakarta | | | |
| B7 | integritas jadwal | 0 pelanggaran | | | |
| C1 | generator dry-run | ringkasan, DB tak berubah | | | |
| C2 | generator dev dan test | tanpa error | | | |
| C3 | jumlah baris | 93.063 / 93.112 | | | |
| C4 | aturan grid waktu | semua sesuai | | | |
| C5 | okupansi per ruang | mendekati acuan | | | |
| C6 | determinisme | hash sama | | | |
| C7 | ground truth CSV | 2.010 / 2.007 | | | |
| C8 | argumen tidak sah | ditolak | | | |
| D1 | unit test sistem pakar | 24 lulus | | | |
| D2 | skenario manual | semua LULUS | | | |
| D3 | tanpa ground truth | git grep kosong | | | |
| D4 | tanpa literal ambang | hanya komentar | | | |
| D5 | sesuai kontrak | sama | | | |
| E1 | unit test utilisasi | 18 lulus | | | |
| E2 | skrip utilisasi | semua LULUS | | | |
| E3 | konsistensi SQL | sama | | | |
| F1 | runner dry-run | tanpa tulis | | | |
| F2 | runner dev dan test | tanpa error | | | |
| F3 | jumlah baris klasifikasi | 2018 / 2013 | | | |
| F4 | invarian | semua 0 | | | |
| F5 | idempoten | hash sama | | | |
| F6 | banding ground truth | 1704 / 214 / 41; episode 51 / 59 | | | |
| F7 | `smart_space` tak tersentuh | 0 | | | |
| G1 sampai G11 | API | sesuai tabel Bagian 9 | | | |
| H1 sampai H7 | model ML | sesuai tabel Bagian 10 | | | |
| I1 sampai I3 | validasi SS1-12 | setelah selesai | | | |
| J1 sampai J3 | ujung ke ujung | hash dan angka sama | | | |
| K1 sampai K10 | non-fungsional | sesuai tabel Bagian 13 | | | |
| L1 sampai L3 | regresi Laravel | sesuai tabel Bagian 14 | | | |

**Memetakan hasil ke DoD issue:**

| Issue | Butir DoD yang dibuktikan | Uji |
|---|---|---|
| #41 (SS1-08) | seed sama menghasilkan data identik; tidak ada log 17.00; ringkasan distribusi | C3, C4, C6, C5 |
| #47 (SS1-09) | setiap aturan punya test; hasil memuat rule_id dan penjelasan; tanpa ambang di kode | D1, D2, D4, F4 |
| #49 (SS1-11) | idempoten; Python tidak menulis tabel Laravel; Swagger tampil | F5, F7, K1, G10 (`/classify`: G12) |
| #52 (SS1-14) | tanpa kebocoran; dibandingkan baseline; reprodusibel; endpoint lulus | H1 sampai H7, Lampiran 17.4 |

---

## 16. Troubleshooting

| Gejala | Kemungkinan penyebab | Perbaikan |
|---|---|---|
| `Can't connect to MySQL server` | MySQL belum menyala | Nyalakan dari XAMPP Control Panel; ulangi 2.3 |
| `Access denied for user 'root'` | Ada MySQL dengan konfigurasi lain atau password berubah | Periksa proses (2.3), pastikan hanya MySQL XAMPP; cek `.env` |
| `PENGAMAN AKTIF ... harus berakhiran '_test'` | Pytest diarahkan ke database non-test | Normal bila `DATABASE_URL`/`DB_DATABASE` tertinggal di terminal; `Remove-Item Env:DATABASE_URL`; `Remove-Item Env:DB_DATABASE` |
| `Table '...' doesn't exist` pada pytest | `smart_space_test` belum dimigrasi | Langkah migrasi di Bagian 2.6 |
| `ModuleNotFoundError: No module named 'app'` | Skrip dijalankan tanpa `PYTHONPATH` | `Set-Location $REPO\ai-service; $env:PYTHONPATH = (Get-Location).Path` |
| `Address already in use` pada port 8001 | Server lama masih jalan | Tutup terminal server lama atau pakai `--port 8002` |
| `/results` menjawab `total: 0` | API terhubung ke `smart_space`, bukan set dev | Atur `DATABASE_URL` ke set dev (Bagian 9) |
| `/utilization` menjawab 500 menyebut kunci hilang | Threshold belum di-seed | `php artisan migrate:fresh --seed` pada database tujuan |
| Jumlah baris generator berbeda dari acuan | Data master berubah (jadwal, kalender) atau seeder duplikat | Periksa B2 dan B7 lebih dulu |
| Hash klasifikasi berbeda | Runner atau aturan berubah, atau data okupansi berbeda | Cek hash okupansi (C6) dulu; baru periksa kode |
| `migrate:fresh` menimpa database yang salah | `DB_DATABASE` tertinggal | Selalu `Remove-Item Env:DB_DATABASE` sesudahnya |
| Test Laravel dan pytest saling gagal | Dijalankan bersamaan | Jalankan bergantian |
| `evaluasi-akhir` ingin dijalankan lagi | Penasaran dengan hasil | Jangan. Lihat Lampiran 17.4 |

---

## 17. Lampiran

### 17.1 Angka acuan data
| Item | Dev | Test |
|---|---|---|
| Rentang | 2026-09-07 sampai 2027-01-22 | sama |
| Seed | 1001 | 2002 |
| `occupancy_logs` | 93.063 | 93.112 |
| Hash okupansi dev (semua) | `00e20073e875a91b1e266a9f2a6f13be8274d98d27a3c303832d94145af8eb68` | |
| Hash okupansi dev (< 2026-10-17, 27.911 baris) | `1bd2dd2f5aa32e70ca565475944218f8bb35b833ea4be490494aeaa71e757136` | |
| Ground truth | 2.010 baris (1.959 sesi, 51 episode) | 2.007 baris (1.959 sesi, 48 episode) |
| Sesi terjadwal | 1.959 | 1.959 |
| Hari kerja | 100 (67 biasa, 20 ujian, 9 kegiatan khusus, 4 libur) | sama |

### 17.2 Okupansi per ruang (dev, acuan)
| Ruang | Total slot | Terisi | Okupansi |
|---|---|---|---|
| GU 604 | 9.298 | 1.462 | 15,72% |
| GU 701 | 9.292 | 1.703 | 18,33% |
| GU 702 | 9.306 | 3.611 | 38,80% |
| GU 704 | 9.318 | 5.024 | 53,92% |
| GU 705 | 9.306 | 2.719 | 29,22% |
| GU 706 | 9.304 | 5.202 | 55,91% |
| GU 707 | 9.310 | 3.090 | 33,19% |
| GU 805 | 9.302 | 3.077 | 33,08% |
| TA 10.3 | 9.310 | 1.263 | 13,57% |
| TA 11.5A | 9.317 | 378 | 4,06% |

### 17.3 Hasil klasifikasi (acuan)
| Item | Dev | Test |
|---|---|---|
| `classification_results` | 2.018 | 2.013 |
| `sesuai_jadwal` | 1.745 | 1.714 |
| `kosong_meski_terjadwal` | 214 | 245 |
| `dipakai_di_luar_jadwal` | 59 | 54 |
| Hash klasifikasi dev | `0eaf401c75f9a4c59cd18464b8771fca86b2281c849858846f9e48261a1a7956` | |

Perbandingan dev dengan ground truth: akurasi sesi sekitar 0,980; recall `kosong_meski_terjadwal` 0,839 (41 sesi kosong terbaca sesuai jadwal karena noise 1% pada ambang 10 menit); episode: presisi 0,864 dan recall 1,000 (8 dari 59 prediksi adalah pecahan episode yang terputus slot hilang 2%).

### 17.4 Hasil model ML (acuan, jangan dijalankan ulang di set test)
Blok data: latih 2026-09-07 sampai 2026-11-13 (1.020 sesi, 119 positif); validasi 2026-11-16 sampai 2026-12-18 (510 sesi, 25 positif); uji akhir di set test 2026-12-21 sampai 2027-01-22 (429 sesi, 87 positif).

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Sesi ditandai |
|---|---|---|---|---|---|---|---|
| Baseline mayoritas | 0,797 | 0,000 | 0,000 | 0,000 | 0,500 | 0,203 | 0% |
| Baseline rata ruang | 0,797 | 0,000 | 0,000 | 0,000 | 0,554 | 0,223 | |
| Baseline rata jenis hari | 0,767 | 0,420 | 0,391 | 0,405 | 0,685 | 0,316 | 18,9% |
| Decision Tree (ambang 0,45) | 0,618 | 0,305 | 0,690 | 0,423 | 0,699 | 0,350 | 45,9% |
| Logistic Regression (ambang 0,56) | 0,275 | 0,211 | 0,943 | 0,345 | 0,675 | 0,370 | 90,4% |

Catatan: F1 Decision Tree (interval bootstrap 95% 0,348 sampai 0,493) tidak berbeda nyata dari baseline jenis hari (0,405). Evaluasi akhir dijalankan dua kali dengan hasil identik; tidak ada perubahan kode fitur, pembagian, model, evaluasi, atau CLI di antara keduanya.

### 17.5 Ringkasan perintah
```powershell
# Persiapan sesi
$MYSQL = "d:\xampp\mysql\bin\mysql.exe"; $REPO = "d:\xampp\htdocs\Smart-Space"
Set-Location $REPO\ai-service; $env:PYTHONPATH = (Get-Location).Path

# Pengujian otomatis (bergantian, jangan bersamaan)
python -m pytest -q
Set-Location $REPO\backend; php artisan test

# Data dan klasifikasi
python -m app.generator --set dev|test [--dry-run]
python -m app.classification --set dev|test [--dry-run]

# API (arahkan ke set dev hanya untuk terminal itu)
$env:DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/smart_space_ai_dev"
python -m uvicorn app.main:app --port 8001

# ML (branch SS1-14)
python -m app.ml latih --set dev
```

---

## 18. Batas cakupan (apa yang belum teruji karena belum ada)

- `POST /classify` (G12) dan hasil validasi SS1-12 (Tahap I).
- Integrasi Laravel dengan FastAPI, dashboard analitik, laporan PDF/Excel, halaman status Mahasiswa, pengaturan threshold dan akun Admin di aplikasi web.
- Status ketersediaan "saat ini" dan simulasi data berjalan (NFR-01).
- Integrasi API Learning dan API PENRU (menunggu token).
- Autentikasi dan CORS pada FastAPI, HTTPS, deployment, dan backup berkala (NFR-03, NFR-06).
- Uji beban dan uji kegunaan (UAT).

Setiap kali kartu di atas selesai, tambahkan tahapnya ke dokumen ini dan perbarui lembar catat.
