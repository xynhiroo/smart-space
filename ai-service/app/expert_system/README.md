# Sistem Pakar Klasifikasi Status Ruangan (Tier 1) - SS1-09

Paket `app.expert_system` adalah implementasi sistem pakar berbasis aturan (*rule-based expert system*) dan frame (*frame-based knowledge representation*) untuk mengklasifikasikan status okupansi ruangan di Smart Space Analytics Platform.

## Arsitektur

Sistem dirancang sebagai **kumpulan fungsi murni** tanpa efek samping:
- **Tanpa akses basis data langsung**: Seluruh fakta diinjeksi melalui dataclass murni (`FaktaRuang`, `FaktaJadwal`, `SlotOkupansi`, `Ambang`). Lapisan I/O basis data ditangani terpisah oleh repositori (SS1-11).
- **Tanpa waktu sistem**: `waktu_evaluasi` selalu dikirim sebagai parameter argumen eksplisit sehingga evaluasi sepenuhnya dapat direka ulang (*replayable*) dan deterministik.
- **Konfigurasi dinamis**: Seluruh ambang batas (`empty_min_occupied_minutes`, `outside_schedule_min_minutes`, dsb.) dikirim via objek `Ambang`. Tidak ada angka ambang yang di-hardcode di logika inferensi.

### Komponen Utama

1. **Frames (`frames.py`)**:
   Representasi pengetahuan berstruktur untuk entitas fisik dan temporal:
   - `FrameRuang`: Memuat identitas ruang (`room_id`, `nama_ruangan`, `is_open_space`) serta relasi slot jadwal perkuliahan.
   - `FrameJadwal`: Pengetahuan jadwal sesi (`schedule_id`, `hari`, `jam_mulai`, `jam_selesai`, `mata_kuliah`).
   - Menyediakan metode `jadwal_pada(tanggal)` dengan normalisasi hari Bahasa Indonesia (`calendar_utils`).

2. **Pemrosesan Okupansi (`okupansi.py`)**:
   Fungsi pembantu murni untuk agregasi slot 10 menit:
   - `hitung_menit_sesi`: Menghitung `menit_terjadwal` dan `menit_terpakai` dalam jendela sesi. Mengecualikan slot jeda 17.00 dan di luar jam operasional (07.00 - 23.00). Slot hilang diperlakukan sebagai tidak terisi.
   - `kumpulkan_episode_luar_jadwal`: Mendeteksi rangkaian berurutan slot terisi di luar seluruh jadwal pada tanggal terkait. Rangkaian berdurasi $\ge$ `outside_schedule_min_minutes` dikumpulkan sebagai episode; rangkaian yang lebih pendek disaring sebagai *noise*.

3. **Basis Pengetahuan (`basis_pengetahuan.py`)**:
   Aturan didefinisikan murni sebagai **data** (`Aturan`), terpisah dari mesin inferensi:
   - **Aturan Turunan (`F01` s.d. `F04`)**: Menurunkan fakta perantara (`sesi_telah_berakhir`, `okupansi_sesi_kurang`, `okupansi_sesi_cukup`, `episode_cukup_panjang`).
   - **Aturan Keputusan (`R01` s.d. `R03`)**: Menetapkan status akhir (`sesuai_jadwal`, `kosong_meski_terjadwal`, `dipakai_di_luar_jadwal`). Hanya id `R..` yang dicatat pada hasil akhir klasifikasi.

4. **Mesin Inferensi (`mesin_inferensi.py`)**:
   Mesin *forward chaining* deterministik:
   - Memori kerja (`MemoriKerja`) menampung fakta observasi dan fakta turunan.
   - Mengevaluasi aturan dengan urutan tetap (*fixed firing order*) dan mengulang evaluasi hingga kondisi *fixpoint* tercapai (tidak ada fakta baru yang dihasilkan).
   - Mencatat seluruh aturan yang aktif ke dalam `jejak` inferensi (*explanation trace*).

5. **Penjelasan (`penjelasan.py`)**:
   Membangun kalimat penjelasan Bahasa Indonesia alami berdasarkan templat resmi per `rule_id` (format waktu `"07.00"`, rujukan peminjaman TU pada `R02`).

6. **Pemetaan (`pemetaan.py`)**:
   - `ke_sesi`: Memetakan `HasilKlasifikasi` ke tipe `Sesi` untuk penghitungan utilisasi (SS1-10). Mengembalikan `None` untuk episode di luar jadwal.
   - `ke_baris_classification_results`: Memetakan ke kamus baris tabel `classification_results` (DATA_CONTRACT Bagian 5) dengan pembulatan 2 desimal `ROUND_HALF_UP` pada persentase utilisasi.

## Contoh Penggunaan

```python
from datetime import date, datetime, time
from app.expert_system import (
    Ambang,
    FaktaRuang,
    FaktaJadwal,
    SlotOkupansi,
    klasifikasikan_hari,
)

# 1. Definisikan ambang dan fakta master
ambang = Ambang(
    empty_min_occupied_minutes=10,
    outside_schedule_min_minutes=30,
    batas_rendah=40.0,
    batas_sedang=80.0,
)
ruang = FaktaRuang(room_id=1, nama_ruangan="GU 604", is_open_space=False)
jadwal = [
    FaktaJadwal(
        schedule_id=101,
        room_id=1,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Pemrograman Web",
    )
]

# 2. Log okupansi slot
tanggal_eval = date(2026, 9, 7)
waktu_eval = datetime(2026, 9, 7, 23, 0)
slots = [
    SlotOkupansi(room_id=1, slot_mulai=datetime(2026, 9, 7, 8, m), is_occupied=True)
    for m in range(0, 60, 10)
]

# 3. Klasifikasikan seluruh hari
hasil = klasifikasikan_hari(
    ruang=ruang,
    daftar_jadwal=jadwal,
    slot_list=slots,
    tanggal=tanggal_eval,
    waktu_evaluasi=waktu_eval,
    ambang=ambang,
    is_holiday=False,
)

for h in hasil:
    print(f"[{h.rule_id}] {h.status}: {h.penjelasan} (Utilisasi: {h.utilisasi_pct}%)")
```

## Menjalankan Pengujian

Jalankan pengujian unit pytest:

```bash
# Dari root repositori
python -m pytest ai-service/tests/test_expert_system.py -v

# Atau jalankan seluruh test ai-service
cd ai-service
pytest -v
```
