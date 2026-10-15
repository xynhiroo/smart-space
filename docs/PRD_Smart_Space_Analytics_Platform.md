# Product Requirements Document (PRD)
## Smart Space Analytics Platform (PBLIF3-PD08)

| | |
|---|---|
| **Status** | Final v1.1 (menggantikan v1.0), acuan coding Sprint 1 dan roadmap menuju ATS |
| **Tanggal** | 15 Oktober 2026 (v1.0: 9 Oktober 2026) |
| **Tim** | Rangga Surya Saputra (3312501036), Muradika Laksamana Putra (3312501059) |
| **Manajer Proyek / Klien** | Yeni Rokhayati, S.Si., M.Sc |
| **Institusi** | Program Studi Teknik Informatika, Politeknik Negeri Batam |
| **Proyek pendahulu** | Eco-Light & Space Optimizer (AIoT, selesai Juli 2026) |

## Perubahan dari v1.0 (15 Oktober 2026)

1. Prioritas AI: Tier 2 dinaikkan menjadi Must untuk satu model klasifikasi (risiko sesi terjadwal kosong), karena materi matkul AI sudah mencakup ML dasar dan evaluasi. Tier 3 tetap setelah ATS. (Bagian 9)
2. FR-05: setiap hasil klasifikasi menyertakan aturan yang dipakai (rule_id) dan penjelasan singkat. (Bagian 5)
3. FR-11: dua ambang baru berstatus asumsi tim, yaitu durasi terisi minimum agar sesi tidak dianggap kosong dan durasi minimum pemakaian di luar jadwal. Divalidasi dengan manpro pada sprint review. (Bagian 5)
4. Model data: slot okupansi 10 menit; classification_results menjadi satu baris per ruang per sesi per tanggal. (Bagian 10)
5. Roadmap: AI diselesaikan sebelum ATS (2-13 Nov 2026); autentikasi Admin (SS1-01), CRUD ruangan (SS1-04), dashboard, laporan, dan finalisasi setelah ATS. Rincian di docs/ROADMAP.md dan docs/BACKLOG.md. (Bagian 15)
6. Risiko baru: label dari data simulasi, dan ruang terjadwal yang kosong lalu dipinjam lewat TU. (Bagian 11 dan 13)

Lingkup tidak berubah: tanpa IoT, sensor, kamera, kontrol hardware, booking ruang, dan aktor selain Admin dan Mahasiswa.


> Dokumen ini akan diperbarui setelah wawancara dengan manpro (rencana Senin) dan setelah dokumen RPP/Praktikum 3 difinalkan sepenuhnya. Item yang masih berstatus **TBD** ditandai eksplisit, bukan diasumsikan selesai.

---

## 1. Latar Belakang & Masalah

Pengelolaan ruang kelas/lab di Polibatam saat ini masih manual dan human-centric: aktivasi/deaktivasi perangkat berdasarkan sakelar fisik, tidak ada pencatatan digital pola pemakaian ruang, dan tidak ada visibilitas apakah ruangan benar-benar dipakai sesuai jadwal resmi. Admin fasilitas tidak punya data untuk audit pemanfaatan ruang secara objektif.

Smart Space Analytics Platform adalah **pengembangan lanjutan dari Eco-Light & Space Optimizer**, menggeser fokus dari kontrol hardware (lampu/AC) ke **analitik pemanfaatan ruang berbasis data okupansi dan jadwal resmi**.

## 2. Tujuan Produk

1. Memberi Admin visibilitas status pemanfaatan setiap ruangan (sesuai jadwal / kosong meski terjadwal / dipakai di luar jadwal).
2. Menghitung tingkat utilisasi ruangan secara terukur untuk mendukung keputusan berbasis data (data-driven decision making).
3. Memberi Mahasiswa akses cepat melihat ketersediaan ruang tanpa perlu datang langsung ke lokasi.

## 3. Scope & Non-Goals

**Masuk scope:**
- AI/analitik atas data okupansi dan jadwal resmi, menggunakan **data okupansi dummy** (karena tidak ada sensor fisik).
- Dua aktor: **Admin** (login) dan **Mahasiswa** (login pakai akun dummy simulasi Learning, lihat Bagian 4).
- Implementasi awal difokuskan pada **ruang kelas/lab Program Studi Teknik Informatika** (10 ruangan, lihat Bagian 8).

**Tegas di luar scope (non-goals):**
- Implementasi IoT, sensor fisik, kamera, atau kontrol hardware apapun (keputusan resmi manpro).
- Fitur transaksional seperti booking/reservasi ruang.
- Peta denah interaktif/visual gedung (didrop dari rencana awal — diganti card/list view).
- Aktor selain Admin dan Mahasiswa.

## 4. Pengguna & Model Akses

| Aktor | Akses | Catatan |
|---|---|---|
| **Admin** | Login wajib (akun terverifikasi) | Mengelola data master, jadwal, threshold, melihat dashboard & laporan |
| **Mahasiswa** | Login wajib (akun dummy simulasi Learning — NIM+password) | Hanya melihat status ketersediaan ruang. **Direvisi 5 Okt 2026**: awalnya read-only tanpa login, diubah manpro karena risiko disalahgunakan pihak luar yang bukan mahasiswa aktif |

## 5. Kebutuhan Fungsional (FR)

| Kode | Deskripsi | Status |
|---|---|---|
| FR-01 | Admin dapat login dan logout menggunakan akun terverifikasi. Mahasiswa login menggunakan akun data dummy seperti yang ada di Learning | Final (direvisi) |
| FR-02 | Admin dapat mengelola data master ruangan (tambah/ubah/hapus) | Final |
| FR-03 | Sistem dapat mengimpor jadwal resmi penggunaan ruangan secara otomatis dari API Learning; Admin dapat melakukan koreksi/override (tambah/ubah/hapus) bila diperlukan | Final (direvisi) |
| FR-04 | Sistem dapat membangkitkan data dummy okupansi ruangan yang menyerupai pola data sensor nyata | Final |
| FR-05 | Sistem dapat mengklasifikasikan status tiap ruangan (sesuai jadwal / kosong meski terjadwal / dipakai di luar jadwal) menggunakan ambang batas yang dapat dikonfigurasi Admin (lihat FR-11). Setiap hasil menyertakan aturan yang dipakai (rule_id) dan penjelasan singkat dalam Bahasa Indonesia. Sesi dinilai setelah jam terjadwalnya berakhir | Final (direvisi v1.1) |
| FR-06 | Sistem dapat menghitung tingkat utilisasi tiap ruangan — formula: **(jam benar-benar terpakai ÷ jam terjadwal) × 100%** | Final |
| FR-07 | Admin dapat melihat dashboard analitik berisi ringkasan status okupansi dan utilisasi seluruh ruangan | Final |
| FR-08 | Admin dapat mengunduh laporan analitik dalam format PDF/Excel | Final |
| FR-09 | Mahasiswa dapat melihat status ketersediaan ruang (kosong/terisi) | Final (direvisi — login kini wajib, lihat FR-01) |
| FR-10 | Sistem dapat menandai (highlight) ruangan yang dipakai di luar jadwal agar ditinjau Admin | Final |
| FR-11 | Admin dapat mengatur ambang batas (threshold) klasifikasi: (a) durasi minimum ruang dianggap "kosong" meski terjadwal — **nilai: dievaluasi setelah jam terjadwal benar-benar habis**, (b) rentang persentase utilisasi — **nilai final: rendah 0–40%, sedang 41–80%, tinggi 81–100%** Ditambahkan v1.1 (asumsi tim, belum divalidasi manpro): (c) durasi terisi minimum selama jam terjadwal agar sesi tidak dianggap kosong, nilai awal 10 menit; (d) durasi minimum episode pemakaian di luar jadwal agar ditandai, nilai awal 30 menit. Batas kategori utilisasi dibaca: rendah sampai 40%, sedang di atas 40% sampai 80%, tinggi di atas 80% | Final (revisi v1.1) |
| FR-12 | Admin dapat mengelola akun sendiri (ubah nama/email, ganti password) | Final |
| FR-13 | Sistem dapat mengambil data peminjaman ruangan dari API PENRU untuk memperkaya informasi pada kategori status "dipakai di luar jadwal", tanpa menambah kategori klasifikasi baru | **Draf** — menunggu akses token dari Pak Andri Betra |

## 6. Kebutuhan Non-Fungsional (NFR)

| Kode | Deskripsi |
|---|---|
| NFR-01 | Proses & tampilkan pembaruan data okupansi dummy maksimal 5 detik setelah data baru diterima |
| NFR-02 | Dashboard responsif, dapat diakses baik via desktop maupun mobile |
| NFR-03 | Enkripsi HTTPS pada seluruh komunikasi client-server |
| NFR-04 | Kepatuhan UU PDP dalam pengelolaan data terkait aktivitas individu di ruangan |
| NFR-05 | Bahasa antarmuka konsisten & mudah dipahami Admin maupun Mahasiswa |
| NFR-06 | Mekanisme backup data berkala |
| NFR-07 | Kode mengikuti standar clean code (capaian pembelajaran RPL Lanjut) |

## 7. Arsitektur Sistem

**Pola: Hybrid**, mengikuti preseden arsitektur Eco-Light (pemisahan backend utama dan AI service):

| Layer | Teknologi | Tanggung Jawab |
|---|---|---|
| Backend utama | Laravel + MySQL | CRUD ruangan/jadwal/threshold/akun, autentikasi Admin, API gateway |
| Frontend | Blade + TailwindCSS + Alpine.js + Chart.js | Dashboard, status ketersediaan ruang, laporan |
| **AI/Analytics Engine** | **Python (FastAPI)** | Rule engine klasifikasi (Tier 1), generator data dummy, model ML (Tier 2), logika rekomendasi (Tier 3) |
| Database | MySQL (shared) | Laravel = pemilik data master; Python = pemilik data hasil olahan (baca data master via koneksi yang sama) |

Pembagian kepemilikan data:
- **Laravel menulis**: `rooms`, `schedules`, `threshold_settings`, akun Admin, akun dummy Mahasiswa (simulasi Learning — NIM+password, lihat FR-01). Autentikasi memakai 2 guard terpisah (Admin & Mahasiswa) karena sumber akunnya berbeda.
- **Python menulis**: `occupancy_logs` (dummy), `classification_results`, (nanti) `ml_predictions`/`recommendations`.
- Masing-masing pihak lain hanya **membaca** tabel yang bukan miliknya — tidak ada duplikasi logika.

## 7a. Integrasi API Eksternal (temuan wawancara manpro 5 Okt 2026)

| API | Pemilik Akses | Fungsi | Status |
|---|---|---|---|
| **API Learning** | Pak Anung | Sumber jadwal resmi (FR-03) — diimpor otomatis, Admin hanya override | Token belum didapat, akses "bebas dipakai tapi harus ketemu dulu" |
| **API PENRU** | Pak Andri Betra | Data peminjaman ruangan nyata, memperkaya kategori "dipakai di luar jadwal" (FR-13) | Token belum didapat, sama seperti di atas |

Tidak ada ruangan yang boleh dipakai tanpa peminjaman (kecuali 3 ruangan open-space: GU 701, GU 705, GU 707 — bebas dimasuki tapi AC/TV tetap perlu pinjam remote ke TU). Ini berarti skenario "dipakai di luar jadwal tanpa alasan apapun" kemungkinan besar jarang terjadi di ruangan non-open-space, dan generator data dummy sebaiknya mencerminkan ini (probabilitas lebih rendah untuk ruangan non-open-space, sedikit lebih tinggi untuk 3 ruangan open-space).

**Keputusan:** Sprint 1-2 tetap jalan dengan data dummy murni (FR-04) tanpa bergantung pada kedua API ini (karena token belum di tangan). Integrasi PENRU/Learning dirancang modular supaya bisa "dicolok" begitu akses didapat, idealnya Sprint 3-4 — bukan blocker MVP.

## 8. Data Real: Ruangan & Jadwal Prodi IF

Sumber: jadwal resmi Prodi IF Semester Ganjil 2026/2027 (Reguler Pagi + Reguler Malam/Karyawan), mencakup kelas Semester 1, 3, dan 5.

**10 ruangan fisik:** GU 604, GU 701, GU 702, GU 704, GU 705, GU 706, GU 707, GU 805, TA 10.3, TA 11.5A

**102 blok jadwal** (48 pagi + 54 malam), lintas Senin-Jumat. Jam operasional riil: **07.00–23.00**, dengan ketentuan **jeda 17.00–17.10 dianggap ruangan "tutup"** (di luar jam operasional, tidak dievaluasi klasifikasi/okupansi pada rentang ini).

Sesi berstatus "Online" (tanpa ruangan fisik) sudah dikecualikan — tidak relevan untuk analitik ruang fisik.

File data: `rooms_if.csv`, `schedules_if_gabungan.csv`, `calendar_exceptions_ganjil2627.csv` (disertakan terpisah dari dokumen ini). Kalender akademik bersumber dari Kalender Akademik TA 2026/2027 Polibatam — mencakup hari libur (Natal, Tahun Baru, Isra Mi'raj), masa ujian ATS & AAS, dan minggu pengganti, untuk kebutuhan variasi skenario generator dummy (mitigasi HIRARC risiko #2).

## 9. Strategi AI / Analitik — Bertingkat

| Tier | Pendekatan | Prioritas | Fungsi |
|---|---|---|---|
| **Tier 1** | Rule-based / Expert System (IF-THEN, threshold) | **Must Have, Sprint 1** | Klasifikasi status ruangan (FR-05), deterministik, tidak ada training |
| **Tier 2** | ML klasifikasi (Decision Tree dan Logistic Regression dibanding baseline) | **Must Have, sebelum ATS** (satu model: risiko sesi terjadwal kosong) | Memprediksi sesi terjadwal yang berisiko tidak dipakai; dievaluasi dengan confusion matrix, precision, recall, F1, ROC-AUC |
| **Tier 3** | Rekomendasi berbasis template + hasil Tier 1/2 | Could Have, Sprint 2 (setelah ATS) | Narasi kesimpulan otomatis di laporan (mis. saran relokasi ruang kurang dimanfaatkan) |

Tier 2 dibatasi pada satu model klasifikasi agar sesuai lingkup RPP (analisis dan klasifikasi tingkat pemanfaatan ruang dan estimasi statistik efisiensi). Regresi, Isolation Forest, K-Means, scraping, dan dataset publik tidak dikerjakan sebelum ATS. Mao dkk. 2024 dan Aliero dkk. 2022 tetap menjadi rujukan. Tier 3 bukan syarat MVP.

## 10. Model Data (ringkas)

| Tabel | Pemilik | Field Utama |
|---|---|---|
| `admin_accounts` | Laravel | id, nama, email, password_hash |
| `mahasiswa_accounts` | Laravel | id, nim, password_hash (akun dummy simulasi Learning — **baru**, akibat revisi FR-01) |
| `rooms` | Laravel | id, nama_ruangan, kapasitas, lokasi, status |
| `schedules` | Laravel | id, room_id, hari, jam_mulai, jam_selesai, mata_kuliah |
| `threshold_settings` | Laravel | key, value, keterangan (FR-11). Kunci tambahan v1.1: `empty_min_occupied_minutes` (10) dan `outside_schedule_min_minutes` (30) |
| `calendar_exceptions` | Laravel (seed dari data real) | tanggal_mulai, tanggal_selesai, tipe (`libur`/`ujian`/`kegiatan_khusus`), keterangan |
| `occupancy_logs` | Python | id, room_id, slot_mulai (slot 10 menit), is_occupied, source='dummy'; unik pada room_id + slot_mulai |
| `classification_results` | Python | id, room_id, schedule_id (kosong untuk pemakaian di luar jadwal), tanggal, waktu_mulai, waktu_selesai, status, menit_terjadwal, menit_terpakai, utilisasi_pct (kosong bila menit_terjadwal = 0), rule_id, penjelasan, computed_at; satu baris per ruang per sesi per tanggal, atau per episode pemakaian di luar jadwal |

Catatan v1.1: utilisasi per periode (hari, minggu, semester berjalan) dihitung saat query dari classification_results. Rincian di docs/DATA_CONTRACT.md (kartu SS1-07).

## 11. Risiko Utama (ringkas dari HIRARC)

| Risiko | Tingkat | Mitigasi |
|---|---|---|
| Akurasi rendah akibat variasi data dummy terbatas | Sedang | Pola dummy realistis (jam sibuk/sepi), divalidasi sebelum demo |
| Overfitting pada pola dummy buatan sendiri | Sedang | Variasi skenario, pisah data evaluasi sejak awal (relevan untuk Tier 2) |
| Beban kerja tim (2 orang, 1 semester) | **Tinggi** | Prioritas MVP ketat, fitur Could Have ditunda |
| Data leakage saat evaluasi | Sedang-Tinggi | Split kronologis train/test (khusus Tier 2, belum berlaku untuk Tier 1) |
| ~~Threshold klasifikasi berbasis asumsi sepihak tim~~ | Sedang | **Resolved** — sudah divalidasi manpro (wawancara 5 Okt): lihat FR-11 |
| Ketergantungan token API PENRU/Learning belum di tangan, waktu akses tidak pasti | Sedang | Sprint 1-2 tidak bergantung pada API ini (data dummy murni); integrasi dirancang modular untuk Sprint 3-4 |
| Label berasal dari simulasi buatan sendiri, sehingga model bisa hanya mempelajari aturan generator | Sedang | Baseline wajib, split kronologis, set dev dan test dengan seed terpisah, keterbatasan dinyatakan terbuka di laporan |
| Ruang terjadwal yang kosong lalu dipinjam kegiatan lain lewat TU tampak sebagai terisi dan tidak terdeteksi tanpa data PENRU | Rendah-Sedang | Dicatat sebagai keterbatasan dan disimulasikan di generator; FR-13 (PENRU) dapat memperjelas kelak, tanpa menambah kategori status |

## 12. Tim & Peran

| Nama | Peran praktis (harian) | Peran formal (dokumen Working Agreement) |
|---|---|---|
| Rangga Surya Saputra | Product Owner (praktik), Dev | Development Team |
| Muradika Laksamana Putra | Scrum Master (praktik), Dev | Development Team |
| Yeni Rokhayati, S.Si., M.Sc | Manpro/Klien | Product Owner (formal) |
| Agung Riyadi, S.Si., M.Kom | Dosen Agile | Scrum Master (formal) |

## 13. Pertanyaan Terbuka / Pending

1. Token akses API Learning (Pak Anung) dan API PENRU (Pak Andri Betra) belum didapat, perlu dijadwalkan pertemuan. Tidak memblokir Sprint 1 (lihat Bagian 7a).
2. ~~FR-03 (revisi) dan FR-13 (baru) belum masuk dokumen Praktikum 3 resmi~~, Resolved: sudah masuk resmi, kata-kata persis sesuai PRD.
3. RPP bagian 11 dan 13 sengaja dikosongkan untuk saat ini, keputusan tim, bukan terlewat. Tidak memblokir coding.
4. Asumsi ambang baru (FR-11 c dan d) divalidasi dengan manpro pada sprint review 29 Okt 2026.
5. Bentuk dan tanggal penilaian ATS belum diketahui. Rencana mengasumsikan yang dinilai adalah AI yang sudah berjalan; slide IF316 menyebut ATS sebagai presentasi rancangan, sehingga dokumen rancangan AI (SS1-13) disiapkan untuk keduanya.

Catatan kecil: FR-12 di dokumen Praktikum 3 resmi ada typo pengetikan ("megalopa" seharusnya "mengelola"), tidak memengaruhi arti, perbaiki saat sempat.

## 14. Aturan & Ritme Kerja Tim (Sprint 1)

Berdasarkan arahan matkul Proyek Inovasi Agile Minggu 4-5:

**Git dan Clean Code:**
- Tidak boleh commit langsung ke branch `main`. Setiap kartu backlog dikerjakan di branch terpisah dengan pola nama `feature/kode-backlog-ringkasan`, misalnya `feature/ss1-01-autentikasi-admin`.
- Setiap fitur selesai dibuka sebagai Pull Request, direview oleh pasangan tim (bukan self-merge), minimal 1 approval sebelum merge ke `main`.
- Penamaan variabel, fungsi, dan file mengikuti standar clean code (deskriptif, konsisten), sesuai NFR-07.
- Hindari kode mati (dead code) dan duplikasi sebelum merge.

**Ritme Kerja:**
- Daily Standup Sync berpasangan: progres kemarin, target hari ini, kendala (blockers). Idealnya tiap awal sesi kerja, bukan cuma pas kelas.
- WIP limit: maksimal 1 kartu berstatus In Progress per mahasiswa di Siap PBL. Selesaikan atau pindahkan dulu sebelum menarik kartu baru.
- Status kartu bergerak: Backlog → Sprint Backlog → In Progress → Testing/Ready for Review → Done, konsisten dengan board Siap PBL.

**Pelaporan (Tugas P3):**
- Bukti tangkapan layar minimal 2 Pull Request yang saling direview dan disetujui antar pasangan.
- Riwayat commit harus menunjukkan kontribusi seimbang dari kedua akun anggota tim.
- Status board Siap PBL harus mencerminkan progres aktual sebelum pertemuan Minggu 6.

## 15. Roadmap Tingkat Tinggi (v1.1, rinci di docs/ROADMAP.md)

- **Sprint 1 (sampai 30 Okt 2026, inti AI):** kontrak data dan migrasi, generator data dummy, sistem pakar klasifikasi (Tier 1), utilisasi dan statistik, FastAPI, validasi, model ML klasifikasi (Tier 2), dokumen rancangan AI. Sudah selesai: skema DB dan setup (SS1-03), autentikasi Mahasiswa dan layout (SS1-02).
- **ATS (2-13 Nov 2026):** cadangan, perbaikan kecil, latihan presentasi.
- **Sprint 2 (setelah ATS):** autentikasi Admin (SS1-01), CRUD ruangan dan jadwal, dashboard, laporan unduh, halaman status Mahasiswa, pengaturan threshold dan akun, rekomendasi Tier 3, simulasi data berjalan, UAT, deployment, dokumen luaran.
- **Terblokir token:** integrasi API Learning dan PENRU (FR-03, FR-13).

---
*Dokumen ini dibuat berdasarkan RPP PBLIF3-PD08, Praktikum 3 (FR/NFR/Use Case), hasil diskusi arsitektur, dan data jadwal real Prodi IF. Perbarui bagian 13 setelah setiap keputusan baru. Diperbarui ke v1.1 pada 15 Oktober 2026 berdasarkan keputusan tim dan materi matkul AI minggu 1 sampai 6.*
