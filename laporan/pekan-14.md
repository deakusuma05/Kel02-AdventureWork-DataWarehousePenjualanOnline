# Laporan Steering Review Pekan 14 — Implementasi Skema Mondrian OLAP, DimensionUsage, Calculated Members, Pengujian Kueri MDX vs SQL Pembanding, dan Kesiapan Dashboard

## Proyek Data Warehouse AdventureWorks — Penjualan Online

**Mata kuliah:** Data Warehouse  
**Program studi:** Sistem Informasi, Fakultas Ilmu Komputer, UPN "Veteran" Jawa Timur  
**Periode:** Semester Ganjil 2026/2027  
**Proses bisnis:** Penjualan Online (*Online Sales* — `OnlineOrderFlag = 1`)  
**Database sumber:** `adventureworks` (MySQL/MariaDB melalui XAMPP, *read-only*)  
**Database target DW:** `adventureworks_dw` (MySQL/MariaDB)  
**Project sponsor:** Dosen pengampu mata kuliah Data Warehouse  
**Status dokumen:** Final — Laporan Progres untuk Steering Review Pekan 14  

---

## 1. Matriks Pemenuhan 8 Kriteria Checklist Pekan 14

Berikut rekapitulasi formal pemenuhan seluruh kriteria penilaian yang ditetapkan oleh dosen pembimbing untuk penugasan Pekan 13 yang dilaporkan pada **Steering Review Pekan 14**:

| No. | Kriteria Penugasan Dosen | Status Pemenuhan | Berkas Bukti & Implementasi |
|:---:|---|:---:|---|
| **1** | `olap/schema.xml` tanpa elemen merah di Schema Workbench. Sesuai tabel desain cube Pekan 10/11. | **100% Selesai** | [`olap/schema.xml`](../olap/schema.xml)<br>Tervalidasi parser XML & skema tabel fisik `fact_online_sales`. |
| **2** | Dimensi Waktu lewat `DimensionUsage`: Didefinisikan di tingkat Schema (*shared dimension*), bukan di dalam cube. | **100% Selesai** | [`olap/schema.xml`](../olap/schema.xml#L22-L34)<br>`<Dimension type="TimeDimension" name="Waktu">` di root `<Schema>` dan dipanggil via `<DimensionUsage name="Waktu" source="Waktu" foreignKey="tanggal_key"/>`. |
| **3** | Bulan urut dengan benar (kronologis kalender 1..12, bukan abjad). | **100% Selesai** | [`olap/schema.xml`](../olap/schema.xml#L31)<br>Menggunakan atribut `ordinalColumn="bulan"` pada level Bulan (`dim_date.bulan`). |
| **4** | Minimal satu *calculated member* (misal margin persen atau harga rata-rata). | **100% Selesai** | [`olap/schema.xml`](../olap/schema.xml#L112-L123)<br>Dua calculated members: `[Measures].[Average Order Value]` dan `[Measures].[Average Unit Price]`. |
| **5** | Minimal 5 kueri MDX di `olap/query.mdx`, masing-masing diberi nomor pertanyaan bisnis. | **100% Selesai** | [`olap/query.mdx`](../olap/query.mdx)<br>Menyediakan 7 kueri lengkap teruji menjawab seluruh PB-01 s.d. PB-07. |
| **6** | Setiap kueri punya SQL pembanding dengan angka yang sama persis. | **100% Selesai** | [`olap/query.mdx`](../olap/query.mdx) & [`sql/pengujian/pengujian-olap-mdx-vs-sql.sql`](../sql/pengujian/pengujian-olap-mdx-vs-sql.sql)<br>Angka cocok 100% pada seluruh kueri. |
| **7** | Selisih dijelaskan jika ada. | **100% Selesai** | Bagian 6 & 7 laporan ini.<br>Kecocokan numerik 100% (selisih = Rp 0,00 dan 0 baris). |
| **8** | Laporan `laporan/pekan-14.md` siap. | **100% Selesai** | Dokumen [`laporan/pekan-14.md`](pekan-14.md) |

---

## 2. Tim dan Pembagian Peran

| No. | Nama | NPM | Peran Utama | Fokus Kontribusi Pekan 13–14 |
|---:|---|---|---|---|
| 1 | Dea Kusuma Ningrum | 23082010048 | Project Manager & Business Analyst | Koordinasi deliverable 8 checklist Pekan 14, sinkronisasi piagam proyek, dan penyusunan laporan progres |
| 2 | Fivediniar Edra Primaulidina | 23082010046 | Data Engineer & ETL Developer | Pemeliharaan konsistensi skema fisik `adventureworks_dw`, verifikasi indeks relasi FK ke tabel fakta, dan automasi skrip SQL pembanding |
| 3 | Siti Anisa Safitri | 23082010045 | Data Warehouse & Dimensional Modeler | Desain skema Mondrian XML, konfigurasi *shared dimension* Waktu, dan implementasi `ordinalColumn="bulan"` |
| 4 | Haura Taqiya Azza Nabila | 23082010165 | OLAP & Dashboard Developer | Rekayasa kueri MDX (PB-01 s.d. PB-07), perumusan formula *calculated members*, pengujian di Pentaho Schema Workbench, dan penyempurnaan wireframe dashboard |
| 5 | Alifa Zuriyatul Haq | 23082010050 | Data Quality, Testing & Documentation | Rekonsiliasi angka MDX vs SQL pembanding, validasi akurasi perhitungan AOV, dan dokumentasi bukti pengujian |

---

## 3. Ringkasan Eksekutif Pekan 14

Pada siklus pengembangan Pekan 13 menuju **Steering Review Pekan 14**, fokus tim Kelompok 2 adalah mewujudkan lapisan analitik multidimensi **Online Analytical Processing (OLAP)** berbasis **Pentaho Schema Workbench (PSW) / Mondrian ROLAP** dan melakukan pengujian kueri **Multi-Dimensional eXpressions (MDX)** terhadap basis data data warehouse `adventureworks_dw`.

Seluruh **8 Kriteria Checklist Penugasan Dosen** telah diselesaikan secara tuntas:

1. **Skema Mondrian Resmi (`olap/schema.xml`):** Dibangun sesuai spesifikasi Star Schema V2 dan desain cube Pekan 10/11. Seluruh tabel dan kolom merujuk langsung ke tabel fisik yang telah terisi data hasil ETL (60.398 baris fakta).
2. **Dimensi Waktu lewat `DimensionUsage`:** Dimensi Waktu didefinisikan secara modular di tingkat `<Schema>` sebagai *shared dimension*, kemudian dihubungkan ke kubus utama melalui elemen `<DimensionUsage name="Waktu" source="Waktu" foreignKey="tanggal_key"/>`.
3. **Pengurutan Bulan Kalender:** Masalah urutan bulan alfabetis diselesaikan tuntas dengan menyematkan atribut `ordinalColumn="bulan"` pada level Bulan, sehingga agregasi bulanan otomatis tersusun urut Januari hingga Desember.
4. **Calculated Members Formal:** Didefinisikan dua anggota terhitung:
   - `[Measures].[Average Order Value]`: Menghitung rasio omzet terhadap transaksi unik `[Sales Amount] / [Distinct Orders]`.
   - `[Measures].[Average Unit Price]`: Menghitung rata-rata harga per unit barang `[Sales Amount] / [Order Quantity]`.
5. **Koleksi 7 Kueri MDX & SQL Pembanding (`olap/query.mdx`):** Disusun 7 paket kueri MDX yang menjawab seluruh 7 Pertanyaan Bisnis resmi (PB-01 s.d. PB-07).
6. **Rekonsiliasi Sempurna (100% Match):** Seluruh hasil kalkulasi kueri MDX telah diverifikasi terhadap kueri SQL pembanding pada DBMS MySQL. Tidak terdapat selisih nilai finansial maupun kuantitas (`$29.358.677,22`, 27.659 pesanan, 60.398 unit).
7. **Penyempurnaan Prototipe Dashboard:** File [`dashboard/wireframe-dashboard.html`](../dashboard/wireframe-dashboard.html) telah diperbarui dengan fitur interaktif *Top 10 Pelanggan VIP (PB-03)*, *Expandable Top 10 Produk (PB-02)*, dan *Ekspor Data CSV*.

---

## 4. Arsitektur Skema Cube Mondrian (`olap/schema.xml`)

### 4.1 Definisi Shared Dimension Waktu
Sesuai instruksi penugasan dosen, dimensi waktu harus didefinisikan di tingkat `<Schema>` agar dapat dimanfaatkan oleh berbagai kubus analitik (*shared/conformed dimension*):

```xml
<Dimension type="TimeDimension" name="Waktu">
  <Hierarchy hasAll="true" allMemberName="Semua Waktu" primaryKey="tanggal_key">
    <Table name="dim_date"/>
    <Level name="Tahun" column="tahun" type="Numeric" uniqueMembers="true" levelType="TimeYears"/>
    <Level name="Semester" column="semester" type="Numeric" uniqueMembers="false" levelType="TimeHalfYears"/>
    <Level name="Kuartal" column="kuartal" type="Numeric" uniqueMembers="false" levelType="TimeQuarters"/>
    <Level name="Bulan" column="nama_bulan" ordinalColumn="bulan" type="String" uniqueMembers="false" levelType="TimeMonths"/>
    <Level name="Tanggal" column="tanggal" type="Date" uniqueMembers="true" levelType="TimeDays"/>
  </Hierarchy>
</Dimension>
```

> **Catatan Teknis Pengurutan Bulan:** Level Bulan menggunakan `column="nama_bulan"` (menampilkan caption nama bulan seperti *Januari*, *Februari*) dan dipasangkan dengan `ordinalColumn="bulan"` (integer 1..12). Hal ini mencegah Mondrian mengurutkan bulan secara alfabetis (*Agustus, April, Desember, ...*).

---

### 4.2 Pemanggilan via `<DimensionUsage>` dan Dimensi Kubus Lainnya
Di dalam elemen `<Cube name="OnlineSalesCube">`, Dimensi Waktu dipanggil menggunakan:

```xml
<DimensionUsage name="Waktu" source="Waktu" foreignKey="tanggal_key"/>
```

Tabel fakta `fact_online_sales` selanjutnya dihubungkan ke 6 dimensi lainnya di dalam kubus:
1. **`Produk` (`foreignKey="product_key"`):** Hierarki `Kategori` $\rightarrow$ `Subkategori` $\rightarrow$ `Produk` (`dim_product`).
2. **`Pelanggan` (`foreignKey="customer_key"`):** Hierarki `Tipe Pelanggan` $\rightarrow$ `Pelanggan` (`dim_customer`).
3. **`Wilayah` (`foreignKey="territory_key"`):** Hierarki `Grup Wilayah` $\rightarrow$ `Negara` $\rightarrow$ `Wilayah` (`dim_territory`).
4. **`Promosi` (`foreignKey="promotion_key"`):** Hierarki `Kategori Promosi` $\rightarrow$ `Tipe Promosi` $\rightarrow$ `Penawaran` (`dim_promotion`).
5. **`Mata Uang` (`foreignKey="currency_key"`):** Hierarki `Mata Uang Asal` $\rightarrow$ `Mata Uang Tujuan` $\rightarrow$ `ID Kurs` (`dim_currency`).
6. **`Metode Kirim` (`foreignKey="ship_method_key"`):** Level `Metode Pengiriman` (`dim_ship_method`).

---

### 4.3 Base Measures dan Calculated Members

#### A. Base Measures (Ukuran Fisik Fakta)
* `[Measures].[Sales Amount]`: `SUM(fact_online_sales.line_total)` — format `$#,##0.00`.
* `[Measures].[Order Quantity]`: `SUM(fact_online_sales.order_qty)` — format `#,##0`.
* `[Measures].[Distinct Orders]`: `COUNT(DISTINCT fact_online_sales.sales_order_id)` — format `#,##0`.
* `[Measures].[Active Customers]`: `COUNT(DISTINCT fact_online_sales.customer_key)` — format `#,##0`.
* `[Measures].[Total Rows]`: `COUNT(fact_online_sales.sales_detail_key)` — format `#,##0`.

#### B. Calculated Members (Ukuran Terhitung)
1. **Average Order Value (AOV / Rata-rata Nilai Pesanan):**
   ```xml
   <CalculatedMember name="Average Order Value" dimension="Measures"
     formula="IIf([Measures].[Distinct Orders] = 0, NULL, [Measures].[Sales Amount] / [Measures].[Distinct Orders])">
     <CalculatedMemberProperty name="FORMAT_STRING" value="$#,##0.00"/>
   </CalculatedMember>
   ```
2. **Average Unit Price (Harga Rata-rata per Unit Terjual):**
   ```xml
   <CalculatedMember name="Average Unit Price" dimension="Measures"
     formula="IIf([Measures].[Order Quantity] = 0, NULL, [Measures].[Sales Amount] / [Measures].[Order Quantity])">
     <CalculatedMemberProperty name="FORMAT_STRING" value="$#,##0.00"/>
   </CalculatedMember>
   ```

---

## 5. Validasi Skema pada Pentaho Schema Workbench (PSW)

Pengujian skema XML [`olap/schema.xml`](../olap/schema.xml) dilakukan dengan memverifikasi kepatuhan DTD Mondrian dan ketiadaan elemen merah (*zero errors*):
- **Koneksi Database:** Terhubung ke driver JDBC MySQL (`com.mysql.cj.jdbc.Driver`) pada skema `adventureworks_dw`.
- **Integritas Metadata:** Seluruh nama tabel (`dim_date`, `dim_product`, `dim_customer`, `dim_territory`, `dim_promotion`, `dim_currency`, `dim_ship_method`, `fact_online_sales`) dan atribut kolom terdeteksi valid secara otomatis oleh Schema Workbench.
- **Status Validasi:** **Lolos Penuh (Tanpa Elemen Merah / 0 Error)**.

---

## 6. Pembuktian Kueri MDX vs SQL Pembanding (`olap/query.mdx`)

Berikut adalah perbandingan hasil eksekusi kueri MDX terhadap SQL pembanding pada masing-masing pertanyaan bisnis:

### 6.1 PB-01: Tren Penjualan Online Tahunan & Bulanan
* **Tujuan Bisnis:** Menganalisis pertumbuhan omzet, volume unit, transaksi, dan AOV per tahun transaksi.
* **Kueri MDX:**
  ```mdx
  SELECT
    {[Measures].[Sales Amount], [Measures].[Order Quantity], [Measures].[Distinct Orders], [Measures].[Average Order Value]} ON COLUMNS,
    NON EMPTY [Waktu].[Tahun].Members ON ROWS
  FROM [OnlineSalesCube];
  ```
* **Kueri SQL Pembanding:**
  ```sql
  SELECT 
    d.tahun,
    COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
    SUM(f.order_qty) AS order_quantity,
    ROUND(SUM(f.line_total), 2) AS sales_amount,
    ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS average_order_value
  FROM fact_online_sales f
  JOIN dim_date d ON f.tanggal_key = d.tanggal_key
  GROUP BY d.tahun ORDER BY d.tahun;
  ```
* **Hasil Rekonsiliasi Angka (Kecocokan 100%):**

  | Tahun | Hasil MDX: Sales Amount | Hasil SQL: sales_amount | Hasil MDX: Distinct Orders | Hasil SQL: distinct_orders | Hasil MDX: AOV | Hasil SQL: AOV | Evaluasi Selisih |
  |:---:|---:|---:|---:|---:|---:|---:|:---:|
  | **2011** | $3.863.120,21 | $3.863.120,21 | 1.201 | 1.201 | $3.216,59 | $3.216,59 | **Rp 0,00 (Cocok)** |
  | **2012** | $6.390.599,95 | $6.390.599,95 | 2.743 | 2.743 | $2.329,78 | $2.329,78 | **Rp 0,00 (Cocok)** |
  | **2013** | $10.732.127,33 | $10.732.127,33 | 12.584 | 12.584 | $852,84 | $852,84 | **Rp 0,00 (Cocok)** |
  | **2014** | $8.372.829,73 | $8.372.829,73 | 11.131 | 11.131 | $752,21 | $752,21 | **Rp 0,00 (Cocok)** |
  | **TOTAL** | **$29.358.677,22** | **$29.358.677,22** | **27.659** | **27.659** | **$1.061,45** | **$1.061,45** | **Rp 0,00 (Cocok)** |

---

### 6.2 PB-02: Kategori Produk dengan Penjualan Terbesar
* **Tujuan Bisnis:** Mengidentifikasi kategori produk dengan kontribusi penjualan tertinggi beserta rata-rata harga per unit barang.
* **Kueri MDX:**
  ```mdx
  SELECT
    {[Measures].[Sales Amount], [Measures].[Order Quantity], [Measures].[Average Unit Price]} ON COLUMNS,
    ORDER([Produk].[Kategori].Members, [Measures].[Sales Amount], BDESC) ON ROWS
  FROM [OnlineSalesCube];
  ```
* **Kueri SQL Pembanding:**
  ```sql
  SELECT 
    p.category_name AS kategori,
    ROUND(SUM(f.line_total), 2) AS sales_amount,
    SUM(f.order_qty) AS order_quantity,
    ROUND(SUM(f.line_total) / SUM(f.order_qty), 2) AS average_unit_price
  FROM fact_online_sales f
  JOIN dim_product p ON f.product_key = p.product_key
  GROUP BY p.category_name ORDER BY sales_amount DESC;
  ```
* **Hasil Rekonsiliasi Angka (Kecocokan 100%):**

  | Kategori Produk | Nilai Penjualan (MDX) | Nilai Penjualan (SQL) | Volume Unit | Avg Unit Price (MDX) | Avg Unit Price (SQL) | Status |
  |---|---:|---:|---:|---:|---:|:---:|
  | **1. Bikes** | $28.318.144,65 | $28.318.144,65 | 15.205 | $1.862,42 | $1.862,42 | **Cocok 100%** |
  | **2. Accessories** | $700.759,96 | $700.759,96 | 36.092 | $19,42 | $19,42 | **Cocok 100%** |
  | **3. Clothing** | $339.772,61 | $339.772,61 | 9.101 | $37,33 | $37,33 | **Cocok 100%** |
  | **TOTAL** | **$29.358.677,22** | **$29.358.677,22** | **60.398** | **$486,09** | **$486,09** | **Cocok 100%** |

---

### 6.3 PB-03: Top 10 Pelanggan VIP Kontributor Terbesar
* **Tujuan Bisnis:** Mengidentifikasi pelanggan berulang dengan nilai belanja online tertinggi (> $10.000).
* **Kueri MDX:**
  ```mdx
  SELECT
    {[Measures].[Sales Amount], [Measures].[Distinct Orders], [Measures].[Average Order Value]} ON COLUMNS,
    TOPCOUNT([Pelanggan].[Pelanggan].Members, 10, [Measures].[Sales Amount]) ON ROWS
  FROM [OnlineSalesCube];
  ```
* **Kueri SQL Pembanding:**
  ```sql
  SELECT 
    c.customer_id,
    c.customer_name,
    ROUND(SUM(f.line_total), 2) AS sales_amount,
    COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
    ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS average_order_value
  FROM fact_online_sales f
  JOIN dim_customer c ON f.customer_key = c.customer_key
  GROUP BY c.customer_id, c.customer_name
  ORDER BY sales_amount DESC LIMIT 10;
  ```
* **Hasil Rekonsiliasi Angka (Kecocokan 100%):**

  | Peringkat | ID & Nama Pelanggan | Belanja MDX | Belanja SQL | Pesanan | AOV MDX | AOV SQL | Status |
  |:---:|---|---:|---:|:---:|---:|---:|:---:|
  | **#1** | 12301 — Nichole Nara | $13.295,38 | $13.295,38 | 5 | $2.659,08 | $2.659,08 | **Sama** |
  | **#2** | 12132 — Kaitlyn J Henderson | $13.294,27 | $13.294,27 | 5 | $2.658,85 | $2.658,85 | **Sama** |
  | **#3** | 12308 — Margaret He | $13.269,27 | $13.269,27 | 5 | $2.653,85 | $2.653,85 | **Sama** |
  | **#4** | 12131 — Randall M Dominguez | $13.265,99 | $13.265,99 | 5 | $2.653,20 | $2.653,20 | **Sama** |
  | **#5** | 12300 — Adriana L Gonzalez | $13.242,70 | $13.242,70 | 5 | $2.648,54 | $2.648,54 | **Sama** |
  | **#6** | 12321 — Rosa K Hu | $13.215,65 | $13.215,65 | 5 | $2.643,13 | $2.643,13 | **Sama** |
  | **#7** | 12124 — Brandi D Gill | $13.195,64 | $13.195,64 | 5 | $2.639,13 | $2.639,13 | **Sama** |
  | **#8** | 12307 — Brad She | $13.173,19 | $13.173,19 | 5 | $2.634,64 | $2.634,64 | **Sama** |
  | **#9** | 12296 — Francisco A Sara | $13.164,64 | $13.164,64 | 5 | $2.632,93 | $2.632,93 | **Sama** |
  | **#10** | 11433 — Maurice M Shan | $12.909,67 | $12.909,67 | 6 | $2.151,61 | $2.151,61 | **Sama** |

---

### 6.4 PB-04: Penjualan per Grup Wilayah
* **Tujuan Bisnis:** Mengetahui wilayah geografis dengan kontribusi omzet terbesar.
* **Kueri MDX:**
  ```mdx
  SELECT
    {[Measures].[Sales Amount], [Measures].[Distinct Orders], [Measures].[Average Order Value]} ON COLUMNS,
    ORDER([Wilayah].[Grup Wilayah].Members, [Measures].[Sales Amount], BDESC) ON ROWS
  FROM [OnlineSalesCube];
  ```
* **Kueri SQL Pembanding:**
  ```sql
  SELECT 
    t.territory_group AS grup_wilayah,
    ROUND(SUM(f.line_total), 2) AS sales_amount,
    COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
    ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS average_order_value
  FROM fact_online_sales f
  JOIN dim_territory t ON f.territory_key = t.territory_key
  GROUP BY t.territory_group ORDER BY sales_amount DESC;
  ```
* **Hasil Rekonsiliasi Angka (Kecocokan 100%):**
  - **North America:** MDX `$11.367.634,37` = SQL `$11.367.634,37` (12.942 Pesanan, AOV `$878,35`).
  - **Pacific:** MDX `$9.061.000,58` = SQL `$9.061.000,58` (6.718 Pesanan, AOV `$1.348,76`).
  - **Europe:** MDX `$8.930.042,26` = SQL `$8.930.042,26` (7.999 Pesanan, AOV `$1.116,39`).

---

### 6.5 PB-05: Penjualan Berdasarkan Program Promosi
* **Tujuan Bisnis:** Mengukur distribusi penjualan menurut penawaran diskon promosi.
* **Kueri MDX:**
  ```mdx
  SELECT
    {[Measures].[Sales Amount], [Measures].[Order Quantity], [Measures].[Total Rows]} ON COLUMNS,
    ORDER([Promosi].[Penawaran].Members, [Measures].[Sales Amount], BDESC) ON ROWS
  FROM [OnlineSalesCube];
  ```
* **Kueri SQL Pembanding:**
  ```sql
  SELECT 
    p.special_offer_id,
    p.description AS program_promosi,
    p.discount_pct,
    ROUND(SUM(f.line_total), 2) AS sales_amount,
    SUM(f.order_qty) AS order_quantity,
    COUNT(*) AS total_rows
  FROM fact_online_sales f
  JOIN dim_promotion p ON f.promotion_key = p.promotion_key
  GROUP BY p.special_offer_id, p.description, p.discount_pct ORDER BY sales_amount DESC;
  ```
* **Hasil Rekonsiliasi Angka (Kecocokan 100%):**
  - **No Discount (0%):** $27.307.607,08 | 58.247 Unit (58.247 baris).
  - **Volume Discount 11 to 14 (2%):** $2.005.230,23 | 2.118 Unit (2.118 baris).
  - **Touring-1000 Promotion (20%):** $30.992,91 | 13 Unit (13 baris).
  - **Touring-3000 Promotion (15%):** $14.847,00 | 20 Unit (20 baris).

---

## 7. Analisis Pertanyaan Bisnis yang Belum Bisa Dijawab Cube

Berdasarkan evaluasi terhadap piagam proyek dan data operasional sumber, tim mencatat satu kondisi domain bisnis:

1. **Analisis Sales Person / Tenaga Penjual:**
   - **Kondisi:** Pada tabel operasional `sales_salesorderheader`, kolom `SalesPersonID` bernilai `NULL` pada seluruh 27.659 pesanan online (`OnlineOrderFlag = 1`).
   - **Alasan Bisnis:** Seluruh transaksi penjualan online dilakukan secara mandiri oleh pelanggan melalui portal web tanpa perantara tenaga penjual (*self-service e-commerce*).
   - **Keputusan Desain:** Dimensi `dim_sales_person` sengaja tidak disertakan pada kubus penjualan online demi menjaga kepatuhan grain dan efisiensi model data (tidak memuat dimensi kosong).

2. **Perhitungan Margin Keuntungan Bersih (*Net Profit Margin*):**
   - **Kondisi:** Informasi biaya produksi (*standard cost*) dilacak pada `dim_product` melalui SCD Tipe 2, namun biaya operasional pengiriman riil (*freight*) berada pada tingkat header pesanan, bukan detail transaksi.
   - **Status di Kubus:** Kubus saat ini berfokus pada *Gross Sales Amount*, *Order Quantity*, dan *Average Order Value*. Analisis margin bersih disiapkan untuk fase penyempurnaan data mart lanjutan.

---

## 8. Kesiapan Menuju Dashboard Interaktif (Pekan 14–15)

Prototipe wireframe dashboard interaktif pada [`dashboard/wireframe-dashboard.html`](../dashboard/wireframe-dashboard.html) dan dokumentasinya pada [`docs/wireframe-dashboard.md`](../docs/wireframe-dashboard.md) telah berada dalam kondisi siap produksi (*production-ready*):
* **Format:** Mengikuti standar desain dosen (*Urutan baca: Ringkasan di atas, Tren di tengah, Rincian di bawah; 5-7 visual per halaman*).
* **Integrasi Data Aktual:** Seluruh 80 irisan data dimensional terintegrasi secara dinamis via JavaScript `DW_SLICES` mencakup interaksi filter Tahun, Wilayah, dan Kategori Produk.
* **Fitur Analitik Baru:**
  1. Tombol *Ekspor CSV* untuk mengunduh rekapitulasi data aktif.
  2. Modal interaktif *Top 10 Pelanggan VIP (PB-03)*.
  3. Tombol toggle dinamis untuk memperluas *Top 10 Produk Terlaris (PB-02)*.
* **Kesiapan Endpoint API:** Tab *Spesifikasi Kueri JSON* telah merinci kueri SQL dan struktur JSON response yang dibutuhkan untuk backend kecil pada Pekan 15.

---

## 9. Kesimpulan dan Rencana Pekan Berikutnya

Seluruh deliverable tugas Pekan 13 yang dilaporkan pada **Steering Review Pekan 14** telah terselesaikan 100% dan terverifikasi secara formal:
1. `olap/schema.xml` selesai dengan ketaatan penuh pada aturan `DimensionUsage` dan `ordinalColumn="bulan"`.
2. Dua *calculated members* aktif dan menghasilkan nilai AOV serta harga rata-rata yang terbukti akurat.
3. Tujuh kueri MDX tersimpan di `olap/query.mdx` dan terbukti menghasilkan angka yang sama persis dengan SQL pembanding (selisih Rp 0,00).
4. Prototipe dashboard dan dokumentasi wireframe siap dihubungkan ke backend database.

**Rencana Tindak Lanjut Pekan 15:**
* Membangun server backend ringan (Node.js Express / Python Flask) untuk melayani endpoint REST API data warehouse.
* Menghubungkan visualisasi dashboard langsung ke basis data `adventureworks_dw`.
* Menyiapkan pengujian end-to-end dashboard dan penyusunan laporan akhir proyek data warehouse.

---

**Disusun oleh:** Kelompok 2 — Tim Data Warehouse Penjualan Online  
**Tanggal:** 24 November 2026  
**Status Pengesahan:** Siap untuk Steering Review Pekan 14.
