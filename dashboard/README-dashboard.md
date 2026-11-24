# Dashboard Penjualan Online AdventureWorks — Kelompok 2

## Menjalankan dashboard

Dari root repository:

```powershell
python scripts/build_dashboard_snapshot.py --check
python -m http.server 8000 --bind 127.0.0.1
```

Buka `http://127.0.0.1:8000/dashboard/`. Gunakan server HTTP; membuka `index.html` melalui `file://` tidak mendukung pemuatan JSON dengan benar. Mode **Snapshot SQL** tidak memerlukan database. Jika dump berubah, bangun ulang dengan `python scripts/build_dashboard_snapshot.py`, lalu jalankan pemeriksaan `--check`.

## Sumber dan definisi metrik

[`assets/data/snapshot.json`](assets/data/snapshot.json) dibangun dari [`sql/adventureworks_dw (2).sql`](../sql/adventureworks_dw%20(2).sql). Generator memilih dump tersebut karena memakai `tanggal_key` serta atribut kalender Indonesia; dump lama masih memiliki kontrak tanggal berbeda. Nama tabel historis `dim_date` dipetakan menjadi nama resmi `dim_tanggal` dalam kontrak aplikasi. Dump asli tetap dipertahankan.

Snapshot menyertakan seluruh 60.398 detail fakta. Dimensi hanya membawa anggota yang dirujuk fakta dan anggota -1 jika tersedia; statistik kualitas tetap dihitung terhadap seluruh dump. SHA-256 sumber disertakan dalam metadata dan halaman Pemeriksaan Data.

| Metrik | Definisi |
|---|---|
| Nilai penjualan | `SUM(line_total)` pada grain satu detail pesanan |
| Pesanan unik | `COUNT(DISTINCT sales_order_id)` |
| Unit terjual | `SUM(order_qty)` |
| Pelanggan aktif | Jumlah `customer_id` bisnis unik yang diketahui; bukan jumlah surrogate key |
| Rata-rata per pesanan | Nilai penjualan dibagi pesanan unik; 0 jika hasil kosong |
| Estimasi diskon promosi | `SUM(line_total * discount_pct)` dari referensi promosi; bukan diskon aktual |
| Referensi kurs | `currency_rate_id > 0`; placeholder -1 tetap tanpa referensi meskipun kode sumber tertulis USD |

Nilai uang disimpan sebagai integer dengan skala 10.000 sehingga penjumlahan mempertahankan empat angka desimal sumber. Tampilan nominal dibulatkan menjadi dua desimal dan ekspor mempertahankan empat desimal. Tidak ada asumsi bahwa seluruh nilai telah dikonversi ke USD. Jumlah pesanan tidak aditif lintas kelompok produk; setiap kelompok menggunakan himpunan pesanan sendiri.

## Halaman dan kontrol

| Halaman | Isi |
|---|---|
| Ringkasan Penjualan | KPI, tren bulanan beserta tabel angka, kontribusi kategori dan wilayah |
| Produk dan Pelanggan | Sepuluh produk teratas, kategori, pencarian semua pelanggan terpilih, 25 pelanggan per halaman |
| Wilayah dan Promosi | Distribusi wilayah/grup, program promosi, estimasi diskon, pelanggan berulang |
| Kurs dan Pengiriman | Pesanan dengan/tanpa kurs, kode tujuan kurs, pesanan unik per metode kirim |
| Jelajahi Data (OLAP) | Tujuh dimensi, tiga ukuran, pilih anggota, drill-down, drill-up, pencarian dan 50 anggota per halaman |
| Pemeriksaan Data | Detail unik, pesanan, referensi dimensi, Unknown, diskon aktual, kualitas dump dan asal data |

Filter Tahun, Wilayah, dan Kategori berlaku untuk seluruh agregasi, pencarian pelanggan, OLAP, pemeriksaan kontekstual, dan ekspor. Tombol reset menghapus ketiga filter serta pencarian pelanggan. Pergantian filter mengembalikan OLAP ke tingkat teratas agar jalur lama tidak tertinggal. Paginasi membatasi jumlah elemen yang digambar, tidak mengurangi fakta yang dihitung.

Pilih anggota OLAP lalu tekan **Drill down**; tombol **Naik level** mengembalikan tingkat sebelumnya. Hierarki waktu adalah Tahun → Semester → Kuartal → Bulan → Tanggal. Operasi ini merupakan agregasi JavaScript, bukan eksekusi MDX Mondrian. Bukti pengujian Mondrian dicatat terpisah pada laporan audit.

CSV berisi seluruh detail yang memenuhi filter global. Sel teks di-quote, tanda kutip digandakan, serta awalan rumus spreadsheet dinetralkan. Hasil kosong tetap dapat diekspor sebagai header. Data sumber ditulis ke DOM menggunakan `textContent`, bukan disisipkan sebagai HTML.

## Mode MySQL lokal

Endpoint: [`api/dashboard.php`](api/dashboard.php). Jalankan PHP dengan ekstensi `pdo_mysql` dan variabel lingkungan `DW_HOST`, `DW_PORT`, `DW_DATABASE`, `DW_USER`, `DW_PASSWORD`. Gunakan akun yang hanya mempunyai hak SELECT. Jangan menyimpan kredensial dalam Git.

API memerlukan tabel `dim_tanggal` sesuai [`olap/source_contract.json`](../olap/source_contract.json). Untuk server lama, audit salinan database dan ikuti [catatan migrasi](../docs/pembaruan-dim-tanggal-20261124.md). Python HTTP server hanya melayani file statis; gunakan Apache atau server PHP untuk mode MySQL.

Kontrol MySQL mula-mula nonaktif. Browser mengaktifkannya hanya jika endpoint `?health=1` menyatakan tersedia. Respons data tetap divalidasi sebelum ditampilkan. Kegagalan koneksi menyembunyikan nilai lama, menampilkan pesan aman, dan menyediakan tombol coba lagi. API tidak mengubah database sumber.

## Pengujian dan batas bukti

Jalankan `node --check dashboard/assets/dashboard.js` dan `python -m py_compile scripts/build_dashboard_snapshot.py` untuk pemeriksaan sintaks. Bukti browser, rekonsiliasi SQL/API, viewport, dan status gerbang akhir tersedia dalam [audit final](../docs/audit-final-dashboard-pertemuan-12.md). Pemeriksaan sintaks tidak menggantikan uji browser atau runtime ETL/Mondrian.

Gambar dashboard lama dipertahankan sebagai bukti historis. `wireframe-dashboard.html` merupakan rancangan awal, sedangkan aplikasi aktif adalah `index.html` dengan CSS, JavaScript, dan snapshot di direktori `assets/`.
