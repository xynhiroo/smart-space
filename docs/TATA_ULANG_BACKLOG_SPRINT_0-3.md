# Tata Ulang Backlog: Sprint 0, 1, 2, dan 3 (Smart Space Analytics Platform)

Versi 1.3, 25 November 2026 (menyesuaikan Figma dan menambah aturan IMK, software engineering, dan modern-web-guidance). Menggantikan v1.2. Penomoran disamakan dengan Laporan Kemajuan: Sprint 0 (US-01 sampai US-06), Sprint 1 (US-07 sampai US-12), Sprint 2 (US-13 sampai US-20), Sprint 3 (pasca-ATS). Format issue mengikuti `docs/GITHUB_ISSUES.md`.

## 1. Kalender dan posisi sprint

Dari Kalender Akademik TA 2026/2027 (jadwal tentatif): kuliah perdana 7 Sep; minggu pengganti pra ATS 26-30 Okt; ATS 2-13 Nov; Natal 24-25 Des; Tahun Baru 1 Jan; minggu pengganti 4-8 Jan; **AAS 11-22 Jan 2027**. Kalender menomori minggu kuliah I sampai XIV tanpa minggu pengganti dan ATS, jadi bila RPS memakai penomoran yang sama (mohon konfirmasi ke Pak Agung): Sprint 2 (minggu 7-10) berakhir Jum 4 Des, Sprint 3 (minggu 11-13) berjalan 7-25 Des, dan minggu 14 (28 Des-1 Jan) untuk finalisasi. Pekerjaan Sprint 3 yang dimulai lebih awal ditandai di kolom target.

## 2. Susunan sprint di GitHub

| Sprint | Kode | Isi | Status sekarang |
|---|---|---|---|
| 0 | SS-S0-01 sampai 14, [RPP-xx], [PLAN] (#1 sampai #33) | Perencanaan | Semua closed. Hanya pasang milestone Sprint 0. |
| 1 | SS-S1-01 sampai 06 (#34 sampai #39) | Fondasi aplikasi | 01-05 closed. **SS-S1-06 (#39) masih open (carry-over)**, dikerjakan di Sprint 2. |
| 2 | SS-S2-01 sampai 08 (#40 sampai #52, dulu SS-S1-07 sampai 14) | Inti AI | Closed kecuali **#49 (SS2-05) dibuka kembali** dan **#51 (SS2-07) open**. |
| 2 | SS-S2-09 (baru) | CI | Baru |
| 3 | SS-S3-01 sampai 15 (baru) | Dashboard, laporan, status Mahasiswa, ambang, deployment, UAT, dokumen | Baru |

### 2.1 Penggantian nama issue Sprint 2

Kartu AI yang sekarang berkode SS-S1-07 sampai 14 sebenarnya Sprint 2 menurut laporan (Tabel 4.8, US-13 sampai US-20). Judul issue diganti dan kode lama disimpan sebagai alias supaya PR, ROADMAP, DATA_CONTRACT, dan DATA_CARD yang menyebut kode lama tetap bisa ditelusuri.

| Issue | Kode lama | Judul baru | US laporan | Aksi |
|---|---|---|---|---|
| #40 | SS1-07 | [SS-S2-01] Kontrak data dan migrasi tabel AI | US-13 | ganti judul, milestone Sprint 2 |
| #41 | SS1-08 | [SS-S2-02] Generator data dummy okupansi historis | US-14 | ganti judul, milestone Sprint 2 |
| #47 | SS1-09 | [SS-S2-03] Sistem pakar klasifikasi status ruangan (Tier 1) | US-15 | ganti judul, milestone Sprint 2 |
| #48 | SS1-10 | [SS-S2-04] Utilisasi dan statistik efisiensi ruangan | US-16 | ganti judul, milestone Sprint 2 |
| #49 | SS1-11 | [SS-S2-05] FastAPI dan integrasi database | US-17 | **buka kembali**, ganti judul, isi sisa di bagian 6 |
| #50 | SS1-12 | [SS-S2-06] Validasi akurasi sistem pakar | US-18 | ganti judul, milestone Sprint 2 |
| #51 | SS1-13 | [SS-S2-07] Dokumen rancangan AI dan bahan presentasi | US-19 | ganti judul, perbarui isi sisa di bagian 6 |
| #52 | SS1-14 | [SS-S2-08] Model ML: risiko sesi terjadwal kosong | US-20 | ganti judul, milestone Sprint 2 |

### 2.2 Merapikan lainnya

- #34 dan #37: hapus label `pasca-ats` yang tertinggal (keduanya sudah selesai di main), pasang milestone Sprint 1.
- #35, #36, #38: pasang milestone Sprint 1. #39: ganti label `pasca-ats` menjadi `carry-over`, pasang milestone Sprint 2.
- #1 sampai #33: pasang milestone Sprint 0 (opsional).
- Label baru yang perlu dibuat: `carry-over`, `frontend`, `devops`, `should`, `could`.
- Milestone: buat empat milestone sesuai nama di bagian 4; tutup milestone lama 'Sprint 1 - Inti AI' dan 'Sprint 2 - Finalisasi'.
- #49 ditutup pada hal `POST /classify` belum ada di `main.py` dan `rute.py` (hanya GET `/results`, `/utilization`, `/health`). Mohon dicek dulu apakah ada PR atau branch yang belum di-merge sebelum membukanya kembali.
- Kode lama di dokumen repo (BACKLOG.md, ROADMAP.md, GITHUB_ISSUES.md) disinkronkan lewat SS3-10 dengan tabel alias ini. Judul PR lama tidak diubah.
- Kartu lama SS2-02 sampai SS2-13 pada BACKLOG.md bagian 3 dihapus, digantikan SS3-xx: SS2-02 menjadi SS3-03, SS2-03 menjadi SS3-07, SS2-04 menjadi SS3-04, SS2-05 menjadi SS3-06, SS2-06 menjadi SS3-12, SS2-07 menjadi SS3-05, SS2-08 menjadi SS3-13, SS2-11 menjadi SS3-08, SS2-12 menjadi SS3-09, SS2-13 menjadi SS3-10 dan SS3-11. SS2-09 dan SS2-10 (API Learning dan PENRU, terblokir token) diganti nama menjadi BLK-01 dan BLK-02 agar tidak bentrok dengan SS2-09 yang baru.

## 3. Beban

- Total 99 SP. Penutupan Sprint 2 sampai 4 Des: 16 SP (Rangga 2, Dika 14). Sprint 3: 83 SP (Rangga 47, Dika 31, UAT berdua 5). Per orang: Rangga 49 SP, Dika 45 SP.
- Kecepatan Sprint 2 sekitar 12 SP per minggu; 20 Nov sampai 23 Des sekitar 5 minggu kerja, jadi beban masuk akal tetapi ketat. Tidak ada kartu yang menunggu persetujuan manpro.
- Berikutnya: Rangga mendorong SS2-09 (CI) dan membuka PR, lalu SS3-01 (fondasi UI); Dika SS2-05 (`POST /classify`) lalu SS1-06 (kelola jadwal). Tanggal ditinjau ulang setelah status terbaru keduanya diketahui.

## 4. Milestone GitHub

- **Sprint 0 (minggu 1-3)**, **Sprint 1 (minggu 4-6)**, **Sprint 2 - Inti AI (minggu 7-10, sampai 4 Des)**, **Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)**.

## 5. Ringkasan kartu yang dikerjakan

| Kode | Judul | Pemilik | Reviewer | SP | Prioritas | Target | Bergantung pada |
|---|---|---|---|---|---|---|---|
| **Sprint 2 - Inti AI (minggu 7-10, sampai 4 Des)** | | | | | | | |
| SS1-06 | Pengelolaan jadwal oleh Admin: CRUD, cek bentrok, jejak perubahan (carry-over Sprint 1) | Dika | Rangga | 8 | must | PR Jum 27 Nov, merge Sen 30 Nov | SS1-01 (selesai); komponen UI dari SS2-05 bila sudah tersedia (boleh Blade biasa dulu) |
| SS2-05 | FastAPI dan integrasi database (sisa: POST /classify idempoten) | Dika | Rangga | 3 | must | PR Sen 23 Nov, merge Sel 24 Nov | SS2-03 dan SS2-04 (selesai); GET /results dan /utilization (PR #62) serta runner klasifikasi (PR #63) sudah merged |
| SS2-07 | Dokumen rancangan AI dan bahan presentasi (sisa: bagian Dika, gabung ke main) | Dika | Rangga | 3 | must | PR Rab 2 Des, merge Kam 3 Des | SS2-03, SS2-06, SS2-08 (selesai). Bagian Rangga sudah selesai; bagian Dika masih di branch dan belum ada di main |
| SS2-09 | CI GitHub Actions: pytest dan php artisan test pada setiap PR | Rangga | Dika | 2 | must | PR Sen 23 Nov, merge Sel 24 Nov | - |
| **Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)** | | | | | | | |
| SS3-01 | Fondasi UI sesuai Figma: token, layout, komponen, landing, login, halaman error | Rangga | Dika | 8 | must | PR Kam 26 Nov, merge Jum 27 Nov (mulai lebih awal) | - |
| SS3-02 | Jembatan Laravel dan hasil AI (model baca, layanan analitik, klien API) | Rangga | Dika | 5 | must | PR Rab 2 Des, merge Kam 3 Des (mulai lebih awal) | SS2-05 (hanya bagian klien API); bagian baca DB tidak bergantung |
| SS3-03 | Dashboard analitik Admin sesuai Figma | Rangga | Dika | 8 | must | PR Rab 9 Des, merge Kam 10 Des | SS3-01, SS3-02 |
| SS3-04 | Halaman status ketersediaan ruang untuk Mahasiswa | Dika | Rangga | 5 | must | PR Sel 8 Des, merge Rab 9 Des | SS3-01 |
| SS3-05 | Insight otomatis berbasis templat dan panel 'Cara membaca hasil' | Dika | Rangga | 5 | must | PR Jum 11 Des, merge Sen 14 Des | SS2-05; penempatan di dashboard setelah SS3-03 |
| SS3-06 | Pengaturan ambang batas klasifikasi oleh Admin | Rangga | Dika | 5 | should | PR Sen 14 Des, merge Sel 15 Des | SS3-02 |
| SS3-07 | Laporan analitik PDF dan Excel | Dika | Rangga | 8 | must | PR Sen 21 Des, merge Sel 22 Des | SS3-03; SS3-05 untuk bagian kesimpulan |
| SS3-08 | Deployment VPS dengan Docker Compose, HTTPS, dan backup | Rangga | Dika | 8 | must | Compose lokal Jum 4 Des; PR Jum 18 Des, merge Sen 21 Des | SS3-02 dan SS3-03 sudah berjalan |
| SS3-09 | UAT, uji responsif, audit bahasa, dan bug bash | Rangga dan Dika | silang | 5 | must | UAT Sen 21 - Rab 23 Des; perbaikan Sen 28 - Rab 30 Des | SS3-03 sampai SS3-08 |
| SS3-10 | Dokumen luaran A: sinkronisasi dokumen, Laporan Akhir, HKI, SDGs | Rangga | Dika | 5 | must | Draf Jum 18 Des, final Rab 30 Des | Berjalan paralel |
| SS3-11 | Dokumen luaran B: manual book, poster, video demo, BAST, presentasi | Dika | Rangga | 5 | must | Draf Jum 18 Des, final Rab 30 Des | SS3-08 untuk tangkapan layar dan video dari versi final |
| SS3-12 | Pengaturan akun Admin | Dika | Rangga | 3 | could | Could: PR Sen 28 Des | SS1-01 (selesai) |
| SS3-13 | Simulasi okupansi berjalan untuk membuktikan NFR-01 | Rangga | Dika | 3 | could | Could: sebelum Jum 18 Des | SS3-03, SS3-04 |
| SS3-14 | Kartu detail ruangan (dialog) pada Kelola Ruangan | Dika | Rangga | 5 | should | PR Rab 16 Des, merge Kam 17 Des | SS3-01 (komponen), SS3-02 (AnalitikService), SS3-03 |
| SS3-15 | Impor jadwal dari berkas XLSX | Rangga | Dika | 5 | could | Could: PR Rab 23 Des | SS1-06 (sudah merged) |

**Garis potong.** Jum 4 Des: SS2-05, SS2-07, SS1-06, SS2-09 Done, dan SS3-01 serta SS3-02 merged. Jum 11 Des: dashboard, status Mahasiswa, dan insight merged. Bila terlambat, persempit isi kartu ke 'Batas minimum', lalu korbankan berurutan SS3-15, SS3-13, SS3-12, SS3-14, dan persempit SS3-06 serta SS3-07. Tidak boleh dikorbankan: SS2-05, SS1-06, SS3-02, SS3-03, SS3-04, SS3-08, SS3-09. Cadangan 4-8 Jan sebelum AAS 11-22 Jan.

## 6. Keputusan yang kuambil dan hal di luar backlog

1. SS3-05 (insight otomatis) dinaikkan dari Could menjadi Must: manpro dan pengembang Eco-Light menyebut kesimpulan analisis sebagai output yang paling berguna, dan dosen penguji kesulitan memahami output proyek. Isinya deskriptif dan tidak menyarankan perubahan jadwal.
2. Prediksi risiko ML tidak ditampilkan di dashboard karena belum melampaui baseline (F1 0,423 berbanding 0,405); tetap dilaporkan jujur.
3. Laravel membaca langsung `classification_results` dan `occupancy_logs`; FastAPI dipakai untuk memicu klasifikasi (DATA_CONTRACT bagian 3).
4. Ambang bawaan tetap 10 dan 30 menit sampai manpro menyetujui; evaluasi 20 menit pada set test dilaporkan sebagai keterbatasan metodologis.
5. Status Mahasiswa memakai slot okupansi terkini dari data semester penuh (7 Sep 2026 sampai 22 Jan 2027).
6. Deployment ke VPS pribadi tanpa biaya tambahan. Opsi hosting gratis dibahas setelah versi lokal siap.
7. Di luar backlog sampai manpro memutuskan: saran dosen penguji soal data mahasiswa dan fitur relokasi jadwal dari hasil AI. SS1-06 sudah menyediakan fondasinya (cek bentrok, sumber jadwal, jejak perubahan).
8. Halaman DetailRuangan di Figma diimplementasikan sebagai kartu melayang (dialog) pada Kelola Ruangan, bukan halaman baru (keputusan Rangga, SS3-14).
9. Di luar scope tetap: IoT, sensor, kamera, kontrol hardware, booking ruang, dan aktor selain Admin dan Mahasiswa.

## 7. Aturan UI dan engineering (berlaku untuk kartu UI)

- **IMK:** 10 heuristik Nielsen dan aturan emas Shneiderman (konsistensi, umpan balik, pencegahan galat, aksi mudah dibatalkan), target sentuh minimal 44 px, kontras WCAG AA, status tidak hanya warna, pesan galat menjelaskan solusi, bahasa Indonesia konsisten. Uji kemudahan penggunaan dengan skor SUS dilakukan di SS3-09.
- **Software engineering:** controller tipis, logika di service class, validasi di Form Request, komponen Blade tanpa duplikasi, penamaan deskriptif, Feature test untuk perilaku utama, PR kecil dengan CI hijau, tanpa angka ambang di kode, dan keputusan desain dicatat di Catatan Perubahan Desain (laporan Tabel 3.7).
- **modern-web-guidance (GoogleChrome):** sebelum menulis HTML, CSS, atau JS klien, agent menjalankan `npx -y modern-web-guidance@latest search "<2-5 kata>"` lalu `retrieve "<id>"`, memeriksa hasilnya, dan menulis bagian 'Modern Web Guidance' di deskripsi PR. Tidak dipakai untuk backend, CI, atau Docker.
- **Kebijakan peramban (usul untuk AGENTS.md):** 'Browser Support: fitur Baseline Widely available boleh dipakai tanpa fallback; fitur yang belum Widely available hanya dengan deteksi fitur dan degradasi yang wajar, tanpa polyfill besar.'

---

# Isi issue siap tempel

Kartu di bawah adalah kartu yang baru atau yang isinya berubah. Kartu SS2-01 sampai SS2-04, SS2-06, dan SS2-08 hanya perlu ganti judul dan milestone (bagian 2.1).

## [SS-S1-06] Pengelolaan jadwal oleh Admin: CRUD, cek bentrok, jejak perubahan (carry-over Sprint 1)

- Tindakan: PERBARUI issue #39
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 2 - Inti AI (minggu 7-10, sampai 4 Des)
- Label: laravel, must
- Branch: `feature/ss1-06-kelola-jadwal-admin`
- Target: PR Jum 27 Nov, merge Sen 30 Nov
- Estimasi: 8 SP | Prioritas: must
- Kebutuhan: FR-03 (sisi Admin); Praktikum 3 skenario Kelola Jadwal; US-12
- Bergantung pada: SS1-01 (selesai); komponen UI dari SS2-05 bila sudah tersedia (boleh Blade biasa dulu)

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin menambah, mengubah, dan menghapus jadwal resmi penggunaan ruangan, supaya data jadwal yang menjadi acuan sistem selalu akurat.

Acceptance Criteria:

- Daftar jadwal dengan filter ruang dan hari serta pencarian mata kuliah.
- Form tambah dan ubah (ruang, hari, jam mulai, jam selesai, mata kuliah); hapus dengan dialog konfirmasi.
- Validasi: field wajib; hari salah satu dari Senin, Selasa, Rabu, Kamis, Jum'at; jam mulai lebih awal dari jam selesai; kelipatan 10 menit; dalam 07.00-23.00 (DATA_CONTRACT bagian 2).
- Cek bentrok pada ruang dan hari yang sama (tumpang tindih) ditolak dengan pesan jelas; mengikuti alur alternatif 7a dan 7b skenario Praktikum 3.
- Kolom sumber (seed atau override Admin) dan tabel schedule_changes (aksi, jadwal, nilai sebelum dan sesudah, admin, waktu) lewat migrasi Laravel.
- Seeder jadwal tetap idempoten (102 jadwal) dan tidak menimpa jadwal yang sudah di-override (test).
- Penyimpanan dibungkus satu antarmuka sehingga sumber dapat diganti ke API Learning tanpa mengubah UI (US-12).
- Setelah simpan tampil pemberitahuan bahwa klasifikasi perlu dijalankan ulang; hasil klasifikasi lampau tidak diubah.
- Minimal 12 test baru (CRUD, bentrok, validasi, seeder, jejak perubahan).
- Tampilan dan state mengikuti frame KelolaJadwal (halaman 06 Hi-Fi Admin): tampilan Tabel wajib, tampilan Kalender mingguan bila waktu cukup.

Batas minimum bila waktu habis: Tanpa filter pencarian dan tanpa halaman riwayat (jejak tetap dicatat di DB).

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S2-05] FastAPI dan integrasi database (sisa: POST /classify idempoten)

- Tindakan: BUKA KEMBALI dan perbarui #49
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 2 - Inti AI (minggu 7-10, sampai 4 Des)
- Label: ai, must
- Branch: `feature/ss2-05-classify-endpoint`
- Target: PR Sen 23 Nov, merge Sel 24 Nov
- Estimasi: 3 SP | Prioritas: must
- Kebutuhan: FR-05, FR-06, FR-10; NFR-07
- Bergantung pada: SS2-03 dan SS2-04 (selesai); GET /results dan /utilization (PR #62) serta runner klasifikasi (PR #63) sudah merged

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai aplikasi Laravel, saya ingin memicu klasifikasi untuk rentang tanggal lewat API, supaya hasil terbaru tersedia di classification_results tanpa menjalankan skrip manual.

Acceptance Criteria:

- POST /classify menerima tanggal_mulai, tanggal_selesai, dan room_id (opsional); memakai runner klasifikasi (PR #63), sistem pakar, dan ambang dari threshold_settings.
- Idempoten: menjalankan ulang rentang yang sama mengganti hasil dalam satu transaksi dan tidak menggandakan baris (DATA_CONTRACT bagian 9); dibuktikan test.
- Hanya menulis classification_results; tidak menulis tabel milik Laravel.
- Validasi: rentang terbalik 422, ruang tidak ada 404, rentang melebihi satu semester ditolak; galat DB menghasilkan 500 dengan pesan jelas tanpa membocorkan detail internal.
- Endpoint dilindungi token internal (header, nilai dari .env) supaya tidak bisa dipanggil bebas dari luar.
- Respons memuat jumlah baris ditulis dan lama proses; Swagger tampil; test dengan TestClient; README diperbarui.

Batas minimum bila waktu habis: Tanpa filter room_id.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S2-07] Dokumen rancangan AI dan bahan presentasi (sisa: bagian Dika, gabung ke main)

- Tindakan: PERBARUI issue #51
- Assignee (username GitHub): xynhiroo dan Muradika (Muradika yang menyelesaikan sisa) (reviewer: xynhiroo)
- Milestone: Sprint 2 - Inti AI (minggu 7-10, sampai 4 Des)
- Label: ai, docs, must
- Branch: `feature/ss1-13-dokumen-rancangan-ai (branch yang sudah ada)`
- Target: PR Rab 2 Des, merge Kam 3 Des
- Estimasi: 3 SP | Prioritas: must
- Kebutuhan: RPP fase Design; NFR-04, NFR-07; matriks ROADMAP bagian 8
- Bergantung pada: SS2-03, SS2-06, SS2-08 (selesai). Bagian Rangga sudah selesai; bagian Dika masih di branch dan belum ada di main

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim pengembang, saya ingin dokumen rancangan AI yang menunjuk bukti di repositori, supaya penerapan materi matkul AI dapat ditelusuri dan dipresentasikan.

Acceptance Criteria:

- Bagian Dika diselesaikan dan digabung dengan bagian Rangga menjadi docs/AI_DESIGN.md di main lewat satu PR.
- Isi lengkap: posisi proyek dalam ruang lingkup AI (AI1); arsitektur sistem pakar dengan aturan F01-F04 dan R01-R03, frame Ruang dan Sesi, serta diagram jaringan semantik (AI2, AI4); pemetaan DSS (AI3); alur data, kontrak data, ringkasan EVALUASI_AI.md dan hasil model ML terhadap baseline (AI5, AI6); keterbatasan data simulasi; etika dan UU PDP (NFR-04).
- README ai-service dan skrip demo yang berjalan dari nol mengikuti README.
- Kolom 'Tautan bukti' pada matriks ROADMAP bagian 8 terisi; setiap klaim menunjuk berkas atau PR.
- Satu kali latihan presentasi berdua.

Batas minimum bila waktu habis: Lewati diagram jaringan semantik.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S2-09] CI GitHub Actions: pytest dan php artisan test pada setiap PR

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 2 - Inti AI (minggu 7-10, sampai 4 Des)
- Label: docs, devops, must
- Branch: `feature/ss2-09-ci-github-actions`
- Target: PR Sen 23 Nov, merge Sel 24 Nov
- Estimasi: 2 SP | Prioritas: must
- Kebutuhan: NFR-07; DoD proyek
- Bergantung pada: -

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim pengembang, saya ingin pemeriksaan otomatis di setiap Pull Request, supaya error tertangkap sebelum merge dan tidak muncul menjelang deployment.

Acceptance Criteria:

- Workflow backend: composer install, migrate dan seed pada layanan MySQL, lalu php artisan test.
- Workflow ai-service: pip install -r requirements.txt, lalu pytest dengan layanan MySQL.
- Berjalan pada pull_request ke main dengan cache dependensi; lencana status di README.
- Tidak ada kredensial di repositori; .env.example memuat semua variabel yang dibutuhkan.
- Branch protection (wajib status check hijau dan satu approval) diaktifkan oleh pemilik repositori, langkahnya dicatat di README.

Batas minimum bila waktu habis: Satu workflow gabungan.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-01] Fondasi UI sesuai Figma: token, layout, komponen, landing, login, halaman error

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, frontend, must
- Branch: `feature/ss3-01-fondasi-ui`
- Target: PR Kam 26 Nov, merge Jum 27 Nov (mulai lebih awal)
- Estimasi: 8 SP | Prioritas: must
- Kebutuhan: NFR-02, NFR-05; Tabel 3.5 laporan (Landing Page)
- Bergantung pada: -

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai pengguna (Admin dan Mahasiswa), saya ingin tampilan yang konsisten, rapi, dan mudah dipahami, supaya platform terasa profesional dan mudah dipakai.

Acceptance Criteria:

- Sumber desain: Figma file OrIGmaqXH1Sm0HKzSU7GoP, halaman 01 Style Guide dan 02 Components. Frame 'SG Fondasi' dipakai sebagai acuan token; bila berselisih dengan frame lama (Plus Jakarta Sans dan Inter), ikuti SG Fondasi dan catat di PR.
- Token di tema Tailwind v4: ink #112250, primary #3C507D, gold #E0C58F (hanya sebagai latar), paper #F5F0E9, surface #FFFFFF, line #D9CBC2, ok #E3F1EA dan #1E5C42, warn #FBEFD5 dan #7A4F0C, bad #F9E1DF dan #8C1D18, error #B3261E; spasi 4, 8, 12, 16, 24, 32, 48, 64 px; radius 4 (chip), 8 (kontrol), 12 (panel); bayangan modal dan toast 0 8 24 ink 12%.
- Tipografi: Bricolage Grotesque SemiBold (Display 56/60, H1 36/42, H2 28/34, H3 20/26) dan Hanken Grotesk (Body 16/24, Small 14/20, Caption 12/16, Regular dan Medium) dengan angka tabular; cara memuat font mengikuti panduan modern-web-guidance.
- Layout Admin (sidebar enam menu: Dashboard, Kelola Ruangan, Kelola Jadwal, Ambang Batas, Laporan, Akun, dan top bar) serta layout Mahasiswa yang mobile-first.
- Komponen Blade sesuai halaman 02 Components: Button (primary, secondary, danger; default, hover, focus, disabled, loading), Input (default, focus, error, disabled), Status Badge, Utilization Badge, Stat Card, Room Card, Data Table, Modal dan Confirm Dialog (normal dan blocked-warning) berbasis elemen dialog native, Toast (success dan error), Skeleton loader, Empty state, dan Error state.
- Status selalu berikon dan berlabel, tidak hanya warna. Mahasiswa: Kosong dan Terisi. Admin: Sesuai Jadwal, Kosong Meski Terjadwal, Dipakai di Luar Jadwal.
- Halaman Landing dan Login (Admin dan Mahasiswa; state default, terisi, fokus, error field, salah kredensial, batas percobaan, memuat) sesuai halaman 04 Hi-Fi Publik; halaman error 403, 404, 419, dan 500 berbahasa Indonesia.
- Halaman Kelola Ruangan yang sudah ada dipindah ke komponen baru; 12 test PR #54 tetap lulus.
- Responsif mobile, tablet, dan desktop; kontras WCAG AA; navigasi keyboard; tanpa galat JavaScript di console.

Batas minimum bila waktu habis: Landing dan komponen yang belum dipakai kartu lain ditunda; Login, layout, dan komponen inti (Button, Input, Badge, Table, Dialog, Toast) wajib.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-02] Jembatan Laravel dan hasil AI (model baca, layanan analitik, klien API)

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, ai, must
- Branch: `feature/ss3-02-jembatan-laravel-ai`
- Target: PR Rab 2 Des, merge Kam 3 Des (mulai lebih awal)
- Estimasi: 5 SP | Prioritas: must
- Kebutuhan: FR-05, FR-06, FR-07; PRD bagian 7
- Bergantung pada: SS2-05 (hanya bagian klien API); bagian baca DB tidak bergantung

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin dashboard memakai hasil AI terbaru, supaya angka yang saya lihat berasal dari klasifikasi sistem pakar dan bukan data tetap.

Acceptance Criteria:

- Model Eloquent hanya-baca untuk ClassificationResult dan OccupancyLog (tanpa migrasi baru, tanpa operasi tulis dari Laravel).
- AnalitikService: ringkasan status per rentang dan utilisasi per ruang memakai rumus terbobot DATA_CONTRACT bagian 10; kategori dari threshold_settings (<= batas rendah, <= batas sedang, selebihnya tinggi).
- Hasil AnalitikService sama dengan GET /utilization FastAPI pada data contoh yang sama (test kesetaraan).
- AiServiceClient (HTTP client, timeout 10 detik, satu kali coba ulang, token internal) untuk POST /classify; URL dan token dari .env.
- Perintah artisan analitik:klasifikasi {mulai} {selesai} memanggil klien tersebut (dipakai tombol Admin dan penjadwal).
- Layanan AI mati atau lambat: tampil pesan ramah dan data terakhir tetap tampil, bukan halaman galat; diuji dengan Http::fake.

Batas minimum bila waktu habis: Tanpa penjadwal otomatis.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-03] Dashboard analitik Admin sesuai Figma

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, frontend, must
- Branch: `feature/ss3-03-dashboard-analitik`
- Target: PR Rab 9 Des, merge Kam 10 Des
- Estimasi: 8 SP | Prioritas: must
- Kebutuhan: FR-07, FR-10; NFR-01, NFR-02
- Bergantung pada: SS3-01, SS3-02

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin melihat ringkasan status dan utilisasi seluruh ruangan serta ruang yang dipakai di luar jadwal, supaya saya dapat mengevaluasi pemanfaatan ruang.

Acceptance Criteria:

- Menggantikan placeholder admin.dashboard; hanya untuk guard admin; mengikuti frame Dashboard (default, empty, error, loading, tanpa item luar jadwal) pada halaman 06 Hi-Fi Admin.
- Filter periode: hari ini, 7 hari, semester berjalan (bawaan), dan rentang kustom.
- Angka ringkasan sesuai frame, mis. total sesi, persentase sesuai jadwal, kosong meski terjadwal, dan episode di luar jadwal.
- Panel jalur waktu matriks per ruang per hari dengan status berikon dan berlabel, dibangun dengan CSS grid.
- Panel utilisasi per ruang dengan kategori (rendah 0-40, sedang 41-80, tinggi 81-100) dan selisih jam terjadwal dan terpakai.
- Panel 'perlu ditinjau' berisi episode dipakai di luar jadwal (FR-10) dengan ruang, tanggal, jam, durasi, penjelasan, dan rule_id.
- Panel insight diisi dari kartu insight otomatis.
- Tombol 'Jalankan ulang klasifikasi' dengan indikator memuat dan pesan hasil.
- Label 'Data simulasi'; state memuat, kosong, dan galat tertangani; responsif desktop dan mobile; waktu muat di bawah 2 detik pada data semester penuh.
- Prediksi risiko ML tidak ditampilkan karena belum melampaui baseline (laporan 4.2.4).

Batas minimum bila waktu habis: Tanpa panel insight sampai kartu insight selesai.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-04] Halaman status ketersediaan ruang untuk Mahasiswa

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, frontend, must
- Branch: `feature/ss3-04-status-ruang-mahasiswa`
- Target: PR Sel 8 Des, merge Rab 9 Des
- Estimasi: 5 SP | Prioritas: must
- Kebutuhan: FR-09; NFR-02, NFR-04
- Bergantung pada: SS3-01

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Mahasiswa, saya ingin melihat status ketersediaan ruang (kosong atau terisi), supaya saya tidak perlu datang ke lokasi untuk mengetahuinya.

Acceptance Criteria:

- Menggantikan placeholder mahasiswa.home; hanya untuk guard mahasiswa.
- Kartu 10 ruangan dengan status Kosong atau Terisi dari slot 10 menit terkini (WIB) pada occupancy_logs.
- Bila tidak ada baris (jeda 17.00, di luar 07.00-23.00, data hilang) tampil 'Tidak ada data' beserta alasan singkat, bukan dianggap kosong.
- Menampilkan jadwal berikutnya ruang tersebut (jam dan mata kuliah) sebagai informasi.
- Pencarian dan filter (gedung atau lantai, status); pembaruan otomatis tanpa muat ulang halaman.
- Label 'Data simulasi'; mobile-first; tidak menampilkan identitas orang (NFR-04).
- Tidak ada tombol pinjam atau booking; hanya teks informasi bahwa peminjaman lewat PENRU atau TU.
- State mengikuti frame Ketersediaan (halaman 05 Hi-Fi Mahasiswa): default, memuat, pencarian kosong, filter kosong, galat, menu akun.

Batas minimum bila waktu habis: Tanpa filter.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-05] Insight otomatis berbasis templat dan panel 'Cara membaca hasil'

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: ai, laravel, must
- Branch: `feature/ss3-05-insight-otomatis`
- Target: PR Jum 11 Des, merge Sen 14 Des
- Estimasi: 5 SP | Prioritas: must
- Kebutuhan: Tier 3 PRD bagian 9 (prioritas dinaikkan); wawancara manpro 5 Okt no. 10; wawancara Ridho no. 14
- Bergantung pada: SS2-05; penempatan di dashboard setelah SS3-03

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin atau pembaca hasil proyek, saya ingin kesimpulan analisis dalam kalimat biasa, supaya hasil AI mudah dipahami tanpa membaca tabel angka.

Acceptance Criteria:

- Fungsi murni berpenamaan Indonesia di ai-service/app/insight/ (mis. susun_insight_periode) yang memakai hasil klasifikasi dan statistik utilisasi.
- Kalimat templat memuat angka sumber, mis. 'Ruang GU 702 dijadwalkan 20 jam, terpakai 6 jam'; ruang utilisasi terendah dan tertinggi; jumlah sesi kosong beserta pola harinya; episode di luar jadwal.
- Netral dan deskriptif: tidak menyarankan memindahkan atau mengubah jadwal; menyertakan catatan data simulasi dan bahwa pemakaian lewat TU tidak terbedakan.
- Deterministik tanpa LLM dan tanpa API eksternal.
- Endpoint GET /insights?tanggal_mulai&tanggal_selesai; klien Laravel memakai AiServiceClient SS3-02.
- Panel 'Kesimpulan' dan panel ringkas 'Cara membaca hasil ini' (tiga status, tiga kategori, arti data simulasi) ditempel ke dashboard.
- Unit test per templat dan kasus tanpa data ('belum ada data pada periode ini').
- Panel insight pada dashboard mengikuti frame Dashboard di Figma.

Batas minimum bila waktu habis: Empat templat kalimat.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-06] Pengaturan ambang batas klasifikasi oleh Admin

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, should
- Branch: `feature/ss3-06-pengaturan-ambang`
- Target: PR Sen 14 Des, merge Sel 15 Des
- Estimasi: 5 SP | Prioritas: should
- Kebutuhan: FR-11
- Bergantung pada: SS3-02

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin mengatur ambang klasifikasi dan kategori utilisasi, supaya status ruang sesuai kebijakan pengelolaan ruang.

Acceptance Criteria:

- Form empat nilai: empty_min_occupied_minutes (bawaan 10), outside_schedule_min_minutes (30), utilization_low_max (40), utilization_medium_max (80).
- Validasi: bilangan bulat positif; batas rendah lebih kecil dari batas sedang dan tidak lebih dari 100; dua durasi berkelipatan 10 menit.
- Tombol kembalikan ke nilai bawaan; dua durasi diberi keterangan 'asumsi tim, menunggu validasi manpro'.
- Perubahan tersimpan di threshold_settings beserta pencatatan siapa dan kapan.
- Setelah simpan tampil pemberitahuan untuk menjalankan ulang klasifikasi; test integrasi membuktikan perubahan nilai mengubah hasil.
- Nilai bawaan tetap 10 menit sampai manpro menyetujui perubahan (laporan 4.2.4 dan 4.1.6).
- State mengikuti frame AmbangBatas (edited, error bilangan bulat, error rentang, reset, saving).

Batas minimum bila waktu habis: Hanya dua ambang durasi.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-07] Laporan analitik PDF dan Excel

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, must
- Branch: `feature/ss3-07-laporan-pdf-excel`
- Target: PR Sen 21 Des, merge Sel 22 Des
- Estimasi: 8 SP | Prioritas: must
- Kebutuhan: FR-08
- Bergantung pada: SS3-03; SS3-05 untuk bagian kesimpulan

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin mengunduh laporan pemanfaatan ruang untuk periode tertentu, supaya hasil analitik dapat dibagikan dan dipakai sebagai dasar keputusan.

Acceptance Criteria:

- Pilih periode (dan ruang opsional), lalu unduh PDF atau Excel.
- Isi: judul, periode, tanggal cetak, label data simulasi, ringkasan status, tabel utilisasi per ruang dengan kategori, daftar sesi kosong meski terjadwal dan episode di luar jadwal beserta penjelasan, serta kesimpulan dari SS3-05.
- PDF A4 rapi dengan header, footer, dan nomor halaman; Excel berisi sheet Ringkasan, Utilisasi, Sesi, dan Luar Jadwal dengan header dan format angka.
- Memakai pustaka gratis; tanpa identitas individu (NFR-04).
- Periode maksimal satu semester dan selesai di bawah 10 detik; hanya guard admin.
- Test unduhan: status 200, tipe konten, dan isi sheet.
- State mengikuti frame Laporan (atur laporan, periode kustom, generating, success).

Batas minimum bila waktu habis: Excel dengan dua sheet.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-08] Deployment VPS dengan Docker Compose, HTTPS, dan backup

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: devops, must
- Branch: `feature/ss3-08-deployment`
- Target: Compose lokal Jum 4 Des; PR Jum 18 Des, merge Sen 21 Des
- Estimasi: 8 SP | Prioritas: must
- Kebutuhan: NFR-03, NFR-06
- Bergantung pada: SS3-02 dan SS3-03 sudah berjalan

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim, saya ingin platform berjalan di server dengan HTTPS dan cadangan data, supaya demo akhir dan serah terima berjalan tanpa setup lokal dan tanpa biaya tambahan.

Acceptance Criteria:

- Docker Compose: Laravel, ai-service (uvicorn), MySQL, dan reverse proxy dengan sertifikat Let's Encrypt otomatis.
- Hanya port 80 dan 443 terbuka; MySQL dan FastAPI tidak dapat diakses dari luar; FastAPI hanya lewat jaringan internal dengan token internal.
- APP_ENV=production, APP_DEBUG=false; .env produksi tidak ada di repositori.
- Satu skrip menjalankan migrasi, seeder, dan generator data demo.
- Backup mysqldump harian dengan retensi 7 hari, salinan di luar server, dan prosedur pemulihan yang teruji (NFR-06).
- Panduan docker compose up lokal di README agar proyek dapat dihidupkan kembali tanpa biaya.
- Smoke test dari server bersih mengikuti README; bila domain belum siap, deploy via IP dan NFR-03 dicatat tertunda.

Batas minimum bila waktu habis: Tanpa rotasi log otomatis.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-09] UAT, uji responsif, audit bahasa, dan bug bash

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo dan Muradika (reviewer silang)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: docs, must
- Branch: `feature/ss3-09-uat-dan-perbaikan`
- Target: UAT Sen 21 - Rab 23 Des; perbaikan Sen 28 - Rab 30 Des
- Estimasi: 5 SP | Prioritas: must
- Kebutuhan: NFR-02, NFR-05; RPP fase Test
- Bergantung pada: SS3-03 sampai SS3-08

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim, saya ingin menguji seluruh alur dari sisi pengguna, supaya tidak ada error yang tersisa saat presentasi akhir.

Acceptance Criteria:

- Skenario UAT: 10 untuk Admin dan 5 untuk Mahasiswa, dengan data uji dan hasil di tabel (bahan bab Pengujian Penerimaan).
- Uji responsif pada 360, 768, dan 1280 px di Chrome dan Firefox serta satu ponsel.
- Audit bahasa semua halaman dan pesan galat (NFR-05); pemeriksaan aksesibilitas dasar.
- Pemeriksaan keamanan dasar: halaman Admin tanpa login dialihkan, Mahasiswa tidak dapat membuka Admin, CSRF aktif, pembatasan percobaan login, tidak ada halaman debug.
- Daftar bug berprioritas; semua bug prioritas tinggi tertutup.
- Satu sesi UAT dengan manpro dijadwalkan bersama pertemuan manpro bila memungkinkan.
- Uji kemudahan penggunaan (IMK): 5 Mahasiswa dan 2 Admin simulasi, tiga tugas per peran, catat waktu, kesalahan, dan skor SUS; hasil masuk laporan.
- Evaluasi heuristik Nielsen dan aturan emas Shneiderman pada setiap halaman; temuan dikelompokkan berdasarkan keparahan.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-10] Dokumen luaran A: sinkronisasi dokumen, Laporan Akhir, HKI, SDGs

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: docs, must
- Branch: `feature/ss3-10-dokumen-laporan-akhir`
- Target: Draf Jum 18 Des, final Rab 30 Des
- Estimasi: 5 SP | Prioritas: must
- Kebutuhan: RPP luaran 4, 8, 9
- Bergantung pada: Berjalan paralel

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim, saya ingin dokumen proyek dan laporan akhir konsisten dengan kondisi sebenarnya, supaya penilaian dan serah terima tidak menemui kontradiksi.

Acceptance Criteria:

- PRD diperbarui ke v1.3 (Tier 3 naik prioritas, penomoran sprint, status FR, saran dosen penguji menunggu manpro); ROADMAP dan BACKLOG disinkronkan.
- Laporan akhir: koreksi Bab IV Sprint 2 (status US17 terhadap POST /classify, status US20 terhadap PR #64, hapus catatan '[cek Tabel 2.1...]', peran PO dan SM konsisten).
- Bab IV Sprint 3 dan 4 (planning, pelaksanaan, pengujian, review, retrospektif, bukti kolaborasi) dan audit rilis akhir terhadap DoD.
- Evaluasi ambang 20 menit pada set test dilaporkan sebagai keterbatasan metodologis.
- Dokumen HKI dan Laporan Dampak SDGs; Lampiran B sampai G dilengkapi, termasuk deklarasi alat bantu AI yang benar-benar dipakai.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-11] Dokumen luaran B: manual book, poster, video demo, BAST, presentasi

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: docs, must
- Branch: `feature/ss3-11-manual-poster-video`
- Target: Draf Jum 18 Des, final Rab 30 Des
- Estimasi: 5 SP | Prioritas: must
- Kebutuhan: RPP luaran 2, 3, 5, 6, 7
- Bergantung pada: SS3-08 untuk tangkapan layar dan video dari versi final

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim, saya ingin luaran proyek yang menjelaskan platform dengan jelas, supaya penguji dan klien memahami apa yang dihasilkan.

Acceptance Criteria:

- Manual book untuk Admin dan Mahasiswa dengan tangkapan layar.
- Poster proyek dan video demo aplikasi.
- File presentasi dengan satu halaman 'apa output proyek ini' dan skrip demo: masuk, dashboard, kesimpulan, laporan unduhan, status Mahasiswa.
- Draf BAST untuk ditandatangani manpro.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-12] Pengaturan akun Admin

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, could
- Branch: `feature/ss3-12-pengaturan-akun`
- Target: Could: PR Sen 28 Des
- Estimasi: 3 SP | Prioritas: could
- Kebutuhan: FR-12
- Bergantung pada: SS1-01 (selesai)

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin mengelola akun saya sendiri, supaya data dan kata sandi saya tetap aman dan mutakhir.

Acceptance Criteria:

- Ubah nama dan email (valid dan unik).
- Ganti kata sandi: wajib kata sandi lama, minimal 8 karakter, konfirmasi, disimpan sebagai hash.
- Sesi di perangkat lain berakhir setelah kata sandi diganti; ada pembatasan percobaan.
- Pesan galat berbahasa Indonesia; test untuk setiap alur.
- State mengikuti frame Akun (checklist kata sandi, konfirmasi tinggalkan halaman, saving).

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-13] Simulasi okupansi berjalan untuk membuktikan NFR-01

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: ai, could
- Branch: `feature/ss3-13-simulasi-berjalan`
- Target: Could: sebelum Jum 18 Des
- Estimasi: 3 SP | Prioritas: could
- Kebutuhan: FR-04, NFR-01
- Bergantung pada: SS3-03, SS3-04

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai tim, saya ingin data okupansi baru dapat 'masuk' saat demo, supaya batas 5 detik dari data diterima sampai tampil dapat dibuktikan.

Acceptance Criteria:

- Perintah atau endpoint yang menulis slot okupansi berjalan dengan seed tetap (hanya menulis occupancy_logs).
- Waktu dari data masuk sampai tampil di dashboard atau halaman Mahasiswa diukur dan dicatat, maksimal 5 detik.
- Idempoten pada kunci unik room_id dan slot_mulai.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).

## [SS-S3-14] Kartu detail ruangan (dialog) pada Kelola Ruangan

- Tindakan: BUAT issue baru
- Assignee (username GitHub): Muradika (reviewer: xynhiroo)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, frontend, should
- Branch: `feature/ss3-14-detail-ruangan-dialog`
- Target: PR Rab 16 Des, merge Kam 17 Des
- Estimasi: 5 SP | Prioritas: should
- Kebutuhan: FR-07 (pendukung); frame DetailRuangan di Figma
- Bergantung pada: SS3-01 (komponen), SS3-02 (AnalitikService), SS3-03

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin melihat ringkasan satu ruangan dalam kartu melayang di halaman Kelola Ruangan, supaya saya dapat memeriksa pemanfaatannya tanpa berpindah halaman.

Acceptance Criteria:

- Kartu melayang memakai elemen dialog native, dibuka dari baris atau kartu ruangan di Kelola Ruangan; tidak ada halaman baru.
- Esc dan klik di luar menutupnya, fokus kembali ke pemicu, latar tidak ikut tergulir; pada mobile tampil layar penuh.
- Isi: nama, lokasi, kapasitas, kondisi ruangan; utilisasi dan kategori periode terpilih; jalur waktu harian; tabel riwayat sesi terbaru dengan status dan penjelasan (rule_id).
- Data dimuat saat dibuka lewat endpoint JSON yang memakai AnalitikService; state memuat, kosong, dan galat mengikuti frame DetailRuangan di Figma.
- Filter dan posisi daftar Kelola Ruangan tidak hilang setelah kartu ditutup.
- Test: hanya guard admin, ruang tanpa jadwal (state kosong), dan galat layanan.

Batas minimum bila waktu habis: Tanpa tabel riwayat sesi (ringkasan dan jalur waktu saja).

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.

## [SS-S3-15] Impor jadwal dari berkas XLSX

- Tindakan: BUAT issue baru
- Assignee (username GitHub): xynhiroo (reviewer: Muradika)
- Milestone: Sprint 3 - Finalisasi dan Deployment (minggu 11-13, 7-25 Des)
- Label: laravel, could
- Branch: `feature/ss3-15-impor-jadwal-xlsx`
- Target: Could: PR Rab 23 Des
- Estimasi: 5 SP | Prioritas: could
- Kebutuhan: FR-03; wawancara manpro 5 Okt (jadwal tersedia dalam xlsx); state Mengimpor di Figma
- Bergantung pada: SS1-06 (sudah merged)

Salin isi di bawah garis ini ke badan issue:

---

User Story:
Sebagai Admin, saya ingin mengimpor jadwal dari berkas XLSX, supaya data jadwal dapat diperbarui sebelum integrasi API Learning tersedia.

Acceptance Criteria:

- Admin mengunggah berkas .xlsx dengan format lembar jadwal; tampil pratinjau baris valid dan tidak valid sebelum disimpan (state Mengimpor sesuai Figma).
- Validasi sama dengan kelola jadwal (hari, kelipatan 10 menit, bentrok); baris bermasalah dilaporkan beserta nomor barisnya tanpa menggagalkan seluruh impor.
- Idempoten pada room_id, hari, dan jam_mulai; tidak menimpa jadwal override Admin tanpa konfirmasi.
- Batas ukuran berkas dan hanya .xlsx; memakai pustaka gratis; perubahan tercatat di jejak perubahan jadwal.
- Tidak memakai API Learning (terblokir token).

Batas minimum bila waktu habis: Hanya memproses berkas dengan semua baris valid.

DOD:

- [ ] php artisan test dan pytest lulus (dan CI hijau setelah SS2-09).
- [ ] Memenuhi DoD di docs/ROADMAP.md bagian 7.
- [ ] PR di-approve pasangan, tanpa self-merge, branch dihapus setelah merge.
- [ ] Kode sudah direview rekan satu tim dan tidak ada bug prioritas tinggi yang terbuka.
- [ ] Seluruh teks antarmuka berbahasa Indonesia yang konsisten (NFR-05).
- [ ] Sesuai Figma (frame dan state terkait) dan token Style Guide; penyimpangan dicatat di PR.
- [ ] Lolos checklist IMK: 10 heuristik Nielsen dan aturan emas Shneiderman, target sentuh minimal 44 px, kontras WCAG AA, navigasi keyboard, status tidak hanya warna, pesan galat menjelaskan solusi.
- [ ] Panduan modern-web-guidance dijalankan sebelum menulis HTML, CSS, dan JS klien; bagian 'Modern Web Guidance' ditulis di deskripsi PR.
- [ ] Prinsip software engineering: controller tipis, logika di service class, validasi di Form Request, tanpa duplikasi (komponen Blade), penamaan deskriptif, Feature test untuk perilaku utama.
