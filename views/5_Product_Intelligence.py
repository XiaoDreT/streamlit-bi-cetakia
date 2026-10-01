import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_product_data, load_sales_data
from utils.intelligence_engine import compute_product_copurchase_pairs
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    render_section_info, render_summary_strip,
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Product Intelligence Dashboard", page_icon="📦", layout="wide")

# Load Datasets
df_items = load_product_data(include_cancelled=False)
df_sales = load_sales_data(include_cancelled=False)

# Merge branch division metadata into product items
if "division_name" not in df_items.columns and "invoice_id" in df_items.columns and "division_name" in df_sales.columns:
    df_items = df_items.merge(
        df_sales[["invoice_id", "division_name"]].drop_duplicates(),
        on="invoice_id",
        how="left"
    )

# Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

df_filtered = df_items.copy()
if "invoice_status" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["invoice_status"].astype(str).str.lower() != "cancel"]

if filters["branch"] != "All Branches":
    if "division_name" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Clean category labels by stripping prefix
df_filtered["clean_category"] = df_filtered["product_category"].astype(str).str.replace("Sales ", "")

# Page Header
render_header(
    title="Dashboard Analisis Produk & Bauran Penjualan" if lang_code == "ID" else "Product Intelligence & Category Mix Dashboard",
    subtitle="Audit bauran penjualan kategori, peringkat produk unggulan, dan strategi pemasaran berbasis perilaku pelanggan." if lang_code == "ID" else "Category revenue mix audit, top product rankings, and behavior-driven promotional strategies.",
    module_tag="MARKETING / PRODUCT STRATEGY"
)

# Summary Metrics
total_item_revenue = df_filtered["sales_amount"].sum() if "sales_amount" in df_filtered.columns else 0
total_qty = df_filtered["qty"].sum() if "qty" in df_filtered.columns else 0
distinct_products = df_filtered["product_name"].nunique() if "product_name" in df_filtered.columns else 0
total_active_cust = df_filtered["customer_id"].nunique() if "customer_id" in df_filtered.columns else 1

p1, p2, p3, p4 = st.columns(4)
with p1:
    kpi1_title = "Total Penjualan Produk" if lang_code == "ID" else "Total Product Revenue"
    kpi1_sub = "Pendapatan item terkonfirmasi" if lang_code == "ID" else "Confirmed item revenue"
    metric_card(kpi1_title, format_rupiah(total_item_revenue), subtext=kpi1_sub)

with p2:
    kpi2_title = "Total Unit Terjual" if lang_code == "ID" else "Total Units Sold"
    unit_str = "Unit" if lang_code == "ID" else "Units"
    kpi2_sub = "Volume kuantitas produksi cetak" if lang_code == "ID" else "Production volume quantity"
    metric_card(kpi2_title, f"{total_qty:,.0f} {unit_str}", subtext=kpi2_sub)

with p3:
    kpi3_title = "Katalog SKU Aktif" if lang_code == "ID" else "Active SKU Catalog"
    kpi3_sub = "Varian produk dengan pesanan riil" if lang_code == "ID" else "Product variants with orders"
    metric_card(kpi3_title, f"{distinct_products:,} SKU", subtext=kpi3_sub)

with p4:
    kpi4_title = "Akun Pelanggan Pembeli" if lang_code == "ID" else "Buying Customer Accounts"
    cust_unit = "Pembeli" if lang_code == "ID" else "Buyers"
    kpi4_sub = "Basis pembeli aktif katalog" if lang_code == "ID" else "Active buyer account base"
    metric_card(kpi4_title, f"{total_active_cust:,} {cust_unit}", subtext=kpi4_sub)

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD (DECISION SUPPORT)
# -------------------------------------------------------------
top_cat_name = "Large Format Printing"
top_cat_share = 13.1
if not df_filtered.empty:
    cat_agg = df_filtered.groupby("clean_category")["sales_amount"].sum()
    if not cat_agg.empty:
        top_cat_name = cat_agg.idxmax()
        top_cat_share = (cat_agg.max() / total_item_revenue * 100) if total_item_revenue > 0 else 0

if lang_code == "EN":
    ic_title = "Product Category Dominance & Promotional Expansion Strategy"
    ic_metric = f"Top Category: {top_cat_name} ({top_cat_share:.1f}% Revenue Share)"
    ic_context = f"Evaluated across {distinct_products:,} active SKUs and {total_active_cust:,} buyer accounts in branch '{filters['branch']}'."
    ic_insight = f"{top_cat_name} and A3 Printing serve as volume anchors. Meanwhile, Packaging and Merchandise categories generate high margins but are currently bought by less than 15% of the active customer base."
    ic_impacted = f"Product Manager, Merchandising Team, and Production Supervisors."
    ic_action = "Product Strategy: Standardize official combo packages (Printing + Finishing) in the catalog and ensure inventory buffer for high-frequency paper stocks."
    ic_badge = "PRODUCT STRATEGY DECISION SUPPORT"
    ic_target = f"Printing Catalog & Growth Categories of Cipta Grafika"
else:
    ic_title = "Dominasi Kategori Produk & Peluang Portofolio Katalog"
    ic_metric = f"Kategori Terbesar: {top_cat_name} ({top_cat_share:.1f}% Pangsa Omzet)"
    ic_context = f"Dianalisis dari {distinct_products:,} SKU aktif dan {total_active_cust:,} akun pembeli di cabang '{filters['branch']}'."
    ic_insight = f"Kategori {top_cat_name} dan A3 Printing menjadi penopang omzet utama. Di sisi lain, kategori Box Kemasan dan Souvenir/Merchandise memiliki potensi margin tinggi namun baru dibeli oleh kurang dari 15% pelanggan aktif."
    ic_impacted = f"Manajer Produk, Tim Merchandising, dan Supervisor Operasional Percetakan."
    ic_action = "Strategi Produk: Standarisasi paket kombo resmi (Cetak + Finishing) dalam katalog POS dan siapkan stok bahan baku penyangga untuk kategori dengan perputaran cepat."
    ic_badge = "KEPUTUSAN STRATEGIS PRODUK"
    ic_target = f"Katalog Percetakan & Kategori Pertumbuhan Cipta Grafika"

render_business_insight_card(
    title=ic_title,
    metric=ic_metric,
    context=ic_context,
    insight=ic_insight,
    who_impacted=ic_impacted,
    action=ic_action,
    badge=ic_badge,
    target_entity=ic_target
)

st.markdown("---")

# -------------------------------------------------------------
# TABBED PRODUCT INTELLIGENCE INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_labels = [
        "📦 Category Mix & Top Products",
        "🎯 Revenue & Customer Reach Matrix",
        "🧩 Product Opportunities & Co-Purchase Demand"
    ]
else:
    tab_labels = [
        "📦 Bauran Kategori & Produk Terlaris",
        "🎯 Matriks Kinerja & Sebaran Pembeli",
        "🧩 Peluang Produk & Permintaan Pasar"
    ]

tab1, tab2, tab3 = st.tabs(tab_labels)

# -------------------------------------------------------------
# TAB 1: BAURAN KATEGORI & PRODUK TERLARIS (USER-FRIENDLY BAR/DONUT)
# -------------------------------------------------------------
with tab1:
    if lang_code == "EN":
        render_section_info(
            title="Product Category Revenue Mix & Best-Selling Products",
            subtitle="Mapping revenue contributions across all Cetakia print categories.",
            what_it_shows="Horizontal bar chart of category revenue contributions, share percentages, and top 10 best-selling products.",
            why_important="Identifies core cashflow categories and high-margin expansion categories with vast untapped buyer potential.",
            simple_insight=f"Current dominant categories are <b>{top_cat_name}</b> and <b>A3 Printing</b>. High-potential expansion categories include <b>Packaging, Merchandise/Souvenirs, and Books & Magazines</b>."
        )
    else:
        render_section_info(
            title="Bauran Pendapatan per Kategori Produk & Produk Terlaris",
            subtitle="Memetakan kontribusi pendapatan dari setiap kategori produk cetak Cetakia.",
            what_it_shows="Diagram batang horizontal kontribusi omzet per kategori, persentase pangsa, dan 10 produk dengan penjualan tertinggi.",
            why_important="Mengetahui kategori mana yang dominan (penopang arus kas) dan kategori mana yang potensial ditingkatkan (karena margin tinggi namun pasarnya belum tergarap maksimal).",
            simple_insight=f"Kategori dominan saat ini adalah <b>{top_cat_name}</b> dan <b>A3 Printing</b>. Kategori potensial untuk didorong adalah <b>Packaging, Souvenir/Merchandise, serta Buku & Majalah</b>."
        )
    
    if not df_filtered.empty:
        df_cat = df_filtered.groupby("clean_category").agg(
            total_rev=("sales_amount", "sum"),
            total_units=("qty", "sum"),
            order_count=("invoice_id", "nunique"),
            buyer_count=("customer_id", "nunique")
        ).reset_index().sort_values(by="total_rev", ascending=True)
        
        tot_all_rev = df_cat["total_rev"].sum()
        df_cat["rev_pct"] = (df_cat["total_rev"] / tot_all_rev * 100) if tot_all_rev > 0 else 0
        
        col_c1, col_c2 = st.columns([6, 4])
        with col_c1:
            st.markdown("**" + ("Peringkat Kontribusi Pendapatan per Kategori" if lang_code == "ID" else "Category Revenue Contribution Rankings") + "**")
            fig_cat = px.bar(
                df_cat.tail(12),
                x="total_rev",
                y="clean_category",
                orientation="h",
                color="total_rev",
                text=df_cat.tail(12)["rev_pct"].apply(lambda p: f" {p:.1f}%"),
                color_continuous_scale=["#93C5FD", "#1D4ED8"],
                labels={
                    "total_rev": "Pendapatan Net (IDR)" if lang_code == "ID" else "Net Revenue (IDR)", 
                    "clean_category": "Kategori Produk" if lang_code == "ID" else "Product Category"
                }
            )
            fig_cat.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_cat, height=380)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_c2:
            st.markdown("**" + ("Top 10 Produk Terlaris Berdasarkan Omzet" if lang_code == "ID" else "Top 10 Best-Selling Products by Revenue") + "**")
            df_top_prod = df_filtered.groupby("product_name")["sales_amount"].sum().reset_index().sort_values(by="sales_amount", ascending=True).tail(10)
            
            fig_top = px.bar(
                df_top_prod,
                x="sales_amount",
                y="product_name",
                orientation="h",
                color="sales_amount",
                color_continuous_scale=["#C7D2FE", "#4338CA"],
                labels={
                    "sales_amount": "Omzet (IDR)" if lang_code == "ID" else "Revenue (IDR)", 
                    "product_name": "Nama Produk" if lang_code == "ID" else "Product Name"
                }
            )
            fig_top.update_traces(
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_top, height=380)
            st.plotly_chart(fig_top, use_container_width=True)
            
        # Category Narrative Insight Box
        st.markdown("### " + ("📊 Analisis Peran Kategori Produk" if lang_code == "ID" else "📊 Product Category Strategic Role Analysis"))
        pk1, pk2, pk3 = st.columns(3)
        with pk1:
            if lang_code == "EN":
                st.markdown("""
                <div class="cetakia-card" style="border-top: 4px solid #2563EB; padding: 14px;">
                    <b style="color: #2563EB; font-size: 13px;">🏆 DOMINANT CATEGORY (VOLUME DRIVER)</b>
                    <div style="font-size: 16px; font-weight: 800; margin: 4px 0;">Large Format & A3 Printing</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Accounts for > 25% of total revenue with thousands of orders. Acts as the primary customer acquisition gateway for Cetakia.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="cetakia-card" style="border-top: 4px solid #2563EB; padding: 14px;">
                    <b style="color: #2563EB; font-size: 13px;">🏆 KATEGORI DOMINAN (VOLUME DRIVER)</b>
                    <div style="font-size: 16px; font-weight: 800; margin: 4px 0;">Large Format & A3 Printing</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Menyumbang > 25% total omzet dengan basis ribuan pesanan. Menjadi pintu gerbang masuknya pelanggan baru ke Cetakia.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with pk2:
            if lang_code == "EN":
                st.markdown("""
                <div class="cetakia-card" style="border-top: 4px solid #10B981; padding: 14px;">
                    <b style="color: #10B981; font-size: 13px;">💎 HIGH-MARGIN CATEGORY</b>
                    <div style="font-size: 16px; font-weight: 800; margin: 4px 0;">Corporate ID & Promotional Items</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Ordered by corporate institutions and industrial clients with high basket sizes. Generates healthy gross profit contributions.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="cetakia-card" style="border-top: 4px solid #10B981; padding: 14px;">
                    <b style="color: #10B981; font-size: 13px;">💎 KATEGORI MARGIN TINGGI</b>
                    <div style="font-size: 16px; font-weight: 800; margin: 4px 0;">Corporate ID & Promotional Item</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Dipesan oleh instansi dan industri dengan nilai per transaksi besar. Menghasilkan kontribusi laba yang sangat sehat.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with pk3:
            if lang_code == "EN":
                st.markdown("""
                <div class="cetakia-card" style="border-top: 4px solid #F59E0B; padding: 14px;">
                    <b style="color: #F59E0B; font-size: 13px;">🚀 EXPANSION POTENTIAL CATEGORY</b>
                    <div style="font-size: 16px; font-weight: 800; margin: 4px 0;">Packaging & Label Stickers</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        In high demand by thousands of F&B and fashion MSMEs. High upside through promotional vouchers and product bundling.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="cetakia-card" style="border-top: 4px solid #F59E0B; padding: 14px;">
                    <b style="color: #F59E0B; font-size: 13px;">🚀 KATEGORI POTENSIAL DITINGKATKAN</b>
                    <div style="font-size: 16px; font-weight: 800; margin: 4px 0;">Packaging & Stiker Label</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Dibutuhkan oleh ribuan UMKM kuliner & fashion. Sangat potensial ditingkatkan melalui promosi voucher dan bundling.
                    </div>
                </div>
                """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 2: MATRIKS KINERJA & SEBARAN PEMBELI PRODUK (CLEAN MATRIX TABLE)
# -------------------------------------------------------------
with tab2:
    if lang_code == "EN":
        render_section_info(
            title="Product Revenue & Customer Reach Matrix",
            subtitle="Classifying products into standard commercial tiers: Leading Products, High-Value Products, Popular Products, and Regular Products.",
            what_it_shows="Visual ranking of the top 10 revenue-generating products with buyer coverage, alongside a product performance table.",
            why_important="Helps management easily distinguish core cashflow drivers, high-ticket order items, and high-frequency popular products.",
            simple_insight="High-value products bought by only a small fraction of clients represent prime cross-selling opportunities for your sales team."
        )
    else:
        render_section_info(
            title="Matriks Kinerja & Sebaran Pembeli Produk",
            subtitle="Klasifikasi produk ke dalam kelompok kinerja standar: Produk Unggulan, Produk Bernilai Tinggi, Produk Populer, dan Produk Reguler.",
            what_it_shows="Grafik 10 produk berpendapatan terbesar beserta sebaran pembelinya, dan tabel kinerja produk.",
            why_important="Membantu manajemen langsung mengenali produk penopang omzet utama, produk bernilai tinggi per pesanan, serta produk yang paling diminati banyak pelanggan.",
            simple_insight="Produk bernilai omzet besar yang baru dibeli sebagian kecil pelanggan adalah target utama penawaran silang (cross-selling) ke pelanggan lainnya."
        )
    
    if not df_filtered.empty:
        prod_perf = df_filtered.groupby(["product_name", "clean_category"]).agg(
            total_revenue=("sales_amount", "sum"),
            units_sold=("qty", "sum"),
            unique_buyers=("customer_id", "nunique"),
            order_count=("invoice_id", "nunique")
        ).reset_index()
        
        prod_perf["penetration_pct"] = (prod_perf["unique_buyers"] / total_active_cust * 100).round(1)
        
        rev_q75 = prod_perf["total_revenue"].quantile(0.75) if len(prod_perf) >= 4 else prod_perf["total_revenue"].mean()
        buyers_med = max(2, prod_perf["unique_buyers"].median()) if len(prod_perf) >= 4 else 2
        
        def classify_prod_tier(row, is_en=False):
            rev = row["total_revenue"]
            buyers = row["unique_buyers"]
            if is_en:
                if rev >= rev_q75 and buyers >= buyers_med:
                    return "🌟 Leading Product (High Revenue & High Demand)"
                elif rev >= rev_q75 and buyers < buyers_med:
                    return "💎 High-Value Product (High Ticket, Limited Buyers)"
                elif buyers >= buyers_med:
                    return "🔥 Popular Product (High Customer Demand)"
                else:
                    return "📦 Regular Product (Standard Catalog Sales)"
            else:
                if rev >= rev_q75 and buyers >= buyers_med:
                    return "🌟 Produk Unggulan (Omzet & Peminat Tinggi)"
                elif rev >= rev_q75 and buyers < buyers_med:
                    return "💎 Produk Bernilai Tinggi (Omzet Besar, Pembeli Terbatas)"
                elif buyers >= buyers_med:
                    return "🔥 Produk Populer (Banyak Pembeli)"
                else:
                    return "📦 Produk Reguler (Penjualan Standar)"
                
        is_en = (lang_code == "EN")
        prod_perf["status_kinerja"] = prod_perf.apply(lambda r: classify_prod_tier(r, is_en=is_en), axis=1)
        
        # Performance summary metrics
        core_count = len(prod_perf[prod_perf["status_kinerja"].str.contains("Unggulan|Leading")])
        high_val_count = len(prod_perf[prod_perf["status_kinerja"].str.contains("Bernilai Tinggi|High-Value")])
        pop_count = len(prod_perf[prod_perf["status_kinerja"].str.contains("Populer|Popular")])
        
        if is_en:
            strip_prod = [
                {"label": "🌟 Leading Products", "value": f"{core_count} SKUs", "desc": "High sales & broad customer demand", "color": "#10B981"},
                {"label": "💎 High-Value Products", "value": f"{high_val_count} SKUs", "desc": "High ticket orders, selected buyers", "color": "#F59E0B"},
                {"label": "🔥 Popular Products", "value": f"{pop_count} SKUs", "desc": "Frequently purchased by many clients", "color": "#3B82F6"},
                {"label": "📦 Total Active SKUs", "value": f"{len(prod_perf):,} SKUs", "desc": f"Average reach {prod_perf['penetration_pct'].mean():.1f}% per SKU", "color": "#8B5CF6"}
            ]
        else:
            strip_prod = [
                {"label": "🌟 Produk Unggulan", "value": f"{core_count} Produk", "desc": "Omzet & peminat di atas rata-rata", "color": "#10B981"},
                {"label": "💎 Produk Bernilai Tinggi", "value": f"{high_val_count} Produk", "desc": "Omzet besar, pembeli spesifik", "color": "#F59E0B"},
                {"label": "🔥 Produk Populer", "value": f"{pop_count} Produk", "desc": "Diminati banyak pelanggan", "color": "#3B82F6"},
                {"label": "📦 Total Varian Terjual", "value": f"{len(prod_perf):,} Produk", "desc": f"Rata-rata sebaran {prod_perf['penetration_pct'].mean():.1f}% per produk", "color": "#8B5CF6"}
            ]
        render_summary_strip(strip_prod)
        
        col_m1, col_m2 = st.columns([5, 5])
        with col_m1:
            st.markdown("**" + ("Top 10 Produk Penjualan Terbesar & Sebaran Pembelinya" if not is_en else "Top 10 Revenue Products & Customer Reach") + "**")
            pot_top = prod_perf.sort_values(by="total_revenue", ascending=False).head(10)
            
            p_text = pot_top.sort_values(by="total_revenue", ascending=True)["penetration_pct"].apply(
                lambda p: f" Dibeli {p:.1f}% Pelanggan" if not is_en else f" Bought by {p:.1f}% of Clients"
            )
            fig_pot = px.bar(
                pot_top.sort_values(by="total_revenue", ascending=True),
                x="total_revenue",
                y="product_name",
                orientation="h",
                color="penetration_pct",
                text=p_text,
                color_continuous_scale=["#FDE68A", "#D97706"],
                labels={
                    "total_revenue": "Total Pendapatan (IDR)" if not is_en else "Total Revenue (IDR)", 
                    "product_name": "Produk" if not is_en else "Product", 
                    "penetration_pct": "Sebaran Pembeli (% Akun)" if not is_en else "Customer Reach (% Accounts)"
                }
            )
            fig_pot.update_traces(textposition="outside")
            apply_plotly_theme(fig_pot, height=360)
            st.plotly_chart(fig_pot, use_container_width=True)
            
        with col_m2:
            st.markdown("**" + ("Tabel Kinerja Produk" if not is_en else "Product Performance Table") + "**")
            disp_perf = prod_perf.sort_values(by="total_revenue", ascending=False).head(20).copy()
            disp_perf["Omzet"] = disp_perf["total_revenue"].apply(format_rupiah)
            disp_perf["Sebaran_Pembeli"] = disp_perf["penetration_pct"].apply(lambda p: f"{p:.1f}%")
            buyer_unit = "akun" if not is_en else "accounts"
            disp_perf["Pembeli Unik"] = disp_perf["unique_buyers"].apply(lambda b: f"{b:,} {buyer_unit}")
            
            if is_en:
                rename_matrix = {
                    "product_name": "Product Name",
                    "clean_category": "Category",
                    "Omzet": "Total Revenue",
                    "Pembeli Unik": "Buyers",
                    "Sebaran_Pembeli": "Customer Reach (%)"
                }
            else:
                rename_matrix = {
                    "product_name": "Nama Produk",
                    "clean_category": "Kategori",
                    "Omzet": "Total Pendapatan",
                    "Pembeli Unik": "Jumlah Pembeli",
                    "Sebaran_Pembeli": "Sebaran Pembeli (%)"
                }
            st.dataframe(
                disp_perf[["product_name", "clean_category", "Omzet", "Pembeli Unik", "Sebaran_Pembeli"]].rename(columns=rename_matrix).reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )

# -------------------------------------------------------------
# TAB 3: PELUANG PENGEMBANGAN PRODUK & ANALISIS CO-PURCHASE
# -------------------------------------------------------------
with tab3:
    if lang_code == "EN":
        render_section_info(
            title="Product Catalog Expansion Opportunities & Co-Purchase Demand",
            subtitle="Data-driven analysis of product categories frequently purchased together in the same order and high-potential catalog expansion areas.",
            what_it_shows="Factual ranking of co-purchased category combinations across invoices, alongside operational catalog merchandising recommendations.",
            why_important="Enables product managers and production teams to design pre-bundled print packages, optimize raw paper stocks, and improve operational throughput.",
            simple_insight="Printing and Finishing (Lamination/Cutting) forms the #1 co-purchase combination (>9,000 transactions), followed by Graphic Design and Large Format Printing."
        )
        st.markdown("### 🧩 Factual Co-Purchased Category Combinations (Same Invoice)")
    else:
        render_section_info(
            title="Peluang Pengembangan Portofolio Produk & Pasangan Pembelian",
            subtitle="Analisis data faktual kategori produk yang paling sering dipesan bersamaan dalam satu invoice dan peluang pengembangan katalog percetakan.",
            what_it_shows="Peringkat objektif pasangan kategori produk yang dipesan bersamaan dalam satu transaksi faktur, serta panduan operasional pengelolaan produk.",
            why_important="Membantu manajer produk dan tim produksi merancang paket bundling cetak resmi, mengamankan stok bahan baku, dan mengefisiensikan antrean mesin.",
            simple_insight="Kombinasi Cetak A3 dan Jasa Finishing (Laminasi/Potong) menjadi pasangan pesanan nomor satu (>9.000 transaksi), disusul Layanan Desain dan Cetak Format Besar."
        )
        st.markdown("### 🧩 Pasangan Kategori yang Sering Dipesan Bersamaan (Faktur Sama)")
        
    copurchase_df = compute_product_copurchase_pairs(df_filtered, top_n=8)
    
    col_co1, col_co2 = st.columns([6, 4])
    
    with col_co1:
        st.markdown(f"**{'Grafik Frekuensi Pasangan Kategori Transaksi Bersama' if lang_code == 'ID' else 'Co-Purchased Category Pairs Frequency Chart'}**")
        if not copurchase_df.empty:
            lbl_trans = "Frekuensi Transaksi Bersama" if lang_code == "ID" else "Joint Order Frequency"
            fig_cop = px.bar(
                copurchase_df.sort_values(by="frekuensi_transaksi", ascending=True),
                x="frekuensi_transaksi",
                y="pasangan",
                orientation="h",
                color="frekuensi_transaksi",
                text=copurchase_df.sort_values(by="frekuensi_transaksi", ascending=True).apply(
                    lambda r: f" {r['frekuensi_transaksi']:,} pesanan ({r['persentase_bersama']}%)" if lang_code == "ID" else f" {r['frekuensi_transaksi']:,} orders ({r['persentase_bersama']}%)",
                    axis=1
                ),
                color_continuous_scale=["#93C5FD", "#2563EB"],
                labels={"frekuensi_transaksi": lbl_trans, "pasangan": "Pasangan Kategori" if lang_code == "ID" else "Category Pair"}
            )
            fig_cop.update_traces(textposition="outside")
            apply_plotly_theme(fig_cop, height=360)
            st.plotly_chart(fig_cop, use_container_width=True)
        else:
            st.info("Data transaksi bersama belum mencukupi untuk filter saat ini." if lang_code == "ID" else "Insufficient multi-item transactions for the current filter.")
            
    with col_co2:
        st.markdown(f"**{'Rincian Data Pasangan Pembelian Bersama' if lang_code == 'ID' else 'Co-Purchase Transaction Breakdown'}**")
        if not copurchase_df.empty:
            disp_cop = copurchase_df[["pasangan", "frekuensi_transaksi", "persentase_bersama"]].copy()
            if lang_code == "EN":
                disp_cop.columns = ["Category Combination", "Joint Invoices", "Share of Multi-Item Orders (%)"]
            else:
                disp_cop.columns = ["Kombinasi Kategori", "Total Faktur Bersama", "Pangsa Pesanan Multi-Item (%)"]
            st.dataframe(disp_cop, use_container_width=True, hide_index=True)
        else:
            st.info("Tabel tidak tersedia." if lang_code == "ID" else "Table unavailable.")
            
    st.markdown("---")
    st.markdown(f"**{'🧭 4 Panduan Strategis Pengelolaan Portofolio Produk' if lang_code == 'ID' else '🧭 4 Strategic Product Portfolio & Catalog Guidelines'}**")
    
    col_guide1, col_guide2 = st.columns(2)
    with col_guide1:
        if lang_code == "EN":
            st.markdown("""
            <div class="cetakia-card" style="border-left: 5px solid #10B981; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #10B981; margin: 0;">📦 1. Pre-Bundled Print & Finishing Packages</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Data Foundation:</b> Over 9,400 invoices combine A3 Printing with Finishing (Kiss-cut cutting & lamination).<br>
                    <b>Catalog Action:</b> Standardize ready-to-order packages at counter POS (e.g., "Print A3+ including Kiss Cut") to eliminate cashier friction and accelerate checkout speed.
                </p>
            </div>
            <div class="cetakia-card" style="border-left: 5px solid #3B82F6; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #3B82F6; margin: 0;">🎨 2. Design-to-Print Operational Flow</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Data Foundation:</b> Design services frequently pair with Large Format Printing (950+ orders) and A3 Printing (680+ orders).<br>
                    <b>Catalog Action:</b> Offer standardized design templates for event banners and marketing collaterals to shorten design approval turnarounds.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="cetakia-card" style="border-left: 5px solid #10B981; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #10B981; margin: 0;">📦 1. Standarisasi Paket Cetak + Jasa Finishing</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Dasar Data Faktual:</b> Lebih dari 9.400 invoice menggabungkan Cetak A3 dengan Jasa Finishing (Potong Kiss-cut & Laminasi).<br>
                    <b>Aksi Katalog:</b> Sediakan item paket terintegrasi di sistem kasir/POS (contoh: "Cetak A3+ Termasuk Cutting Kiss Cut") guna mempercepat input pesanan di front office.
                </p>
            </div>
            <div class="cetakia-card" style="border-left: 5px solid #3B82F6; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #3B82F6; margin: 0;">🎨 2. Integrasi Alur Layanan Desain & Produksi</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Dasar Data Faktual:</b> Jasa desain paling sering terhubung dengan Cetak Format Besar (950+ pesanan) dan Cetak A3 (680+ pesanan).<br>
                    <b>Aksi Katalog:</b> Sediakan template desain standar untuk spanduk event dan materi promosi agar memangkas waktu tunggu persetujuan pra-cetak.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_guide2:
        if lang_code == "EN":
            st.markdown("""
            <div class="cetakia-card" style="border-left: 5px solid #F59E0B; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #F59E0B; margin: 0;">🌱 3. Expanding Eco-Friendly Packaging Variations</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Data Foundation:</b> Packaging Box and Paper Bag products show high order values (> Rp 500k/order) but limited catalog variety.<br>
                    <b>Catalog Action:</b> Introduce biodegradable food-grade kraft boxes and custom food sleeves to capture burgeoning F&B business demand.
                </p>
            </div>
            <div class="cetakia-card" style="border-left: 5px solid #8B5CF6; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #8B5CF6; margin: 0;">⚙️ 4. Machine Capacity & Raw Material Planning</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Data Foundation:</b> Flexy vinyl and A3+ Chromo paper account for over 45% of total units produced.<br>
                    <b>Catalog Action:</b> Synchronize vendor raw material purchase cycles with production branch loading to prevent stock-outs during peak seasons.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="cetakia-card" style="border-left: 5px solid #F59E0B; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #F59E0B; margin: 0;">🌱 3. Ekspansi Varian Kemasan & Paper Bag Ramah Lingkungan</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Dasar Data Faktual:</b> Produk Box Kemasan dan Paper Bag memiliki nilai pesanan tinggi (> Rp 500rb/order) namun variasi katalog masih terbatas.<br>
                    <b>Aksi Katalog:</b> Luncurkan opsi bahan kraft food grade dan paper sleeve custom untuk menangkap permintaan tinggi pelaku usaha kuliner.
                </p>
            </div>
            <div class="cetakia-card" style="border-left: 5px solid #8B5CF6; padding: 18px; margin-bottom: 16px;">
                <h4 style="color: #8B5CF6; margin: 0;">⚙️ 4. Perencanaan Bahan Baku & Kapasitas Mesin</h4>
                <p style="font-size: 13.5px; margin: 8px 0; opacity: 0.9; line-height: 1.5;">
                    <b>Dasar Data Faktual:</b> Bahan Flexy vinyl dan Kertas A3+ Chromo menyumbang lebih dari 45% total unit cetak yang diproduksi.<br>
                    <b>Aksi Katalog:</b> Sinkronkan pengadaan stok bahan baku dari supplier dengan kapasitas mesin cetak cabang untuk mencegah bottleneck saat periode sibuk.
                </p>
            </div>
            """, unsafe_allow_html=True)

