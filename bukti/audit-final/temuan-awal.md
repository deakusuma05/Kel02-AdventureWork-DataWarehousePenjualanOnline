# Temuan awal audit — 24 November 2026

Kondisi awal: branch `main`, commit `af2fc29`, working tree bersih.
Remote: `https://github.com/deakusuma05/Kel02-AdventureWork-DataWarehousePenjualanOnline.git`.

| Risiko | Temuan sebelum perbaikan | Lokasi |
|---|---|---|
| CRITICAL | Halaman merujuk CSS, JavaScript dan snapshot yang belum tersedia; dashboard belum dapat berjalan | `dashboard/index.html`, folder `dashboard/assets/` |
| HIGH | Generator snapshot belum ada; asal angka belum dapat direproduksi | `scripts/build_dashboard_snapshot.py` |
| HIGH | DDL menggunakan DROP TABLE; eksekusi ulang menghapus data | `sql/ddl.sql` |
| HIGH | Laporan menganggap rebuild tanpa error sebagai bukti idempotensi aman terhadap data | `laporan/pekan-12.md` |
| HIGH | Paket OLAP merujuk direktori SQL/MDX yang belum tersedia; validator berpotensi melewati daftar MDX kosong | `olap/README.md`, `olap/validate_package.py` |
| HIGH | Endpoint PHP belum tersedia tetapi tombol MySQL ditampilkan aktif | `dashboard/index.html` |
| MEDIUM | Identitas dashboard masih memakai branding lama | `dashboard/index.html`, `olap/` |
| MEDIUM | Terdapat perbedaan nama kolom/struktur antara DDL, dump, dokumen grain, dan ETL | `sql/`, `etl/`, `docs/` |
| MEDIUM | Standar kalender resmi dosen belum ditemukan di repository | Pemeriksaan formal checkpoint 12.1 |

Temuan ini adalah catatan keadaan awal, bukan status akhir. Hasil perbaikan dan uji terdapat dalam laporan audit final. Screenshot historis dipertahankan tanpa perubahan.
