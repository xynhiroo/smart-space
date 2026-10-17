# Kontrak Data Smart Space Analytics Platform (PBLIF3-PD08)
 
| | |
|---|---|
| **Kartu** | SS1-07 (issue #40) |
| **Versi** | Draf 1.0, 16 Oktober 2026 |
| **Pemilik** | Rangga Surya Saputra (reviewer: Muradika Laksamana Putra) |
| **Acuan** | PRD v1.1 Bagian 5 (FR-04, FR-05, FR-06, FR-10, FR-11), Bagian 10; docs/ROADMAP.md Bagian 3 |
| **Pengguna dokumen** | SS1-08 generator, SS1-09 sistem pakar, SS1-10 utilisasi, SS1-11 FastAPI, SS1-12 validasi, SS1-14 model ML |
 
Dokumen ini adalah kesepakatan bentuk data dan definisi operasional antara generator, sistem pakar, penghitung utilisasi, dan API. Perubahan setelah PR SS1-07 di-merge harus lewat PR yang diperiksa kedua anggota tim dan dicatat di Bagian 13.
 
Butir bertanda **[USULAN]** adalah keputusan rancangan yang belum tertulis di PRD atau ROADMAP dan perlu disetujui reviewer di PR ini.
 
---
 
## 1. Ruang lingkup
 
Kontrak mencakup dua tabel baru (`occupancy_logs`, `classification_results`), kunci baru di `threshold_settings`, definisi operasional tiga status ruangan, rumus utilisasi, dan antarmuka fungsi Python untuk klasifikasi serta utilisasi. Tabel master (`rooms`, `schedules`, `calendar_exceptions`) sudah ada dari SS1-03 dan tidak diubah.
 
Di luar lingkup: IoT, sensor, kamera, kontrol hardware, booking ruang, dan aktor selain Admin dan Mahasiswa. Semua data okupansi berasal dari generator dummy (`source = 'dummy'`).
 
## 2. Konvensi waktu dan slot
 
| Hal | Ketentuan |
|---|---|
| Zona waktu | WIB (Asia/Jakarta). Semua `DATETIME`/`TIME` disimpan sebagai waktu WIB tanpa konversi. Laravel (`config/app.php`) dan ai-service harus memakai zona yang sama. |
| Ukuran slot | 10 menit. Slot dengan `slot_mulai = T` mencakup rentang `[T, T + 10 menit)`. |
| Jam operasional | 07.00 sampai 23.00. Slot pertama 07.00, slot terakhir 22.50. Total 96 slot per hari. |
| Jeda | Slot 17.00 (rentang 17.00 sampai 17.10) dianggap ruangan tutup. Tidak ada baris `occupancy_logs` pada slot ini, dan slot ini tidak dihitung dalam menit terjadwal maupun menit terpakai. Maksimum baris per ruang per hari adalah 95. |
| Hari | `schedules.hari` memakai nama hari Bahasa Indonesia (Senin sampai Jumat). Pemetaan ke tanggal kalender lewat hari dalam minggu. |
| Kelipatan 10 menit | Semua `jam_mulai` dan `jam_selesai` di `schedules` harus kelipatan 10 menit dan jatuh pada batas slot. Test SS1-07 memeriksa ke-102 jadwal hasil seeder. Bila ada yang tidak selaras, dicatat sebagai temuan dan diselesaikan sebelum SS1-09. |
| Tumpang tindih | Dua jadwal pada ruang dan hari yang sama tidak boleh saling tumpang tindih. Dicek oleh test yang sama. |
 
## 3. Kepemilikan tabel
 
| Tabel | Dibuat lewat migrasi | Ditulis oleh | Dibaca oleh |
|---|---|---|---|
| `rooms`, `schedules`, `threshold_settings`, `calendar_exceptions` | Laravel | Laravel | Python |
| `occupancy_logs` | Laravel | Python (generator) | Python, Laravel |
| `classification_results` | Laravel | Python (sistem pakar) | Python, Laravel |
 
Aturan: skema selalu dibuat lewat migrasi Laravel. Python tidak boleh memanggil `create_all` atau `drop_all`, dan tidak boleh menulis ke tabel yang bukan miliknya. Model SQLAlchemy di `ai-service/app/models.py` hanya mencerminkan skema.
 
## 4. Tabel `occupancy_logs`
 
Satu baris mewakili status okupansi satu ruang pada satu slot 10 menit.
 
| Kolom | Tipe | Null | Keterangan |
|---|---|---|---|
| `id` | BIGINT UNSIGNED, PK, auto increment | tidak | |
| `room_id` | BIGINT UNSIGNED, FK ke `rooms.id` | tidak | |
| `slot_mulai` | DATETIME | tidak | Awal slot (WIB), menit selalu kelipatan 10 |
| `is_occupied` | BOOLEAN | tidak | `true` bila ada aktivitas terdeteksi di ruang selama slot |
| `source` | VARCHAR(20) | tidak | Default `dummy` |
| `created_at`, `updated_at` | TIMESTAMP | ya | Diisi Laravel bila memakai model Eloquent. Python boleh mengosongkan. |
 
Kunci dan indeks:
 
- Unik pada (`room_id`, `slot_mulai`).
- Indeks pada `slot_mulai` untuk kueri rentang tanggal lintas ruang.
Arti `is_occupied`:
 
- `true` berarti slot dianggap terisi oleh aktivitas, entah kelas, belajar mandiri, atau kegiatan lain. Tidak ada identitas individu yang disimpan (NFR-04).
- `false` berarti slot teramati dan tidak terisi.
- **Tidak ada baris** berarti slot hilang (simulasi gangguan sensor) atau slot jeda. Slot hilang diperlakukan sebagai tidak terisi dalam semua perhitungan (lihat Bagian 7.2). Tidak boleh ada baris dengan `is_occupied = NULL`.
## 5. Tabel `classification_results`
 
Satu baris mewakili hasil klasifikasi untuk **satu ruang, satu sesi, satu tanggal**, atau untuk **satu episode pemakaian di luar jadwal**.
 
| Kolom | Tipe | Null | Keterangan |
|---|---|---|---|
| `id` | BIGINT UNSIGNED, PK, auto increment | tidak | |
| `room_id` | BIGINT UNSIGNED, FK ke `rooms.id` | tidak | |
| `schedule_id` | BIGINT UNSIGNED, FK ke `schedules.id` | **ya** | Kosong untuk episode di luar jadwal |
| `tanggal` | DATE | tidak | Tanggal kalender sesi atau episode |
| `waktu_mulai` | TIME | tidak | Mulai sesi (dari jadwal) atau mulai episode |
| `waktu_selesai` | TIME | tidak | Selesai sesi atau akhir episode |
| `status` | VARCHAR(30) | tidak | Salah satu nilai di Bagian 6 |
| `menit_terjadwal` | UNSIGNED SMALLINT | tidak | 0 untuk episode di luar jadwal |
| `menit_terpakai` | UNSIGNED SMALLINT | tidak | Menit slot terisi (Bagian 7.2) |
| `utilisasi_pct` | DECIMAL(5,2) | **ya** | Kosong bila `menit_terjadwal = 0` |
| `rule_id` | VARCHAR(10) | tidak | Aturan yang dipakai, mis. `R01` |
| `penjelasan` | TEXT | tidak | Kalimat Bahasa Indonesia (FR-05) |
| `computed_at` | DATETIME | tidak | Waktu hasil dihitung (WIB) |
 
Kunci dan indeks:
 
- **[USULAN]** Unik pada (`room_id`, `tanggal`, `waktu_mulai`). Kunci ini dipilih menggantikan (`room_id`, `schedule_id`, `tanggal`) karena `schedule_id` bisa NULL, dan MySQL menganggap setiap NULL berbeda sehingga baris episode tidak akan pernah bentrok. Kunci ini bekerja untuk sesi dan episode sekaligus, dan menjadi dasar idempotensi (Bagian 9).
- Indeks pada (`tanggal`, `room_id`) dan pada `status`.
Invarian yang harus dijaga:
 
1. `status = 'dipakai_di_luar_jadwal'` jika dan hanya jika `schedule_id IS NULL`.
2. Untuk baris sesi: `0 <= menit_terpakai <= menit_terjadwal`.
3. Untuk episode: `menit_terjadwal = 0`, `utilisasi_pct IS NULL`, `menit_terpakai >= outside_schedule_min_minutes`.
## 6. Tiga status
 
| Nilai `status` | Arti | Berlaku untuk |
|---|---|---|
| `sesuai_jadwal` | Ruang terisi cukup lama selama jam terjadwal | Baris sesi |
| `kosong_meski_terjadwal` | Ruang terjadwal tetapi hampir tidak terisi | Baris sesi |
| `dipakai_di_luar_jadwal` | Ruang terisi di luar semua jendela jadwalnya | Baris episode |
 
Nilai disimpan sebagai string biasa, bukan ENUM DB, agar perubahan tidak butuh migrasi. Status "dipinjam" dari PENRU tidak menjadi status baru (FR-13).
 
## 7. Definisi operasional
 
### 7.1 Waktu evaluasi
Sebuah sesi dinilai **setelah jam terjadwalnya berakhir** (`waktu_evaluasi >= jam_selesai`). Sesi yang belum berakhir tidak menghasilkan baris. Hanya slot dengan `slot_mulai + 10 menit <= waktu_evaluasi` yang dipertimbangkan.
 
### 7.2 Menit
- `menit_terjadwal` = jumlah slot evaluasi di dalam `[jam_mulai, jam_selesai)` dikali 10. Slot jeda 17.00 tidak dihitung bila jatuh dalam rentang.
- `menit_terpakai` = jumlah slot dalam rentang yang sama dengan `is_occupied = true` dikali 10. Slot hilang dan slot jeda dihitung tidak terisi.
### 7.3 Status sesi
Untuk setiap jadwal yang berlaku pada tanggal itu:
 
- Bila `menit_terpakai < empty_min_occupied_minutes` maka `kosong_meski_terjadwal`.
- Selain itu `sesuai_jadwal`.
Nilai batas: `menit_terpakai` yang tepat sama dengan ambang masuk `sesuai_jadwal` (pembanding `<`, bukan `<=`). Nilai awal ambang adalah 10 menit, asumsi tim yang divalidasi dengan manpro pada sprint review 29 Okt 2026.
 
### 7.4 Episode di luar jadwal
1. Kumpulkan slot pada ruang dan tanggal itu yang: berada dalam jam operasional, bukan slot jeda, dan **tidak** berada di dalam jendela jadwal mana pun milik ruang itu pada hari itu.
2. Dari slot itu, ambil rangkaian berurutan slot `is_occupied = true`. Slot hilang, slot tidak terisi, slot jeda, dan batas jendela jadwal memutus rangkaian.
3. Tiap rangkaian berdurasi `>= outside_schedule_min_minutes` (awal 30 menit, asumsi tim) menjadi satu baris `dipakai_di_luar_jadwal`. `waktu_mulai` adalah awal slot pertama dan `waktu_selesai` adalah akhir slot terakhir rangkaian.
4. Rangkaian yang lebih pendek tidak menghasilkan baris. Ini menyaring noise deteksi agar Admin tidak kebanjiran penanda (FR-10).
### 7.5 Kalender akademik
- Tanggal dalam rentang `calendar_exceptions.tipe = 'libur'`: tidak ada sesi yang dievaluasi. Okupansi pada tanggal itu tetap dicek sebagai episode di luar jadwal.
- Tipe `ujian` dan `kegiatan_khusus`: sesi dievaluasi seperti biasa. Perbedaan pola ditangani generator (SS1-08), bukan sistem pakar.
### 7.6 Sumber kebenaran
Sistem pakar hanya membaca `rooms`, `schedules`, `threshold_settings`, `calendar_exceptions`, dan `occupancy_logs`. Berkas `ground_truth_*.csv` dari generator berada di luar DB dan **tidak boleh dibaca** sistem pakar. Berkas itu hanya dipakai validasi (SS1-12) dan label model (SS1-14 membaca label dari `classification_results`, bukan dari ground truth).
 
## 8. Threshold
 
Dibaca dari `threshold_settings` (kolom `value` bertipe teks, di-parse oleh pemuat ambang).
 
| Key | Nilai awal | Keterangan | Status |
|---|---|---|---|
| `empty_min_occupied_minutes` | 10 | Menit terisi minimum agar sesi tidak dianggap kosong (FR-11c) | **Baru**, asumsi tim |
| `outside_schedule_min_minutes` | 30 | Durasi minimum episode di luar jadwal agar ditandai (FR-11d) | **Baru**, asumsi tim |
| `utilization_low_max` | 40 | Batas atas kategori rendah (%) | Sudah ada |
| `utilization_medium_max` | 80 | Batas atas kategori sedang (%) | Sudah ada |
| `empty_status_evaluation_timing` | `after_schedule_finished` | Kebijakan waktu evaluasi (Bagian 7.1) | Sudah ada |
| `empty_status_use_start_tolerance` | | Tidak ada di PRD dan tidak dipakai | **Dihapus** |
 
Kunci `utilization_low_min`, `utilization_medium_min`, `utilization_high_min`, dan `utilization_high_max` tetap ada di seeder untuk tampilan UI, tetapi penghitung kategori hanya memakai dua batas atas di atas (Bagian 10).
 
Tidak ada angka ambang yang boleh ditulis langsung di kode. Seluruh ambang masuk ke fungsi lewat objek `Thresholds`.
 
## 9. Idempotensi
 
Menjalankan klasifikasi ulang untuk rentang tanggal yang sama harus **mengganti** hasil, bukan menggandakan. Mekanismenya: hapus baris `classification_results` pada rentang `tanggal` (dan ruang) yang dihitung ulang, lalu tulis baris baru dalam satu transaksi, atau gunakan upsert pada kunci unik Bagian 5. Hal yang sama berlaku untuk `occupancy_logs` pada generator: kunci unik (`room_id`, `slot_mulai`) mencegah duplikasi.
 
## 10. Utilisasi
 
Rumus (FR-06):
 
```
utilisasi_pct = menit_terpakai / menit_terjadwal x 100
```
 
- **Per baris sesi:** dihitung langsung, dibulatkan 2 desimal. Bernilai kosong bila `menit_terjadwal = 0`.
- **Per periode (hari, minggu, semester berjalan):** dihitung saat kueri dari baris sesi:
  `sum(menit_terpakai) / sum(menit_terjadwal) x 100`, hanya baris dengan `schedule_id IS NOT NULL`. Ini rata-rata terbobot, bukan rata-rata persentase. Episode di luar jadwal tidak masuk pembilang maupun penyebut.
- Bila `sum(menit_terjadwal) = 0`, hasilnya `None` dan kategorinya `None` (ditampilkan sebagai "tidak ada jadwal").
Kategori (celah desimal 40 sampai 41 dan 80 sampai 81 ditutup sesuai PRD FR-11):
 
| Kondisi | Kategori |
|---|---|
| `pct <= utilization_low_max` (40) | `rendah` |
| `pct <= utilization_medium_max` (80) | `sedang` |
| selebihnya | `tinggi` |
 
## 11. Antarmuka fungsi Python
 
Lokasi usulan: `ai-service/app/contracts.py` (tipe data) dan `ai-service/app/expert_system/`, `ai-service/app/analytics/` (implementasi). Semua fungsi di bawah adalah **fungsi murni**: tidak mengakses DB, tidak membaca waktu sistem, dan deterministik. Akses DB ada di lapisan repositori terpisah (SS1-11), sehingga SS1-09 dan SS1-10 dapat dites dengan data buatan tangan.
 
```python
from dataclasses import dataclass
from datetime import date, datetime, time
 
@dataclass(frozen=True)
class Thresholds:
    empty_min_occupied_minutes: int
    outside_schedule_min_minutes: int
    utilization_low_max: float
    utilization_medium_max: float
 
@dataclass(frozen=True)
class RoomFact:
    room_id: int
    nama_ruangan: str
    is_open_space: bool          # GU 701, GU 705, GU 707
 
@dataclass(frozen=True)
class ScheduleFact:
    schedule_id: int
    room_id: int
    hari: str
    jam_mulai: time
    jam_selesai: time
    mata_kuliah: str
 
@dataclass(frozen=True)
class OccupancySlot:
    room_id: int
    slot_mulai: datetime         # WIB, kelipatan 10 menit
    is_occupied: bool
 
@dataclass(frozen=True)
class ClassificationResult:      # satu baris classification_results
    room_id: int
    schedule_id: int | None
    tanggal: date
    waktu_mulai: time
    waktu_selesai: time
    status: str                  # nilai Bagian 6
    menit_terjadwal: int
    menit_terpakai: int
    utilisasi_pct: float | None
    rule_id: str
    penjelasan: str
 
@dataclass(frozen=True)
class UtilizationSummary:
    room_id: int
    periode_mulai: date
    periode_selesai: date
    menit_terjadwal: int
    menit_terpakai: int
    utilisasi_pct: float | None
    kategori: str | None         # rendah / sedang / tinggi / None
    jumlah_sesi: int
    jumlah_sesi_kosong: int
    jumlah_episode_di_luar_jadwal: int
```
 
Fungsi (diimplementasikan di kartu yang tercantum):
 
```python
# SS1-09
def classify_session(
    room: RoomFact, schedule: ScheduleFact, slots: list[OccupancySlot],
    tanggal: date, waktu_evaluasi: datetime, thresholds: Thresholds,
) -> ClassificationResult | None:
    """Klasifikasi satu sesi. None bila sesi belum berakhir pada waktu_evaluasi."""
 
def detect_outside_schedule(
    room: RoomFact, schedules: list[ScheduleFact], slots: list[OccupancySlot],
    tanggal: date, waktu_evaluasi: datetime, thresholds: Thresholds,
) -> list[ClassificationResult]:
    """Episode pemakaian di luar jadwal pada satu ruang dan satu tanggal."""
 
def classify_day(
    room: RoomFact, schedules: list[ScheduleFact], slots: list[OccupancySlot],
    tanggal: date, waktu_evaluasi: datetime, thresholds: Thresholds,
    is_holiday: bool,
) -> list[ClassificationResult]:
    """Gabungan keduanya. Pada hari libur hanya episode yang dievaluasi."""
 
# SS1-10
def categorize_utilization(pct: float | None, thresholds: Thresholds) -> str | None: ...
 
def compute_utilization(
    results: list[ClassificationResult], periode_mulai: date,
    periode_selesai: date, thresholds: Thresholds,
) -> UtilizationSummary:
    """Satu ruang, satu periode. Aturan Bagian 10."""
```
 
Pemuat ambang (`load_thresholds(session) -> Thresholds`) dan penulis hasil (`save_results(session, results)`) ada di lapisan repositori (SS1-11) dan memakai kunci unik serta aturan idempotensi di Bagian 5 dan 9.
 
## 12. Aturan awal sistem pakar (indikatif)
 
Daftar final aturan ditetapkan di SS1-09. Di sini hanya ID yang dicadangkan agar `rule_id` konsisten sejak awal.
 
| rule_id | Kondisi | Status | Contoh penjelasan |
|---|---|---|---|
| R01 | Sesi berakhir dan `menit_terpakai >= empty_min_occupied_minutes` | `sesuai_jadwal` | "Ruang terisi {x} dari {y} menit terjadwal." |
| R02 | Sesi berakhir dan `menit_terpakai < empty_min_occupied_minutes` | `kosong_meski_terjadwal` | "Ruang terisi hanya {x} menit dari {y} menit terjadwal. Ruang ini berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU." |
| R03 | Episode okupansi di luar jadwal berdurasi `>= outside_schedule_min_minutes` | `dipakai_di_luar_jadwal` | "Ruang terisi {x} menit di luar jadwal ({mulai} sampai {selesai}). Perlu ditinjau Admin." |
 
Kalimat tentang TU pada R02 bersifat informasi saja, bukan fitur booking.
 
## 13. Keterbatasan yang diketahui
 
1. Semua okupansi berasal dari simulasi buatan tim. Akurasi terhadap ground truth tidak menjamin akurasi di dunia nyata.
2. Ruang terjadwal yang kosong lalu dipinjam kegiatan lain lewat TU tampak sebagai terisi dan tidak terbedakan tanpa data PENRU (FR-13, terblokir token).
3. Rangkaian episode diputus oleh slot hilang, sehingga satu pemakaian panjang dapat terpecah dan tidak mencapai 30 menit bila noise slot hilang mengenai bagian tengah. Dampaknya diukur di SS1-12.
4. Dua ambang awal (10 dan 30 menit) adalah asumsi tim sampai divalidasi manpro pada 29 Okt 2026.
5. Kalender akademik memengaruhi sesi hanya lewat tipe `libur`. Pola khusus masa ujian ditangani generator.
## 14. Perubahan dari PRD v1.1 dan riwayat
 
Butir yang menambah atau memperjelas PRD v1.1 (untuk disetujui reviewer):
 
- Kunci unik `classification_results` pada (`room_id`, `tanggal`, `waktu_mulai`) [USULAN].
- Slot hilang dihitung tidak terisi dan memutus episode [USULAN].
- Pembanding `<` pada ambang sesi kosong dan pembobotan utilisasi per periode [USULAN].
- Aturan hari libur dan syarat jadwal kelipatan 10 menit tanpa tumpang tindih [USULAN].
| Versi | Tanggal | Perubahan |
|---|---|---|
| Draf 1.0 | 16 Okt 2026 | Draf awal SS1-07 |
 