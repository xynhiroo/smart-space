"""Mesin inferensi forward chaining deterministik untuk sistem pakar."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from app.expert_system.basis_pengetahuan import DAFTAR_ATURAN_DEFAULT, Aturan


class MemoriKerja:
    """Working memory sistem pakar untuk menyimpan fakta observasi dan fakta turunan."""

    def __init__(self, fakta_awal: Mapping[str, Any] | None = None) -> None:
        self._fakta: dict[str, Any] = dict(fakta_awal or {})

    def get(self, kunci: str, default: Any = None) -> Any:
        return self._fakta.get(kunci, default)

    def set(self, kunci: str, nilai: Any) -> None:
        self._fakta[kunci] = nilai

    def update(self, fakta_baru: Mapping[str, Any]) -> None:
        self._fakta.update(fakta_baru)

    def sebagai_dict(self) -> dict[str, Any]:
        return dict(self._fakta)

    def __getitem__(self, kunci: str) -> Any:
        return self._fakta[kunci]

    def __contains__(self, kunci: str) -> bool:
        return kunci in self._fakta

    def __repr__(self) -> str:
        return f"MemoriKerja({self._fakta})"


@dataclass(frozen=True)
class HasilInferensi:
    """Hasil eksekusi mesin inferensi: memori kerja akhir dan jejak penembakan aturan."""

    memori_kerja: MemoriKerja
    jejak: tuple[str, ...] = field(default_factory=tuple)


def jalankan_inferensi(
    memori_kerja: MemoriKerja,
    basis_pengetahuan: Sequence[Aturan] = DAFTAR_ATURAN_DEFAULT,
) -> HasilInferensi:
    """Menjalankan mesin inferensi forward-chaining deterministik hingga mencapai fixpoint.

    Karakteristik:
    - Urutan evaluasi aturan mengikuti urutan pasti pada `basis_pengetahuan`.
    - Setiap aturan hanya menembak maksimum satu kali per siklus inferensi.
    - Fakta baru ditambahkan langsung ke memori kerja.
    - Berulang terus sampai tidak ada lagi aturan yang dapat ditembakkan (kondisi fixpoint).
    - Mencatat seluruh `rule_id` yang ditembakkan secara berurutan ke dalam `jejak`.
    - Basis pengetahuan dapat diinjeksi secara bebas untuk keperluan pengujian.
    """
    jejak: list[str] = []
    aturan_sudah_menembak: set[str] = set()

    while True:
        ada_aturan_baru_menembak = False
        for aturan in basis_pengetahuan:
            if aturan.rule_id in aturan_sudah_menembak:
                continue

            if aturan.kondisi(memori_kerja):
                fakta_baru = aturan.kesimpulan(memori_kerja)
                memori_kerja.update(fakta_baru)
                aturan_sudah_menembak.add(aturan.rule_id)
                jejak.append(aturan.rule_id)
                ada_aturan_baru_menembak = True

        if not ada_aturan_baru_menembak:
            break

    return HasilInferensi(memori_kerja=memori_kerja, jejak=tuple(jejak))
