# Roadmap Smart Space Analytics Platform (PBLIF3-PD08) sampai ATS

Versi 1.1 final, 15 Oktober 2026. Pemilik dokumen: Rangga Surya Saputra (PO praktik) dan Muradika Laksamana Putra (SM praktik).
Dokumen pendamping: `docs/BACKLOG.md` (rincian kartu) dan `docs/PRD_Smart_Space_Analytics_Platform.md` (v1.1).

## 1. Tujuan dan prinsip

Tujuan: menyelesaikan inti AI yang berjalan dan tervalidasi sebelum ATS (2-13 Nov 2026). Seluruh finalisasi aplikasi (auth Admin, CRUD, dashboard, laporan, dokumen luaran) dikerjakan setelah ATS.

Prinsip:
1. Lingkup mengikuti RPP bagian 3: modul AI berupa "algoritma analisis dan klasifikasi tingkat pemanfaatan ruang berdasarkan data okupansi dummy dan jadwal resmi, dan estimasi statistik efisiensi", ditambah validasi keakuratan.
2. Tidak melebih-lebihkan fitur. Aturan penyaring: bila ragu sebuah fitur perlu atau tidak, cek RPP bagian 3. Bila tidak disebut di sana, tunda.
3. Di luar lingkup (keputusan resmi manpro): IoT, sensor fisik, kamera, kontrol hardware, booking ruang, aktor selain Admin dan Mahasiswa.
4. Tanpa dataset publik dan tanpa scraping (pelajaran kebocoran data dari Eco-Light, HIRARC risiko 4).

Asumsi kerja ATS: yang dinilai adalah AI yang sudah berjalan, jadi rencana ini memaksimalkan hasilnya. Catatan: slide kontrak IF316 menyebut ATS sebagai presentasi rancangan proyek; dokumen rancangan AI (SS1-13) disiapkan untuk keduanya, jadi tidak perlu diputuskan sekarang.

## 2. Alur AI yang dibangun

```
Generator dummy -> occupancy_logs (slot 10 menit) -> Sistem pakar (aturan + ambang dari DB)
-> classification_results (status + rule_id + penjelasan) -> FastAPI
-> Validasi terhadap label kebenaran generator
-> Model ML risiko sesi terjadwal kosong (label dari classification_results)
```

## 3. Keputusan final (15 Okt 2026)

| No | Hal | Keputusan |
|---|---|---|
| 1 | Penilaian ATS | Dianggap menilai AI yang sudah berjalan; hasil dimaksimalkan (lihat bagian 1) |
| 2 | Definisi "kosong meski terjadwal" | Sesi dinilai setelah jam terjadwal berakhir. Kosong bila menit terisi < `empty_min_occupied_minutes` (awal 10 menit). Nilai awal adalah asumsi tim dan dapat diubah Admin |
| 3 | Ruang terjadwal kosong yang dipinjam lewat TU | Tidak menambah kategori status (sesuai FR-13). Tanpa data PENRU, pemakaian seperti itu tampak sebagai terisi. Dicatat sebagai keterbatasan, disimulasikan di generator, dan penjelasan status kosong menyebut ruang berpotensi dimanfaatkan lewat peminjaman di TU (informasi saja, bukan booking) |
| 4 | Pemakaian di luar jadwal | Ditandai bila episode okupansi di luar jadwal berdurasi >= `outside_schedule_min_minutes` (awal 30 menit), agar noise sensor tidak membanjiri Admin. Asumsi tim |
| 5 | Granularitas `classification_results` | Satu baris per ruang per sesi per tanggal; episode di luar jadwal menjadi baris dengan `schedule_id` kosong; utilisasi periode dihitung saat query |
| 6 | Rentang data generator | Awal semester (7 Sep 2026) sampai tanggal berjalan, dapat dikonfigurasi; historis sekali jalan. Simulasi berjalan (NFR-01) setelah ATS |
| 7 | Penjelasan hasil klasifikasi | Ditambahkan: `rule_id` dan teks penjelasan Bahasa Indonesia |
| 8 | Slot okupansi | 10 menit (selaras dengan jeda 17.00-17.10) |
| 9 | Model ML | Satu model klasifikasi (Decision Tree dan Logistic Regression dibanding baseline) |

Asumsi tim (nomor 2 dan 4) divalidasi dengan manpro pada sprint review Kamis 29 Okt.

## 4. Pembagian kerja

| Pemilik | Kartu |
|---|---|
| Rangga (jalur kritis AI) | SS1-07 kontrak data dan migrasi, SS1-08 generator dummy, SS1-09 sistem pakar, SS1-14 model ML |
| Dika (tidak memblokir jalur kritis) | SS1-10 utilisasi dan statistik, SS1-11 FastAPI dan integrasi DB, SS1-12 validasi |
| Berdua | SS1-13 dokumen rancangan AI dan bahan presentasi (masing-masing menulis bagiannya) |

Alasan: data, sistem pakar, dan model adalah inti yang dinilai dan saling bergantung. Kartu Dika dikerjakan terhadap antarmuka fungsi yang ditetapkan di SS1-07, sehingga tidak menunggu kode Rangga. SS1-01, SS1-04, dan SS1-06 diparkir ke Sprint 2. SS1-05 (impor jadwal) sudah dicakup seeder SS1-03.

### Pemetaan nomor kartu ke issue GitHub

Penomoran mengikuti issue yang sudah ada di repo (judul issue berbentuk `[SS-S1-NN]`). Kartu baru dimulai dari SS1-09.

| Kartu | Issue GitHub | Tindakan |
|---|---|---|
| SS1-01 Autentikasi Admin | #34 (Closed) | Login Admin belum ada di main; buka kembali atau pastikan PR-nya ada. Pasca-ATS |
| SS1-04 Data master ruangan | #37 | Pasca-ATS |
| SS1-05 Impor data jadwal real | #38 | Sudah dicakup seeder SS1-03; verifikasi bisa dijalankan ulang tanpa duplikat, lalu tutup |
| SS1-06 Pengelolaan jadwal oleh Admin | #39 | Pasca-ATS (menggantikan SS2-01) |
| SS1-07 Kontrak data dan migrasi tabel AI | #40 | Perbarui isi: interval 10 menit (bukan 15), tambah tabel hasil klasifikasi, migrasi lewat Laravel |
| SS1-08 Generator data dummy | #41 | Perbarui isi: tambah label kebenaran, noise, set dev dan test |
| SS1-09 sampai SS1-14 | baru | Dibuat sebagai issue baru; isi siap tempel di `docs/GITHUB_ISSUES.md` |

Aturan pengalihan (untuk disepakati di sinkron pertama): kartu tanpa commit sampai titik cek Kam 22 Okt dialihkan ke Rangga, dan Dika tetap mereview. Review PR maksimal 24 jam karena merge membutuhkan approval pasangan.

## 5. Linimasa

| Kapan | Rangga | Dika | Titik kontrol |
|---|---|---|---|
| Rab 14 - Jum 16 Okt | Sinkron 45 menit; PR docs; isi board; SS1-07 (PR Jum 16) | Setup lokal; review PR #43 dan PR docs; commit pertama; baca PRD Bagian 5, 9, 10 | Jum 16: keputusan bagian 3 tercatat; commit pertama Dika |
| Minggu 7 (19-23 Okt) | SS1-07 merge (Sen 19); SS1-08 (PR Rab 21, merge Kam 22); mulai SS1-09 (Kam 22) | SS1-10 (mulai Rab 21, PR Jum 23); draf bagian SS1-13 | Kam 22: cek bersama dan aturan pengalihan; Jum 23: PR SS1-10 dibuka |
| Minggu 8 (26-30 Okt) | SS1-09 (PR Sen 26, merge Sel 27); SS1-14 (Sel 27 - Kam 29, merge Jum 30); bagian SS1-13 | SS1-10 merge (Sen 26); SS1-11 (PR Rab 28, merge Kam 29); SS1-12 (PR Kam 29, merge Jum 30) | Sen 26: titik pengaman; Kam 29: sprint review dengan manpro; Jum 30: AI dibekukan |
| ATS 2-13 Nov | Cadangan 2-6 Nov: kartu yang molor, SS1-13 final, latihan presentasi | sama | Tanpa kartu baru |

Titik pengaman Sen 26 Okt: bila SS1-07 sampai SS1-09 belum merged, SS1-14 dipersempit menjadi satu model plus baseline. Kartu Rangga yang selesai PR dipindah ke Ready for Review sebelum kartu berikutnya dimulai (WIP maksimal 1 kartu In Progress per orang).
Tanggal adalah rencana kerja. Asumsi penomoran minggu: Minggu 1 = 7 Sep 2026.

## 6. Ritme komunikasi

- Satu sumber kebenaran: dokumen ini, `docs/BACKLOG.md`, dan board (Siap PBL dan GitHub Projects).
- Standup asinkron di WA tiap hari kerja, tiga baris: kemarin, hari ini, kendala.
- Sinkron 30 menit dua kali seminggu (usul: Senin dan Kamis). Kamis 29 Okt diganti sprint review dengan manpro.
- Kendala yang belum selesai dalam 24 jam: telepon, jangan menunggu balasan chat.
- Review PR maksimal 24 jam. Satu kartu satu PR. Merge dengan merge commit.
- Keputusan baru dicatat di bagian 3 dokumen ini.

## 7. Definisi selesai (DoD) kartu AI

1. Kode mengikuti clean code (penamaan deskriptif, tanpa dead code dan duplikasi).
2. Unit test lulus (`pytest` untuk ai-service, `php artisan test` untuk backend).
3. Dokumentasi singkat (docstring dan README bila perlu).
4. PR di-approve pasangan, branch dihapus setelah merge.
5. Kartu dipindah ke Done di Siap PBL dan GitHub Projects.

## 8. Matriks keterlacakan: materi matkul AI (minggu 1 sampai 6) ke bukti di PBL

Kolom "Tautan bukti" diisi saat kartu selesai (berkas atau PR).

| Pertemuan | Konsep yang diajarkan | Penerapan di PBL | Kartu | Tautan bukti |
|---|---|---|---|---|
| AI1 Pengantar | Definisi AI, ruang lingkup (AI, ML, DL), AI tidak sama dengan ML | Proyek memadukan sistem pakar (knowledge-based) dan ML dalam satu aplikasi; dijelaskan di AI_DESIGN | SS1-13 | |
| AI2 Representasi pengetahuan | Logika, jaringan semantik, production rules, frames | Aturan klasifikasi sebagai production rules IF-THEN; Ruang dan Sesi sebagai frames; diagram jaringan semantik ruang-jadwal-okupansi-status | SS1-09, SS1-13 | |
| AI3 DSS | Fase keputusan (intelligence, design, choice, implementation, monitoring), jenis DSS (pasif, aktif), taksonomi (data-driven, model-driven, knowledge-driven), komponen | Platform dipetakan sebagai DSS: dashboard dan laporan bersifat pasif, penanda "dipakai di luar jadwal" bersifat aktif; lima fase dipetakan ke fitur | SS1-13 (rancangan), SS2-02 (dashboard) | |
| AI3 MCDM | Metode AHP, TOPSIS, dan lainnya | Tidak dipakai sebelum ATS. Opsional untuk memberi peringkat saran relokasi di Tier 3, hanya bila diminta dosen atau manpro | SS2-07 | |
| AI4 Sistem pakar | Basis pengetahuan, mesin inferensi (forward chaining, deterministik), mekanisme penjelasan, rekayasa pengetahuan | Aturan terpisah dari mesin inferensi; forward chaining; setiap hasil membawa rule_id dan penjelasan; ambang divalidasi manpro | SS1-09 | |
| AI5 ML dasar | Supervised vs unsupervised; klasifikasi (Decision Tree, Logistic Regression, dan lainnya) | Model klasifikasi "sesi terjadwal berisiko kosong": Decision Tree dan Logistic Regression dibanding baseline | SS1-14 | |
| AI6 Evaluasi ML | Overfitting dan underfitting, confusion matrix, accuracy, precision, recall, F1, ROC-AUC, metrik regresi, korelasi Pearson dan Spearman, memilih metrik saat kelas tidak seimbang | Confusion matrix dan metrik per kelas untuk sistem pakar (SS1-12) dan model ML (SS1-14); tabel error latih vs uji; korelasi jam terjadwal vs terpakai (SS1-10). Metrik regresi tidak dipakai karena tugasnya klasifikasi | SS1-10, SS1-12, SS1-14 | |
| AI8 Etika (belum diajarkan) | Etika AI | Data dummy tanpa identitas individu, kepatuhan UU PDP (NFR-04), keterbatasan data simulasi dinyatakan terbuka | SS1-13 | |
| Capaian umum matkul | Standar coding, konfigurasi lingkungan, rancangan dari kebutuhan, hubungan database, pengujian, dokumentasi, presentasi ke klien | requirements.txt dan .env.example, kontrak data, SQLAlchemy ke MySQL, unit test, README, sprint review dengan manpro | SS1-07, SS1-11, SS1-13 | |

Kalimat jawaban bila ditanya "apakah tim PBL sudah menerapkan materi matkul AI":

> Ya. Kami menerapkan sistem pakar (representasi pengetahuan berupa production rules dan frames, mesin inferensi forward chaining, dan mekanisme penjelasan), memetakan platform sebagai Decision Support System, dan melatih serta mengevaluasi model klasifikasi dengan baseline, confusion matrix, precision, recall, F1, ROC-AUC, serta analisis overfitting. Seluruhnya terhubung ke database dan API, didokumentasikan, dan dipresentasikan ke klien. Data yang dipakai adalah simulasi, dan kami menyatakannya sebagai keterbatasan.

## 9. Risiko utama menuju ATS

| Risiko | Penanganan |
|---|---|
| Jalur kritis menumpuk pada satu orang | Pipeline kartu (PR dibuka lalu lanjut kartu berikut); SS1-14 yang pertama dipersempit bila molor |
| Review PR lambat menahan merge | Batas review 24 jam; PR kecil; dibicarakan di sinkron |
| Model hanya mempelajari aturan generator | Baseline, split kronologis, seed dev dan test terpisah, keterbatasan dinyatakan di laporan |
| Ambang awal (10 dan 30 menit) adalah asumsi tim | Disetel pada set dev, divalidasi manpro 29 Okt, dapat diubah Admin |
| Kontribusi commit timpang (syarat P3) | Kartu Dika SS1-10, SS1-11, SS1-12 dan bagian SS1-13; review silang di semua PR |

## 10. Pasca-ATS (indikatif, mengikuti RPP)

| Periode | Fokus |
|---|---|
| 16-27 Nov | Auth Admin (SS1-01), CRUD ruangan (SS1-04) dan jadwal, dashboard, laporan unduh, halaman status Mahasiswa, UI threshold dan akun |
| 30 Nov - 4 Des | Integrasi AI-backend-frontend, pengujian, UAT |
| 7-11 Des | Deployment, manual book, HKI, SDGs, BAST, poster, video |
| 14-18 Des | Cadangan dan sprint review akhir |

Perincian kartu pasca-ATS ada di `docs/BACKLOG.md` bagian 3.
