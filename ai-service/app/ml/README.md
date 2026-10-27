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

```
POST /predict/risk
{
  "schedule_id": 42,
  "tanggal": "2026-10-20"
}
```

Mengembalikan `skor_risiko`, `risiko` (tinggi/rendah), `ambang`, `nama_model`, dan `fitur` yang dipakai.

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

## Keterbatasan

- Label berasal dari data simulasi dan sistem pakar, sehingga model bisa hanya mempelajari aturan generator.
- Jenis hari dominan mempengaruhi distribusi kelas.
- Sampel positif kecil pada beberapa irisan (masa ujian, kegiatan khusus).
