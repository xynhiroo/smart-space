# Evaluasi Sistem Pakar terhadap Ground Truth (SS1-12)

Dokumen ini melaporkan akurasi sistem pakar klasifikasi status ruangan (SS1-09) terhadap label kebenaran dari generator data dummy (SS1-08). Semua data adalah simulasi, jadi angka di sini mengukur kecocokan dengan simulator, bukan akurasi di ruang sungguhan.

## 1. Cara evaluasi

- **Ground truth** dihasilkan generator dan disimpan di `ai-service/data/ground_truth/` (tidak ikut git). Set dev memakai seed 1001, set test seed 2002.
- **Pencocokan:** sesi terjadwal dicocokkan lewat (`tanggal`, `room_id`, `schedule_id`). Episode di luar jadwal dicocokkan lewat irisan waktu. Baris tanpa pasangan dilaporkan terpisah dan tidak masuk metrik.
- **Metrik:** accuracy, precision, recall, F1 per kelas, macro F1, dan matriks kebingungan untuk tiga status (`sesuai_jadwal`, `kosong_meski_terjadwal`, `dipakai_di_luar_jadwal`).
- **Aturan penyetelan:** ambang hanya disetel di set dev. Set test dipakai untuk angka akhir.

Mereproduksi, dari `ai-service/` dengan venv aktif:

```bash
python -m app.generator --set dev
python -m app.generator --set test
python -m app.classification --set dev
python -m app.classification --set test
python -m app.evaluation --set dev
python -m app.evaluation --set test
```

## 2. Hasil dengan ambang awal

Ambang awal: `empty_min_occupied_minutes` = 10 dan `outside_schedule_min_minutes` = 30 (keduanya asumsi tim).

| Set | Pasangan | Accuracy | Macro F1 | Galat |
|---|---|---|---|---|
| dev | 2.010 | 0,9796 | 0,9669 | 41 |
| test | 2.007 | 0,9846 | 0,9771 | 31 |

Set test, per kelas:

| Kelas | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| sesuai_jadwal | 0,9819 | 1,0000 | 0,9909 | 1683 |
| kosong_meski_terjadwal | 1,0000 | 0,8877 | 0,9405 | 276 |
| dipakai_di_luar_jadwal | 1,0000 | 1,0000 | 1,0000 | 48 |

Matriks kebingungan set test (baris = benar, kolom = prediksi):

| | sesuai_jadwal | kosong_meski_terjadwal | dipakai_di_luar_jadwal |
|---|---|---|---|
| sesuai_jadwal | 1683 | 0 | 0 |
| kosong_meski_terjadwal | 31 | 245 | 0 |
| dipakai_di_luar_jadwal | 0 | 0 | 48 |

Set dev, kelas `kosong_meski_terjadwal`: precision 1,0000, recall 0,8392, F1 0,9126, support 255 (214 benar, 41 terbaca `sesuai_jadwal`).

Seluruh galat di kedua set berasal dari satu arah dan satu penyebab: sesi yang tidak dihadiri (`tidak_hadir`) terbaca `sesuai_jadwal`. Kelas `dipakai_di_luar_jadwal` benar seluruhnya.

## 3. Penyetelan `empty_min_occupied_minutes` (set dev saja)

Hanya nilai ini yang divariasikan, nilai lain tetap. Setiap putaran menjalankan ulang runner lalu evaluasi pada seluruh set dev. Putaran terakhir mengembalikan nilai ke 10 dan hasilnya identik dengan putaran pertama (accuracy 0,9796).

| `empty_min_occupied_minutes` | Accuracy | Macro F1 | Galat | Rincian galat |
|---|---|---|---|---|
| 10 | 0,9796 | 0,9669 | 41 | 41 sesi `tidak_hadir` terbaca sesuai |
| 20 | 0,9955 | 0,9933 | 9 | 6 `selesai_awal` terbaca kosong, 3 `tidak_hadir` terbaca sesuai |
| 30 | 0,9950 | 0,9926 | 10 | 8 `selesai_awal` dan 2 `terlambat` terbaca kosong |
| 40 | 0,9910 | 0,9869 | 18 | 10 `selesai_awal`, 7 `terlambat`, 1 `dipinjam_kegiatan_lain` terbaca kosong |

Catatan membaca tabel:

- Menit terpakai selalu kelipatan 10 dan aturannya memakai `<`. Karena itu nilai 11 sampai 20 menghasilkan hasil yang sama dengan 20, dan nilai 21 sampai 30 sama dengan 30. Grid di atas sudah mencakup semua perilaku berbeda sampai 40.
- Menaikkan ambang menukar jenis galat: sesi yang tidak hadir semakin terdeteksi, tetapi sesi yang hadir sebentar (`terlambat`, `selesai_awal`) mulai terbaca kosong.
- Ambang 20 dan 30 hanya berselisih satu galat dari 2.010 pasangan. Perbedaan itu tidak cukup untuk menyatakan salah satunya lebih baik.
- Kriteria pemilihan: macro F1 tertinggi di set dev, yaitu 20. Alternatifnya 30 bila yang diprioritaskan adalah tidak ada sesi kosong yang terlewat.

## 4. Analisis galat

Dengan ambang 10, sebuah sesi dianggap kosong hanya bila tidak ada satu pun slot terisi. Satu slot 10 menit yang salah terdeteksi sudah cukup membalik hasil. Dugaan penyebabnya adalah noise simulator (salah deteksi sekitar 1% per slot): ground truth dihitung dari okupansi sebelum noise, sedangkan runner membaca okupansi sesudah noise.

Dugaan ini sejalan dengan dua hal yang teramati: seluruh galat berasal dari sesi `tidak_hadir`, dan galat turun dari 41 ke 3 ketika ambang dinaikkan sehingga satu slot palsu tidak lagi cukup untuk membalik hasil. Dugaan ini belum diuji langsung dengan mengubah tingkat noise (lihat bagian 6).

## 5. Hasil akhir

- Keputusan ambang final: **TODO-ISI** (hasil sprint review dengan manpro).
- Set test sudah dievaluasi satu kali dengan ambang awal 10 sebelum penyetelan. Setelah ambang final ditetapkan, set test dievaluasi satu kali lagi.

| Set test | Accuracy | Macro F1 | Galat |
|---|---|---|---|
| Ambang 10 (sebelum penyetelan) | 0,9846 | 0,9771 | 31 |
| Ambang final | TODO-ISI | TODO-ISI | TODO-ISI |

Mengubah nilai bawaan ambang berarti mengubah seeder `threshold_settings` dan DATA_CONTRACT Bagian 7.3 dan 8. Perubahan itu dikerjakan di PR terpisah yang disepakati kedua anggota tim.

## 6. Keterbatasan

1. Semua data adalah simulasi. Ambang terbaik di sini adalah ambang terbaik untuk simulator ini, belum tentu untuk ruang sungguhan.
2. Galat `selesai_awal` dan `terlambat` bergantung pada parameter skenario simulator. Ambang yang lebih tinggi tampak buruk di set ini karena simulator memang membuat sesi hadir singkat.
3. Hanya satu seed per set dan hanya 10 ruang. Selisih satu atau dua galat tidak bermakna secara statistik.
4. Sesi yang ruangannya dipakai kegiatan lain lewat peminjaman di TU tidak terbedakan dari sesi biasa tanpa data PENRU (DATA_CONTRACT Bagian 13 butir 2).
5. Uji sensitivitas terhadap tingkat noise belum dikerjakan: **TODO-ISI** (dikerjakan, atau dicatat sebagai pekerjaan lanjutan bila generator tidak mengizinkan noise diatur tanpa mengubah kodenya).
