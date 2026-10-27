"""Pelaksana klasifikasi: memuat data, memanggil sistem pakar, menyimpan hasil (SS1-11).

klasifikasikan_data murni (tanpa database) sehingga dapat diuji dengan data buatan tangan.
jalankan_klasifikasi membaca database lalu menyimpan lewat penyimpan idempoten dan
TIDAK melakukan commit. Pemanggil (runner CLI atau endpoint) yang menutup transaksi
(DATA_CONTRACT Bagian 9).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Collection, Iterable, Mapping, Sequence

from sqlalchemy.orm import Session

from app.classification.fakta import (
    muat_fakta_jadwal,
    muat_fakta_ruang,
    muat_slot_okupansi,
    muat_tanggal_libur,
)
from app.classification.pemuat import muat_ambang
from app.classification.penyimpan import simpan_hasil_idempoten
from app.classification.waktu import waktu_evaluasi_historis, waktu_sekarang_wib
from app.expert_system.klasifikasi import klasifikasikan_hari
from app.expert_system.tipe import (
    Ambang,
    FaktaJadwal,
    FaktaRuang,
    HasilKlasifikasi,
    SlotOkupansi,
)

# Ruang open space menurut DATA_CONTRACT Bagian 11.2.
# Pindahkan ke sumber bersama dengan generator bila sudah ada di sana.
NAMA_OPEN_SPACE = frozenset({"GU 701", "GU 705", "GU 707"})


class RuangTidakDitemukanError(ValueError):
    """Ruang yang diminta tidak ada di database."""


class DataOkupansiKosongError(ValueError):
    """Tidak ada data okupansi pada rentang dan ruang yang diminta.

    Tanpa data okupansi setiap sesi terbaca kosong. Hasil seperti itu
    menyesatkan, jadi klasifikasi ditolak.
    """


@dataclass(frozen=True)
class RingkasanKlasifikasi:
    tanggal_mulai: date
    tanggal_selesai: date
    jumlah_ruang: int
    jumlah_baris: int
    per_status: dict[str, int]


def klasifikasikan_data(
    daftar_ruang: Iterable[FaktaRuang],
    daftar_jadwal: Iterable[FaktaJadwal],
    slot_per_ruang: Mapping[int, Sequence[SlotOkupansi]],
    tanggal_libur: Collection[date],
    tanggal_mulai: date,
    tanggal_selesai: date,
    ambang: Ambang,
) -> list[HasilKlasifikasi]:
    """Menjalankan klasifikasikan_hari untuk tiap ruang dan tiap tanggal (inklusif).

    Waktu evaluasi tiap tanggal adalah 00.00 hari berikutnya (run historis).
    """
    if tanggal_mulai > tanggal_selesai:
        raise ValueError("tanggal_mulai tidak boleh setelah tanggal_selesai.")

    jadwal_per_ruang: dict[int, list[FaktaJadwal]] = defaultdict(list)
    for jadwal in daftar_jadwal:
        jadwal_per_ruang[jadwal.room_id].append(jadwal)

    hasil: list[HasilKlasifikasi] = []
    for ruang in daftar_ruang:
        slot_per_tanggal: dict[date, list[SlotOkupansi]] = defaultdict(list)
        for slot in slot_per_ruang.get(ruang.room_id, ()):
            slot_per_tanggal[slot.slot_mulai.date()].append(slot)

        tanggal = tanggal_mulai
        while tanggal <= tanggal_selesai:
            hasil.extend(
                klasifikasikan_hari(
                    ruang=ruang,
                    daftar_jadwal=jadwal_per_ruang.get(ruang.room_id, []),
                    slot_list=slot_per_tanggal.get(tanggal, []),
                    tanggal=tanggal,
                    waktu_evaluasi=waktu_evaluasi_historis(tanggal),
                    ambang=ambang,
                    is_holiday=tanggal in tanggal_libur,
                )
            )
            tanggal += timedelta(days=1)
    return hasil


def jalankan_klasifikasi(
    session: Session,
    tanggal_mulai: date,
    tanggal_selesai: date,
    room_ids: Collection[int] | None = None,
    computed_at: datetime | None = None,
    nama_open_space: Collection[str] = NAMA_OPEN_SPACE,
) -> RingkasanKlasifikasi:
    """Memuat data, mengklasifikasikan, lalu mengganti hasil lama pada rentang dan ruang itu.

    Tidak melakukan commit. Pemanggil yang commit atau rollback.

    Raises:
        ValueError: rentang terbalik, ambang tidak valid, atau hasil melanggar invarian.
        RuangTidakDitemukanError: ada room_id yang tidak ada di database.
        DataOkupansiKosongError: tidak ada data okupansi pada rentang itu.
    """
    if tanggal_mulai > tanggal_selesai:
        raise ValueError("tanggal_mulai tidak boleh setelah tanggal_selesai.")

    ambang = muat_ambang(session)
    daftar_ruang = muat_fakta_ruang(session, nama_open_space)

    if room_ids is not None:
        dipilih = set(room_ids)
        hilang = dipilih - {ruang.room_id for ruang in daftar_ruang}
        if hilang:
            raise RuangTidakDitemukanError(f"Ruang tidak ditemukan: {sorted(hilang)}")
        daftar_ruang = [ruang for ruang in daftar_ruang if ruang.room_id in dipilih]

    slot_per_ruang = muat_slot_okupansi(session, tanggal_mulai, tanggal_selesai)
    if not any(slot_per_ruang.get(ruang.room_id) for ruang in daftar_ruang):
        raise DataOkupansiKosongError(
            f"Tidak ada data okupansi pada {tanggal_mulai} sampai {tanggal_selesai}. "
            "Jalankan generator data lebih dulu."
        )

    hasil = klasifikasikan_data(
        daftar_ruang,
        muat_fakta_jadwal(session),
        slot_per_ruang,
        muat_tanggal_libur(session, tanggal_mulai, tanggal_selesai),
        tanggal_mulai,
        tanggal_selesai,
        ambang,
    )

    jumlah = simpan_hasil_idempoten(
        session,
        hasil,
        [ruang.room_id for ruang in daftar_ruang],
        tanggal_mulai,
        tanggal_selesai,
        computed_at or waktu_sekarang_wib(),
    )
    return RingkasanKlasifikasi(
        tanggal_mulai=tanggal_mulai,
        tanggal_selesai=tanggal_selesai,
        jumlah_ruang=len(daftar_ruang),
        jumlah_baris=jumlah,
        per_status=dict(Counter(h.status for h in hasil)),
    )
