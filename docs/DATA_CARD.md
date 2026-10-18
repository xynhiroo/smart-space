# Data Card: Dataset Dummy Okupansi Historis & Ground Truth (SS1-08)

Dokumen ini menjelaskan spesifikasi, asumsi parameter, definisi skenario, prosedur pembuatan ulang, serta ringkasan distribusi dataset dummy okupansi historis dan label kebenaran (*ground truth*) untuk Smart Space Analytics Platform (PBLIF3-PD08).

---

## 1. Tujuan dan Lingkup Data

### Tujuan
Dataset ini disediakan untuk melatih, mengevaluasi, dan memvalidasi model inferensi sistem pakar (SS1-09), modul analitik utilisasi ruang (SS1-10), layanan API analitik (SS1-11), validasi akurasi sistem (SS1-12), dan model Machine Learning (SS1-14) tanpa ketergantungan pada perangkat keras sensor fisik IoT.

### Lingkup
- **Cakupan Entitas**: 10 ruangan laboratorium/teori Jurusan Teknik Informatika Polibatam (GU 604, GU 701, GU 702, GU 704, GU 705, GU 706, GU 707, GU 805, TA 10.3, TA 11.5A) dan 102 jadwal mata kuliah reguler semester Ganjil 2026/2027.
- **Batasan Sensor**: Generator meniru keluaran biner deteksi okupansi sensor per slot 10 menit. Tidak ada hardware, mikrokontroler, kamera, RFID, atau aktor selain Admin dan Mahasiswa.
- **Rentang Waktu**: Tanggal 7 September 2026 (awal perkuliahan aktif) sampai kemarin WIB (17 Oktober 2026), hanya hari kerja aktif (Senin s.d. Jumat).
- **Target Penyimpanan**: Tabel `occupancy_logs` pada database terisolasi (`smart_space_ai_dev` dan `smart_space_ai_test`) serta berkas CSV ground truth di `ai-service/data/ground_truth/`.

---

## 2. Asumsi dan Parameter

Semua parameter dibungkus dalam dataclass frozen `GeneratorParams` pada `ai-service/app/generator/params.py`:

| Parameter | Nilai | Satuan / Keterangan |
|---|---|---|
| `slot_minutes` | 10 | Menit per slot observasi |
| `operational_start_hour` | 07:00 | Jam awal operasional harian |
| `operational_end_hour` | 23:00 | Jam akhir operasional harian (slot terakhir mulai 22:50) |
| `break_hour:break_minute` | 17:00 | Slot jeda harian (17:00-17:10); ruangan tutup, tidak ada baris data |
| `weights_biasa` | (0.78, 0.08, 0.06, 0.06, 0.02) | Peluang skenario hari biasa (tepat waktu, terlambat, selesai awal, tidak hadir, dipinjam kegiatan lain) |
| `weights_ujian` | (0.58, 0.05, 0.15, 0.20, 0.02) | Peluang skenario masa ATS/AAS |
| `weights_kegiatan_khusus`| (0.40, 0.04, 0.04, 0.50, 0.02) | Peluang skenario minggu pengganti / perwalian |
| `prob_outside_regular` | 0.03 (3%) | Peluang per hari episode luar jadwal ruang reguler |
| `prob_outside_openspace`| 0.10 (10%)| Peluang per hari episode luar jadwal ruang open-space (GU 701, GU 705, GU 707) |
| `holiday_outside_multiplier` | 0.3 | Pengali peluang episode luar jadwal pada hari libur nasional |
| `min_outside_duration` | 30 | Durasi minimum episode pemakaian luar jadwal (menit) |
| `max_outside_duration` | 180 | Durasi maksimum episode pemakaian luar jadwal (menit) |
| `prob_short_outside` | 0.05 (5%) | Peluang episode singkat 10-20 menit (noise aktivitas, tidak masuk ground truth) |
| `prob_detection_error` | 0.01 (1%) | Peluang salah deteksi per slot (nilai boolean dibalik) |
| `prob_missing_slot` | 0.02 (2%) | Peluang slot hilang per slot (baris ditiadakan / packet loss) |
| `empty_min_occupied_minutes`| 10 | Ambang batas terisi minimum agar sesi tidak dianggap kosong |
| `outside_schedule_min_minutes`| 30 | Ambang batas durasi episode luar jadwal agar dicatat ground truth |
| `DEV_SEED` | 1001 | Seed deterministik dataset pengembangan (`dev`) |
| `TEST_SEED` | 2002 | Seed deterministik dataset pengujian (`test`) |

---

## 3. Definisi Skenario

Setiap sesi perkuliahan yang terjadwal disimulasikan ke dalam salah satu dari 5 skenario:

1. **`tepat_waktu`** (`penyebab: kelas_berlangsung`):
   Ruangan terisi sepanjang jendela jadwal terjadwal. Menghasilkan label `status_benar = sesuai_jadwal`.
2. **`terlambat`** (`penyebab: terlambat`):
   Ruangan mulai terisi setelah offset 10, 20, 30, atau 40 menit dari jam mulai jadwal. Jika menit terpakai >= 10 menit, menghasilkan label `status_benar = sesuai_jadwal`.
3. **`selesai_awal`** (`penyebab: selesai_awal`):
   Ruangan berhenti terisi 10, 20, 30, atau 40 menit sebelum jam selesai jadwal. Jika menit terpakai >= 10 menit, menghasilkan label `status_benar = sesuai_jadwal`.
4. **`tidak_hadir`** (`penyebab: tidak_hadir`):
   Kelas tidak berlangsung dan tidak ada okupansi sama sekali sepanjang jendela jadwal (0 menit terpakai). Menghasilkan label `status_benar = kosong_meski_terjadwal`.
5. **`dipinjam_kegiatan_lain`** (`penyebab: dipinjam_kegiatan_lain`):
   Kelas resmi tidak berlangsung, namun ruangan terisi oleh aktivitas lain untuk 60% s.d. 100% durasi jadwal. Menghasilkan label `status_benar = sesuai_jadwal` (karena terisi >= 10 menit) dengan penanda khusus pada kolom `penyebab`.

### Pemakaian di Luar Jadwal
- **Episode Panjang (>= 30 menit)** (`penyebab: pemakaian_luar_jadwal`):
  Okupansi di luar seluruh jendela jadwal ruang pada hari tersebut dan tidak mencakup slot 17.00. Dicatat pada ground truth dengan `schedule_id` kosong dan `status_benar = dipakai_di_luar_jadwal`.
- **Episode Singkat (10-20 menit)**:
  Aktivitas singkat di luar jadwal yang tidak mencapai ambang batas 30 menit. Tidak dicatat ke dalam berkas ground truth sesuai DATA_CONTRACT Bagian 7.4.

---

## 4. Cara Membuat Ulang

### Persiapan Database
1. Buat database `smart_space_ai_dev` dan `smart_space_ai_test` di MySQL (utf8mb4, utf8mb4_unicode_ci):
   ```bash
   mysql -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_ai_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   mysql -u root -e "CREATE DATABASE IF NOT EXISTS smart_space_ai_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```
2. Migrasikan skema dan seeder master data (SATU KALI SAJA per database) dari direktori `backend/`:
   ```powershell
   $env:DB_DATABASE="smart_space_ai_dev"; php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE
   $env:DB_DATABASE="smart_space_ai_test"; php artisan migrate:fresh --seed; Remove-Item Env:DB_DATABASE
   ```

### Perintah CLI Generator
Jalankan dari direktori root atau `ai-service/`:
```bash
# Menghasilkan dataset dev (seed: 1001)
python -m app.generator --set dev

# Menghasilkan dataset test (seed: 2002)
python -m app.generator --set test
```

---

## 5. Ringkasan Distribusi Dataset Dev

- **Target Database**: `smart_space_ai_dev`
- **Seed**: `1001`
- **Rentang Tanggal**: `2026-09-07` s.d. `2026-10-17` (30 hari kerja aktif)
- **Total Baris `occupancy_logs`**: 27.911 baris
- **Total Baris Ground Truth**: 631 baris (612 baris sesi terjadwal, 19 baris episode pemakaian luar jadwal)

### Ringkasan per Ruangan (Set Dev)

| ID | Nama Ruangan | Karakteristik | Total Sesi | Total Slot | Slot Terisi | Okupansi (%) |
|---|---|---|---|---|---|---|
| 1 | GU 604 | Reguler | 30 | 2.782 | 508 | 18,26% |
| 2 | GU 701 | Open-Space | 30 | 2.786 | 586 | 21,03% |
| 3 | GU 702 | Reguler | 90 | 2.797 | 1.208 | 43,19% |
| 4 | GU 704 | Reguler | 90 | 2.787 | 1.637 | 58,74% |
| 5 | GU 705 | Open-Space | 66 | 2.790 | 983 | 35,23% |
| 6 | GU 706 | Reguler | 114 | 2.791 | 1.753 | 62,81% |
| 7 | GU 707 | Open-Space | 66 | 2.788 | 1.041 | 37,34% |
| 8 | GU 805 | Reguler | 78 | 2.798 | 1.085 | 38,78% |
| 9 | TA 10.3 | Reguler | 36 | 2.791 | 393 | 14,08% |
| 10 | TA 11.5A | Reguler | 12 | 2.801 | 113 | 4,03% |
| **Total** | | | **612** | **27.911** | **9.307** | **33,35%** |

### Distribusi Ground Truth Status Benar (Set Dev)
- `sesuai_jadwal`: 574 baris (90,97%)
- `kosong_meski_terjadwal`: 38 baris (6,02%)
- `dipakai_di_luar_jadwal`: 19 baris (3,01%)

### Distribusi Ground Truth Penyebab (Set Dev)
- `kelas_berlangsung`: 499 baris (79,08%)
- `tidak_hadir`: 38 baris (6,02%)
- `terlambat`: 37 baris (5,86%)
- `selesai_awal`: 30 baris (4,75%)
- `pemakaian_luar_jadwal`: 19 baris (3,01%)
- `dipinjam_kegiatan_lain`: 8 baris (1,27%)

---

## 6. Ringkasan Dataset Test

Sesuai ketentuan isolasi pengujian, data test dibangkitkan secara independen tanpa analisis pola mendalam:
- **Target Database**: `smart_space_ai_test`
- **Seed**: `2002`
- **Rentang Tanggal**: `2026-09-07` s.d. `2026-10-17` (30 hari kerja aktif)
- **Total Baris `occupancy_logs`**: 27.986 baris
- **Total Baris Ground Truth**: 624 baris (612 baris sesi terjadwal, 12 baris episode pemakaian luar jadwal)

---

## 7. Keterbatasan yang Diketahui & Catatan Penting

1. **Simulasi Buatan Tim**: Data ini sepenuhnya hasil pembangkitan probabilistik deterministik. Kinerja sistem pakar atau model machine learning pada dataset ini tidak menjamin keakuratan setara pada kondisi fisik dunia nyata.
2. **Ketiadaan Data PENRU (Peminjaman Ruang TU)**: Kasus `dipinjam_kegiatan_lain` (ruangan terjadwal kosong lalu dipinjam mahasiswa lain via tata usaha) secara observasi slot biner tampak identik dengan kelas yang sedang berlangsung. Tanpa integrasi data PENRU, sistem analitik tidak dapat membedakan kedua penyebab ini (tercatat di PRD FR-13).
3. **Ground Truth Berbasis Definisi Tetap**: Label `status_benar` diturunkan secara deterministik dari definisi operasional DATA_CONTRACT Bagian 7.4 (ambang batas 10 menit untuk sesi dan 30 menit untuk episode), bukan observasi fisik mata manusia.
4. **Kerentanan Ambang Batas 10 Menit terhadap Noise (Hipotesis SS1-12)**:
   Dengan adanya noise salah deteksi 1% dan missing slot 2%, sesi yang sebenarnya kosong dapat secara acak terisi 1 slot (10 menit) akibat noise positif tunggal, sehingga terklasifikasi sebagai `sesuai_jadwal`. Fenomena ini dicatat sebagai hipotesis risiko analitik yang akan diuji secara formal pada kartu validasi sistem pakar (SS1-12).
