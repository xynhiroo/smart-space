# Backlog Smart Space Analytics Platform (PBLIF3-PD08)

Versi 1.2, 18 Oktober 2026. Pendamping `docs/ROADMAP.md` (v1.2) dan `docs/PRD_Smart_Space_Analytics_Platform.md` (v1.2). Nomor kartu mengikuti issue GitHub (judul issue berbentuk [SS-S1-NN]). SS1-01 sampai SS1-08 sudah ada; SS1-07 dan SS1-08 memperluas issue #40 dan #41, sedangkan SS1-09 sampai SS1-14 adalah kartu baru.

Label GitHub yang disarankan: `ai`, `ml`, `laravel`, `docs`, `must`, `pasca-ats`. Milestone: **Sprint 1 - Inti AI (sampai 30 Okt)** dan **Sprint 2 - Finalisasi (setelah ATS)**.

## 1. Ringkasan

| Kode | Judul | Pemilik | Target | Bergantung pada | Priority | Size | Status |
|---|---|---|---|---|---|---|---|
| SS1-07 | Kontrak data dan migrasi tabel AI | Rangga | PR Jum 16 Okt, merge Sen 19 Okt | SS1-03 (selesai) | P0 | M (5) | Done (PR #55 merged) |
| SS1-08 | Generator data dummy okupansi historis | Rangga | PR Rab 21 Okt, merge Kam 22 Okt | SS1-07 | P0 | L (8) | Ready for Review |
| SS1-09 | Sistem pakar klasifikasi status ruangan (Tier 1) | Rangga | PR Sen 26 Okt, merge Sel 27 Okt | SS1-07 (kontrak data) | P0 | L (8) | Sprint Backlog |
| SS1-10 | Utilisasi dan statistik efisiensi ruangan | Dika | PR Jum 23 Okt, merge Sen 26 Okt | SS1-07 (skema dan antarmuka fungsi) | P1 | S (3) | Done (PR #56 merged) |
| SS1-11 | FastAPI dan integrasi database | Dika | PR Rab 28 Okt, merge Kam 29 Okt | SS1-07 (antarmuka fungsi), SS1-09, SS1-10 | P1 | M (5) | Sprint Backlog |
| SS1-12 | Validasi akurasi sistem pakar | Dika | PR Kam 29 Okt, merge Jum 30 Okt | SS1-08, SS1-09 | P1 | M (5) | Sprint Backlog |
| SS1-13 | Dokumen rancangan AI dan bahan presentasi | Rangga dan Dika | Draf Jum 23 Okt, final Jum 6 Nov (cadangan), latihan 2-6 Nov | Berjalan paralel dengan SS1-07 sampai SS1-12 | P1 | L (8) | Sprint Backlog |
| SS1-14 | Model ML: risiko sesi terjadwal kosong | Rangga | Mulai Sel 27 Okt, PR Kam 29 Okt, merge Jum 30 Okt | SS1-08, SS1-09 (label status) | P1 | L (8) | Sprint Backlog |

Skala Size: XS=2, S=3, M=5, L=8 poin (usulan, disepakati di sinkron). Selesai: SS1-01 (PR #53) dan SS1-04 (PR #54) diselesaikan Dika lebih awal; SS1-02 (PR #44), SS1-03 (PR #42), SS1-07 (PR #55), dan SS1-10 (PR #56). SS1-08 selesai lebih awal (18 Okt) siap review PR. Jalur kritis AI (SS1-07, SS1-08, SS1-09, SS1-14) dipegang Rangga; kartu yang tidak memblokir (SS1-10, SS1-11, SS1-12) dipegang Dika; SS1-13 berdua.

## 2. Rincian kartu Sprint 1 (inti AI)

### SS1-07 Kontrak data dan migrasi tabel AI

- Label: ai, laravel, must
- Pemilik: Rangga (reviewer: Dika)
- Priority: P0 | Size: M (5) | Status: Done (PR #55 merged)
- Target: PR Jum 16 Okt, merge Sen 19 Okt
- Branch: `feature/ss1-07-kontrak-data-migrasi`
- Kebutuhan: FR-04, FR-05, FR-06 (skema); PRD Bagian 10
- Materi matkul AI: Rancangan aplikasi AI dan hubungan database (capaian umum matkul)
- Bergantung pada: SS1-03 (selesai)

**Tujuan.** Menyepakati bentuk data yang dipertukarkan antara generator, sistem pakar, dan API sebelum kode AI ditulis, supaya Rangga dan Dika dapat bekerja paralel.

**Tugas**

- [x] Tulis docs/DATA_CONTRACT.md: slot 10 menit, jam operasional 07.00-23.00 (96 slot per hari), jeda 17.00-17.10 tidak dievaluasi, arti is_occupied, zona waktu WIB.
- [x] Catat definisi operasional final: sesi dinilai setelah jam terjadwal berakhir; status kosong meski terjadwal bila menit_terpakai < empty_min_occupied_minutes (awal 10); sesuai jadwal bila sebaliknya; dipakai di luar jadwal bila ada episode okupansi di luar semua jendela jadwal ruang itu, dalam jam operasional, dengan durasi >= outside_schedule_min_minutes (awal 30). Kedua nilai awal adalah asumsi tim yang divalidasi dengan manpro.
- [x] Granularitas final: satu baris classification_results per ruang per sesi per tanggal; episode di luar jadwal menjadi baris dengan schedule_id kosong.
- [x] Migrasi Laravel occupancy_logs: id, room_id, slot_mulai, is_occupied, source (default dummy); unik pada room_id + slot_mulai.
- [x] Migrasi Laravel classification_results: id, room_id, schedule_id (boleh kosong), tanggal, waktu_mulai, waktu_selesai, status, menit_terjadwal, menit_terpakai, utilisasi_pct (kosong bila menit_terjadwal = 0), rule_id, penjelasan, computed_at.
- [x] Perbarui ThresholdSettingSeeder: tambah empty_min_occupied_minutes (10) dan outside_schedule_min_minutes (30); sesuaikan test threshold yang ada.
- [x] Tetapkan antarmuka fungsi (nama, parameter, bentuk hasil) untuk klasifikasi sesi dan penghitungan utilisasi di DATA_CONTRACT.md, agar SS1-10 dan SS1-11 dapat dikerjakan paralel.
- [x] Tambahkan model SQLAlchemy yang sesuai di ai-service/app/models.py.
- [x] Masukkan PRD v1.1 ke docs/ (menggantikan v1.0).

**Kriteria selesai**

- [x] php artisan migrate:fresh --seed sukses.
- [x] Test skema lulus di database smart_space_test.
- [x] Model SQLAlchemy dapat membaca tabel baru.
- [x] DATA_CONTRACT.md disetujui Dika di PR.
- [x] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-08 Generator data dummy okupansi historis

- Label: ai, must
- Pemilik: Rangga (reviewer: Dika)
- Priority: P0 | Size: L (8) | Status: Ready for Review (selesai 18 Okt)
- Target: PR Rab 21 Okt, merge Kam 22 Okt
- Branch: `feature/ss1-08-generator-dummy-okupansi`
- Kebutuhan: FR-04; HIRARC risiko 2 dan 4
- Materi matkul AI: Persiapan data; pembagian data tanpa kebocoran (AI6)
- Bergantung pada: SS1-07

**Tujuan.** Membangkitkan data okupansi yang menyerupai keluaran sensor dari jadwal nyata, lengkap dengan label kebenaran untuk validasi.

**Tugas**

- [x] Modul ai-service/app/generator/ membaca rooms, schedules, calendar_exceptions dari DB; rentang tanggal default satu semester penuh (2026-09-07 sampai 2027-01-22) dan seed dapat diatur lewat CLI.
- [x] Normalisasi nama hari kalender akademik dan jadwal menggunakan modul bersama app/calendar_utils.py.
- [x] Perilaku per sesi: hadir tepat waktu, terlambat, selesai lebih awal, tidak hadir; parameter dapat diubah.
- [x] Efek kalender: libur tidak ada sesi; masa ujian dan minggu pengganti berpola berbeda.
- [x] Pemakaian di luar jadwal: peluang rendah di ruang biasa, sedikit lebih tinggi di GU 701, GU 705, GU 707.
- [x] Skenario sesi tidak berlangsung lalu ruang dipinjam kegiatan lain lewat TU (peluang kecil): okupansi muncul pada jendela jadwal.
- [x] Noise (nilai awal, asumsi): salah deteksi 1% per slot dan slot hilang 2%; jeda 17.00-17.10 tidak diisi.
- [x] Dua set data dengan seed berbeda: set dev (`smart_space_ai_dev`, seed 1001) dan set test (`smart_space_ai_test`, seed 2002), ditandai jelas.
- [x] Tulis ke occupancy_logs (source=dummy) dan ke berkas ground truth di `ai-service/data/ground_truth/` (ground_truth_dev.csv dan ground_truth_test.csv) di luar DB, tidak dibaca sistem pakar. Kolom: tanggal, room_id, schedule_id, waktu_mulai, waktu_selesai, status_benar, penyebab.
- [x] Tulis docs/DATA_CARD.md: asumsi, parameter, skenario, keterbatasan (termasuk kasus dipinjam TU yang tidak terbedakan tanpa data PENRU).

**Kriteria selesai**

- [x] Seed sama menghasilkan data identik (diuji).
- [x] Tidak ada log pada jeda 17.00-17.10 (diuji).
- [x] Ringkasan distribusi per ruang masuk akal dan tercatat di DATA_CARD.md.
- [ ] Test lulus dan PR di-approve.
- [ ] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-09 Sistem pakar klasifikasi status ruangan (Tier 1)

- Label: ai, must
- Pemilik: Rangga (reviewer: Dika)
- Priority: P0 | Size: L (8) | Status: Sprint Backlog
- Target: PR Sen 26 Okt, merge Sel 27 Okt
- Branch: `feature/ss1-09-sistem-pakar-klasifikasi`
- Kebutuhan: FR-05, FR-10, FR-11
- Materi matkul AI: AI2 production rules dan frames; AI4 sistem pakar
- Bergantung pada: SS1-07 (kontrak data). Dites dengan data contoh buatan tangan; tidak menunggu SS1-08.

**Tujuan.** Mengklasifikasikan status ruangan sebagai sistem pakar dengan arsitektur dari materi AI4 (basis pengetahuan, mesin inferensi, mekanisme penjelasan).

**Tugas**

- [ ] Basis pengetahuan: aturan IF-THEN ber-rule_id (R01, R02, dst) terpisah dari mesin inferensi; Ruang dan Sesi direpresentasikan sebagai frame (slot: nama, tipe open-space, jadwal).
- [ ] Semua ambang dibaca dari threshold_settings (empty_min_occupied_minutes, outside_schedule_min_minutes, batas utilisasi), tanpa angka yang ditulis langsung di kode.
- [ ] Normalisasi dan pencocokan nama hari pada jadwal menggunakan modul bersama app/calendar_utils.py.
- [ ] Mesin inferensi forward chaining deterministik dari fakta (jadwal, okupansi, waktu evaluasi) ke status.
- [ ] Tiga status sesuai definisi operasional di DATA_CONTRACT.md; jeda 17.00-17.10 dan di luar jam operasional tidak dievaluasi; episode di luar jadwal ditandai untuk Admin (FR-10).
- [ ] Mekanisme penjelasan: tiap hasil menyimpan rule_id dan kalimat penjelasan Bahasa Indonesia. Penjelasan status kosong boleh menyebut bahwa ruang berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU (informasi saja, bukan fitur booking).
- [ ] Menulis hasil sesuai skema classification_results dengan antarmuka fungsi murni berbahasa Indonesia (mengikuti gaya modul utilisasi SS1-10: `klasifikasikan_sesi`, `deteksi_pemakaian_luar_jadwal`, `klasifikasikan_hari`) dan hasil evaluasi dapat dipetakan langsung ke tipe `Sesi` untuk penghitungan utilisasi.
- [ ] Unit test per aturan dan per kasus batas, termasuk sesi yang berakhir tepat di batas ambang.

**Kriteria selesai**

- [ ] Setiap aturan punya test.
- [ ] Hasil memuat rule_id dan penjelasan.
- [ ] Tidak ada ambang yang ditulis langsung di kode (diperiksa reviewer).
- [ ] Perilaku sesuai definisi operasional di DATA_CONTRACT.md.
- [ ] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-10 Utilisasi dan statistik efisiensi ruangan

- Label: ai, must
- Pemilik: Dika (reviewer: Rangga)
- Priority: P1 | Size: S (3) | Status: Done (PR #56 merged)
- Target: PR Jum 23 Okt, merge Sen 26 Okt
- Branch: `feature/ss1-10-utilisasi-statistik`
- Kebutuhan: FR-06; RPP: estimasi statistik efisiensi
- Materi matkul AI: AI6 metrik statistik (korelasi Pearson dan Spearman)
- Bergantung pada: SS1-07 (skema dan antarmuka fungsi). Mulai Rab 21 Okt.

**Tujuan.** Menghitung tingkat utilisasi tiap ruangan dan statistik efisiensi pemanfaatannya.

**Tugas**

- [x] Utilisasi = (jam benar-benar terpakai / jam terjadwal) x 100% per ruang per periode (hari, minggu, semester berjalan).
- [x] Kategori rendah (0-40), sedang (41-80), tinggi (81-100) dari threshold_settings; tangani celah desimal (usulan: <=40 rendah, <=80 sedang, selebihnya tinggi) dan jam terjadwal nol.
- [x] Statistik efisiensi: rata-rata, minimum, maksimum per ruang; selisih jam terjadwal dan terpakai; korelasi Pearson dan Spearman antara jam terjadwal dan terpakai antar ruang (catat bahwa jumlah ruang hanya 10).
- [x] Unit test dengan hitungan manual.

**Kriteria selesai**

- [x] Hasil cocok dengan hitungan manual pada data contoh.
- [x] Kasus jam terjadwal nol dan nilai batas teruji.
- [x] Kategori memakai ambang dari DB.
- [x] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-11 FastAPI dan integrasi database

- Label: ai, must
- Pemilik: Dika (reviewer: Rangga)
- Priority: P1 | Size: M (5) | Status: Sprint Backlog
- Target: PR Rab 28 Okt, merge Kam 29 Okt
- Branch: `feature/ss1-11-fastapi-integrasi-db`
- Kebutuhan: FR-05, FR-06, FR-10; NFR-07
- Materi matkul AI: Hubungan database dan pengujian aplikasi AI (capaian umum matkul)
- Bergantung pada: SS1-07 (antarmuka fungsi), SS1-09, SS1-10

**Tujuan.** Menyajikan klasifikasi dan utilisasi lewat API yang membaca data master dari MySQL dan menulis hasil ke tabel milik Python.

**Tugas**

- [ ] Endpoint: GET /health, POST /classify (rentang tanggal, menulis classification_results), GET /results, GET /utilization.
- [ ] Idempoten: menjalankan ulang rentang yang sama mengganti hasil, tidak menggandakan baris.
- [ ] Membaca rooms, schedules, threshold_settings dari MySQL; memetakan key threshold ke parameter fungsi (mis. `utilization_low_max` ke `batas_rendah`, `utilization_medium_max` ke `batas_sedang`); mengintegrasikan fungsi analitik nyata (`hitung_statistik_ruang`, `tentukan_kategori`) dan sistem pakar; hanya menulis ke `occupancy_logs` dan `classification_results`.
- [ ] Konfigurasi dari .env; dokumentasi Swagger; test dengan TestClient; README cara menjalankan.

**Kriteria selesai**

- [ ] Semua endpoint lulus test.
- [ ] Menjalankan ulang tidak menggandakan baris.
- [ ] Python tidak menulis tabel milik Laravel (diperiksa reviewer).
- [ ] Swagger tampil.
- [ ] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-12 Validasi akurasi sistem pakar

- Label: ai, must
- Pemilik: Dika (reviewer: Rangga)
- Priority: P1 | Size: M (5) | Status: Sprint Backlog
- Target: PR Kam 29 Okt, merge Jum 30 Okt
- Branch: `feature/ss1-12-validasi-sistem-pakar`
- Kebutuhan: RPP fase Test (validasi keakuratan data analitik); HIRARC risiko 2 dan 4
- Materi matkul AI: AI6 evaluasi (confusion matrix, precision, recall, F1)
- Bergantung pada: SS1-08, SS1-09

**Tujuan.** Membuktikan seberapa akurat sistem pakar terhadap label kebenaran generator, tanpa kebocoran data.

**Tugas**

- [ ] Notebook ai-service/notebooks/01_validasi_sistem_pakar.ipynb: membaca ground truth dari `ai-service/data/ground_truth/ground_truth_test.csv` dan database `smart_space_ai_test`.
- [ ] Confusion matrix 3 kelas; precision, recall, F1 per kelas; accuracy.
- [ ] Analisis kesalahan: kapan dan mengapa aturan salah (terutama akibat noise); uji sensitivitas terhadap tingkat noise.
- [ ] Penyetelan empty_min_occupied_minutes dan outside_schedule_min_minutes hanya pada set dev (`smart_space_ai_dev`), lalu dievaluasi sekali pada set test (`smart_space_ai_test`) tanpa kebocoran data; catat dampak nilai ambang terhadap precision dan recall.
- [ ] Bukti bahwa aturan dirancang hanya dari set dev; ringkasan di docs/EVALUASI_AI.md beserta keterbatasan data simulasi.

**Kriteria selesai**

- [ ] Set test tidak dipakai untuk mengubah aturan (dicatat di PR).
- [ ] Hasil dapat diulang dengan seed yang sama.
- [ ] EVALUASI_AI.md memuat keterbatasan.
- [ ] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-13 Dokumen rancangan AI dan bahan presentasi

- Label: ai, docs, must
- Pemilik: Rangga dan Dika (masing-masing menulis bagiannya; reviewer silang)
- Priority: P1 | Size: L (8) | Status: Sprint Backlog
- Target: Draf Jum 23 Okt, final Jum 6 Nov (cadangan), latihan 2-6 Nov
- Branch: `feature/ss1-13-dokumen-rancangan-ai`
- Kebutuhan: RPP fase Design; NFR-04, NFR-07
- Materi matkul AI: Seluruh AI1 sampai AI6 (lihat matriks di ROADMAP.md bagian 8)
- Bergantung pada: Berjalan paralel dengan SS1-07 sampai SS1-12

**Tujuan.** Mendokumentasikan rancangan AI dan menunjukkan secara terlacak bahwa materi matkul AI diterapkan.

**Tugas**

- [x] docs/AI_DESIGN.md: posisi proyek dalam ruang lingkup AI (AI1).
- [x] Arsitektur sistem pakar dan representasi pengetahuan: production rules, frames, diagram jaringan semantik ruang-jadwal-okupansi-status (AI2, AI4).
- [ ] Pemetaan DSS: jenis, pasif vs aktif, lima fase keputusan, komponen (AI3).
- [ ] Alur data, kontrak data, rancangan evaluasi (AI6), keterbatasan data simulasi.
- [ ] Etika dan UU PDP: data dummy tanpa identitas individu (NFR-04).
- [ ] README ai-service dan skrip demo yang dapat dijalankan dari nol; slide presentasi.
- [x] Isi kolom 'Tautan bukti' di matriks ROADMAP.md.

**Kriteria selesai**

- [ ] Setiap klaim penerapan materi menunjuk ke berkas atau PR di repo.
- [ ] Satu kali latihan presentasi berdua.
- [ ] Skrip demo berjalan dari nol mengikuti README.
- [ ] Memenuhi DoD di ROADMAP.md bagian 7.

### SS1-14 Model ML: risiko sesi terjadwal kosong

- Label: ai, ml, must
- Pemilik: Rangga (reviewer: Dika)
- Priority: P1 | Size: L (8) | Status: Sprint Backlog
- Target: Mulai Sel 27 Okt, PR Kam 29 Okt, merge Jum 30 Okt
- Branch: `feature/ss1-14-model-risiko-sesi-kosong`
- Kebutuhan: Tier 2 (PRD Bagian 9, dinaikkan prioritasnya)
- Materi matkul AI: AI5 klasifikasi; AI6 evaluasi, overfitting, kelas tidak seimbang
- Bergantung pada: SS1-08, SS1-09 (label status)

**Tujuan.** Memprediksi sesi terjadwal mana yang berisiko tidak dipakai, dan mengevaluasinya sesuai materi AI6.

**Tugas**

- [ ] Dataset fitur per sesi hanya dari informasi sebelum sesi: ruang, hari, jam mulai, durasi, shift, tipe open-space, pekan ke-, dekat libur atau ujian, tingkat kosong ruang itu pada pekan-pekan sebelumnya. Label: status sesi dari classification_results (kosong meski terjadwal vs lainnya).
- [ ] Pembagian kronologis (pekan awal untuk latih, pekan akhir untuk uji) pada data satu semester penuh memungkinkan pengujian tambahan pada potongan pekan ujian atau libur dengan jumlah sampel kelas positif yang lebih memadai.
- [ ] Baseline: selalu menebak kelas mayoritas; rata-rata historis per ruang.
- [ ] Dua model klasifikasi dari AI5: Decision Tree dan Logistic Regression.
- [ ] Metrik AI6: confusion matrix, accuracy, precision, recall, F1, ROC-AUC; bahas ketidakseimbangan kelas dan pilihan metrik.
- [ ] Tabel error latih vs uji untuk memeriksa overfitting dan underfitting (misalnya pengaruh kedalaman pohon); analisis kesalahan.
- [ ] Simpan model (joblib) dan endpoint POST /predict/risk; notebook ai-service/notebooks/02_model_risiko_kosong.ipynb.
- [ ] Tulis keterbatasan: label berasal dari data simulasi, sehingga model bisa hanya mempelajari aturan generator.

**Kriteria selesai**

- [ ] Tidak ada fitur yang memuat informasi dari sesi yang diprediksi (diperiksa reviewer).
- [ ] Model dibandingkan baseline dengan angka.
- [ ] Hasil dapat diulang (seed tetap); test endpoint lulus.
- [ ] Bila SS1-07 sampai SS1-09 belum merged pada Sen 26 Okt, lingkup dipersempit menjadi satu model plus baseline.
- [ ] Memenuhi DoD di ROADMAP.md bagian 7.

## 3. Backlog Sprint 2 (setelah ATS, belum dirinci)

Issue yang sudah ada di GitHub dan tidak masuk jalur AI sebelum ATS:

| Kode | Issue GitHub | Judul | Kebutuhan | Catatan |
|---|---|---|---|---|
| SS1-01 | #34 | Autentikasi Admin | FR-01 | Selesai di main lebih awal (PR #53) dikerjakan Dika sebelum ATS. |
| SS1-04 | #37 | CRUD data master ruangan | FR-02 | Selesai di main lebih awal (PR #54) dikerjakan Dika; pengaman tolak hapus ruangan yang memiliki jadwal/riwayat serta label kondisi ruangan ditambahkan di PR #57. |
| SS1-05 | #38 | Impor data jadwal real Prodi IF | FR-03 (data awal) | Seeder jadwal dibuat idempoten dengan unique index slot jadwal pada schedules (PR #57). |
| SS1-06 | #39 | Pengelolaan jadwal oleh Admin (CRUD dan override) | FR-03 (bagian Admin) | Pasca-ATS. Bergantung pada autentikasi Admin (SS1-01). |

Kartu baru:

| Kode | Judul | Kebutuhan | Catatan |
|---|---|---|---|
| SS2-02 | Dashboard analitik Admin | FR-07 | Memakai hasil SS1-11 |
| SS2-03 | Laporan analitik PDF/Excel | FR-08 | Setelah SS2-02 |
| SS2-04 | Halaman status ketersediaan ruang Mahasiswa | FR-09 | Login Mahasiswa sudah ada (SS1-02) |
| SS2-05 | Pengaturan threshold oleh Admin | FR-11 | Bergantung SS1-01 |
| SS2-06 | Pengaturan akun Admin | FR-12 | Bergantung SS1-01 |
| SS2-07 | Rekomendasi otomatis berbasis template (Tier 3) | PRD Bagian 9 | MCDM hanya bila diminta dosen atau manpro |
| SS2-08 | Simulasi data okupansi berjalan | FR-04, NFR-01 | Setelah generator historis |
| SS2-09 | Integrasi API Learning (impor jadwal) | FR-03 | Terblokir: menunggu token Pak Anung |
| SS2-10 | Integrasi API PENRU (peminjaman ruang) | FR-13 (draf) | Terblokir: menunggu token Pak Andri Betra |
| SS2-11 | Deployment, HTTPS, dan backup berkala | NFR-03, NFR-06 |  |
| SS2-12 | Pengujian UAT, responsivitas, bahasa antarmuka | NFR-02, NFR-05 |  |
| SS2-13 | Dokumen luaran: laporan akhir, manual book, poster, video, BAST, HKI, SDGs | RPP |  |

Perincian kartu Sprint 2 disusun setelah ATS, dengan tetap mengikuti aturan penyaring lingkup di ROADMAP.md.
