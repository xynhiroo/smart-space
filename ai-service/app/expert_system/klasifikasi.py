"""Fungsi publik murni klasifikasi status ruangan (DATA_CONTRACT Bagian 11.2).

Sistem pakar Tier 1 untuk Smart Space:
- Tidak mengakses basis data
- Tidak membaca waktu sistem (waktu_evaluasi dikirim sebagai argumen)
- Deterministik dan bebas mutasi masukan
- Konvensi Bahasa Indonesia
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Sequence

from app.analytics.utilization import hitung_utilisasi_pct
from app.calendar_utils import matches_day_of_week
from app.expert_system.frames import buat_frame_ruang
from app.expert_system.mesin_inferensi import MemoriKerja, jalankan_inferensi
from app.expert_system.okupansi import (
    hitung_menit_sesi,
    kumpulkan_episode_luar_jadwal,
)
from app.expert_system.penjelasan import bangun_penjelasan
from app.expert_system.tipe import (
    Ambang,
    FaktaJadwal,
    FaktaRuang,
    HasilKlasifikasi,
    SlotOkupansi,
)


def klasifikasikan_sesi(
    ruang: FaktaRuang,
    jadwal: FaktaJadwal,
    slot_list: list[SlotOkupansi],
    tanggal: date,
    waktu_evaluasi: datetime,
    ambang: Ambang,
) -> HasilKlasifikasi | None:
    """Klasifikasi status satu sesi perkuliahan terjadwal (Bagian 7.1, 7.3, 11.2).

    Mengembalikan None bila sesi belum berakhir pada waktu_evaluasi
    (waktu_evaluasi < tanggal + jam_selesai).
    """
    sesi_selesai_dt = datetime.combine(tanggal, jadwal.jam_selesai)
    if waktu_evaluasi < sesi_selesai_dt:
        return None

    menit_terjadwal, menit_terpakai = hitung_menit_sesi(
        room_id=ruang.room_id,
        tanggal=tanggal,
        jam_mulai=jadwal.jam_mulai,
        jam_selesai=jadwal.jam_selesai,
        slot_list=slot_list,
        waktu_evaluasi=waktu_evaluasi,
    )

    utilisasi_pct = hitung_utilisasi_pct(menit_terjadwal, menit_terpakai)

    # Inisialisasi memori kerja untuk mesin inferensi
    wm = MemoriKerja(
        {
            "jenis_evaluasi": "sesi",
            "room_id": ruang.room_id,
            "schedule_id": jadwal.schedule_id,
            "tanggal": tanggal,
            "jam_mulai": jadwal.jam_mulai,
            "jam_selesai": jadwal.jam_selesai,
            "waktu_evaluasi": waktu_evaluasi,
            "menit_terjadwal": menit_terjadwal,
            "menit_terpakai": menit_terpakai,
            "utilisasi_pct": utilisasi_pct,
            "empty_min_occupied_minutes": ambang.empty_min_occupied_minutes,
            "outside_schedule_min_minutes": ambang.outside_schedule_min_minutes,
        }
    )

    hasil_inf = jalankan_inferensi(wm)
    status = hasil_inf.memori_kerja.get("status")
    rule_id = hasil_inf.memori_kerja.get("rule_id")

    if not status or not rule_id:
        raise RuntimeError(
            f"Mesin inferensi gagal menentukan status sesi schedule_id={jadwal.schedule_id} "
            f"(jejak: {hasil_inf.jejak})."
        )

    penjelasan = bangun_penjelasan(
        rule_id=rule_id,
        menit_terjadwal=menit_terjadwal,
        menit_terpakai=menit_terpakai,
        waktu_mulai=jadwal.jam_mulai,
        waktu_selesai=jadwal.jam_selesai,
    )

    return HasilKlasifikasi(
        room_id=ruang.room_id,
        schedule_id=jadwal.schedule_id,
        tanggal=tanggal,
        waktu_mulai=jadwal.jam_mulai,
        waktu_selesai=jadwal.jam_selesai,
        status=status,
        menit_terjadwal=menit_terjadwal,
        menit_terpakai=menit_terpakai,
        utilisasi_pct=utilisasi_pct,
        rule_id=rule_id,
        penjelasan=penjelasan,
    )


def deteksi_pemakaian_luar_jadwal(
    ruang: FaktaRuang,
    daftar_jadwal: list[FaktaJadwal],
    slot_list: list[SlotOkupansi],
    tanggal: date,
    waktu_evaluasi: datetime,
    ambang: Ambang,
) -> list[HasilKlasifikasi]:
    """Deteksi episode pemakaian di luar seluruh jadwal pada satu ruang dan tanggal (Bagian 7.4)."""
    # Filter jadwal yang aktif untuk ruang ini pada hari tersebut
    weekday = tanggal.weekday()
    jadwal_hari_ini = [
        j
        for j in daftar_jadwal
        if j.room_id == ruang.room_id and matches_day_of_week(j.hari, weekday)
    ]
    rentang_jadwal = [(j.jam_mulai, j.jam_selesai) for j in jadwal_hari_ini]

    episodes = kumpulkan_episode_luar_jadwal(
        room_id=ruang.room_id,
        tanggal=tanggal,
        rentang_jadwal=rentang_jadwal,
        slot_list=slot_list,
        waktu_evaluasi=waktu_evaluasi,
        ambang_durasi_menit=ambang.outside_schedule_min_minutes,
    )

    hasil: list[HasilKlasifikasi] = []
    for ep in episodes:
        wm = MemoriKerja(
            {
                "jenis_evaluasi": "episode",
                "room_id": ruang.room_id,
                "tanggal": tanggal,
                "durasi_episode": ep.durasi_menit,
                "menit_terpakai": ep.durasi_menit,
                "waktu_mulai": ep.waktu_mulai,
                "waktu_selesai": ep.waktu_selesai,
                "empty_min_occupied_minutes": ambang.empty_min_occupied_minutes,
                "outside_schedule_min_minutes": ambang.outside_schedule_min_minutes,
            }
        )
        hasil_inf = jalankan_inferensi(wm)
        status = hasil_inf.memori_kerja.get("status")
        rule_id = hasil_inf.memori_kerja.get("rule_id")

        if not status or not rule_id:
            raise RuntimeError(
                f"Mesin inferensi gagal menentukan status episode {ep} (jejak: {hasil_inf.jejak})."
            )

        penjelasan = bangun_penjelasan(
            rule_id=rule_id,
            menit_terjadwal=0,
            menit_terpakai=ep.durasi_menit,
            waktu_mulai=ep.waktu_mulai,
            waktu_selesai=ep.waktu_selesai,
        )

        hasil.append(
            HasilKlasifikasi(
                room_id=ruang.room_id,
                schedule_id=None,
                tanggal=tanggal,
                waktu_mulai=ep.waktu_mulai,
                waktu_selesai=ep.waktu_selesai,
                status=status,
                menit_terjadwal=0,
                menit_terpakai=ep.durasi_menit,
                utilisasi_pct=None,
                rule_id=rule_id,
                penjelasan=penjelasan,
            )
        )

    # Urutkan episode menurut waktu_mulai
    hasil.sort(key=lambda h: h.waktu_mulai)
    return hasil


def klasifikasikan_hari(
    ruang: FaktaRuang,
    daftar_jadwal: list[FaktaJadwal],
    slot_list: list[SlotOkupansi],
    tanggal: date,
    waktu_evaluasi: datetime,
    ambang: Ambang,
    is_holiday: bool,
) -> list[HasilKlasifikasi]:
    """Gabungan evaluasi harian satu ruang (Bagian 11.2).

    Aturan:
    - Tanggal setelah waktu_evaluasi menghasilkan list kosong.
    - Pada hari libur (is_holiday=True): sesi kuliah tidak dievaluasi,
      seluruh jendela jadwal dianggap kosong, dan episode luar jadwal tetap dievaluasi.
    - Pada hari biasa: sesi yang cocok dengan hari dievaluasi, kemudian episode luar jadwal.
    - Hasil terurut: baris sesi menurut jam_mulai, diikuti baris episode menurut waktu_mulai.
    """
    if tanggal > waktu_evaluasi.date():
        return []

    hasil_sesi: list[HasilKlasifikasi] = []

    if not is_holiday:
        # Gunakan frame ruang untuk seleksi dan pengurutan jadwal
        frame_ruang = buat_frame_ruang(ruang, daftar_jadwal)
        jadwal_hari_ini = frame_ruang.jadwal_pada(tanggal)

        # Petakan kembali ke FaktaJadwal asli untuk menjaga konsistensi
        jadwal_map = {j.schedule_id: j for j in daftar_jadwal if j.room_id == ruang.room_id}

        for frame_j in jadwal_hari_ini:
            fakta_j = jadwal_map[frame_j.schedule_id]
            res_sesi = klasifikasikan_sesi(
                ruang=ruang,
                jadwal=fakta_j,
                slot_list=slot_list,
                tanggal=tanggal,
                waktu_evaluasi=waktu_evaluasi,
                ambang=ambang,
            )
            if res_sesi is not None:
                hasil_sesi.append(res_sesi)

    # Episode luar jadwal: jika libur, jadwal dikirim kosong sehingga seluruh slot dianggap luar jadwal
    jadwal_untuk_episode = [] if is_holiday else daftar_jadwal
    hasil_episode = deteksi_pemakaian_luar_jadwal(
        ruang=ruang,
        daftar_jadwal=jadwal_untuk_episode,
        slot_list=slot_list,
        tanggal=tanggal,
        waktu_evaluasi=waktu_evaluasi,
        ambang=ambang,
    )

    # Hasil terurut: sesi menurut jam_mulai, lalu episode menurut waktu_mulai
    return hasil_sesi + hasil_episode
