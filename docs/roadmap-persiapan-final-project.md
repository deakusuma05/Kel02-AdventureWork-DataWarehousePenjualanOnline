# Panduan Roadmap & Persiapan Menuju Presentasi Akhir (Final Project) Data Warehouse

**Proyek:** Data Warehouse Penjualan Online (*AdventureWorks Online Sales*)  
**Kelompok:** 2 · Data Warehouse & OLAP · Sistem Informasi UPN "Veteran" Jawa Timur  
**Berkas:** `docs/roadmap-persiapan-final-project.md`  
**Target:** Penyelesaian Tuntas dari Steering Review Pekan 14 hingga Presentasi Final (Pekan 16)  

---

## 1. Evaluasi Capaian Saat Ini (Status Kesehatan Proyek)

Secara arsitektur teknis dan kelengkapan repositori, kelompok kita telah berada pada posisi yang sangat maju (*ahead of schedule*):

* ✅ **Pekan 9–10 (Inisiasi & Pemodelan):** Piagam proyek, profil data sumber (60.398 baris detail, 27.659 pesanan), Bus Matrix, Star Schema V1/V2 tuntas.
* ✅ **Pekan 11 (Spesifikasi Teknis):** Source-to-Target Mapping, strategi SCD Tipe 2 pada harga pokok produk, desain kubus awal, dan wireframe dashboard tuntas.
* ✅ **Pekan 12–13 (Implementasi ETL & Pipeline):** Ekstraksi staging (`t01_ekstrak.ktr`), 7 transformasi dimensi, 1 transformasi fakta (`08-fact-online-sales.ktr`), master job (`job_utama.kjb`), eksekusi CLI Kitchen terminal, uji idempotensi (run 2x tanpa duplikasi), dan rekonsiliasi data 100% cocok.
* ✅ **Pekan 14 (OLAP & MDX):** Skema kubus Mondrian [`olap/schema.xml`](../olap/schema.xml), 7 kueri MDX [`olap/query.mdx`](../olap/query.mdx), skrip SQL pembanding [`pengujian-olap-mdx-vs-sql.sql`](../sql/pengujian/pengujian-olap-mdx-vs-sql.sql), penyempurnaan dashboard (10 wilayah, 10 pelanggan VIP, ekspor CSV komprehensif), dan laporan [`laporan/pekan-14.md`](../laporan/pekan-14.md).

---

## 2. Matriks Persiapan Menuju Presentasi Akhir (Apa yang Kurang & Perlu Dilengkapi)

Berikut adalah tabel rincian tahapan, daftar periksa kekurangan, dan aksi konkret yang harus diselesaikan hingga presentasi akhir:

| Fase / Periode | Fokus Deliverable | Status Repositori Saat Ini | Kekurangan yang Perlu Dilakukan (Action Items) | Penanggung Jawab |
|---|---|:---:|---|---|
| **Pekan 14 (Minggu Ini)** | **OLAP Mondrian & Bukti MDX** | Kode & Laporan Siap (100%) | 1. Buka `olap/schema.xml` di Pentaho Schema Workbench (PSW).<br>2. Ambil tangkapan layar PSW (*Zero Red Elements*).<br>3. Jalankan 5–7 kueri MDX dan SQL pembanding, simpan screenshot hasil eksekusi ke `bukti/olap/`. | Haura (OLAP), Alifa (Bukti), Dea (Laporan) |
| **Pekan 15** | **Backend API & Integrasi Dashboard** | Prototipe Siap (Wireframe 100%), Endpoint JSON terdokumentasi | 1. Bangun server backend kecil (Node.js Express / Python Flask) yang mengembalikan JSON.<br>2. Hubungkan `fetch()` di `dashboard/wireframe-dashboard.html` ke endpoint API lokal.<br>3. Uji responsivitas filter Tahun, Wilayah, dan Kategori langsung dari DB.<br>4. Susun `laporan/pekan-15.md`. | Fivediniar (Backend), Haura (Dashboard), Siti Anisa (DB API) |
| **Pekan 16 (Final Project)** | **Presentasi Akhir & Serah Terima** | Belum Dibuat | 1. Buat Slide PPT Presentasi Final (10–12 slide eksekutif).<br>2. Rekam video demo sistem (backup jika live demo terkendala jaringan).<br>3. Gladi bersih demo alur: ETL Kitchen &rarr; OLAP PSW &rarr; Dashboard Web.<br>4. Susun Laporan Akhir Komprehensif (*Final Project Report*). | Seluruh Anggota Tim Kelompok 2 |

---

## 3. Panduan Step-by-Step Khusus OLAP (Pentaho Schema Workbench & MDX)

Bagian ini adalah panduan langkah demi langkah teknis untuk mengeksekusi, memvalidasi, dan mengambil bukti pengujian OLAP untuk laporan Pekan 14.

```
+--------------------------------------------------------------------------------------------------+
| ALUR KERJA OLAP MONDRIAN KELOMPOK 2                                                              |
|                                                                                                  |
| [Database DW: MySQL] ───(JDBC Driver)───> [Pentaho Schema Workbench] ───> [Validasi XML Hijau]  |
|         │                                             │                                          |
|         ▼                                             ▼                                          |
|  Kueri SQL Pembanding                         Kueri MDX (MDX Runner)                             |
|  (phpMyAdmin / CLI)                           (7 Pertanyaan Bisnis)                              |
|         │                                             │                                          |
|         └───────────────> [Cocok 100% (Rp 0 Selisih)] <────────────────┘                         |
+--------------------------------------------------------------------------------------------------+
```

### Langkah 1: Persiapan Lingkungan Pentaho Schema Workbench (PSW)
1. Pastikan Java Runtime Environment (JRE/JDK 8 atau 11) telah terpasang.
2. Buka folder Schema Workbench kamu (misalnya di `c:\Users\User\Downloads\psw-ce-3.14.0.0-12\schema-workbench`).
3. **PENTING — Pasang Driver JDBC MySQL:**
   - Salin file driver JDBC MySQL (`mysql-connector-j-8.x.x.jar` atau `mysql-connector-java-5.1.x.jar` atau `mariadb-java-client.jar`) ke dalam folder `drivers/` atau `lib/` di dalam direktori Schema Workbench.
   - *Jika driver ini belum ada di folder lib PSW, PSW tidak akan bisa membaca tabel fisik MySQL!*
4. Jalankan aplikasi Schema Workbench:
   - Di Windows: Klik ganda `workbench.bat` (atau buka terminal dan ketik `./workbench.bat`).

---

### Langkah 2: Konfigurasi Koneksi Database di Schema Workbench
1. Pada menu navigasi atas PSW, klik **Options** &rarr; **Connection...**.
2. Isi formulir koneksi sesuai database lokal XAMPP kita:
   - **Connection Name:** `AdventureWorks_DW_Conn`
   - **Database Type:** `MySQL`
   - **Access:** `Native (JDBC)`
   - **Host Name:** `localhost` (atau `127.0.0.1`)
   - **Database Name:** `adventureworks_dw`
   - **Port Number:** `3306`
   - **User Name:** `root`
   - **Password:** *(kosongkan jika default XAMPP, atau isi jika ada)*
3. Klik tombol **Test Connection**.
   - *Pastikan muncul pesan pop-up: "Connection to database is OK!"*.
4. Klik **OK** untuk menyimpan koneksi.

---

### Langkah 3: Membuka dan Memvalidasi `olap/schema.xml`
1. Di Schema Workbench, klik **File** &rarr; **Open...**.
2. Navigasikan ke file repositori proyek kita:  
   `d:\SEMESTER 7\DWO\FINAL PROJECT\adventureworks-online-sales-dw\olap\schema.xml`
3. Periksa pohon struktur (*Tree View*) di sebelah kiri:
   - Pastikan terdapat elemen `<Schema name="AdventureWorksOnlineSales">`.
   - Pastikan terdapat Shared Dimension `<Dimension name="Waktu">` dengan ikon jam (TimeDimension).
   - Pastikan terdapat `<Cube name="OnlineSalesCube">`.
   - Di dalam Cube, pastikan `<DimensionUsage name="Waktu">` terpasang rapi.
   - Periksa 6 dimensi lainnya (`Produk`, `Pelanggan`, `Wilayah`, `Promosi`, `Mata Uang`, `Metode Kirim`).
   - Periksa bagian `<Measures>` (5 Base Measures dan 2 Calculated Members).
4. **Cek Validasi (*Zero Red Elements*):**
   - Perhatikan tidak boleh ada teks atau tanda seru merah pada ikon mana pun.
   - Jika semua berwarna hitam/normal, artinya **skema kubus 100% valid dan memenuhi Kriteria 1 Dosen**!
5. **Ambil Tangkapan Layar (Screenshot 1):**
   - Ambil screenshot seluruh jendela Schema Workbench yang memperlihatkan pohon skema terbuka tanpa tanda merah.
   - Simpan berkas gambar ke: `bukti/olap/01-schema-workbench-validasi.png`.

---

### Langkah 4: Cara Menjalankan Kueri MDX di Schema Workbench
Untuk menguji kueri MDX langsung di dalam Schema Workbench:
1. Klik menu **Tools** &rarr; **MDX Query...** (atau klik ikon kueri MDX di toolbar atas).
2. Jendela pop-up editor MDX akan muncul.
3. Buka file kueri kita: [`olap/query.mdx`](file:///d:/SEMESTER%207/DWO/FINAL%20PROJECT/adventureworks-online-sales-dw/olap/query.mdx).
4. Salin salah satu kueri MDX, misalnya **Kueri PB-01**:
   ```mdx
   SELECT
     {[Measures].[Sales Amount], [Measures].[Order Quantity], [Measures].[Distinct Orders], [Measures].[Average Order Value]} ON COLUMNS,
     NON EMPTY [Waktu].[Tahun].Members ON ROWS
   FROM [OnlineSalesCube]
   ```
5. Tempelkan ke editor MDX di PSW, lalu klik tombol **Execute** (ikon petir hijau).
6. Hasil tabel data multidimensi akan muncul di panel bawah (menampilkan baris tahun 2011 s.d. 2014, volume penjualan, unit, dan AOV).

---

### Langkah 5: Mengambil Tangkapan Layar (Screenshot) Bukti MDX vs SQL
Untuk memenuhi **Kriteria 6 Checklist Pekan 14 (Bukti MDX sama dengan SQL)**:
1. **Untuk Setiap Kueri (PB-01 s.d. PB-05):**
   - **Screenshot Kueri MDX:** Ambil tangkapan layar jendela eksekusi MDX di Schema Workbench yang menampilkan teks kueri dan hasil tabelnya.
   - **Screenshot Kueri SQL:** Buka phpMyAdmin atau MySQL Workbench, jalankan kueri SQL pembanding yang ada di [`sql/pengujian/pengujian-olap-mdx-vs-sql.sql`](file:///d:/SEMESTER%207/DWO/FINAL%20PROJECT/adventureworks-online-sales-dw/sql/pengujian/pengujian-olap-mdx-vs-sql.sql), dan ambil tangkapan layar hasilnya.
2. Simpan tangkapan layar ke folder `bukti/olap/` dengan penamaan terstruktur:
   - `bukti/olap/mdx-pb01-tren-penjualan.png` & `bukti/olap/sql-pb01-tren-penjualan.png`
   - `bukti/olap/mdx-pb02-kategori-produk.png` & `bukti/olap/sql-pb02-kategori-produk.png`
   - `bukti/olap/mdx-pb03-top10-pelanggan-vip.png` & `bukti/olap/sql-pb03-top10-pelanggan-vip.png`
   - `bukti/olap/mdx-pb04-penjualan-wilayah.png` & `bukti/olap/sql-pb04-penjualan-wilayah.png`
   - `bukti/olap/mdx-pb05-distribusi-promosi.png` & `bukti/olap/sql-pb05-distribusi-promosi.png`
3. Setelah gambar disimpan, tautkan di [`laporan/pekan-14.md`](file:///d:/SEMESTER%207/DWO/FINAL%20PROJECT/adventureworks-online-sales-dw/laporan/pekan-14.md).

---

### Langkah 6: Troubleshooting Kendala Umum OLAP

| Gejala Error | Penyebab Utama | Solusi Konkret |
|---|---|---|
| `ClassNotFoundException: com.mysql.cj.jdbc.Driver` | Driver JDBC MySQL belum ada di folder lib PSW. | Unduh `mysql-connector-j-8.x.jar`, masukkan ke folder `schema-workbench/lib/`, lalu restart `workbench.bat`. |
| `Communications link failure / Connection refused` | Layanan MySQL di XAMPP belum aktif atau port bukan 3306. | Buka XAMPP Control Panel, pastikan tombol **Start** pada modul MySQL berwarna hijau (Port 3306). |
| Elemen Bertanda Merah pada Tabel/Kolom di PSW | PSW tidak menemukan tabel/kolom yang dicari di database. | Pastikan database yang dipilih di koneksi adalah `adventureworks_dw`, bukan database lain. |
| Bulan Muncul Urut Abjad (*Agustus, April, ...*) | Level Bulan belum memiliki atribut `ordinalColumn`. | Di `olap/schema.xml`, pastikan level Bulan memiliki `ordinalColumn="bulan"` (sudah terpasang di skema kita). |
| MDX Error: `Hierarchy '[Waktu]' has more than one hierarchy` | Format sintaks penamaan hierarki SSAS vs Mondrian legacy. | Pastikan file `mondrian.properties` di folder PSW menyetel `mondrian.olap.SsasCompatibleNaming=false`. |

---

## 4. Panduan Menuju Pekan 15: Integrasi Backend & Live Dashboard

Setelah Pekan 14 disetujui sponsor, fokus Pekan 15 adalah membuat dashboard kita hidup (*live data* dari database).

### Arsitektur Backend Ringan yang Disarankan:
Gunakan Node.js (Express) atau Python (Flask):

```
[Browser: wireframe-dashboard.html] 
        │
        │ HTTP GET /api/kpi/summary
        ▼
[Backend Server: server.js / app.py] (Port 5000)
        │
        │ SELECT line_total FROM fact_online_sales ...
        ▼
[Database DW: MySQL adventureworks_dw]
```

### Langkah Kerja Pekan 15:
1. **Membuat File Backend (`server/app.py` atau `server/server.js`):**
   - Buat 5 endpoint REST API utama sesuai spesifikasi yang sudah kita dokumentasikan di [`docs/wireframe-dashboard.md`](file:///d:/SEMESTER%207/DWO/FINAL%20PROJECT/adventureworks-online-sales-dw/docs/wireframe-dashboard.md):
     - `GET /api/kpi/summary?year=...&region=...&cat=...`
     - `GET /api/trends/monthly?year=...`
     - `GET /api/products/ranking`
     - `GET /api/regions/sales`
     - `GET /api/promotions/details`
2. **Menghubungkan Frontend Dashboard:**
   - Ubah pembacaan data statis `DW_SLICES` di `dashboard/wireframe-dashboard.html` dengan pemanggilan `fetch('http://localhost:5000/api/...')`.
3. **Menguji Ekspor CSV Live:**
   - Tombol Ekspor CSV yang sudah kita buat akan otomatis menarik seluruh data terbaru dari respons API tersebut.

---

## 5. Panduan Menuju Presentasi Akhir (Pekan 16 / Final Review)

### 5.1 Susunan Slide Presentasi Eksekutif (10–12 Slide)
Slide presentasi akhir harus fokus pada nilai bisnis dan pembuktian teknis yang padat:

* **Slide 1: Judul Proyek & Identitas Tim** (Nama Proyek Penjualan Online AdventureWorks, Anggota Kelompok 2 & Peran).
* **Slide 2: Latar Belakang & 7 Pertanyaan Bisnis (PB-01 s.d. PB-07)** (Masalah bisnis yang dipecahkan).
* **Slide 3: Arsitektur Data Warehouse Menyeluruh** (Diagram alur: Sumber OLTP &rarr; Staging &rarr; Star Schema V2 DW &rarr; OLAP Mondrian &rarr; Dashboard).
* **Slide 4: Profiling Data Sumber & Temuan Kunci** (Volume 60.398 baris, keunikan order, isu kurs 53,73% tanpa rate).
* **Slide 5: Pemodelan Dimensional (Star Schema V2 & SCD Tipe 2)** (Tabel fakta, 7 dimensi, dan pembuktian SCD2 pada riwayat harga pokok produk).
* **Slide 6: Pipeline ETL & Orkestrasi PDI** (Alur `job_utama.kjb`, penanganan NULL `-1`, dan bukti idempotensi run 2x).
* **Slide 7: Otomasi Terminal CLI (Kitchen Script)** (Bukti eksekusi otomatis tanpa GUI di server).
* **Slide 8: Desain Kubus OLAP & Formula Calculated Members** (Shared dimension waktu via `DimensionUsage`, perhitungan AOV dan harga unit).
* **Slide 9: Pembuktian Rekonsiliasi Kueri MDX vs SQL** (Tabel angka 100% cocok Rp 0 selisih pada PB-01 s.d. PB-05).
* **Slide 10: Demo Dashboard Analitis Interaktif** (Tangkapan layar dashboard, filter live, modal 10 wilayah, 10 VIP, dan ekspor CSV).
* **Slide 11: Kendala, Keputusan Desain, & Pembelajaran (*Lessons Learned*)** (Penjelasan `SalesPersonID` NULL, audit kurs).
* **Slide 12: Kesimpulan & Penutup** (Daftar deliverable yang diserahkan dan ucapan terima kasih).

---

### 5.2 Pembagian Peran Presentasi Tim Kelompok 2

| Anggota Tim | Peran Presentasi | Bagian Materi yang Dipresentasikan |
|---|---|---|
| **Dea Kusuma Ningrum** | *Presenter 1 (Opening & Overview)* | Pembukaan, Latar Belakang Bisnis, 7 Pertanyaan Bisnis, Manajemen Proyek, dan Kesimpulan Akhir. |
| **Siti Anisa Safitri** | *Presenter 2 (Dimensional Modeling)* | Desain Star Schema V2, Grain Fakta (60.398 baris), Bus Matrix, dan Kamus Data 7 Dimensi. |
| **Fivediniar Edra Primaulidina** | *Presenter 3 (ETL & Automation)* | Alur Transformasi PDI, Staging Layer, Logika SCD Tipe 2, Master Job, dan Demo CLI Kitchen di Terminal. |
| **Haura Taqiya Azza Nabila** | *Presenter 4 (OLAP & MDX)* | Skema Kubus Mondrian PSW, DimensionUsage Waktu, Formula Calculated Members (AOV), dan Demo Eksekusi Kueri MDX. |
| **Alifa Zuriyatul Haq** | *Presenter 5 (Quality & Dashboard)* | Pembuktian Rekonsiliasi MDX vs SQL (Rp 0 Selisih), Demo Dashboard Interaktif, Fitur Ekspor CSV, dan Tanya Jawab. |

---

### 5.3 Skenario Alur Demo Langsung (*Live Demo*) di Hadapan Dosen
Agar demo berjalan lancar dan memukau dosen penguji, ikuti urutan berikut:
1. **Tahap 1: Tunjukkan Database Sumber (`adventureworks`)**
   - Buka phpMyAdmin, perlihatkan tabel `sales_salesorderheader` dengan filter `OnlineOrderFlag = 1` (27.659 baris).
2. **Tahap 2: Jalankan Pipeline ETL via Terminal (Kitchen CLI)**
   - Buka terminal PowerShell, jalankan `Kitchen.bat /file:etl/job_utama.kjb /level:Basic`.
   - Tunjukkan log eksekusi berstatus `Finished with success` (bebas error).
3. **Tahap 3: Tunjukkan Database Target (`adventureworks_dw`)**
   - Perlihatkan data telah terisi sempurna di `fact_online_sales` (tepat 60.398 baris).
4. **Tahap 4: Tunjukkan Skema & Kueri OLAP di Pentaho Schema Workbench**
   - Buka `olap/schema.xml` di PSW, tunjukkan tidak ada elemen merah.
   - Buka MDX Query Runner, jalankan Kueri PB-01 dan PB-02, bandingkan dengan query SQL di phpMyAdmin untuk membuktikan angka sama persis.
5. **Tahap 5: Buka Dashboard Interaktif di Browser**
   - Buka `wireframe-dashboard.html`, lakukan klik filter Tahun (2011 s.d. 2014) dan Wilayah.
   - Buka Modal *Top 10 Pelanggan VIP* dan Modal *10 Wilayah Pemasaran*.
   - Klik tombol **Ekspor CSV** untuk membuktikan laporan analitis 7 bagian terunduh secara instan.

---

### 5.4 Antisipasi Pertanyaan Kritis Dosen & Jawaban Tim

1. **Pertanyaan: *"Mengapa dimensi Sales Person tidak ada di star schema dan kubus kalian?"***
   - **Jawaban Tim:** *"Berdasarkan profiling data pada 27.659 transaksi online (`OnlineOrderFlag = 1`), kolom `SalesPersonID` bernilai NULL 100%. Ini karena transaksi online di AdventureWorks bersifat e-commerce mandiri (self-service) tanpa perantara tenaga sales. Kami sengaja meniadakan dimensi tersebut agar model data efisien dan tidak memuat dimensi kosong."*
2. **Pertanyaan: *"Bagaimana kalian menjamin bahwa job ETL kalian aman jika dijalankan berulang kali (idempotent)?"***
   - **Jawaban Tim:** *"Pada `job_utama.kjb`, kami menyisipkan SQL pembersihan cerdas sebelum load yang mengosongkan tabel fakta dan dimensi transaksi namun tetap mempertahankan anggota default `-1 (Unknown)`. Kami telah menguji eksekusi 2 kali berturut-turut via Kitchen CLI dan membuktikan tidak terjadi duplikasi data sama sekali (tetap 60.398 baris)."*
3. **Pertanyaan: *"Mengapa Dimensi Waktu dibuat di tingkat Schema dan menggunakan DimensionUsage?"***
   - **Jawaban Tim:** *"Sesuai konsep shared/conformed dimension Ralph Kimball dan standar Pentaho Mondrian, mendefinisikan Dimensi Waktu di tingkat Schema memungkinkan dimensi tersebut digunakan bersama oleh berbagai kubus analitik di masa depan tanpa mendefinisikan ulang hierarkinya. Kubus cukup merujuknya menggunakan `<DimensionUsage>`."*
4. **Pertanyaan: *"Bagaimana kalian memastikan urutan bulan di kubus tidak berantakan sesuai abjad?"***
   - **Jawaban Tim:** *"Kami menyematkan atribut `ordinalColumn="bulan"` pada level Bulan di `olap/schema.xml`. Dengan begitu, Mondrian menampilkan nama bulan dari kolom `nama_bulan` namun mengurutkannya berdasarkan angka kalender 1 sampai 12 dari kolom `bulan`."*

---

## 6. Checklist Aksi Mandiri Kelompok (Prioritas Segera)

Gunakan daftar periksa ini untuk memantau tugas anggota kelompok:

- [ ] **Aksi 1:** Haura & Alifa membuka `olap/schema.xml` di PSW dan mengambil screenshot validasi skema hijau ke `bukti/olap/01-schema-workbench-validasi.png`.
- [ ] **Aksi 2:** Jalankan 5 kueri MDX dan SQL pembanding, simpan screenshot-nya ke `bukti/olap/`.
- [ ] **Aksi 3:** Dea memperbarui tautan gambar di `laporan/pekan-14.md` dan mengumpulkan laporan untuk review Pekan 14.
- [ ] **Aksi 4 (Pekan 15):** Fivediniar menyiapkan backend REST API mini untuk menghubungkan database ke dashboard.
- [ ] **Aksi 5 (Pekan 16):** Susun draft slide presentasi final (PPT) berdasarkan Bagian 5 panduan ini.

---

**Disusun oleh:** Kelompok 2 — Tim Data Warehouse Penjualan Online  
**Dokumen Pendukung:** [`docs/wireframe-dashboard.md`](wireframe-dashboard.md) · [`laporan/pekan-14.md`](../laporan/pekan-14.md) · [`olap/query.mdx`](../olap/query.mdx)
