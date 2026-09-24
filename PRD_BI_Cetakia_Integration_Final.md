# PRD BI Cetakia Integration

**Product Requirements Document · Versi 1.0 · 20 September 2026**

Pemilik dokumen: Product & Business Intelligence · Audiens: Tech Lead, IT Development, Product, Owner, dan Business Stakeholders.

Status: PRD lengkap untuk review; belum merupakan persetujuan implementasi produksi. Prototipe menggunakan data sintetis; dokumen ini tidak menyatakan bahwa integrasi produksi, endpoint, otorisasi, atau target bisnis sudah tersedia.

## 1. Executive Summary

Cetakia memerlukan lapisan Business Intelligence (BI) yang menghubungkan angka operasional dengan keputusan bisnis. Dashboard saat ini telah menampilkan sales, collections, pelanggan baru, pipeline, dan pelanggan terbesar. Produk yang diusulkan mempertahankan konteks operasional tersebut, lalu menambahkan interpretasi, kelompok pelanggan yang terdampak, dan tindak lanjut yang jelas.

Setiap insight menjawab empat pertanyaan: apa yang terjadi, faktor apa yang perlu diperiksa, siapa yang terdampak, dan tindakan apa yang disarankan. Perubahan revenue, misalnya, harus dapat ditelusuri ke jumlah order, average order value (AOV), pelanggan baru atau repeat, cabang, salesperson, dan produk. Korelasi ini menjadi dasar investigasi; bukan kesimpulan sebab-akibat otomatis.

Proposal terdiri atas enam modul: Executive Business Dashboard, Sales Intelligence, Customer Intelligence, Customer 360, Product Intelligence, serta Finance & Collection. Semua menggunakan definisi metrik dan filter yang sama. Pada produksi, UI mengakses BI API; analytical service menyediakan agregasi dari master analitis yang terkontrol.

Prototipe lokal menggunakan Streamlit, Plotly, Pandas, dan CSS. Data sintetis deterministik mencakup 1.000 pelanggan, 5.000 transaksi, 100 produk, enam kategori, dan 12 bulan kalender dari Oktober 2025 sampai September 2026, dengan snapshot 19 September 2026. September adalah bulan parsial dan tidak boleh ditafsirkan sebagai bulan penuh. Angka kartu dihitung dari data, sehingga bukan salinan angka ilustrasi pada brief atau screenshot.

Hasil yang diharapkan dari review adalah kesepakatan definisi metrik, pengalaman penggunaan, batas akses, urutan implementasi, serta pemilik tindak lanjut. Prototipe ini merupakan reference implementation untuk evaluasi konsep, bukan sistem akuntansi atau aplikasi produksi.

| Hasil review | Bukti yang dapat diperiksa |
| --- | --- |
| Nilai produk | Insight, konteks tren, pelanggan atau transaksi terdampak, dan rekomendasi tersedia dalam enam modul. |
| Kesiapan integrasi | Arsitektur, grain data, kontrak metrik, konsep API, serta roadmap terdokumentasi. |
| Konsistensi | Semua kartu, chart, tabel, dan ekspor berasal dari data analitis dengan filter yang sama. |
| Batas prototipe | Data sintetis dan antrean tindakan per sesi diberi label jelas; tidak ada pengiriman pesan atau perubahan data produksi. |

## 2. Business Problem

Dashboard operasional menjawab berapa banyak penjualan atau penerimaan yang tercatat. Owner dan tim pelaksana masih harus menggabungkan laporan lain untuk mengetahui apakah pertumbuhan sehat, pelanggan mana yang mulai tidak aktif, quotation mana yang perlu ditindaklanjuti, atau piutang mana yang paling mendesak.

| Masalah | Dampak keputusan | Kebutuhan produk |
| --- | --- | --- |
| Sales bertambah tanpa penjelasan komposisi | Owner tidak mengetahui apakah pertumbuhan berasal dari pelanggan, frekuensi, atau nilai order. | Tren revenue, customer growth, AOV, dan revenue source dengan drill-down. |
| Pelanggan terbesar hanya diperingkat berdasarkan revenue | Pelanggan bernilai tinggi yang melewati siklus reorder sulit ditemukan. | Customer health, nilai pembelian teramati, dan rekomendasi reaktivasi. |
| Funnel belum memiliki cohort dan denominator seragam | Conversion mudah salah dibaca ketika dokumen dari periode berbeda dicampur. | Funnel berbasis quotation cohort, timestamp tahap, dan definisi conversion. |
| Collections dicampur dengan revenue pada periode yang sama | Rasio cash-in disalahartikan sebagai pelunasan invoice periode tersebut. | Pisahkan cash receipts berdasarkan tanggal pembayaran dan collection rate berdasarkan cohort invoice. |
| Produk populer belum dihubungkan dengan pelanggan | Peluang cross-sell tidak memiliki daftar sasaran atau bukti. | Penetrasi, product pairing, minimum evidence, dan bundle yang bisa ditelusuri. |
| Insight berhenti pada teks | Sulit memastikan siapa melakukan tindak lanjut. | Owner tindakan, prioritas, objek terkait, serta status tindak lanjut. |

Risiko bisnis utama adalah tindakan berdasarkan angka yang tidak sebanding. Karena itu, definisi periode, cabang, nilai transaksi, status dokumen, dan freshness adalah bagian produk yang terlihat oleh pengguna.

## 3. BI Vision & Objective

Visi: menjadikan Cetakia sebagai decision support system yang membantu tim memahami perubahan bisnis, memprioritaskan pekerjaan, dan mengukur hasil tindak lanjut dengan data yang konsisten.

Alur keputusan: Data → Insight → Pemahaman perilaku pelanggan → Recommended Action → Evaluasi hasil bisnis.

| Sasaran | Ukuran keberhasilan yang diusulkan | Cara evaluasi |
| --- | --- | --- |
| Kepercayaan terhadap angka | Selisih rekonsiliasi agregat terhadap sumber yang disepakati = 0, selain pembulatan tampilan. | Rekonsiliasi transaksi, item, pembayaran, dan API sebelum rilis. |
| Insight yang dapat ditindaklanjuti | Seluruh insight prioritas memiliki metrik, trend, interpretasi, tindakan, owner, dan bukti. | Review acceptance criteria Product dan pemilik bisnis. |
| Kecepatan investigasi | Pengguna menemukan objek terdampak dari ringkasan tanpa menyusun laporan manual. | Uji tugas dengan Owner, Sales, CS, dan Finance. Target waktu ditetapkan setelah baseline. |
| Adopsi dan outcome | Penggunaan modul, tindakan dibuat atau selesai, repeat order, quotation conversion, dan overdue balance. | Baseline dan evaluasi periodik; kenaikan KPI saja tidak membuktikan dampak kausal BI. |

Dalam scope: enam modul BI, filter bersama, drill-down pelanggan, ekspor data sesuai tampilan, katalog metrik, dan simulasi tindak lanjut. Antrean tindakan prototipe tersimpan dalam session state; bukan CRM persisten, bukan pengiriman WhatsApp/email, dan bukan perubahan status operasional.

Di luar scope saat ini: live database connection, deployment produksi, autentikasi nyata, pencatatan pembayaran, perpajakan, pembukuan, model prediksi tervalidasi, rekomendasi harga, serta otomatisasi kampanye. Profit atau margin tidak ditampilkan sebagai fakta bila biaya belum tersedia.

## 4. Current Dashboard Analysis

Analisis ini berasal dari screenshot Cetakia yang diberikan pengguna, bukan audit kode atau akses ke sistem operasional. Tampilan menunjukkan sidebar operasional, global branch selector, filter periode, dark navy background, compact KPI cards, dan panel dengan chart serta tabel. Gaya ini dipertahankan agar BI terasa sebagai bagian dari Cetakia.

| Komponen saat ini | Kekuatan | Pengayaan BI yang diusulkan |
| --- | --- | --- |
| Total Sales | Ringkasan nilai invoice dan jumlah order. | Perbandingan periode setara, AOV, revenue source, dan pelanggan yang berkontribusi. |
| Total Collections | Menunjukkan penerimaan dan outstanding. | Pisahkan cash receipts dan invoice-cohort collection; tampilkan dasar perhitungan. |
| New Customers | Memantau akuisisi jangka pendek. | Pisahkan pelanggan terdaftar dengan pelanggan first purchase; ukur kontribusi dan repeat. |
| Sales vs Receipts Report | Tren bulanan sales dan cash-in. | Tambahkan partial-period label, cohort context, dan drill-down ke invoice/payment. |
| Sales & Fulfillment Pipeline | Menunjukkan konversi dan penyelesaian operasional. | Selaraskan cohort, status, tanggal tahap, serta daftar bottleneck. |
| Top Customer Leaderboard | Mengidentifikasi konsentrasi revenue. | Tautkan ke Customer 360, health, repeat cycle, dan pembayaran. |

Prinsip UI: hierarki jelas, compact cards, kontras terbaca, warna status konsisten, label teks selain warna, dan tabel yang tetap berguna pada viewport sempit. Header menampilkan periode, filter aktif, snapshot, serta status data sintetis. Navigasi enam modul mengikuti kebutuhan keputusan, sementara sidebar mempertahankan bahasa visual dashboard Cetakia.

Angka screenshot tidak menjadi target data. Contoh brief “3.200 dari 5.000 quotation = 34,8%” tidak konsisten; hasil aritmetik yang benar adalah 64%. Contoh 2.340 pelanggan aktif juga tidak mungkin berasal dari master dengan 1.000 pelanggan. Prototipe memakai hasil perhitungan dataset dan menjelaskan denominator pada UI.

## 5. Proposed BI Architecture

[ARCHITECTURE_DIAGRAM]

Cetakia Database menyimpan transaksi operasional. Analytical Service melakukan ekstraksi, normalisasi status, deduplikasi, pembentukan master analitis, dan perhitungan metrik. BI API Layer menerapkan kontrak bisnis, filter, tenant/branch authorization, pagination, caching, dan freshness. Dashboard Component mengubah respons API menjadi kartu, chart, serta detail. Business Action mencatat tindak lanjut dan hasilnya pada sistem yang berwenang.

Untuk prototipe, CSV sintetis menggantikan sumber operasional dan service Python lokal menggantikan BI API. UI menggunakan service tersebut; tidak ada query database operasional. Endpoint pada bagian 8 adalah rancangan integrasi produksi, bukan route HTTP yang telah diimplementasikan dalam aplikasi Streamlit.

### 5.1 Model data analitis dan grain

| Entitas | Grain dan key | Isi serta penggunaan |
| --- | --- | --- |
| customer_master | Satu baris per customer_id. | Identitas sintetis, segment, tanggal registrasi, dan atribut pelanggan. Segmen: INDUSTRY, UMKM, CORPORATE, END USER. |
| sales_transaction_master | Satu baris per transaction_id; satu invoice/order analitis pada prototipe. | customer_id, branch, salesperson, tanggal transaksi, due_date, nilai invoice, dan status. Basis revenue, transaksi, AOV, serta piutang. |
| sales_item_master | Satu baris per (transaction_id, product_id) dalam fixture; produksi wajib memiliki sales_item_id stabil. | product_id, quantity, unit_price, line_total; jumlah item direkonsiliasi ke header invoice. |
| customer_transaction_summary | Satu baris per customer_id pada snapshot. | Jumlah order, nilai teramati, first/last order, siklus reorder, dan health. Agregat untuk scope filter dihitung ulang; summary global tidak dijumlahkan sembarang. |
| quotation_funnel_master | Satu baris per quotation_id. | Nilai quotation, customer, branch, salesperson, tanggal quotation/expiry, serta milestone sales order, invoice, dan payment. |
| collection_master | Satu baris per collection_id / allocation pembayaran ke invoice. | transaction_id, payment_date, dan amount. Beberapa pembayaran dapat mengacu ke invoice yang sama. |
| customer_product_basket_master | Satu baris per (transaction_id, category). | customer_id, order_date, category_revenue, distinct_products; basket kategori per transaksi, bukan agregat seluruh pembelian pelanggan. |
| product_master | Satu baris per product_id. | Nama produk, kategori, dan harga referensi. Seratus produk dalam enam kategori. |

Kontrak grain produksi wajib disahkan ketika satu order dapat memiliki beberapa invoice, satu invoice beberapa order, retur, credit note, atau pembayaran yang belum dialokasikan. Join pembayaran dan item langsung ke header tanpa pre-aggregation berisiko menggandakan nilai; setiap agregasi harus mempertahankan grain-nya.

### 5.2 Kontrak periode dan filter

Snapshot prototipe adalah 2026-09-19. Tanggal setelah snapshot tidak boleh masuk metrik. Seluruh label waktu mengikuti Asia/Jakarta; produksi menyimpan timestamp UTC dan mengubah batas waktu berdasarkan business timezone.

Rentang tanggal UI inklusif. Untuk API bertimestamp, backend mengubahnya menjadi interval [date_from 00:00, date_to + 1 hari 00:00) dalam zona bisnis. Rentang pembanding adalah hari tepat sebelum date_from sepanjang rentang terpilih. Contoh 1–19 September 2026 (19 hari) dibandingkan dengan 13–31 Agustus 2026 (19 hari), bukan seluruh Agustus.

Revenue dan order menggunakan tanggal invoice/transaksi; cash receipts menggunakan payment_date; funnel menggunakan quotation_date; aging menggunakan due_date dengan cutoff as_of. Branch filter berlaku terhadap branch transaksi/invoice/quotation, termasuk pembayaran yang dialokasikan kepadanya. Customer health dan riwayat Customer 360 menggunakan data yang tersedia hingga as_of dalam scope cabang/segmen dan harus diberi label berbeda dari nilai periode terpilih.

Segment filter berasal dari customer_master. Produksi harus menentukan apakah segment bersifat current-state atau historical slowly changing dimension; prototipe memakai current-state sintetis. Perubahan filter harus mengubah kartu, chart, tabel, insight, dan export secara konsisten. Jika pembanding keluar dari history yang tersedia, trend diberi status insufficient_history dan tidak dihitung menggunakan periode parsial yang tidak setara.

### 5.3 Kontrak nilai dan kualitas

Prototipe menggunakan IDR nominal; nilai item dan header tidak mencakup model PPN, ongkir, retur, credit note, atau diskon terpisah. Nilai ini disebut nilai penjualan/invoice teramati, bukan pendapatan akuntansi yang telah diakui. Produksi wajib menyepakati gross/net sales, pajak, pembulatan, status draft/cancelled, retur, dan tanggal pengakuan sebelum angka disamakan dengan laporan Finance.

Required checks: primary key unik; foreign key valid; tepat 1.000 customer, 5.000 transaksi, 100 produk dan enam kategori; event transaksi/pembayaran tidak melewati snapshot; due_date dan expiry_date boleh setelah snapshot; tidak ada milestone tahap sebelum tahap sebelumnya; jumlah line_total = revenue dalam toleransi pembulatan; allocation payment tidak melebihi invoice; rate dalam domain yang benar; bucket aging saling eksklusif dan menjumlah ke outstanding.

## 6. BI Module Specification

### 6.1 Executive Business Dashboard

| Aspek | Spesifikasi |
| --- | --- |
| Objective | Memahami kesehatan bisnis, sumber perubahan revenue, konsentrasi pelanggan, dan prioritas lintas tim. |
| User role | Owner, Management; scope seluruh cabang yang diizinkan. |
| Insight cards | Revenue Overview, Transaction Overview, Active Customer, AOV, Collection Overview, dan Sales vs Customer Growth. |
| Business value | Mengarahkan review mingguan ke driver bisnis dan kelompok yang memerlukan tindakan. |
| Data requirement | sales_transaction_master, customer_master, collection_master; pembanding periode sama panjang. |
| Visualization type | KPI cards, monthly revenue bars, customer growth line, sales/receipts chart, revenue source, leaderboard pelanggan. |
| Recommended action | Tinjau pelanggan bernilai tinggi, cabang dengan penurunan, atau pertumbuhan AOV tanpa pertumbuhan customer. Owner: Management dengan Sales/CS terkait. |
| Drill-down | Ringkasan → cabang/pelanggan → Customer 360; rincian invoice sesuai scope akses. |

Revenue growth dijelaskan menggunakan perubahan volume order dan AOV. Kenaikan AOV bersama revenue adalah asosiasi yang dapat diamati; teks tidak menyatakan harga, preferensi, atau kampanye sebagai penyebab tanpa bukti. Customer growth memakai unique purchasing customers, bukan jumlah akun terdaftar. Revenue source memisahkan first observed purchase dan repeat; label menyatakan keterbatasan history 12 bulan.

### 6.2 Sales Intelligence

| Aspek | Spesifikasi |
| --- | --- |
| Objective | Menemukan peluang pipeline, membandingkan kontribusi salesperson/cabang, dan memprioritaskan follow-up. |
| User role | Sales Manager dan Sales Staff; scope salesperson/branch sesuai otorisasi produksi. |
| Insight cards | Sales Performance, Order Volume, AOV, Quotation Conversion, Expired Opportunity. |
| Business value | Memfokuskan kapasitas sales pada quotation bernilai besar dengan status dan bukti yang jelas. |
| Data requirement | quotation_funnel_master, sales_transaction_master, customer_master; milestone tiap tahap dan expiry_date. |
| Visualization type | Quotation → Sales Order → Invoice → Payment funnel, salesperson ranking, bar chart 6 cabang (Cipta Graha, Cipta Digital, Cipta Galuh, Cipta Cianjur, Cipta Purwakarta, Cipta Online), tabel quotation kedaluwarsa. |
| Recommended action | Sales memeriksa kebutuhan, alasan tidak berlanjut, dan kelayakan quotation prioritas sebelum menghubungi pelanggan. |
| Drill-down | Klik objek pelanggan/quotation pada daftar prioritas; tindakan menyimpan konteks dan nilai peluang. |

Funnel berawal dari quotation yang dibuat pada periode terpilih. Jumlah pada setiap tahap dihitung berdasarkan tercapainya milestone hingga as_of, sehingga denominator tetap sama. Payment stage berarti telah ada pembayaran teralokasi, bukan otomatis lunas. Lost opportunity adalah nilai quotation expired yang belum menjadi order; bukan revenue yang telah diakui dan bukan kerugian terjamin.

### 6.3 Customer Intelligence

| Aspek | Spesifikasi |
| --- | --- |
| Objective | Memahami komposisi pelanggan, repeat behavior, dan kelompok yang melewati pola reorder normal. |
| User role | Customer Service, Sales, Marketing. |
| Insight cards | Customer Segmentation, Customer Health, Repeat Customer Rate, Retention Cohort, dan At Risk Customers. |
| Business value | Menyediakan daftar sasaran retensi berdasarkan perilaku pembelian teramati. |
| Data requirement | customer_master, sales_transaction_master, customer_transaction_summary; order history hingga as_of. |
| Visualization type | Segment donut, health distribution, repeat KPI, cohort heatmap, customer worklist. |
| Recommended action | CS meninjau pelanggan At Risk/Dormant menurut nilai teramati dan kebutuhan; Marketing merancang eksperimen reaktivasi terukur. |
| Drill-down | Customer worklist → Customer 360 dengan filter cabang yang tetap dipertahankan. |

Health adalah heuristik, bukan prediksi churn yang tervalidasi. New, Healthy, Active, At Risk, dan Dormant bersifat saling eksklusif; New membedakan pelanggan tanpa pembelian atau dengan pembelian pertama baru-baru ini. Siklus reorder dihitung hanya jika riwayat memadai; fallback harus terlihat pada detail definisi. Pelanggan tanpa pembelian tidak boleh diberi nilai pembelian fiktif. Pada cohort, sel bulan setelah snapshot tidak diberi angka nol karena belum dapat diamati.

### 6.4 Customer 360

| Aspek | Spesifikasi |
| --- | --- |
| Objective | Memberikan profil kerja customer untuk menyiapkan percakapan dan follow-up yang relevan. |
| User role | Customer Service dan Sales; Finance memperoleh bagian pembayaran sesuai hak akses. |
| Insight cards | Segment, observed customer value, total order, last order, favorite product, average repeat interval, health, outstanding, recommended action. |
| Business value | Mengurangi perpindahan antarlaporan dan memberi konteks kebutuhan/pembayaran pelanggan. |
| Data requirement | customer_master, transactions, items, products, collection allocations, dan product basket. |
| Visualization type | CRM profile header, compact metrics, order history, category/product chart, payment panel, action card. |
| Recommended action | Follow-up reorder produk yang relevan; evaluasi bundle hanya jika ada evidence pairing, serta periksa overdue sebelum penawaran kredit baru. |
| Drill-down | Pilih customer ID/nama sintetis, baca transaksi dan pembayaran terkait, lalu tambahkan tindakan ke antrean sesi. |

Label “Observed customer value” atau “Nilai pembelian teramati” digunakan karena history hanya 12 bulan. Nilai ini bukan lifetime value penuh maupun prediksi CLV. Total order dan last order dihitung dari history tersedia hingga as_of; dashboard harus membedakannya dari metrik periode terpilih. Favorite category pada fixture adalah kategori dengan jumlah line_total terbesar dalam history customer; tie-breaker nama kategori ascending. Produksi dapat menambah favorite product pada grain product_id dengan formula dan label terpisah.

### 6.5 Product Intelligence

| Aspek | Spesifikasi |
| --- | --- |
| Objective | Menemukan kontribusi kategori, produk dengan ruang penetrasi, serta pasangan produk untuk investigasi cross-sell. |
| User role | Marketing, Sales, Owner. |
| Insight cards | Top Product, Category Performance, High Revenue–Low Penetration Opportunity, Product Pairing, Bundle Recommendation. |
| Business value | Memberikan kandidat penawaran dengan bukti pembelian dan kelompok pelanggan sasaran. |
| Data requirement | sales_item_master, product_master, sales_transaction_master, customer_master, basket aggregates. |
| Visualization type | Product ranking, category revenue bars, revenue-versus-penetration scatter, pair table, bundle cards. |
| Recommended action | Uji paket UMKM seperti Packaging + Sticker + Thank You Card pada pelanggan yang relevan; validasi kecocokan dan margin sebelum kampanye. |
| Drill-down | Produk/kategori → transaksi dan pelanggan pembeli → Customer 360 atau task prioritas. |

Penetrasi produk adalah proporsi pelanggan aktif dalam scope yang membeli produk tersebut, bukan proporsi seluruh master. Pairing dihitung dari produk/kategori yang muncul dalam transaksi yang sama; membeli dua produk dalam bulan berbeda tidak berarti satu basket. Support, confidence, lift, dan co-purchase count wajib dapat ditelusuri. Minimum evidence menekan rekomendasi dari satu atau dua transaksi; rekomendasi bukan jaminan uplift.

### 6.6 Finance & Collection

| Aspek | Spesifikasi |
| --- | --- |
| Objective | Memisahkan performa penerimaan kas dan pelunasan invoice, serta memprioritaskan piutang berdasarkan jatuh tempo. |
| User role | Finance, Owner; Sales/CS melihat ringkasan pelanggan sesuai akses. |
| Insight cards | Cash Receipts, Invoice-cohort Collection Rate, Outstanding, Overdue, Aging Receivable, Customer Payment Behavior. |
| Business value | Mengurangi salah tafsir sales versus cash dan memberi dasar daftar penagihan. |
| Data requirement | sales_transaction_master dengan due_date, collection_master dengan allocation dan payment_date, customer_master. |
| Visualization type | Collection KPI, aging bars, outstanding customer table, payment behavior classification. |
| Recommended action | Finance meninjau invoice overdue bernilai besar, mengonfirmasi allocation dan perselisihan, lalu menentukan tindak lanjut. |
| Drill-down | Customer/invoice outstanding → rincian invoice dan pembayaran → task penagihan simulasi. |

Collection rate mengikuti invoice yang diterbitkan dalam periode terpilih dan seluruh pembayaran terkait hingga as_of. Cash receipts mengikuti tanggal pembayaran dalam periode dan dapat berasal dari invoice bulan sebelumnya. Keduanya tidak boleh diberi label yang sama. Aging mencakup invoice terbuka yang diterbitkan hingga as_of, dengan bucket Not Due (termasuk jatuh tempo hari ini), 1–30, 31–60, 61–90, dan >90 hari overdue; batas 90 masuk 61–90, bukan dihitung dua kali.

## 7. Insight Card Specification

### 7.1 Kontrak komponen

Setiap insight card berisi urutan Metric → Trend → Business Interpretation → Recommended Action. Komponen juga membawa insight_id, metric_version, scope, evidence, affected_entities, owner_role, priority, as_of, dan data_quality. Tindakan memiliki objek yang jelas, misalnya customer_id atau quotation_id. Label “hipotesis untuk diperiksa” dipakai ketika interpretasi belum memiliki bukti sebab-akibat.

| Field | Aturan |
| --- | --- |
| Insight Name | Nama keputusan/risiko yang dapat dipahami pengguna bisnis. |
| Metric | Nilai numerik, unit, dan cakupan periode. Persentase menyertakan numerator dan denominator. |
| Formula | Formula metric_id terpusat; tampilan tidak menghitung ulang dengan definisi berbeda. |
| Trend | Current versus previous, tanggal kedua rentang, delta absolut atau persen, dan status comparison. |
| Business Meaning | Fakta yang teramati, siapa yang terdampak, dan hipotesis bila diperlukan. |
| Recommended Action | Kata kerja, target, owner, prioritas, serta kriteria selesai; tidak mengirim pesan otomatis. |
| API Requirement | Endpoint, filter, field bukti, freshness, dan hak akses. |

### 7.2 Katalog metrik inti

Nama invoice_amount pada katalog/API berarti field revenue pada CSV; line_amount berarti line_total; quotation_amount berarti quotation_value. Ini mapping konsep, bukan tambahan field dalam fixture. Dalam formula berikut, S adalah transaksi valid dalam periode/filter; C adalah pelanggan unik yang membeli dalam S; H adalah history valid dalam scope hingga as_of. Nilai prototipe berasal dari data sintetis, bukan konstanta ilustrasi.

| Insight / metric_id | Formula, window, dan denominator | Business meaning dan tindakan | API requirement |
| --- | --- | --- | --- |
| Revenue / sales_amount | Σ invoice_amount pada S. Growth = (current − previous) / previous × 100 jika previous > 0 dan history lengkap. | Menilai perubahan nilai penjualan; Management memeriksa order dan AOV sebelum menyimpulkan driver. | dashboard-summary: current, previous, growth_pct, comparison_status. |
| Transactions / order_count | COUNT DISTINCT transaction_id pada S. Prototipe satu transaksi = satu order/invoice analitis. | Mengukur aktivitas pembelian; Sales memeriksa cabang dan pelanggan dengan perubahan volume. | dashboard-summary; sales/performance dengan order_count. |
| Active Customer / active_customers | COUNT DISTINCT customer_id pada S; maksimum jumlah pelanggan dalam scope. | Pelanggan yang benar-benar membeli; CS menilai repeat dan konsentrasi. | dashboard-summary dengan active_customers dan scope. |
| AOV / average_order_value | sales_amount / order_count; null jika order_count = 0. | Nilai rata-rata order; Sales meninjau mix produk dan pembeli. | dashboard-summary; sales/performance. |
| Revenue Source / first_repeat_sales | Pisahkan revenue pelanggan menurut first observed purchase di history tersedia versus pembelian setelahnya. | Menguji komposisi pertumbuhan; Marketing memeriksa acquisition dan retention tanpa menganggap first observed = pelanggan baru seumur hidup. | dashboard-summary: revenue_sources dan observation_start. |
| Sales/Customer Growth | Dua growth series memakai metrik revenue dan active_customers; denominators dihitung per periode, bukan menjumlah unique bulanan. | Revenue tumbuh tanpa customer growth dapat berkaitan dengan AOV/frequency; Management memeriksa rinciannya. | dashboard-summary: trend series dan partial_period. |
| Quotation Conversion / quotation_conversion | Quotation cohort Q dibuat dalam periode. Converted = anggota Q dengan sales_order_date ≤ as_of. Rate = converted / count(Q) × 100. | Menilai progression cohort; Sales memprioritaskan quotation terbuka. | sales/funnel: stage_counts, cohort_count, as_of. |
| Lost Opportunity / expired_quotation_value | Σ quotation_amount untuk Q expired pada as_of dan belum menjadi order. | Peluang yang tidak berlanjut; Sales memvalidasi kebutuhan dan alasan lost. Bukan revenue loss terjamin. | sales/quotations: status=expired, expiry_date, amount. |
| Segmentation / segment_distribution | Count customer unik per segment dalam population yang dilabeli, divided by total population tersebut. | Membandingkan komposisi pelanggan; Marketing menentukan sasaran dengan konteks populasi. | customers/segments: count, denominator, population_basis. |
| Repeat / repeat_customer_rate | Pelanggan dalam C yang memiliki ≥2 transaksi pada S / count(C) × 100. Pelanggan repeat sebelum periode tetapi sekali pada S tidak termasuk numerator definisi ini. | Menilai pembelian berulang dalam window; CS memeriksa kebutuhan dan interval reorder. | customers/health: repeat_customers, active_customers, rate. |
| Customer Health / health_status | Recency sejak last_order dibandingkan observed reorder cycle pada H; aturan dan fallback harus terpusat serta versioned. | Mengurutkan pemeriksaan Healthy/Active/At Risk/Dormant; CS memvalidasi kebutuhan, bukan menganggap churn pasti. | customers/health: recency, cycle, status, rule_version. |
| Retention / cohort_retention | Cohort = bulan first observed order. Retention M+n = customer cohort yang membeli pada bulan n / ukuran cohort awal × 100. | Menilai repeat lintas bulan; Marketing membandingkan cohort pada umur setara. | customers/cohorts: cohort_size, month_index, retained_count, observable. |
| Customer Value / observed_value | Σ invoice_amount pada H untuk customer; total order = distinct transactions; repeat interval = rata-rata gap tanggal order berurutan jika ≥2 tanggal order berbeda. | Konteks relasi pelanggan dalam history terbatas; CS menyesuaikan tindak lanjut. | customer/{id}: observation_start/end, value, order_count, repeat_days. |
| Product Revenue / product_sales | Σ line_amount per product/category pada S. Revenue share = product sales / total item sales. | Menemukan kontribusi produk; Sales mengecek pelanggan/kategori terkait. | products/top: product_id, amount, share, rank. |
| Product Penetration / penetration_rate | Customer unik pembeli produk pada S / count(C) × 100. | Kandidat produk bernilai tinggi dengan penetrasi rendah; Marketing memeriksa kecocokan segmen. | products/opportunities: buyers, active_customers, revenue, threshold. |
| Product Pair / basket_affinity | N = transaksi dalam scope; support(A,B) = N_AB/N; confidence(A→B) = N_AB/N_A; lift = confidence/(N_B/N). | Evidence asosiasi produk; Sales menguji bundle yang memenuhi minimum count. | products/pairs: support, confidence, lift, co_purchase_count, min_count. |
| Cash Receipts / cash_receipts | Σ allocated amount dengan payment_date di periode, terhubung ke invoice yang diizinkan oleh scope. | Penerimaan kas periode; Finance memeriksa allocation dan penerimaan invoice lama. | finance/summary: cash_receipts, payment_window. |
| Collection / invoice_collection_rate | I = invoice diterbitkan dalam periode. Σ pembayaran teralokasi ke I hingga as_of / Σ invoice_amount I × 100. | Pelunasan cohort invoice; Finance meninjau invoice yang belum lunas. | finance/summary: cohort_invoice_amount, allocated_paid, as_of. |
| Outstanding / open_receivable | Σ max(invoice_amount − allocated payments ≤ as_of, 0) untuk invoice pada H. | Posisi piutang pada cutoff; Finance memeriksa allocation sebelum follow-up. | finance/aging: outstanding, invoice_id, due_date. |
| Aging / overdue_days | Untuk outstanding > 0: max(as_of − due_date, 0). due_date ≥ as_of = Not Due; sisanya 1–30, 31–60, 61–90, >90. | Memprioritaskan umur piutang; Finance meninjau invoice tertua/terbesar. | finance/aging: bucket, balance, as_of, basis=due_date. |
| Payment Behavior / payment_behavior | Heuristik berbasis invoice terbuka dan overdue; kategori Good/Average/Risk harus mengembalikan bukti dan rule_version. | Mempersiapkan review penagihan; bukan credit score atau keputusan kredit otomatis. | finance/customers: behavior, overdue balance/days, basis. |

### 7.3 Aturan keputusan yang dapat diimplementasikan

Aturan berikut berstatus baseline desain bi.v1 untuk disahkan pemilik bisnis. Health sesuai generator tersimpan; aturan opportunity dan payment behavior adalah spesifikasi implementasi berikutnya.

| Aturan | Definisi berurutan dan bukti |
| --- | --- |
| Customer health | Hitung recency dari tanggal akhir filter dikurangi last_order. Siklus = max(14 hari, rata-rata selisih tanggal order berbeda); default 30 hari bila tidak ada dua tanggal berbeda. |
| New | Tidak ada pembelian, ATAU first_order berjarak ≤30 hari dari snapshot. Evaluasi paling awal, sebelum status lain. Tidak identik dengan registrasi baru. |
| Dormant | Untuk customer selain New, recency > max(90 hari, 3 × siklus). |
| At Risk | Jika belum Dormant, recency > max(30 hari, 1,5 × siklus). |
| Healthy / Active | Jika tidak memenuhi aturan sebelumnya: recency ≤14 hari → Healthy; selebihnya → Active. Equality pada ambang At Risk/Dormant tidak masuk status tersebut. |
| Product opportunity | Pada grain produk, high revenue = nilai ≥ persentil 75 produk dengan penjualan >0; low penetration = buyers / active_customers <20%; buyers minimal 5. Ketiga syarat wajib. Jika tidak ada kandidat, tampilkan empty state. Ambang dikirim API, bukan tersembunyi di UI. |
| Product pairing | Default minimum N_AB = 10 transaksi; lift >1 untuk badge kandidat bundle. Tampilkan direction A→B, count, support, confidence, lift, dan scope. Di bawah ambang tetap boleh ditinjau sebagai exploratory, tanpa rekomendasi otomatis. |
| Bundle audience | Customer dalam segmen terpilih yang membeli A tetapi belum membeli B dalam periode; hanya dengan evidence pair yang memenuhi ambang. Paket Packaging + Sticker + Thank You Card adalah konsep bisnis: pairing dua kategori tidak membuktikan affinity paket tiga produk. |
| Payment behavior | Basis adalah saldo invoice terbuka pada snapshot, bukan histori credit score. Risk payer: ada saldo >30 hari overdue. Average payer: ada saldo 1–30 hari overdue, tanpa yang >30 hari. Good payer: pernah bertransaksi, tanpa saldo overdue. Customer tanpa invoice = Insufficient data; jangan dilabeli Good payer. |

Kategori fixture: Large Format, Packaging, Sticker & Label, Digital Printing, Offset Printing, Merchandise. Contoh A3 Printing pada brief dipetakan sebagai usulan subkategori Digital Printing, bukan kategori ketujuh yang sudah tersedia. Nama produk Thank You Card tersedia pada Digital Printing; bundle harus memakai product_id yang benar sebelum dijadikan penawaran.

### 7.4 Aturan interpretasi dan edge cases

Previous = 0 menghasilkan growth null dengan label “Tidak ada basis pembanding”, bukan tak hingga atau +100%. Current = 0 dan previous > 0 menghasilkan −100%. Denominator kosong menghasilkan null/“Belum ada data”; kosong tidak otomatis menunjukkan bisnis sehat. Perubahan rate ditampilkan dalam percentage points bila membandingkan dua persentase.

Cohort menggunakan first observed order, sehingga pelanggan lama sebelum Oktober 2025 dapat terlihat seperti cohort baru. Sel bulan masa depan adalah null; bulan berjalan ditandai parsial. Cohort yang lebih muda dibandingkan pada usia cohort yang sama. Unique customers tidak bersifat additive lintas cabang/bulan jika customer membeli di beberapa scope.

Contoh format tindakan: “CS meninjau pelanggan At Risk dengan nilai pembelian teramati tertinggi, mengonfirmasi kebutuhan reorder, dan mencatat hasil.” Teks ini adalah rekomendasi kerja; prototipe hanya membuat task lokal per sesi. Tidak ada janji bahwa follow-up menghasilkan kenaikan revenue tertentu.

## 8. API Design Concept

### 8.1 Endpoint dan akses

Prefix produksi yang diusulkan adalah /api/bi. Contoh berikut adalah kontrak konsep; endpoint belum dijalankan oleh prototipe Streamlit. Semua respons membawa request_id, metric_version, scope, as_of, data_updated_at, dan warnings.

| Method / endpoint | Respons utama | Role minimum yang diusulkan |
| --- | --- | --- |
| GET /api/bi/dashboard-summary | KPI, previous comparison, trends, revenue source, insight list. | Owner/Management; manager dengan branch scope. |
| GET /api/bi/sales/performance | Salesperson dan branch revenue/order/AOV. | Sales Manager/Staff sesuai scope. |
| GET /api/bi/sales/funnel | Cohort count, stage count, conversion, milestone basis. | Sales Manager/Staff. |
| GET /api/bi/sales/quotations | Paginated quotation worklist dan expired value. | Sales Manager/Staff. |
| GET /api/bi/customers/segments | Segment population dan denominator. | CS/Sales/Marketing. |
| GET /api/bi/customers/health | Health worklist, repeat rate, rule version. | CS/Sales/Marketing. |
| GET /api/bi/customers/cohorts | First observed cohorts dan observable cells. | CS/Sales/Marketing/Management. |
| GET /api/bi/customer/{id} | Profile, observed value, orders, health, product preference. | CS/Sales; finance detail memerlukan Finance/Owner. |
| GET /api/bi/products/top | Product/category ranking dengan contribution. | Marketing/Sales/Owner. |
| GET /api/bi/products/opportunities | Revenue/penetration candidate list. | Marketing/Sales/Owner. |
| GET /api/bi/products/pairs | Co-purchase count, support, confidence, lift. | Marketing/Sales/Owner. |
| GET /api/bi/finance/summary | Cash receipts dan invoice-cohort collection. | Finance/Owner. |
| GET /api/bi/finance/aging | Invoice aging, outstanding, due-date basis. | Finance/Owner. |
| GET /api/bi/finance/customers | Payment behavior dan supporting evidence. | Finance/Owner. |

Parameter bersama: date_from, date_to, as_of, branch_ids, segments, dan timezone=Asia/Jakarta. Parameter spesifik: salesperson_ids, customer_id, product_ids, category_ids, health_status, status, min_pair_count, sort, limit, dan cursor. Backend memvalidasi rentang, enum, ID, dan batas limit. Default limit 50; maksimum yang diusulkan 200. Cursor opaque dan stable sort menggunakan metric lalu unique ID sebagai tie-breaker.

Tenant dan identity berasal dari sesi/token terverifikasi server, tidak dipercaya dari query client. branch_ids harus merupakan subset branch yang diizinkan. UI role preview, jika ada, tidak menggantikan authorization server. Ekspor memakai scope dan akses yang sama. Detail customer di luar scope menghasilkan 404 agar keberadaannya tidak dibocorkan; filter cabang terlarang menghasilkan 403.

### 8.2 Contoh request dan response

Contoh kontrak menggunakan angka kecil untuk menjelaskan denominator, bukan angka aktual dashboard atau target produksi.

```http
GET /api/bi/dashboard-summary?date_from=2026-09-01&date_to=2026-09-19&as_of=2026-09-19&branch_ids=CGH
Authorization: Bearer <session-token>
```

```json
{
  "request_id": "req_example_001",
  "metric_version": "bi.v1",
  "scope": {
    "date_from": "2026-09-01",
    "date_to": "2026-09-19",
    "comparison_from": "2026-08-13",
    "comparison_to": "2026-08-31",
    "branch_ids": ["CGH"],
    "segments": [],
    "timezone": "Asia/Jakarta"
  },
  "as_of": "2026-09-19",
  "data_updated_at": "2026-09-19T02:00:00Z",
  "source_mode": "synthetic_example",
  "data": {
    "sales_amount": {
      "value": 12000000,
      "unit": "IDR",
      "previous": 10000000,
      "growth_pct": 20.0,
      "comparison_status": "comparable"
    },
    "order_count": 30,
    "active_customers": 20,
    "average_order_value": 400000,
    "invoice_collection_rate": {
      "value_pct": 50.0,
      "numerator": 6000000,
      "denominator": 12000000,
      "basis": "invoice_cohort_paid_as_of"
    },
    "cash_receipts": 8000000
  },
  "warnings": ["September is a partial month"]
}
```

List response menggunakan data.items dan page.next_cursor. Respons insight menambahkan affected_entities yang dipaginasi atau link drill-down, bukan ribuan customer dalam kartu ringkasan. Nilai uang dikirim sebagai numeric IDR dengan kebijakan decimal yang disepakati; UI melakukan format rupiah Indonesia. Empty result adalah HTTP 200 dengan items kosong, counts 0, dan rate null bila denominator 0.

```json
{
  "request_id": "req_example_002",
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "date_from must not exceed date_to",
    "fields": ["date_from", "date_to"]
  }
}
```

### 8.3 Error, freshness, dan non-functional requirements

| Kondisi | Kontrak yang diusulkan |
| --- | --- |
| 400 validation | INVALID_DATE_RANGE, UNKNOWN_FILTER, atau UNSUPPORTED_TIMEZONE; berikan field bermasalah tanpa SQL/internal trace. |
| 401 / 403 | Sesi tidak valid / role atau branch tidak diizinkan. Server tetap memeriksa setiap request. |
| 404 | Customer/resource tidak ada atau tidak terlihat oleh identity peminta. |
| 429 | Rate limit; Retry-After dan retry terkontrol, terutama untuk export. |
| 503 | Analytical service belum siap; gunakan code DATA_UNAVAILABLE dan tampilkan stale cache hanya bila dilabeli. |
| Freshness | Usulan refresh hourly untuk agregat; Finance cutoff wajib jelas. Frekuensi final disepakati berdasarkan SLA sumber dan biaya. |
| Performance | Target awal untuk validasi: p95 summary <2 detik pada scope normal; workload dan volume uji harus didefinisikan sebelum menjadi SLA. |
| Cache | Key meliputi tenant, akses branch/role, filter, metric_version, snapshot; tidak boleh mencampur scope pengguna. |
| Audit dan observability | Log request_id, endpoint, scope aman, duration, snapshot, error code; hindari data identitas pelanggan pada log umum. |

## 9. Implementation Roadmap

Roadmap menggunakan exit criteria, bukan tanggal yang belum didukung estimasi tim. Customer 360 serta Finance & Collection termasuk fase 2 agar investigasi dan tindak lanjut dari dashboard memiliki halaman tujuan yang utuh.

| Fase | Scope | Dependensi / owner | Exit criteria |
| --- | --- | --- | --- |
| Phase 1 — Executive Dashboard | Metric dictionary, customer/transaction/product masters, revenue/order/active/AOV, receipts, filter dan growth comparison. | Product + Data + Backend + Frontend; Finance menyetujui nilai invoice. | Rekonsiliasi disetujui; null/empty/partial history benar; branch authorization diuji; Owner menyelesaikan task review. |
| Phase 2 — Sales + Customer Intelligence | Funnel, expired worklist, segmentation, health, repeat, cohort, Customer 360, Finance & Collection/aging. | Sales/CS/Finance memvalidasi status, cycle rules, due date, payment allocation; API detail tersedia. | Cohort denominator konsisten; health evidence terlihat; aging cocok dengan sumber; drill-down menghormati akses. |
| Phase 3 — Product + Marketing Intelligence | Product/category revenue, penetration, same-basket pairing, bundle candidates, dan desain eksperimen kampanye. | Item-level quality, product taxonomy, evidence threshold, margin validation oleh bisnis. | Pairing dapat direproduksi; target audience dapat ditelusuri; minimum sample terkontrol; evaluasi tidak mengklaim kausalitas tanpa desain uji. |
| Phase 4 — Operational Intelligence | Integrasi fulfillment, lead time, bottleneck, kapasitas, keterlambatan, serta outcome action ke workflow produksi. | Sumber event produksi/jobs/delivery dan owner operasional disepakati. | Definisi event dan SLA operasional disahkan; source-to-action audit tersedia; monitoring dan support siap. |

Urutan persetujuan: Tech Lead menilai arsitektur dan kontrak; Data/Backend menilai grain dan kesiapan sumber; Finance menilai nilai dan pembayaran; Product bersama pengguna bisnis menyetujui insight dan task; IT menjalankan security, deployment, serta operasi. Prototype review dapat dilakukan sebelum sumber produksi tersedia.

Risiko dan mitigasi: status sumber tidak konsisten → mapping versioned; allocation pembayaran belum lengkap → tampilkan quality warning; history pendek → label observed dan null cohort; pairing jarang → minimum evidence; akses lintas cabang → server-side authorization; insight terlalu banyak → urutkan prioritas berdasarkan evidence dan owner.

## 10. Developer Implementation Notes

### 10.1 Pemisahan tanggung jawab

UI tidak melakukan query raw database. Produksi menggunakan Business/BI API; analytical service menjadi sumber formula metrik. Pada prototipe, service Pandas lokal mensimulasikan boundary tersebut. Komponen metric card, insight card, chart, filter, table, dan action worklist dapat digunakan ulang oleh enam halaman.

Formula tidak disalin ke banyak komponen. Gunakan satu metric definition dan satu scope/filter object. Helper rupiah, persen, unit, sorting, trend, empty state, dan label partial period harus konsisten. Nilai numerik tetap numeric sampai boundary presentasi; export mempertahankan kolom mentah dan metadata scope.

Generator sintetis bersifat deterministik untuk memudahkan review dan regresi. Jangan memasukkan CSV operasional, data pelanggan nyata, credential, atau koneksi produksi ke jalur demo. Dataset sengaja mensimulasikan segmentation, repeat behavior, affinity, revenue trend, dan collection behavior; pola yang terlihat tidak dapat digeneralisasi ke kinerja Cipta Grafika yang sesungguhnya.

### 10.2 Integrasi sumber dan asumsi yang perlu disahkan

| Keputusan | Asumsi prototipe | Validasi sebelum produksi |
| --- | --- | --- |
| Order versus invoice | Satu transaksi analitis mewakili satu order/invoice. | Mapping one-to-many order/invoice, draft, void, serta cancellation. |
| Nilai penjualan | Jumlah nilai item sintetis tanpa model pajak/retur terpisah. | Gross/net, PPN, discounts, shipping, credit notes, returns, currency dan rounding. |
| Customer identity | customer_id stabil dan unik. | Deduplication lintas cabang, merge pelanggan, serta customer rumah/internal. |
| Segment | Current-state sintetis: INDUSTRY, UMKM, CORPORATE, END USER. | Taxonomy bisnis, ownership, dan kebutuhan history perubahan segment. |
| Payment allocation | Setiap collection terkait invoice; tidak ada overpayment. | Unallocated receipt, refund, withholding, payment reversal, dan allocation changes. |
| Customer value | Nilai pembelian dalam history tersedia. | History backfill dan definisi LTV/CLV bila akan digunakan. |
| Customer health | Heuristik berdasarkan recency dan observed cycle. | Ambang, seasonality, low-sample fallback, serta validasi CS. |
| Action | Session-only simulated task; tidak ada external side effect. | Persistence, owner assignment, consent/channel policy, audit, serta integrasi CRM. |

### 10.3 Acceptance criteria dan pengujian

1. Enam modul dapat dibuka, dengan data sintetis, snapshot, periode, dan filter aktif terlihat jelas.
2. Dataset memenuhi 1.000 pelanggan, 5.000 transaksi, 100 produk, enam kategori, dan 12 bulan kalender termasuk September parsial; semua relasi valid.
3. Revenue item dan header cocok; payment tidak melebihi invoice; nilai summary konsisten dengan detail dan export pada filter sama.
4. Periode pembanding sama panjang; insufficient history dan denominator nol menghasilkan state yang informatif tanpa growth fiktif.
5. Active customer tidak melebihi master/scope; repeat rate memiliki denominator purchasing customers yang jelas.
6. Funnel memakai quotation cohort dan milestones hingga as_of; setiap tahap merupakan subset tahap sebelumnya.
7. Health memuat bukti recency/cycle; cohort future cells null dan partial month dilabeli.
8. Customer 360 menunjukkan nilai teramati, riwayat, produk favorit, payment context, dan tindakan yang relevan dengan customer terpilih.
9. Pairing memakai transaksi yang sama, count, denominator, dan evidence threshold; tidak menyebut pairing sebagai hubungan kausal.
10. Cash receipts dan invoice-cohort collection berbeda definisi; aging memakai due_date, menyertakan Not Due, dan jumlah bucket sama dengan outstanding.
11. Insight selalu memuat metric, trend, interpretation, recommended action, dan tujuan drill-down atau objek terdampak.
12. Tindakan demo menambah task sesi dan dapat ditinjau; tidak mengirim pesan atau mengubah data produksi. Reload sesi dapat menghilangkan task.
13. Empty result, customer tanpa order, prior denominator nol, multiple partial payments, invoice due today, aging batas 30/31/60/61/90/91, dan filter cabang sempit diuji.
14. Untuk produksi, server-side tenant/role/branch authorization, pagination, freshness, cache separation, error contract, observability, dan deployment checks wajib lulus sebelum rilis.

### 10.4 Status artefak dan batas penyelesaian

Status berikut merupakan inventaris berkas lokal yang diperiksa pada 20 September 2026, bukan hasil UAT. Penyelesaian PRD tidak berarti seluruh fitur prototipe sudah selesai.

| Artefak | Status saat PRD diterbitkan | Catatan |
| --- | --- | --- |
| PRD Markdown dan Word | Lengkap untuk review | Sepuluh bagian utama, formula, aturan keputusan, API konsep, roadmap, dan acceptance criteria. |
| Delapan CSV sintetis dan generator | Tersedia | 1.000 customer; 5.000 transaksi; 100 produk; 7.296 item; 7.300 quotation; 4.654 allocation pembayaran; 7.296 basket kategori; 1.000 summary. |
| Analytical service dan view model | Tersedia sebagai kode | Ada formula yang masih perlu disatukan; helper period_metrics mengembalikan 0 untuk rate tanpa denominator, sedangkan kontrak PRD menetapkan null. Uji integrasi tetap diperlukan. |
| UI components dan empat module renderer | Tersedia sebagai kode | Executive, Sales, Customer Intelligence, Customer 360. Belum menyatakan seluruh navigasi dan interaksi lolos pengujian end-to-end. |
| App modular, Product, Finance, action plan terpadu | Belum lengkap pada inventaris ini | Menjadi pekerjaan implementasi; definisinya sudah dicakup dalam PRD. File prototype satu halaman awal tetap terpisah. |
| BI HTTP API dan integrasi Cetakia | Rancangan | Endpoint bagian 8 belum menjadi server API produksi. |

Snapshot fixture tetap 19 September 2026 walaupun dokumen diterbitkan 20 September. Tanggal dokumen tidak menggeser data atau melakukan query produksi.

### 10.5 Skenario UAT dan bukti penerimaan

| ID | Skenario | Hasil yang wajib diperiksa | Pemilik review |
| --- | --- | --- | --- |
| UAT-01 | Executive: periode 1–19 Sep, semua cabang | Pembanding 13–31 Agustus; jumlah invoice/detail cocok; sales dan cash receipts berlabel berbeda. | Owner + Finance |
| UAT-02 | Sales: quotation cohort dengan partial payment | Tahap payment menghitung quotation dengan pembayaran; bukan jumlah receipt. Tahap tidak membesar setelah funnel berikutnya. | Sales Manager |
| UAT-03 | Customer: pelanggan tanpa order dan pelanggan baru membeli | Zero-purchase termasuk New; repeat rate hanya purchasing customers; health menampilkan rule version. | CS |
| UAT-04 | Cohort September pada snapshot 19 Sep | M+0 dapat ditampilkan sebagai parsial; M+1 dan seterusnya null, tidak dianggap churn 100%. | Marketing |
| UAT-05 | Customer 360 dengan branch scope sempit | History dan saldo hanya dari cabang yang diizinkan; nilai disebut observed, bukan seluruh lifetime. | CS + Tech Lead |
| UAT-06 | Product: pasangan hanya 2 transaksi | Tidak muncul badge bundle recommendation dengan minimum 10; angka evidence tetap dapat diperiksa. | Marketing + Sales |
| UAT-07 | Finance: invoice due today dan overdue 30/31/60/61/90/91 hari | Today = Not Due; seluruh batas masuk tepat satu bucket; total bucket = outstanding. | Finance |
| UAT-08 | Filter tanpa transaksi dan prior revenue nol | Count/revenue 0; AOV/rate/growth tanpa denominator null; insight tidak menyebut kondisi sehat karena kosong. | Product + QA |
| UAT-09 | Export worklist dan task demo | Export mengikuti filter aktif; task memuat scope/owner; tindakan tidak mengirim pesan. | Product + QA |
| UAT-10 | Akses cabang/resource terlarang pada API produksi | Respons 403/404 sesuai kontrak, cache tidak membocorkan scope tenant lain. | Tech Lead + IT |

Gate sebelum demo: aplikasi modular bisa dijalankan dari README, enam modul dapat dibuka, metric-contract tests lulus, tidak ada placeholder interaksi yang menyesatkan. Gate sebelum produksi: mapping sumber disahkan, rekonsiliasi Finance, kontrol akses dan observability diuji, serta owner operasional menerima SOP.

### 10.6 Decision log dan persetujuan

| Keputusan | Rekomendasi baseline | Pemilik keputusan | Status |
| --- | --- | --- | --- |
| Nilai sales resmi | Sahkan net/gross, pajak, retur, diskon, dan timestamp sebelum menyamakan laporan Finance. | Finance + Product | Perlu validasi |
| Grain order–invoice | Pisahkan order_count dan invoice_count jika mapping tidak 1:1. | Tech Lead + Backend | Perlu mapping sumber |
| Customer identity dan branch | Tentukan cross-branch ID; customer population memakai home branch, transaksi memakai transaction branch. Jangan menyamakan denominator bila pelanggan dapat lintas cabang. | Data + Sales | Perlu validasi |
| Health, opportunity, payer rules | Mulai dengan baseline bagian 7.3; evaluasi false-positive dengan pengguna bisnis. | CS + Marketing + Finance | Usulan |
| Freshness dan performa | Refresh hourly dan p95 <2 detik sebagai target awal yang harus dibuktikan pada workload. | Tech Lead + IT | Usulan |
| Action ownership | Session-only untuk demo; production task memerlukan audit, assignee, dan outcome. | Product + Business Owner | Usulan |

Persetujuan review dicatat terpisah: Product menyetujui scope/UX; Finance menyetujui formula nilai dan collection; Sales/CS/Marketing menyetujui aturan tindakan; Tech Lead menyetujui desain teknis; IT menyetujui kesiapan operasional. Tidak ada approval yang diasumsikan dari penerbitan dokumen ini.

### 10.7 Review dan serah terima

Paket PRD mencakup source Markdown, dokumen Word, pratinjau PDF, catatan penggunaan, dan script reproduksi dokumen. Aplikasi dan dataset merupakan artefak proyek pendukung dengan status pada bagian 10.4. Dokumen Word dihasilkan dari source yang sama agar perubahan kontrak dapat direview melalui diff. Tech Lead menandai keputusan yang disetujui dan yang masih memerlukan mapping ke schema Cetakia; angka sintetis tidak perlu disamakan dengan screenshot operasional.

Keputusan terbuka yang paling menentukan integrasi adalah grain order/invoice, perlakuan pajak/retur, histori status dan segment, payment allocation, cakupan akses cabang, refresh SLA, serta pemilik tindakan. Seluruh keputusan tersebut harus dicatat sebelum API dan KPI diperlakukan sebagai sumber resmi organisasi.
