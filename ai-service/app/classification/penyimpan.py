"""Penyimpan hasil klasifikasi ke tabel classification_results (SS1-11).

Idempoten: baris lama pada ruang dan rentang tanggal yang dihitung ulang dihapus,
lalu baris baru dimasukkan. Fungsi ini TIDAK melakukan commit. Pemanggil (runner)
yang menutup transaksi, sehingga hapus dan masukkan bersifat atomik
(DATA_CONTRACT Bagian 9).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Sequence

from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from app.expert_system.pemetaan import ke_baris_classification_results
from app.expert_system.tipe import HasilKlasifikasi
from app.models import ClassificationResult

UKURAN_BATCH = 2000


def simpan_hasil_idempoten(
    session: Session,
    daftar_hasil: Sequence[HasilKlasifikasi],
    daftar_room_id: Iterable[int],
    tanggal_mulai: date,
    tanggal_selesai: date,
    computed_at: datetime,
) -> int:
    """Mengganti hasil klasifikasi pada ruang dan rentang tanggal (inklusif).

    Seluruh hasil divalidasi lebih dulu. Bila ada yang tidak valid, tidak ada
    baris lama yang dihapus. Daftar hasil boleh kosong: baris lama pada ruang
    dan rentang itu tetap dihapus.

    Returns:
        Jumlah baris yang dimasukkan.
    """
    if tanggal_mulai > tanggal_selesai:
        raise ValueError("tanggal_mulai tidak boleh setelah tanggal_selesai.")

    room_ids = set(daftar_room_id)
    kunci_terlihat: set[tuple] = set()
    baris: list[dict] = []

    for hasil in daftar_hasil:
        if hasil.room_id not in room_ids:
            raise ValueError(
                f"Hasil untuk ruang {hasil.room_id} tidak termasuk ruang yang dihitung ulang."
            )
        if not tanggal_mulai <= hasil.tanggal <= tanggal_selesai:
            raise ValueError(
                f"Hasil tanggal {hasil.tanggal} berada di luar rentang "
                f"{tanggal_mulai} sampai {tanggal_selesai}."
            )
        kunci = (hasil.room_id, hasil.tanggal, hasil.waktu_mulai)
        if kunci in kunci_terlihat:
            raise ValueError(
                f"Hasil ganda untuk ruang {hasil.room_id} tanggal {hasil.tanggal} "
                f"mulai {hasil.waktu_mulai}."
            )
        kunci_terlihat.add(kunci)
        baris.append(ke_baris_classification_results(hasil, computed_at))

    if not room_ids:
        return 0

    session.execute(
        delete(ClassificationResult).where(
            ClassificationResult.room_id.in_(room_ids),
            ClassificationResult.tanggal.between(tanggal_mulai, tanggal_selesai),
        )
    )

    for awal in range(0, len(baris), UKURAN_BATCH):
        session.execute(insert(ClassificationResult), baris[awal : awal + UKURAN_BATCH])

    session.flush()
    return len(baris)
