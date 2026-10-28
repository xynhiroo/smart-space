# Model ML: Risiko Sesi Terjadwal Kosong (SS1-14)

Model klasifikasi yang memprediksi apakah sesi perkuliahan terjadwal berisiko tidak dipakai (*kosong meski terjadwal*).

## Prasyarat

1. **Database `classification_results` harus sudah terisi** di database dev dan test:
   ```bash
   # Set dev (smart_space_ai_dev)
   python -m app.classification --set dev

   # Set test (smart_space_ai_test) — HANYA untuk evaluasi akhir satu kali
   python -m app.classification --set test
   ```
   Runner klasifikasi berasal dari PR terpisah (SS1-11, PR #63).

2. **Membaca data test hanya untuk evaluasi akhir satu kali.** Jangan gunakan set test untuk memilih fitur, hiperparameter, atau ambang keputusan.

3. **Dependensi** sudah terdaftar di `requirements.txt` (scikit-learn, pandas, numpy, joblib). Untuk notebook, instal juga `requirements-notebook.txt`.

## Penggunaan

### Melatih model (set dev)

```bash
cd ai-service
python -m app.ml latih --set dev
```

Perintah ini:
- Memuat sesi terjadwal dari `classification_results` di `smart_space_ai_dev`
- Membangun fitur (hanya informasi sebelum sesi dimulai)
- Membagi data secara kronologis (latih → validasi)
- Memilih hiperparameter dan ambang keputusan di blok validasi
- Menyimpan model ke `ai-service/models/`

### Evaluasi akhir (set test)

```bash
python -m app.ml evaluasi-akhir --set test
```

⚠ **Hanya boleh dijalankan SEKALI.** Jangan mengubah model atau hiperparameter setelah melihat hasilnya.

### Endpoint prediksi

```http
POST /predict/risk
Content-Type: application/json

{
  "schedule_id": 42,
  "tanggal": "2026-10-20"
}
```

Mengembalikan `skor_risiko` (probabilitas 0-1), `risiko` (tinggi/rendah), `ambang`, `nama_model`, dan `fitur` yang dipakai.

**Arti label `risiko`**:
- Model inferensi default yang digunakan adalah **Logistic Regression** dengan ambang keputusan `0.56` (dipilih dari blok validasi).
- Label `'tinggi'` diberikan jika `skor_risiko >= 0.56`, selain itu `'rendah'`.
- Pada blok uji, model beroperasi dengan recall tinggi (94.25%) dan menandai **90.44%** sesi sebagai risiko tinggi (precision 21.13%).
- Label ini berfungsi sebagai sinyal peringatan dini (*alert/prioritization flag*) bagi admin untuk memprioritaskan pemantauan, bukan kepastian mutlak bahwa ruangan pasti kosong.

## Arsitektur paket `app/ml/`

| Modul | Tanggung jawab |
|---|---|
| `konstanta.py` | Semua konstanta bernama (tanggal potong, seed, hiperparameter) |
| `fitur.py` | Fungsi murni pembangun fitur (anti-kebocoran) |
| `dataset.py` | Membaca sesi terjadwal dari database (read-only) |
| `pembagian.py` | Pembagian kronologis latih/validasi/uji |
| `model.py` | Pelatihan, pemilihan hiperparameter, penyimpanan model |
| `evaluasi.py` | Metrik, baseline, bootstrap CI, analisis kesalahan |
| `cli.py` | Antarmuka baris perintah |

## Fitur (hanya informasi sebelum sesi)

- Ruang (one-hot), hari dalam pekan, jam mulai, durasi menit
- Shift (dari kolom `schedules.shift` atau diturunkan dari jam mulai)
- `is_open_space` (dari `NAMA_OPEN_SPACE` di params generator)
- Pekan ke- sejak awal semester
- Jenis hari kalender akademik (biasa, ujian, kegiatan_khusus)
- Dekat libur (ada libur dalam 2 hari kerja sebelum/sesudah)
- Pekan sebelum ujian
- `kosong_rate_ruang_sebelumnya` (proporsi sesi kosong di pekan-pekan sebelumnya)
- `ada_riwayat` (apakah ada riwayat pekan sebelumnya)

## Interpretasi Hasil Evaluasi (Set Uji)

### 1. Perbandingan Jujur terhadap Baseline Per Jenis Hari
Pada blok uji akhir (429 sesi, 87 positif / 20.28%), hasil evaluasi model dibandingkan dengan 3 baseline:

| Model / Baseline | Accuracy | Precision | Recall | F1 Score | ROC-AUC | PR-AUC | Sesi Ditandai Berisiko ((TP+FP)/N) |
|---|---|---|---|---|---|---|---|
| **Baseline: Mayoritas** | 0.7972 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.2028 | 0.00% (0/429) |
| **Baseline: Rata-rata per Ruang** | 0.7972 | 0.0000 | 0.0000 | 0.0000 | 0.5537 | 0.2229 | 0.00% (0/429) |
| **Baseline: Rata-rata per Jenis Hari** | 0.7669 | **0.4198** | 0.3908 | 0.4048 | 0.6848 | 0.3160 | **18.88%** (81/429) |
| **Decision Tree (ambang 0.45 / 0.50)** | 0.6177 | 0.3046 | 0.6897 | 0.4225 | 0.6992 | 0.3504 | **45.92%** (197/429) |
| **Logistic Regression (ambang 0.56)** | 0.2751 | 0.2113 | **0.9425** | 0.3453 | 0.6750 | 0.3695 | **90.44%** (388/429) |
| **Logistic Regression (ambang 0.50)** | 0.2005 | 0.1995 | 0.9770 | 0.3314 | 0.6750 | 0.3695 | **99.30%** (426/429) |

- **Selisih F1 Decision Tree berada dalam interval bootstrap**: F1 Decision Tree adalah 0.4225, sedangkan baseline jenis hari adalah 0.4048 (selisih +0.0177). Interval kepercayaan bootstrap 95% untuk F1 Decision Tree adalah **[0.3475, 0.4933]**. Nilai baseline 0.4048 berada tepat di dalam rentang tersebut, sehingga selisih performa ini tidak signifikan secara statistik.
- **ROC-AUC Logistic Regression di bawah baseline**: ROC-AUC Logistic Regression (0.6750; 95% CI: [0.6105, 0.7386]) berada di bawah ROC-AUC baseline jenis hari (0.6848). F1-nya (0.3453) juga lebih rendah dari baseline jenis hari karena tingginya *false positive* (306 FP) akibat ambang yang terlalu agresif.
- **Persentase sesi yang ditandai tiap model**: Baseline jenis hari menandai 18.88% sesi, Decision Tree menandai 45.92% sesi, sedangkan Logistic Regression menandai 90.44% sesi (hampir seluruh sesi diberi peringatan).

### 2. Kinerja pada Irisan Khusus (Logistic Regression)
Pada irisan blok uji, presisi model Logistic Regression (ambang 0.56) dibandingkan dengan proporsi positif dasar irisan:
- **Masa Ujian (AAS)**: Presisi model = **20.10%** vs Proporsi Positif = **20.10%** (204 sesi, seluruh 204 sesi ditandai berisiko; presisi sama persis dengan prevalensi acak).
- **Kegiatan Khusus**: Presisi model = **41.98%** vs Proporsi Positif = **41.98%** (81 sesi, seluruh 81 sesi ditandai berisiko; presisi sama persis dengan prevalensi acak).
- **Pekan dengan Libur**: Presisi model = **20.26%** vs Proporsi Positif = **18.18%** (187 sesi, 153 ditandai berisiko; selisih marjinal +2.08%).

### 3. Penyebab
1. **Sifat Data Generator Dummy**: Jenis hari (hari biasa, hari ujian, kegiatan khusus, libur) merupakan satu-satunya sinyal makro terkuat yang memengaruhi probabilitas ketidakhadiran pada data simulasi `smart-space`.
2. **Kejadian Tidak Hadir Acak Independen**: Ketidakhadiran di luar pengaruh jenis hari dibangkitkan secara acak independen per sesi (noise sintetis), tanpa korelasi riwayat ruang atau pola shift yang persisten. Model tidak menemukan sinyal laten tambahan yang dapat dipelajari di luar informasi kalender akademik.

### 4. Pergeseran Proporsi Positif Antarblok & Masalah Transfer Ambang
Terjadi pergeseran distribusi kelas (*distribution shift*) yang signifikan antarblok kronologis:
- **Blok Latih (dev)**: 11.67% positif (119 / 1.020)
- **Blok Validasi (dev)**: 4.90% positif (25 / 510) — dominan hari kuliah biasa di pertengahan semester
- **Blok Uji (test)**: 20.28% positif (87 / 429) — mencakup masa ujian AAS dan pergantian tahun

Karena ambang keputusan dioptimalkan pada blok validasi dengan proporsi positif sangat rendah (4.90%), ambang tersebut tidak dapat mentransfer dengan baik ke blok uji yang memiliki proporsi positif 4 kali lipat lebih tinggi (20.28%). Akibatnya, pada blok uji model Logistic Regression memprediksi probabilitas tinggi untuk hampir semua sesi, berujung pada over-flagging (90.44% sesi ditandai).

### 5. Kesimpulan
Pada dataset simulasi saat ini, model Machine Learning (baik Decision Tree maupun Logistic Regression) **belum memberikan nilai tambah nyata** (*no tangible value added*) di atas baseline sederhana berbasis rata-rata jenis hari kalender akademik. Untuk implementasi produksi di masa depan, model memerlukan data perilaku pengguna riil (misalnya pola kehadiran dosen/mahasiswa, jenis mata kuliah, atau riwayat pembatalan) agar dapat melampaui aturan kalender sederhana.

## Keterbatasan

- Label berasal dari data simulasi dan sistem pakar, sehingga model hanya mempelajari aturan generator dan kalender akademik.
- Jenis hari mendominasi klasifikasi; riwayat per-ruang tidak memberikan sinyal prediktif signifikan pada data sintetis.
- Sampel positif kecil pada irisan masa ujian dan kegiatan khusus menyebabkan metrik segmen memiliki variansi tinggi.
