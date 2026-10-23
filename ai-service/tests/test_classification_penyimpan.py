from datetime import date, datetime, time
from decimal import Decimal

import pytest

from app.classification.penyimpan import simpan_hasil_idempoten
from app.expert_system.tipe import HasilKlasifikasi
from app.models import ClassificationResult, Room, Schedule

COMPUTED_AT = datetime(2026, 10, 27, 12, 0, 0)
SENIN = date(2026, 10, 5)
SELASA = date(2026, 10, 6)
RABU = date(2026, 10, 7)


def _buat_ruang(db_session, nama):
    ruang = Room(nama_ruangan=nama, status="tersedia")
    db_session.add(ruang)
    db_session.flush()
    return ruang


def _buat_jadwal(db_session, ruang):
    jadwal = Schedule(
        room_id=ruang.id,
        hari="Senin",
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        mata_kuliah="Mata Kuliah Uji",
    )
    db_session.add(jadwal)
    db_session.flush()
    return jadwal


def _hasil_sesi(ruang, jadwal, tanggal, menit_terpakai=90):
    return HasilKlasifikasi(
        room_id=ruang.id,
        schedule_id=jadwal.id,
        tanggal=tanggal,
        waktu_mulai=time(8, 0),
        waktu_selesai=time(10, 0),
        status="sesuai_jadwal",
        menit_terjadwal=120,
        menit_terpakai=menit_terpakai,
        utilisasi_pct=menit_terpakai * 100 / 120,
        rule_id="R01",
        penjelasan="Ruang terisi sesuai jadwal.",
    )


def _hasil_episode(ruang, tanggal):
    return HasilKlasifikasi(
        room_id=ruang.id,
        schedule_id=None,
        tanggal=tanggal,
        waktu_mulai=time(18, 0),
        waktu_selesai=time(19, 0),
        status="dipakai_di_luar_jadwal",
        menit_terjadwal=0,
        menit_terpakai=60,
        utilisasi_pct=None,
        rule_id="R03",
        penjelasan="Ruang terisi di luar jadwal.",
    )


def _jumlah(db_session, *daftar_ruang):
    ids = [ruang.id for ruang in daftar_ruang]
    return (
        db_session.query(ClassificationResult)
        .filter(ClassificationResult.room_id.in_(ids))
        .count()
    )


def test_simpan_dua_kali_tidak_menggandakan_baris(db_session):
    ruang = _buat_ruang(db_session, "UJI-SS1-11-A")
    jadwal = _buat_jadwal(db_session, ruang)
    hasil = [
        _hasil_sesi(ruang, jadwal, SENIN),
        _hasil_episode(ruang, SENIN),
        _hasil_sesi(ruang, jadwal, SELASA),
    ]

    for _ in range(2):
        jumlah = simpan_hasil_idempoten(
            db_session, hasil, [ruang.id], SENIN, SELASA, COMPUTED_AT
        )
        assert jumlah == 3

    assert _jumlah(db_session, ruang) == 3


def test_simpan_ulang_mengganti_nilai_lama(db_session):
    ruang = _buat_ruang(db_session, "UJI-SS1-11-A")
    jadwal = _buat_jadwal(db_session, ruang)

    simpan_hasil_idempoten(
        db_session, [_hasil_sesi(ruang, jadwal, SENIN, 90)], [ruang.id], SENIN, SENIN, COMPUTED_AT
    )
    simpan_hasil_idempoten(
        db_session, [_hasil_sesi(ruang, jadwal, SENIN, 30)], [ruang.id], SENIN, SENIN, COMPUTED_AT
    )

    baris = db_session.query(ClassificationResult).filter_by(room_id=ruang.id).one()
    assert baris.menit_terpakai == 30
    assert baris.utilisasi_pct == Decimal("25.00")


def test_hanya_rentang_dan_ruang_yang_dihitung_ulang_yang_terhapus(db_session):
    ruang_a = _buat_ruang(db_session, "UJI-SS1-11-A")
    ruang_b = _buat_ruang(db_session, "UJI-SS1-11-B")
    jadwal_a = _buat_jadwal(db_session, ruang_a)
    jadwal_b = _buat_jadwal(db_session, ruang_b)

    simpan_hasil_idempoten(
        db_session,
        [_hasil_sesi(ruang_a, jadwal_a, SENIN), _hasil_sesi(ruang_a, jadwal_a, SELASA)],
        [ruang_a.id], SENIN, SELASA, COMPUTED_AT,
    )
    simpan_hasil_idempoten(
        db_session,
        [_hasil_sesi(ruang_b, jadwal_b, SENIN), _hasil_sesi(ruang_b, jadwal_b, SELASA)],
        [ruang_b.id], SENIN, SELASA, COMPUTED_AT,
    )

    # Hitung ulang hanya ruang A pada hari Senin, hasilnya kosong.
    jumlah = simpan_hasil_idempoten(
        db_session, [], [ruang_a.id], SENIN, SENIN, COMPUTED_AT
    )

    assert jumlah == 0
    assert _jumlah(db_session, ruang_a) == 1
    assert _jumlah(db_session, ruang_b) == 2
    sisa = db_session.query(ClassificationResult).filter_by(room_id=ruang_a.id).one()
    assert sisa.tanggal == SELASA


def test_tolak_hasil_di_luar_rentang_tanpa_menghapus_data_lama(db_session):
    ruang = _buat_ruang(db_session, "UJI-SS1-11-A")
    jadwal = _buat_jadwal(db_session, ruang)
    simpan_hasil_idempoten(
        db_session, [_hasil_sesi(ruang, jadwal, SENIN)], [ruang.id], SENIN, SELASA, COMPUTED_AT
    )

    with pytest.raises(ValueError, match="di luar rentang"):
        simpan_hasil_idempoten(
            db_session, [_hasil_sesi(ruang, jadwal, RABU)], [ruang.id], SENIN, SELASA, COMPUTED_AT
        )

    assert _jumlah(db_session, ruang) == 1


def test_tolak_hasil_dari_ruang_yang_tidak_diproses(db_session):
    ruang_a = _buat_ruang(db_session, "UJI-SS1-11-A")
    ruang_b = _buat_ruang(db_session, "UJI-SS1-11-B")
    jadwal_b = _buat_jadwal(db_session, ruang_b)

    with pytest.raises(ValueError, match="tidak termasuk ruang"):
        simpan_hasil_idempoten(
            db_session, [_hasil_sesi(ruang_b, jadwal_b, SENIN)], [ruang_a.id], SENIN, SENIN, COMPUTED_AT
        )

    assert _jumlah(db_session, ruang_a, ruang_b) == 0


def test_tolak_kunci_ganda(db_session):
    ruang = _buat_ruang(db_session, "UJI-SS1-11-A")
    jadwal = _buat_jadwal(db_session, ruang)
    hasil = [_hasil_sesi(ruang, jadwal, SENIN, 90), _hasil_sesi(ruang, jadwal, SENIN, 30)]

    with pytest.raises(ValueError, match="ganda"):
        simpan_hasil_idempoten(db_session, hasil, [ruang.id], SENIN, SENIN, COMPUTED_AT)

    assert _jumlah(db_session, ruang) == 0


def test_tolak_periode_terbalik(db_session):
    with pytest.raises(ValueError, match="tanggal_mulai"):
        simpan_hasil_idempoten(db_session, [], [1], SELASA, SENIN, COMPUTED_AT)


def test_tanpa_ruang_tidak_melakukan_apa_apa(db_session):
    assert simpan_hasil_idempoten(db_session, [], [], SENIN, SELASA, COMPUTED_AT) == 0


def test_tidak_melakukan_commit(db_session):
    ruang = _buat_ruang(db_session, "UJI-SS1-11-A")
    jadwal = _buat_jadwal(db_session, ruang)

    simpan_hasil_idempoten(
        db_session, [_hasil_sesi(ruang, jadwal, SENIN)], [ruang.id], SENIN, SENIN, COMPUTED_AT
    )

    # Setelah commit, transaksi ditutup. Selama belum commit, masih terbuka.
    assert db_session.in_transaction()
