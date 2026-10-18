# Isi issue GitHub siap tempel (Sprint 1 inti AI)

Format mengikuti issue yang sudah ada di repo (User Story, Acceptance Criteria, DOD). Judul issue memakai pola `[SS-S1-NN] Judul`. Dua issue sudah ada dan perlu diperbarui isinya (#40 dan #41); enam lainnya dibuat baru. Assignee sesuai kolom Pemilik.

## [SS-S1-05] Impor data jadwal real Prodi IF (Perbaikan Idempotensi Seeder)

- Tindakan: PERBARUI issue #38 (buka kembali dengan perbaikan di PR #57)
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-05-seeder-jadwal-idempoten`

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim pengembang, saya ingin seeder jadwal bersifat idempoten dan terlindungi oleh unique index slot jadwal, sehingga penjalanan ulang seeder tidak menduplikasi data atau merusak integritas jadwal.

Acceptance Criteria:

- ScheduleSeeder menggunakan `updateOrCreate` pada kombinasi (`room_id`, `hari`, `jam_mulai`).
- Migrasi menambahkan unique constraint/index (`room_id`, `hari`, `jam_mulai`) pada tabel `schedules` (PR #57).
- Menjalankan `php artisan db:seed --class=ScheduleSeeder` berulang kali menghasilkan tepat 102 jadwal tanpa duplikasi.

DOD:

- [ ] php artisan migrate:fresh --seed sukses tanpa bentrok index.
- [ ] ScheduleSeederTest dan integritas skema lulus.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.

## [SS-S1-07] Kontrak data dan migrasi tabel AI

Selesai (merged), tidak perlu ditempel.

## [SS-S1-08] Generator data dummy okupansi historis

- Tindakan: PERBARUI issue #41 (ganti judul dan isi)
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-08-generator-dummy-okupansi`
- Target: PR Rab 21 Okt, merge Kam 22 Okt
- Bergantung pada: SS1-07

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Sistem, saya ingin membangkitkan data dummy okupansi yang menyerupai pola data sensor nyata beserta label kebenarannya, sehingga modul analitik dan validasi punya data realistis sebagai pengganti data real-time perangkat IoT.

Acceptance Criteria:

- Modul ai-service/app/generator/ membaca rooms, schedules, calendar_exceptions dari DB; rentang tanggal default satu semester penuh (2026-09-07 sampai 2027-01-22) dan seed dapat diatur lewat CLI.
- Normalisasi nama hari kalender akademik dan jadwal menggunakan modul bersama app/calendar_utils.py.
- Perilaku per sesi: hadir tepat waktu, terlambat, selesai lebih awal, tidak hadir; parameter dapat diubah.
- Efek kalender: libur tidak ada sesi; masa ujian dan minggu pengganti berpola berbeda.
- Pemakaian di luar jadwal: peluang rendah di ruang biasa, sedikit lebih tinggi di GU 701, GU 705, GU 707.
- Skenario sesi tidak berlangsung lalu ruang dipinjam kegiatan lain lewat TU (peluang kecil): okupansi muncul pada jendela jadwal.
- Noise (nilai awal, asumsi): salah deteksi 1% per slot dan slot hilang 2%; jeda 17.00-17.10 tidak diisi.
- Dua set data dengan seed berbeda: set dev (`smart_space_ai_dev`, seed 1001) dan set test (`smart_space_ai_test`, seed 2002), ditandai jelas.
- Tulis ke occupancy_logs (source=dummy) dan ke berkas ground truth di `ai-service/data/ground_truth/` (ground_truth_dev.csv dan ground_truth_test.csv) di luar DB, tidak dibaca sistem pakar. Kolom: tanggal, room_id, schedule_id, waktu_mulai, waktu_selesai, status_benar, penyebab.
- Tulis docs/DATA_CARD.md: asumsi, parameter, skenario, keterbatasan (termasuk kasus dipinjam TU yang tidak terbedakan tanpa data PENRU).

DOD:

- [ ] Seed sama menghasilkan data identik (diuji).
- [ ] Tidak ada log pada jeda 17.00-17.10 (diuji).
- [ ] Ringkasan distribusi per ruang masuk akal dan tercatat di DATA_CARD.md.
- [ ] Test lulus dan PR di-approve.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.

## [SS-S1-09] Sistem pakar klasifikasi status ruangan (Tier 1)

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-09-sistem-pakar-klasifikasi`
- Target: PR Sen 26 Okt, merge Sel 27 Okt
- Bergantung pada: SS1-07 (kontrak data). Dites dengan data contoh buatan tangan; tidak menunggu SS1-08.

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin sistem mengklasifikasikan status tiap ruangan beserta alasannya, sehingga saya dapat memantau ruang yang dipakai sesuai jadwal, kosong meski terjadwal, atau dipakai di luar jadwal.

Acceptance Criteria:

- Basis pengetahuan: aturan IF-THEN ber-rule_id (R01, R02, dst) terpisah dari mesin inferensi; Ruang dan Sesi direpresentasikan sebagai frame (slot: nama, tipe open-space, jadwal).
- Semua ambang dibaca dari threshold_settings (empty_min_occupied_minutes, outside_schedule_min_minutes, batas utilisasi), tanpa angka yang ditulis langsung di kode.
- Normalisasi dan pencocokan nama hari pada jadwal menggunakan modul bersama app/calendar_utils.py.
- Mesin inferensi forward chaining deterministik dari fakta (jadwal, okupansi, waktu evaluasi) ke status.
- Tiga status sesuai definisi operasional di DATA_CONTRACT.md; jeda 17.00-17.10 dan di luar jam operasional tidak dievaluasi; episode di luar jadwal ditandai untuk Admin (FR-10).
- Mekanisme penjelasan: tiap hasil menyimpan rule_id dan kalimat penjelasan Bahasa Indonesia. Penjelasan status kosong boleh menyebut bahwa ruang berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU (informasi saja, bukan fitur booking).
- Menulis hasil sesuai skema classification_results dengan antarmuka fungsi murni berbahasa Indonesia (mengikuti gaya modul utilisasi SS1-10: `klasifikasikan_sesi`, `deteksi_pemakaian_luar_jadwal`, `klasifikasikan_hari`) dan hasil evaluasi dapat dipetakan langsung ke tipe `Sesi` untuk penghitungan utilisasi.
- Unit test per aturan dan per kasus batas, termasuk sesi yang berakhir tepat di batas ambang.

DOD:

- [ ] Setiap aturan punya test.
- [ ] Hasil memuat rule_id dan penjelasan.
- [ ] Tidak ada ambang yang ditulis langsung di kode (diperiksa reviewer).
- [ ] Perilaku sesuai definisi operasional di DATA_CONTRACT.md.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.

## [SS-S1-10] Utilisasi dan statistik efisiensi ruangan

Selesai (merged), tidak perlu ditempel.

## [SS-S1-11] FastAPI dan integrasi database

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-11-fastapi-integrasi-db`
- Target: PR Rab 28 Okt, merge Kam 29 Okt
- Bergantung pada: SS1-07 (antarmuka fungsi), SS1-09, SS1-10

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai aplikasi Laravel dan dashboard, saya ingin mengakses hasil klasifikasi dan utilisasi lewat API FastAPI, sehingga AI engine terhubung ke database dan aplikasi.

Acceptance Criteria:

- Endpoint: GET /health, POST /classify (rentang tanggal, menulis classification_results), GET /results, GET /utilization.
- Idempoten: menjalankan ulang rentang yang sama mengganti hasil, tidak menggandakan baris.
- Membaca rooms, schedules, threshold_settings dari MySQL; memetakan key threshold ke parameter fungsi (mis. `utilization_low_max` ke `batas_rendah`, `utilization_medium_max` ke `batas_sedang`); mengintegrasikan fungsi analitik nyata (`hitung_statistik_ruang`, `tentukan_kategori`) dan sistem pakar; hanya menulis ke `occupancy_logs` dan `classification_results`.
- Konfigurasi dari .env; dokumentasi Swagger; test dengan TestClient; README cara menjalankan.

DOD:

- [ ] Semua endpoint lulus test.
- [ ] Menjalankan ulang tidak menggandakan baris.
- [ ] Python tidak menulis tabel milik Laravel (diperiksa reviewer).
- [ ] Swagger tampil.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.

## [SS-S1-12] Validasi akurasi sistem pakar

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-12-validasi-sistem-pakar`
- Target: PR Kam 29 Okt, merge Jum 30 Okt
- Bergantung pada: SS1-08, SS1-09

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim pengembang, saya ingin mengukur akurasi sistem pakar terhadap label kebenaran generator, sehingga keandalan klasifikasi terbukti tanpa kebocoran data.

Acceptance Criteria:

- Notebook ai-service/notebooks/01_validasi_sistem_pakar.ipynb: membaca ground truth dari `ai-service/data/ground_truth/ground_truth_test.csv` dan database `smart_space_ai_test`.
- Confusion matrix 3 kelas; precision, recall, F1 per kelas; accuracy.
- Analisis kesalahan: kapan dan mengapa aturan salah (terutama akibat noise); uji sensitivitas terhadap tingkat noise.
- Penyetelan empty_min_occupied_minutes dan outside_schedule_min_minutes hanya pada set dev (`smart_space_ai_dev`), lalu dievaluasi sekali pada set test (`smart_space_ai_test`) tanpa kebocoran data; catat dampak nilai ambang terhadap precision dan recall.
- Bukti bahwa aturan dirancang hanya dari set dev; ringkasan di docs/EVALUASI_AI.md beserta keterbatasan data simulasi.

DOD:

- [ ] Set test tidak dipakai untuk mengubah aturan (dicatat di PR).
- [ ] Hasil dapat diulang dengan seed yang sama.
- [ ] EVALUASI_AI.md memuat keterbatasan.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.

## [SS-S1-13] Dokumen rancangan AI dan bahan presentasi

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo dan Muradika (masing-masing menulis bagiannya; reviewer silang)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-13-dokumen-rancangan-ai`
- Target: Draf Jum 23 Okt, final Jum 6 Nov (cadangan), latihan 2-6 Nov
- Bergantung pada: Berjalan paralel dengan SS1-07 sampai SS1-12

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim pengembang, saya ingin dokumen rancangan AI dan bahan presentasi, sehingga penerapan materi matkul AI terlacak dan dapat dipresentasikan ke dosen dan klien.

Acceptance Criteria:

- docs/AI_DESIGN.md: posisi proyek dalam ruang lingkup AI (AI1).
- Arsitektur sistem pakar dan representasi pengetahuan: production rules, frames, diagram jaringan semantik ruang-jadwal-okupansi-status (AI2, AI4).
- Pemetaan DSS: jenis, pasif vs aktif, lima fase keputusan, komponen (AI3).
- Alur data, kontrak data, rancangan evaluasi (AI6), keterbatasan data simulasi.
- Etika dan UU PDP: data dummy tanpa identitas individu (NFR-04).
- README ai-service dan skrip demo yang dapat dijalankan dari nol; slide presentasi.
- Isi kolom 'Tautan bukti' di matriks ROADMAP.md.

DOD:

- [ ] Setiap klaim penerapan materi menunjuk ke berkas atau PR di repo.
- [ ] Satu kali latihan presentasi berdua.
- [ ] Skrip demo berjalan dari nol mengikuti README.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.

## [SS-S1-14] Model ML: risiko sesi terjadwal kosong

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 1 - Inti AI (sampai 30 Okt)
- Branch: `feature/ss1-14-model-risiko-sesi-kosong`
- Target: Mulai Sel 27 Okt, PR Kam 29 Okt, merge Jum 30 Okt
- Bergantung pada: SS1-08, SS1-09 (label status)

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin sistem memprediksi sesi terjadwal yang berisiko tidak dipakai, sehingga ruang yang kemungkinan kosong dapat dikenali lebih awal.

Acceptance Criteria:

- Dataset fitur per sesi hanya dari informasi sebelum sesi: ruang, hari, jam mulai, durasi, shift, tipe open-space, pekan ke-, dekat libur atau ujian, tingkat kosong ruang itu pada pekan-pekan sebelumnya. Label: status sesi dari classification_results (kosong meski terjadwal vs lainnya).
- Pembagian kronologis (pekan awal untuk latih, pekan akhir untuk uji) pada data satu semester penuh memungkinkan pengujian tambahan pada potongan pekan ujian atau libur dengan jumlah sampel kelas positif yang lebih memadai.
- Baseline: selalu menebak kelas mayoritas; rata-rata historis per ruang.
- Dua model klasifikasi dari AI5: Decision Tree dan Logistic Regression.
- Metrik AI6: confusion matrix, accuracy, precision, recall, F1, ROC-AUC; bahas ketidakseimbangan kelas dan pilihan metrik.
- Tabel error latih vs uji untuk memeriksa overfitting dan underfitting (misalnya pengaruh kedalaman pohon); analisis kesalahan.
- Simpan model (joblib) dan endpoint POST /predict/risk; notebook ai-service/notebooks/02_model_risiko_kosong.ipynb.
- Tulis keterbatasan: label berasal dari data simulasi, sehingga model bisa hanya mempelajari aturan generator.

DOD:

- [ ] Tidak ada fitur yang memuat informasi dari sesi yang diprediksi (diperiksa reviewer).
- [ ] Model dibandingkan baseline dengan angka.
- [ ] Hasil dapat diulang (seed tetap); test endpoint lulus.
- [ ] Bila SS1-07 sampai SS1-09 belum merged pada Sen 26 Okt, lingkup dipersempit menjadi satu model plus baseline.
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] Kode sudah direview rekan satu tim.
