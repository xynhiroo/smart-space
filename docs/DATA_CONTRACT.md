# Kontrak Data Smart Space Analytics Platform (PBLIF3-PD08)
 
| | |
|---|---|
| **Kartu** | SS1-07 (issue #40) |
| **Versi** | 1.1, 18 Oktober 2026 |
| **Pemilik** | Rangga Surya Saputra (reviewer: Muradika Laksamana Putra) |
| **Acuan** | PRD v1.2 Bagian 5 (FR-04, FR-05, FR-06, FR-10, FR-11), Bagian 10; docs/ROADMAP.md Bagian 3 |
| **Pengguna dokumen** | SS1-08 generator, SS1-09 sistem pakar, SS1-10 utilisasi, SS1-11 FastAPI, SS1-12 validasi, SS1-14 model ML |
 
Dokumen ini adalah kesepakatan bentuk data dan definisi operasional antara generator, sistem pakar, penghitung utilisasi, dan API. Perubahan setelah PR SS1-07 di-merge harus lewat PR yang diperiksa kedua anggota tim dan dicatat di Bagian 14.
 
Butir bertanda **[USULAN]** adalah keputusan rancangan yang belum tertulis di PRD atau ROADMAP dan perlu disetujui reviewer di PR ini. Butir bertanda **[DISETUJUI]** adalah keputusan yang telah disepakati bersama.
 
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
| Hari | `schedules.hari` memakai nama hari Bahasa Indonesia: `Senin, Selasa, Rabu, Kamis, Jum'at` (dengan tanda petik pada `Jum'at`). Normalisasi nama hari disediakan pada modul bersama `app/calendar_utils.py` (menangani variasi penulisan seperti `Jumat` tanpa tanda petik, perbedaan huruf besar/kecil, dan spasi). Pemetaan ke tanggal kalender lewat hari dalam minggu. |
| Kelipatan 10 menit | Semua `jam_mulai` dan `jam_selesai` di `schedules` harus kelipatan 10 menit dan jatuh pada batas slot. Test SS1-07 memeriksa ke-102 jadwal hasil seeder. Bila ada yang tidak selaras, dicatat sebagai temuan dan diselesaikan sebelum SS1-09. |
| Tumpang tindih | Dua jadwal pada ruang dan hari yang sama tidak boleh saling tumpang tindih. Seeder jadwal bersifat idempoten dengan unique index (`room_id`, `hari`, `jam_mulai`) pada `schedules` (menunggu PR #57). |
 
## 2a. Set data dev dan test
 
Untuk menjamin pemisahan data evaluasi dan mencegah kebocoran data (HIRARC risiko 4), generator dummy memisahkan lingkungan database dan berkas ground truth sebagai berikut:
 
| Hal | Ketentuan |
|---|---|
| Database dev | `smart_space_ai_dev` (seed 1001), skema sama dengan database utama. Dipakai untuk merancang dan menyetel aturan sistem pakar serta ambang batas. |
| Database test | `smart_space_ai_test` (seed 2002), skema sama. Dipakai untuk evaluasi akhir dan pengujian performa tanpa bias. |
| Database test otomatis | `smart_space_test` dipakai secara terisolasi untuk unit test `pytest` dan PHPUnit. |
| Database aplikasi | Database aplikasi `smart_space` tidak dipakai oleh generator data dummy. |
| Rentang data | Satu semester penuh: 7 September 2026 sampai 22 Januari 2027 (menggantikan batasan hingga tanggal berjalan pada rencana awal). Data tetap berupa simulasi historis; simulasi berjalan (NFR-01) dikembangkan setelah ATS. |
| Berkas ground truth | Disimpan di `ai-service/data/ground_truth/ground_truth_dev.csv` dan `ground_truth_test.csv` di luar database. Berkas ini tidak masuk git dan dihasilkan ulang secara deterministik dari seed. |
| Aturan evaluasi | Penyetelan aturan dan ambang hanya boleh dilakukan pada set dev; set test hanya dievaluasi satu kali pada tahap pengujian (SS1-12). |
 
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
 
Kunci `utilization_low_min`, `utilization_medium_min`, `utilization_high_min`, dan `utilization_high_max` tetap ada di seeder untuk tampilan UI, tetapi penghitung kategori hanya memakai dua batas atas di atas (Bagian 10).
 
Tidak ada angka ambang yang boleh ditulis langsung di kode. Seluruh ambang masuk ke fungsi lewat objek `Thresholds`.
 
## 9. Idempotensi
 
Menjalankan klasifikasi ulang untuk rentang tanggal yang sama harus **mengganti** hasil, bukan menggandakan. Mekanismenya: hapus baris `classification_results` pada rentang `tanggal` (dan ruang) yang dihitung ulang, lalu tulis baris baru dalam satu transaksi, atau gunakan upsert pada kunci unik Bagian 5. Hal yang sama berlaku untuk `occupancy_logs` pada generator: kunci unik (`room_id`, `slot_mulai`) mencegah duplikasi.
 
## 10. Utilisasi
 
Rumus (FR-06):
 
```
utilisasi_pct = menit_terpakai / menit_terjadwal x 100
```
 
- **Per baris sesi:** dihitung langsung, dibulatkan 2 desimal saat ditulis ke database. Bernilai kosong bila `menit_terjadwal = 0`.
- **Per periode (hari, minggu, semester berjalan):** dihitung saat kueri dari baris sesi:
  `sum(menit_terpakai) / sum(menit_terjadwal) x 100`, hanya baris dengan `schedule_id IS NOT NULL`. Ini rata-rata terbobot, bukan rata-rata persentase. Episode di luar jadwal tidak masuk pembilang maupun penyebut.
- Bila `sum(menit_terjadwal) = 0`, hasilnya `None` dan kategorinya `None` (ditampilkan sebagai "tidak ada jadwal").

Implementasi fungsi analitik nyata berada di modul `ai-service/app/analytics/utilization.py` (`hitung_utilisasi_pct`, `tentukan_kategori`, `hitung_statistik_ruang`, dsb.). Fungsi perhitungan mengembalikan nilai float persis (tidak dibulatkan di dalam modul perhitungan); pembulatan 2 desimal dilakukan saat menyimpan hasil ke kolom `utilisasi_pct` di database atau saat presentasi data.

Ambang kategori dikirimkan sebagai argumen fungsi `batas_rendah` dan `batas_sedang` (mengambil nilai dari `utilization_low_max` dan `utilization_medium_max`). Konstanta kategori: `KATEGORI_RENDAH = "rendah"`, `KATEGORI_SEDANG = "sedang"`, `KATEGORI_TINGGI = "tinggi"`.

Kategori (celah desimal 40 sampai 41 dan 80 sampai 81 ditutup sesuai PRD FR-11):
 
| Kondisi | Kategori |
|---|---|
| `pct <= utilization_low_max` (40) | `rendah` |
| `pct <= utilization_medium_max` (80) | `sedang` |
| selebihnya | `tinggi` |
 
## 11. Antarmuka fungsi Python

Semua fungsi di bawah adalah **fungsi murni**: tidak mengakses database, tidak membaca waktu sistem, deterministik, dan memakai konvensi penamaan Bahasa Indonesia. Akses database berada di lapisan repositori terpisah (SS1-11), sehingga pengujian dapat dilakukan menggunakan data buatan tangan.

### 11.1 Utilisasi (antarmuka nyata SS1-10)

Diimplementasikan pada modul `ai-service/app/analytics/utilization.py` (sudah ter-merge di `main`):

```python
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Sequence

KATEGORI_RENDAH = "rendah"
KATEGORI_SEDANG = "sedang"
KATEGORI_TINGGI = "tinggi"


@dataclass(frozen=True)
class Sesi:
    """Satu sesi pada satu tanggal, dalam satuan menit."""
    room_id: int
    tanggal: date
    menit_terjadwal: int
    menit_terpakai: int


@dataclass(frozen=True)
class StatistikRuang:
    """Ringkasan utilisasi satu ruang pada satu periode."""
    room_id: int
    menit_terjadwal: int
    menit_terpakai: int
    selisih_menit: int
    utilisasi_pct: float | None
    kategori: str | None
    rata_rata_harian_pct: float | None
    min_harian_pct: float | None
    max_harian_pct: float | None


@dataclass(frozen=True)
class KorelasiRuang:
    """Korelasi menit terjadwal vs menit terpakai antar ruang."""
    jumlah_ruang: int
    pearson: float | None
    spearman: float | None


def hitung_utilisasi_pct(menit_terjadwal: int, menit_terpakai: int) -> float | None:
    """Utilisasi (%) = menit terpakai / menit terjadwal x 100.
    Mengembalikan None bila menit terjadwal nol. Nilai kembali tidak dibulatkan.
    """
    ...


def tentukan_kategori(
    utilisasi_pct: float | None, batas_rendah: float, batas_sedang: float
) -> str | None:
    """Kategori utilisasi: <= batas_rendah rendah, <= batas_sedang sedang, selebihnya tinggi."""
    ...


def hitung_statistik_ruang(
    sesi: Iterable[Sesi],
    tanggal_mulai: date,
    tanggal_selesai: date,
    batas_rendah: float,
    batas_sedang: float,
    daftar_room_id: Iterable[int] = (),
) -> dict[int, StatistikRuang]:
    """Statistik per ruang untuk rentang tanggal (inklusif)."""
    ...


def korelasi_pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Korelasi Pearson antara dua deret angka."""
    ...


def korelasi_spearman(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Korelasi Spearman (Pearson pada peringkat)."""
    ...


def korelasi_jadwal_vs_terpakai(statistik: Iterable[StatistikRuang]) -> KorelasiRuang:
    """Korelasi menit terjadwal vs terpakai antar ruang."""
    ...
```

### 11.2 Sistem pakar (FINAL SS1-09)

Antarmuka sistem pakar mengikuti konvensi yang sama dengan SS1-10: fungsi murni Bahasa Indonesia, tanpa akses database, ambang dikirim lewat argumen/dataclass `Ambang`, dan hasil evaluasi dapat dipetakan langsung ke tipe `Sesi` untuk penghitungan utilisasi:

```python
from dataclasses import dataclass
from datetime import date, datetime, time


@dataclass(frozen=True)
class FaktaRuang:
    room_id: int
    nama_ruangan: str
    is_open_space: bool          # GU 701, GU 705, GU 707


@dataclass(frozen=True)
class FaktaJadwal:
    schedule_id: int
    room_id: int
    hari: str
    jam_mulai: time
    jam_selesai: time
    mata_kuliah: str


@dataclass(frozen=True)
class SlotOkupansi:
    room_id: int
    slot_mulai: datetime         # WIB, kelipatan 10 menit
    is_occupied: bool


@dataclass(frozen=True)
class Ambang:
    empty_min_occupied_minutes: int
    outside_schedule_min_minutes: int
    batas_rendah: float
    batas_sedang: float


@dataclass(frozen=True)
class HasilKlasifikasi:          # merepresentasikan satu baris classification_results
    room_id: int
    schedule_id: int | None
    tanggal: date
    waktu_mulai: time
    waktu_selesai: time
    status: str                  # nilai Bagian 6
    menit_terjadwal: int
    menit_terpakai: int
    utilisasi_pct: float | None  # dihitung tidak dibulatkan; dibulatkan saat simpan ke DB
    rule_id: str
    penjelasan: str


# Fungsi murni sistem pakar:
def klasifikasikan_sesi(
    ruang: FaktaRuang,
    jadwal: FaktaJadwal,
    slot_list: list[SlotOkupansi],
    tanggal: date,
    waktu_evaluasi: datetime,
    ambang: Ambang,
) -> HasilKlasifikasi | None:
    """Klasifikasi satu sesi. None bila sesi belum berakhir pada waktu_evaluasi."""
    ...


def deteksi_pemakaian_luar_jadwal(
    ruang: FaktaRuang,
    daftar_jadwal: list[FaktaJadwal],
    slot_list: list[SlotOkupansi],
    tanggal: date,
    waktu_evaluasi: datetime,
    ambang: Ambang,
) -> list[HasilKlasifikasi]:
    """Episode pemakaian di luar jadwal pada satu ruang dan satu tanggal."""
    ...


def klasifikasikan_hari(
    ruang: FaktaRuang,
    daftar_jadwal: list[FaktaJadwal],
    slot_list: list[SlotOkupansi],
    tanggal: date,
    waktu_evaluasi: datetime,
    ambang: Ambang,
    is_holiday: bool,
) -> list[HasilKlasifikasi]:
    """Gabungan evaluasi harian. Pada hari libur hanya episode luar jadwal yang dievaluasi."""
    ...
```

Pemuat ambang dari database dan penyimpan hasil ke database disediakan pada lapisan repositori (SS1-11) dengan memanfaatkan kunci unik dan prinsip idempotensi (Bagian 5 dan 9).
 
## 12. Aturan sistem pakar (FINAL SS1-09)

Aturan sistem pakar dievaluasi menggunakan mesin inferensi *forward chaining* deterministik. Aturan terbagi menjadi dua kelompok:

### 12.1 Aturan turunan fakta (F..)

| rule_id | Nama aturan | Kondisi | Kesimpulan |
|---|---|---|---|
| F01 | Deteksi Sesi Berakhir | Sesi perkuliahan dengan `waktu_evaluasi >= tanggal + jam_selesai` | `sesi_telah_berakhir = True` |
| F02 | Evaluasi Okupansi Sesi Kurang | `sesi_telah_berakhir` dan `menit_terpakai < empty_min_occupied_minutes` | `okupansi_sesi_kurang = True` |
| F03 | Evaluasi Okupansi Sesi Memenuhi | `sesi_telah_berakhir` dan `menit_terpakai >= empty_min_occupied_minutes` | `okupansi_sesi_cukup = True` |
| F04 | Evaluasi Durasi Episode Cukup | Episode di luar jadwal dengan `durasi_episode >= outside_schedule_min_minutes` | `episode_cukup_panjang = True` |

### 12.2 Aturan keputusan status (R..)

| rule_id | Kondisi | Status | Templat penjelasan |
|---|---|---|---|
| R01 | `okupansi_sesi_cukup` terpenuhi | `sesuai_jadwal` | `"Ruang terisi {menit_terpakai} dari {menit_terjadwal} menit terjadwal."` |
| R02 | `okupansi_sesi_kurang` terpenuhi | `kosong_meski_terjadwal` | `"Ruang terisi hanya {menit_terpakai} menit dari {menit_terjadwal} menit terjadwal. Ruang ini berpotensi dimanfaatkan kegiatan lain lewat peminjaman di TU."` |
| R03 | `episode_cukup_panjang` terpenuhi | `dipakai_di_luar_jadwal` | `"Ruang terisi {menit_terpakai} menit di luar jadwal ({waktu_mulai} sampai {waktu_selesai}). Perlu ditinjau Admin."` |

Catatan:
- Format waktu pada penjelasan menggunakan konvensi Bahasa Indonesia dua digit dengan pemisah titik (mis. `"07.00"`).
- Kalimat tentang TU pada R02 bersifat informasi saja, bukan fitur booking.
- Hanya `rule_id` berawalan `R` (aturan keputusan) yang disimpan pada kolom `rule_id` di tabel `classification_results`.
 
## 13. Keterbatasan yang diketahui
 
1. Semua okupansi berasal dari simulasi buatan tim. Akurasi terhadap ground truth tidak menjamin akurasi di dunia nyata.
2. Ruang terjadwal yang kosong lalu dipinjam kegiatan lain lewat TU tampak sebagai terisi dan tidak terbedakan tanpa data PENRU (FR-13, terblokir token).
3. Rangkaian episode diputus oleh slot hilang, sehingga satu pemakaian panjang dapat terpecah dan tidak mencapai 30 menit bila noise slot hilang mengenai bagian tengah. Dampaknya diukur di SS1-12.
4. Dua ambang awal (10 dan 30 menit) adalah asumsi tim sampai divalidasi manpro pada 29 Okt 2026.
5. Kalender akademik memengaruhi sesi hanya lewat tipe `libur`. Pola khusus masa ujian ditangani generator.
6. Data satu semester penuh (7 Sep 2026 s.d. 22 Jan 2027) adalah simulasi sintetis karena sebagian tanggal belum terjadi pada saat implementasi.
7. Ambang 10 menit untuk sesi kosong rapuh terhadap noise 1% per slot (hipotesis bahwa fluktuasi acak dapat mempengaruhi hasil klasifikasi sesi pendek, diuji pada SS1-12).
## 14. Perubahan dari PRD v1.1 dan riwayat
 
Butir yang menambah atau memperjelas PRD v1.1 (untuk disetujui reviewer):
 
- Kunci unik `classification_results` pada (`room_id`, `tanggal`, `waktu_mulai`) [DISETUJUI].
- Slot hilang dihitung tidak terisi dan memutus episode [DISETUJUI].
- Pembanding `<` pada ambang sesi kosong dan pembobotan utilisasi per periode [DISETUJUI].
- Aturan hari libur dan syarat jadwal kelipatan 10 menit tanpa tumpang tindih [DISETUJUI].
- Pemisahan set data dev (`smart_space_ai_dev`, seed 1001) dan test (`smart_space_ai_test`, seed 2002); isolasi test di `smart_space_test` [DISETUJUI].
- Rentang data generator diperluas ke satu semester penuh (7 Sep 2026 s.d. 22 Jan 2027) [DISETUJUI].
- Antarmuka analitik AI menggunakan konvensi Bahasa Indonesia dan fungsi murni pada `app/analytics/utilization.py` (SS1-10) dengan pembulatan 2 desimal saat penulisan ke database [DISETUJUI].
- Nama hari di database: `Senin, Selasa, Rabu, Kamis, Jum'at` (dengan tanda petik) dan normalisasi lewat `app/calendar_utils.py` [DISETUJUI].
- Seeder jadwal idempoten dengan unique index slot jadwal pada `schedules` (menunggu PR #57) [DISETUJUI].
- Pengamanan data master ruangan: penghapusan ruangan ditolak bila memiliki jadwal atau riwayat (`occupancy_logs`, `classification_results`), dan kolom `rooms.status` bermakna kondisi ruangan (`tersedia`/`tidak tersedia`) [DISETUJUI].

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1.0 | 16 Okt 2026 | Draf awal SS1-07 |
| 1.1 | 18 Okt 2026 | Sinkronisasi keputusan pemisahan dev/test DB, rentang semester penuh, antarmuka nyata SS1-10 (utilization.py), normalisasi hari, perlindungan master ruangan, dan penyesuaian status implementasi |
 