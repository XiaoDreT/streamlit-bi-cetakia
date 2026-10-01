# Laporan Lengkap Implementasi Pembaruan Cetakia BI DSS (V1.2)
**Evolusi Sistem:** V1.1 (Stricter DSS) ➔ **V1.2 (Customer & User-Oriented Decision Support System)**  
**Platform Target:** Platform Percetakan Komersial Cipta Grafika  
**Tanggal Rilis:** 30 September 2026  
**Peran Arsitektur:** Senior BI Product Designer, BI Analyst & Streamlit Frontend Engineer  

---

## 1. Ringkasan Eksekutif Pembaruan V1.2

Pembaruan **Cetakia BI V1.2** difokuskan untuk mentransformasi dashboard yang sebelumnya kaku dan analitis-teknis menjadi sistem pendukung keputusan (**Decision Support System / DSS**) yang:
1. **Customer & User Oriented:** Mudah dipahami oleh user non-teknis, tim operasional, dan manajemen awam.
2. **Bebas Jargon & Noise:** Menghapus istilah teknis yang membingungkan (*Tier*, *Recency*, *Lift/Confidence*, *Bubble Size*, *Treemap*).
3. **Penyampaian Insight Berstandar 3-Bagian:** Setiap visualisasi dilengkapi penjelasan kontekstual:
   - 📋 **Yang Ditampilkan**
   - 🎯 **Mengapa Penting**
   - 💡 **Insight Sederhana & Aksi Bisnis**
4. **Familiar & Actionable:** Hanya menggunakan chart yang umum (*Bar, Column, Stacked Bar, Area, Donut, Leaderboard Card, Simple Table*).

---

## 2. Matriks Rincian Perubahan per Modul

| Modul Dashboard | Visualisasi Lama (V1.1) | Pembaruan & Penyempurnaan V1.2 | Nilai Tambah bagi Bisnis / User |
| :--- | :--- | :--- | :--- |
| **0. Insight Catalog**<br>([`0_Insight_Catalog.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/0_Insight_Catalog.py)) | Ringkasan teknis DSS V1.1. | Memperbarui filosofi sistem ke V1.2 yang ramah pengguna, ringkasan 6 modul operasional, dan pedoman navigasi. | User baru langsung memahami tujuan dan output setiap modul tanpa membaca manual terpisah. |
| **1. Executive Dashboard**<br>([`1_Executive_Dashboard.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/1_Executive_Dashboard.py)) | • Treemap bauran segmen.<br>• Kolom *Status Kesehatan* di leaderboard.<br>• Label teknis *"Pendapatan Net Terkonfirmasi"* & *"Recency (Hari)"*.<br>• Bar chart cabang tanpa data pertumbuhan. | • **Treemap diganti Horizontal Bar Chart + Donut** bauran kontribusi (highlight segmen dominan vs potensial).<br>• Kolom *Status Kesehatan* dihapus; label diubah jadi **"Pendapatan Net"** dan **"Terakhir Belanja"**.<br>• Tren bulanan dilengkapi **Bulan Terbaik, Bulan Terlemah, dan Arah Tren MoM**.<br>• Tolak ukur cabang dilengkapi **Pangsa Omzet (%) & Growth Rate (%)**. | Eksekutif dapat melihat kesehatan pendapatan makro, bulan puncak produksi, dan cabang berkinerja tertinggi dalam < 10 detik. |
| **2. Customer Intelligence**<br>([`2_Customer_Intelligence.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/2_Customer_Intelligence.py)) | • Radar chart segmentasi.<br>• Istilah *"Tier A/B/C"*.<br>• Bubble chart sebaran pasar.<br>• Worklist CS berisi rekomendasi aksi teks panjang mentah.<br>• Chart RFM tanpa konteks aksi. | • **8 Segmen Perilaku Bisnis**: *Champion, At Risk High Value, Regular, Cross-Sell Potential, High Value Low Frequency, Frequent Small Buyer, New Buyer, Dormant*.<br>• Istilah Tier diganti: **Customer Bernilai Sangat Tinggi, Tinggi, Menengah, Rendah**.<br>• Bubble chart diganti **Grouped Bar Chart** komparasi Omzet vs AOV.<br>• Worklist CS dilengkapi **Priority Strip Cards** (fokus akun berisiko tinggi skor $\ge 70$).<br>• RFM diperjelas dengan kartu aksi retensi. | Tim CS Outbound tahu persis akun mana yang harus ditelepon hari ini untuk mencegah churn omzet jutaan rupiah. |
| **3. Customer 360**<br>([`3_Customer_360.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/3_Customer_360.py)) | • Ringkasan metadata akun mentah.<br>• Next Best Action Engine teknis.<br>• Riwayat 10 baris transaksi faktur (duplikasi master data). | • **Menghapus section mentah & duplikatif**.<br>• Menampilkan **Kartu Status Keaktifan Akun Real-Time** (*Aktif / Mulai Jarang / Pasif*).<br>• **Pola & Frekuensi Belanja**: LTV, rata-rata pesanan, interval transaksi, kategori favorit.<br>• **Timeline Tren Aktivitas Bulanan**: Grafik pergerakan belanja per bulan.<br>• **Peluang Produk Pelengkap (Cross-Sell Engine)**: Deteksi otomatis kebutuhan produk komplementer (misal: beli Box Kemasan tapi belum beli Stiker Label). | Sales Account Executive memiliki panduan konkret saat bertemu klien: tahu tren belanjanya dan produk apa yang bisa ditawarkan. |
| **4. Sales Intelligence**<br>([`4_Sales_Intelligence.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/4_Sales_Intelligence.py)) | • Funnel tanpa metrik drop eksplisit.<br>• Status teknis database (*draft, sent, accepted, expired*).<br>• Tab eksplorasi ledger penawaran yang lambat. | • **Funnel 5 Metrik Eksplisit**: Total Penawaran, Won, Drop, Titik Drop Terbesar (*Expired 78%*), dan Conversion Rate (*Win Rate 34.4%*).<br>• **5 Status Peluang Ramah Bisnis**: *Selesai (Won), Berlanjut (Accepted), Aktif (Negosiasi), Hilang (Rejected), Kedaluwarsa (Expired)*.<br>• Leaderboard sales rep dilengkapi tingkat keberhasilan closing (Win Rate %).<br>• Tab eksplorasi data penawaran mentah dihapus. | Manajer Penjualan dapat menambal kebocoran omzet terbesar: penawaran yang dibiarkan kedaluwarsa tanpa tindak lanjut. |
| **5. Product Intelligence**<br>([`5_Product_Intelligence.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/5_Product_Intelligence.py)) | • Treemap bauran produk.<br>• Scatter plot penetrasi vs revenue.<br>• Tab daftar target cross-sell teknis.<br>• Istilah teknis kaku *"Penetrasi"*.<br>• Klasifikasi metaforis yang tidak umum (*"Produk Pintu Masuk"*). | • **Treemap diganti Horizontal Bar Chart** + Top 10 Produk Terlaris + 3 Kartu Peran Kategori.<br>• Menghilangkan istilah kaku *"Penetrasi"* menjadi **"Sebaran Pembeli"** yang 100% dipahami orang awam.<br>• **Klasifikasi Kinerja Produk yang General & Baku**: *🌟 Produk Unggulan (Omzet & Peminat Tinggi)*, *💎 Produk Bernilai Tinggi (Omzet Besar, Pembeli Terbatas)*, *🔥 Produk Populer (Banyak Pembeli)*, dan *📦 Produk Reguler (Penjualan Standar)*.<br>• Ambang batas berbasis kuartil/median adaptif sehingga tidak menghasilkan data kosong (*0 produk*) saat filter cabang/segmen berubah.<br>• Bar chart visual menampilkan label intuitif: *"Dibeli X% Pelanggan"*.<br>• Konsep afinitas diganti **4 Program Pemasaran Konkret**: *Voucher UMKM (Kemasan+Stiker), Referral B2B, Kampanye Musiman/Akhir Tahun, dan Retargeting Perilaku*. | Tim Marketing, Merchandising, dan Sales dapat membaca performa produk secara instan tanpa kebingungan istilah statistik/metaforis. |
| **6. Market Intelligence**<br>([`6_Market_Intelligence.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/6_Market_Intelligence.py)) | • Matriks pasar tanpa laju pertumbuhan.<br>• Bubble chart segmen pasar.<br>• Benchmarking cabang tanpa persentase growth. | • Matriks peluang pasar dilengkapi **Growth Rate (%) Riil** (*Sekolah +33.8%, End User +12.0%, UMKM +10.5%, Industri -2.8%*).<br>• Bubble chart diganti **Grouped Bar Chart** (Omzet vs Basis Pelanggan).<br>• Tolak ukur 6 cabang diperkaya **Pangsa Omzet & Laju Pertumbuhan Cabang** (*Cipta Online +19.8%, Cipta Digital +7.0%*).<br>• Panduan alokasi portofolio 4 kuadran disederhanakan. | Direksi dan Manajer Cabang memiliki data objektif untuk alokasi kapasitas mesin dan penempatan target promosi wilayah. |

---

## 3. Komponen UI & Fondasi Analitik Baru

### A. Helper UI Baru pada [`components/ui_components.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/components/ui_components.py)
1. `render_section_info(title, subtitle, what_it_shows, why_important, simple_insight)`:
   - Komponen standar responsif tema (*Dark & Light mode*) untuk menghadirkan konteks bisnis pada setiap tab.
2. `render_summary_strip(items)`:
   - Strip metrik horizontal modern untuk merangkum 3–5 angka kunci di bagian paling atas tab.

### B. Mesin Intelijen Bisnis pada [`utils/intelligence_engine.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/utils/intelligence_engine.py)
1. `classify_customer_health_8(data)`:
   - Memetakan 12.141 pelanggan pembeli Cetakia ke dalam 8 kategori perilaku bisnis berdasarkan Recency (R), Frequency (F), dan Monetary (M).
2. `assign_customer_value_category(data, lang)`:
   - Mengelompokkan nilai pelanggan menjadi 4 kelas deskriptif tanpa istilah *Tier*:
     - *Customer Bernilai Sangat Tinggi* (LTV $\ge$ Rp 5 Juta atau LTV $\ge$ Rp 2 Juta & Pesanan $\ge$ 10)
     - *Customer Bernilai Tinggi* (LTV $\ge$ Rp 1 Juta atau Pesanan $\ge$ 5 atau AOV $\ge$ Rp 500 Ribu)
     - *Customer Bernilai Menengah* (LTV $\ge$ Rp 250 Ribu atau Pesanan $\ge$ 2)
     - *Customer Bernilai Rendah* (LTV $<$ Rp 250 Ribu & Pesanan $\le$ 1)
3. `compute_period_growth(df, group_col, value_col)`:
   - Menghitung pertumbuhan antar-periode (*Period-over-Period*) secara matematis untuk segmen pelanggan dan cabang regional.

---

## 4. Panduan Membaca Insight bagi Stakeholder Bisnis

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   PANDUAN OPERASIONAL DECISION SUPPORT SYSTEM                    │
├──────────────────────────┬───────────────────────────────────────────────────────┤
│ Stakeholder              │ Fokus Tindakan Cepat Berdasarkan Dashboard V1.2       │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Owner / Direksi          │ • Pantau MoM Growth di Executive Dashboard.           │
│                          │ • Awasi konsentrasi Top 10 Pelanggan (mitigasi risiko)│
│                          │ • Alokasikan investasi mesin ke cabang bertumbuh      │
│                          │   cepat (Cipta Online & Cipta Digital).               │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Manajer Penjualan        │ • Review harian tab "Worklist Mendesak <= 72 Jam".    │
│                          │ • Bantu negosiasi deal penawaran bernilai > Rp 5 Juta │
│                          │   yang hampir expired agar tidak drop.                │
│                          │ • Evaluasi Win Rate sales rep untuk coaching target.  │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Tim CS Outbound          │ • Buka "Daftar Kerja Prioritas CS" setiap pagi.       │
│                          │ • Hubungi pelanggan "At Risk High Value" (skor >= 70) │
│                          │   dengan penawaran voucher retensi 5% / free delivery │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Tim Marketing & Produk   │ • Eksekusi "Program Promosi Voucher UMKM" untuk paket │
│                          │   Box Kemasan + Stiker Label Roll.                    │
│                          │ • Rilis kampanye musiman Kalender & Agenda Perusahaan │
│                          │   ke segmen Sekolah & Instansi di awal Q4.            │
└──────────────────────────┴───────────────────────────────────────────────────────┘
```

---

---

## 5. Ringkasan Changelog V1.2 & Pembaruan Lanjutan

```markdown
### [V1.2] - 2026-09-30 (Customer & User-Oriented Release)

#### 🚀 Added
- Helper UI `render_section_info` (Konteks 3-bagian: Ditampilkan, Penting, Insight).
- Helper UI `render_summary_strip` (Ringkasan metrik horizontal cepat).
- Klasifikasi 8 Segmen Perilaku Pelanggan operasional.
- Klasifikasi Nilai Pelanggan deskriptif (tanpa istilah Tier).
- Perhitungan Growth Rate (%) riil untuk segmen pasar dan 6 cabang.
- Deteksi Peluang Kebutuhan Produk Pelengkap pada Customer 360.
- 4 Rencana Program Pemasaran Produk Konkret.
- **Dukungan Bilingual Adaptif Penuh (Bahasa Indonesia & English)** di seluruh modul (Executive, Customer Intelligence, Customer 360, Sales, Product, Market Intelligence, dan UI Components).

#### 🔄 Changed / Refactored
- Seluruh Treemap diganti Horizontal Bar Chart + Donut ranking.
- Seluruh Bubble Chart & Scatter Plot diganti Grouped Bar Chart & Matriks Kinerja.
- Label teknis diubah: "Pendapatan Net" dan "Terakhir Belanja (Hari Lalu)".
- Funnel penawaran menyajikan 5 metrik eksplisit dan 5 status peluang ramah operasional.
- Penyesuaian microcopy menyeluruh ke bahasa bisnis yang natural dan mudah dipahami.
- `render_section_info` otomatis mengubah label header konteks (`📋 What is Displayed:`, `🎯 Why It Matters:`, `💡 Simple Insight:`) saat beralih bahasa.

#### 🛠️ Fixed
- **Perbaikan `KeyError: 'growth_pct'` pada Market Intelligence**: 
  - Mengintegrasikan kalkulasi `compute_period_growth()` langsung ke dalam `calculate_market_opportunity_matrix(df_intel, df_sales)` di `utils/intelligence_engine.py`.
  - Mencegah tabrakan nama kolom akibat pandas merge suffix (`growth_pct_x` / `growth_pct_y`).
  - Menambahkan validasi defensif kolom `growth_pct` pada `views/6_Market_Intelligence.py`.
- **Perbaikan Business Rule & Formula Laju Pertumbuhan Pasar (Market Growth Rate)**:
  - **Normalisasi Durasi Waktu Berimbang (Equal-Time Normalization)**: Menggantikan pemotongan baris `median()` yang cacat (140 hari vs 118 hari) dengan pembagian dua paruh waktu seimbang ($D_1 = D_2$) dan normalisasi laju bulanan (*Monthly Run-Rate*). Menghilangkan angka negatif palsu pada Industri (+21.6%), Divisi (+10.6%), dan Instansi (+17.5%).
  - **Metrik Kontribusi Pertumbuhan Pasar (Market Growth Contribution %)**: Mengatasi *small base effect* pada transaksi mikro staf/karyawan (`EMPLOYEE` Rp 28,5 Juta = 0.1% omzet) dengan menghitung kontribusi riil terhadap ekspansi pasar. Industri memimpin di puncak (+9.10% kontribusi / +Rp 808 Juta) dan Employee proporsional di dasar (+0.13% / +Rp 11,7 Juta).
  - **Klasifikasi Peran Segmen**: Membedakan pasar komersial eksternal (B2B, B2G, Ritel & UMKM) dari operasi internal (Fulfillment Cabang) dan transaksi internal staf (Employee Perk).
  - **Interactive Perspective Toggle**: Menambahkan selektor metrik langsung pada grafik (Kontribusi Pertumbuhan Pasar, Laju Pertumbuhan Bersih per Segmen, dan Nilai Tambahan Omzet Riil).

#### 🗑️ Removed
- Kolom "Status Kesehatan" pada Top Customer Leaderboard.
- Kolom rekomendasi tindakan teknis pada Worklist CS.
- Section ringkasan metadata akun mentah, next best action engine, dan tabel transaksi invoice pada Customer 360.
- Tab Eksplorasi Data Quotation (Sales Intelligence).
- Tab List Target Cross-Sell teknis (Product Intelligence).
- Kolom "Klasifikasi Kinerja" pada tabel kinerja produk (Product Intelligence) karena tidak valid dan membingungkan user.
- Klaim angka marketing palsu (AOV naik 15-25%, diskon statis Rp 50.000, diskon 7%, dsb.) pada Product Intelligence.

---

## 5. Pembaruan Lanjutan: Marketing Campaign Intelligence & SupportUMKM Program

### A. Latar Belakang & Filosofi Transformasi
Tim Pemasaran Cipta Grafika menjalankan program **SupportUMKM** yang melibatkan kunjungan fisik ke tempat usaha UMKM, pendampingan kebutuhan cetak, serta aktivasi promosi (voucher, referral, kampanye produk, retargeting perilaku). Sebelumnya, dashboard belum membedakan antara data historis faktual dengan ide penawaran, serta memuat klaim angka yang tidak berdasar.

Pembaruan ini mentransformasi modul Marketing Intelligence dengan memegang teguh prinsip:
$$\text{DATA} \longrightarrow \text{CUSTOMER BEHAVIOR} \longrightarrow \text{MARKETING OPPORTUNITY} \longrightarrow \text{TARGET CUSTOMER} \longrightarrow \text{CAMPAIGN IDEA} \longrightarrow \text{MARKETING ACTION}$$

### B. Arsitektur Modul Terpadu
1. **Refactoring Product Intelligence ([`5_Product_Intelligence.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/5_Product_Intelligence.py))**:
   - Menghapus tab rencana aksi pemasaran statis dari Product Intelligence agar tidak terjadi duplikasi insight.
   - Menggantinya dengan **Peluang Produk & Permintaan Pasar**: analisis pasangan pembelian bersama (*Co-Purchase Category Pairs*) yang 100% dihitung dari riwayat invoice multi-item faktual (misal: Cetak A3 + Finishing > 9.400 invoice), serta panduan merchandising katalog.
2. **Pembangunan 3 Pilar pada Market Intelligence ([`6_Market_Intelligence.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/6_Market_Intelligence.py))**:
   - **Tab 1: 🌐 Analisis Pasar & Tolok Ukur Cabang**: Matriks pertumbuhan PoP ternormalisasi, kontribusi pasar riil, sebaran omzet vs pelanggan, tolak ukur 6 cabang, dan strategi alokasi portofolio.
   - **Tab 2: 🤝 SupportUMKM Intelligence**:
     - *Ringkasan Status UMKM*: 3.932 akun terdaftar, 2.803 pembeli, 1.129 prospek belum pernah beli, 936 akun aktif, 360 akun baru, 600 akun mulai jarang belanja, dan 392 akun bernilai belanja tinggi.
     - *Pola Belanja UMKM*: Grafik kategori produk terlaris (Cetak A3 & Format Besar menyerap >65% pesanan) & 10 produk terbanyak (Flexy 280 gsm dan Stiker Chromo/Vynil).
     - *Peluang Produk Tambahan*: 372 UMKM beli Kemasan belum beli Stiker; 960 UMKM beli Stiker belum beli Kemasan; 1.113 UMKM beli Spanduk belum beli Display Stand.
     - *Transparansi Data Kunjungan Lapangan*: Status jujur *"Belum tersedia pada Analytical Dataset"* + spesifikasi skema data untuk tim Tech (`visit_id`, `jenis_usaha`, `kebutuhan_teridentifikasi`, dll.) & alur perjalanan konversi ideal.
     - *Daftar Kerja UMKM Interaktif*: Worklist akun UMKM dilengkapi status keaktifan dan rekomendasi promosi yang relevan.
   - **Tab 3: 🎯 Marketing Campaign Intelligence**:
     - *Ukuran Target Audiens*: KPI terukur untuk Target Voucher (1.438 akun), Target Referral (1.000 akun), Target Produk Musiman (325 akun), dan Retargeting Belanja Terakhir (842 akun pada jendela 30 hari).
     - *Analisis Jangkauan Target*: 3.111 akun unik ditargetkan, dengan 445 akun memiliki lebih dari satu peluang promosi (*overlap pool*).
     - *Pola Belanja → Peluang Produk*: Horizontal bar chart kesenjangan pembelian (Kemasan vs Stiker, Spanduk vs Display, Brosur vs Suvenir).
     - *4 Pilar Peluang Promosi dengan Pemisahan Faktual*: Setiap kartu membedakan dengan tegas antara **[DATA]** (fakta dataset), **[INSIGHT]** (interpretasi analitis), dan **[CAMPAIGN IDEA]** (ide program pemasaran).
     - *Tabel Peluang Kampanye Pemasaran*: Kolom dengan bahasa awam (*Peluang Promosi, Target Pelanggan, Kondisi Belanja Aktual, Jumlah Target Customer, Produk yang Ditawarkan, Rekomendasi Aksi Marketing*).
     - *Profil Perilaku Pelanggan (Explorer)*: Eksplorasi akun perorangan menggunakan bahasa sehari-hari (*"Terakhir Belanja: X hari lalu"*, *"Sudah Belanja: X kali"*, *"Total Belanja: Rp X"*).
     - *Kesiapan Pengukuran Kampanye & ROI Gap Notice*: Transparansi bahwa ROI belum dapat dihitung karena data biaya promosi belum dicatat, disertai spesifikasi skema closed-loop analytics.
3. **Pengembangan Engine Baru ([`utils/intelligence_engine.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/utils/intelligence_engine.py))**:
   - `analyze_support_umkm_intelligence()`: Kalkulasi komprehensif metrik, perilaku belanja, gap produk, dan worklist UMKM.
   - `compute_marketing_campaign_intelligence()`: Deteksi audiens voucher, referral, musiman, retargeting dinamis (slider 14–60 hari), dan overlap.
   - `compute_product_copurchase_pairs()`: Analisis kombinasi faktur multi-item berbasis *combinations & counter*.
4. **Pembaruan Katalog Insight ([`views/0_Insight_Catalog.py`](file:///home/zen/Documents/Cetakia/cetakia-bi/views/0_Insight_Catalog.py))**:
   - Menyelaraskan deskripsi modul Product Intelligence dan Market Intelligence dengan kapabilitas V1.2 terbaru.

---
*Dokumen ini merupakan ringkasan resmi implementasi kode Cetakia BI DSS V1.2 dan tersinkronisasi 100% dengan repositori aplikasi Streamlit yang aktif.*

