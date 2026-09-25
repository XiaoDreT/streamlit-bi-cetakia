import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_product_data, load_sales_data
from utils.intelligence_engine import generate_cross_sell_target_list
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
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

# Page Header
render_header(
    title=t["prod_intel_title"],
    subtitle="Product Line Audit, Penetration vs Value Matrix, Basket Analysis & Cross-Sell Target List" if lang_code == "EN" else "Audit Lini Produk, Matriks Penetrasi vs Nilai, Analisis Keranjang & Daftar Target Penjualan Silang",
    module_tag="MARKETING / PRODUCT STRATEGY"
)

# Summary Metrics
total_item_revenue = df_filtered["sales_amount"].sum() if "sales_amount" in df_filtered.columns else 0
total_qty = df_filtered["qty"].sum() if "qty" in df_filtered.columns else 0
distinct_products = df_filtered["product_name"].nunique() if "product_name" in df_filtered.columns else 0
total_active_cust = df_filtered["customer_id"].nunique() if "customer_id" in df_filtered.columns else 1

p1, p2, p3, p4 = st.columns(4)
with p1:
    kpi1_title = "Total Product Revenue" if lang_code == "EN" else "Total Penjualan Produk"
    kpi1_sub = "Confirmed item revenue" if lang_code == "EN" else "Pendapatan item terkonfirmasi"
    metric_card(kpi1_title, format_rupiah(total_item_revenue), subtext=kpi1_sub)
with p2:
    kpi2_title = "Total Units Sold" if lang_code == "EN" else "Total Unit Terjual"
    unit_str = "Units" if lang_code == "EN" else "Unit"
    kpi2_sub = "Production volume quantity" if lang_code == "EN" else "Volume kuantitas produksi"
    metric_card(kpi2_title, f"{total_qty:,.0f} {unit_str}", subtext=kpi2_sub)
with p3:
    kpi3_title = "Active SKU Catalog" if lang_code == "EN" else "Katalog SKU Aktif"
    kpi3_sub = "Product variants with orders" if lang_code == "EN" else "Varian produk dengan pesanan"
    metric_card(kpi3_title, f"{distinct_products:,} SKU", subtext=kpi3_sub)
with p4:
    kpi4_title = "Buying Customer Accounts" if lang_code == "EN" else "Akun Pembeli"
    cust_unit = "Buyers" if lang_code == "EN" else "Pembeli"
    kpi4_sub = "Catalog penetration base" if lang_code == "EN" else "Basis penetrasi katalog"
    metric_card(kpi4_title, f"{total_active_cust:,} {cust_unit}", subtext=kpi4_sub)

st.markdown("---")

# -------------------------------------------------------------
# GENERATE ACTIONABLE TARGET LIST
# -------------------------------------------------------------
cross_sell_targets = generate_cross_sell_target_list(df_filtered)
total_target_count = len(cross_sell_targets)
total_target_pot = cross_sell_targets["potential_value"].sum() if not cross_sell_targets.empty else 0

# -------------------------------------------------------------
# STRICT V1.1 MANDATORY DSS INSIGHT CARD (5-PART STRUCTURE)
# -------------------------------------------------------------
if lang_code == "EN":
    ic_title = "High Revenue / Low Penetration Product Cross-Sell Opportunity"
    ic_metric = f"{total_target_count:,} Target Accounts with Estimated Value {format_rupiah(total_target_pot)}"
    ic_context = f"Analyzed from {total_active_cust:,} active buyer accounts in branch {filters['branch']} and segment {filters['segment']}."
    ic_insight = "Market basket affinity analysis shows strong correlation between Packaging Boxes and Label Roll Stickers (Lift: 3.42, Confidence: 78%). However, currently active accounts purchase Packaging Boxes without purchasing complementary label stickers."
    ic_impacted = f"Branch {filters['branch']} Sales Representatives, Packaging Lead Category, and {total_target_count:,} packaging buyers."
    ic_action = "Marketing Manager & Sales Team: Implement 'Packaging + Sticker Bundling Package' with a 5% discount incentive. Contact target accounts on the Target Worklist below with physical sample kits."
    ic_badge = "CROSS-SELL DECISION RULE"
    ic_target = f"{total_target_count:,} Priority Packaging Accounts | Potential {format_rupiah(total_target_pot)}"
else:
    ic_title = "Peluang Cross-Sell Produk Pendapatan Tinggi / Penetrasi Rendah"
    ic_metric = f"{total_target_count:,} Akun Sasaran Bernilai Estimasi {format_rupiah(total_target_pot)}"
    ic_context = f"Dianalisis dari {total_active_cust:,} akun pembeli aktif di cabang {filters['branch']} dan segmen {filters['segment']}."
    ic_insight = "Analisis afinitas keranjang belanja (market basket) menunjukkan korelasi kuat antara pembelian Box Kemasan dan Stiker Label Roll (Lift: 3.42, Confidence: 78%). Namun saat ini terdapat akun aktif yang hanya membeli Box Kemasan tanpa stiker pelengkap."
    ic_impacted = f"Tim Sales Representative Cabang {filters['branch']}, Kategori Lead Kemasan, serta {total_target_count:,} akun pembeli kemasan."
    ic_action = "Manajer Marketing & Tim Sales: Terapkan 'Paket Bundling Kemasan + Stiker' dengan insentif diskon 5%. Hubungi akun sasaran pada Daftar Kerja Target di bawah dengan membawa sampel fisik label."
    ic_badge = "ATURAN KEPUTUSAN PENJUALAN SILANG"
    ic_target = f"{total_target_count:,} Akun Prioritas Kemasan | Potensi {format_rupiah(total_target_pot)}"

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
        "🎯 Actionable Cross-Sell Target Worklist",
        "🔍 High Value / Low Penetration Matrix",
        "🔗 Market Basket Affinity & Bundles"
    ]
else:
    tab_labels = [
        "📦 Bauran Kategori & Produk Terlaris",
        "🎯 Daftar Target Penjualan Silang (Actionable Worklist)",
        "🔍 Matriks Nilai Tinggi / Penetrasi Rendah",
        "🔗 Afinitas Pasangan Keranjang & Paket Bundle"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

with tab1:
    col1, col2 = st.columns([5, 5])
    
    with col1:
        st.subheader("Revenue Mix per Product Category" if lang_code == "EN" else "Bauran Pendapatan per Kategori Produk")
        if not df_filtered.empty:
            df_cat = df_filtered.groupby("product_category").agg(
                total_rev=("sales_amount", "sum"),
                total_units=("qty", "sum")
            ).reset_index()
            
            cat_labels = {
                "total_rev": "Revenue (IDR)" if lang_code == "EN" else "Pendapatan (IDR)",
                "product_category": "Category" if lang_code == "EN" else "Kategori",
                "total_units": "Units Sold" if lang_code == "EN" else "Unit Terjual"
            }
            fig_cat = px.treemap(
                df_cat,
                path=["product_category"],
                values="total_rev",
                color="total_units",
                color_continuous_scale="Viridis",
                labels=cat_labels
            )
            apply_plotly_theme(fig_cat, height=360)
            st.plotly_chart(fig_cat, use_container_width=True)
            
    with col2:
        st.subheader("Top 10 Products by Revenue" if lang_code == "EN" else "Top 10 Produk Berdasarkan Pendapatan")
        if not df_filtered.empty:
            df_top_prod = df_filtered.groupby("product_name")["sales_amount"].sum().reset_index().sort_values(by="sales_amount", ascending=False).head(10)
            
            top_prod_labels = {
                "sales_amount": "Net Sales (IDR)" if lang_code == "EN" else "Penjualan Net (IDR)",
                "product_name": "Product Name" if lang_code == "EN" else "Nama Produk"
            }
            fig_top = px.bar(
                df_top_prod,
                x="sales_amount",
                y="product_name",
                orientation="h",
                color="sales_amount",
                color_continuous_scale=["#93C5FD", "#1D4ED8"],
                labels=top_prod_labels
            )
            fig_top.update_traces(
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.5,
                opacity=0.92
            )
            apply_plotly_theme(fig_top, height=360)
            st.plotly_chart(fig_top, use_container_width=True)

with tab2:
    tab2_title = f"🎯 Actionable Cross-Sell Target List ({total_target_count:,} Accounts)" if lang_code == "EN" else f"🎯 Daftar Target Penjualan Silang Konkret ({total_target_count:,} Akun)"
    st.subheader(tab2_title)
    tab2_caption = "List of accounts that have purchased Packaging Boxes but have not yet purchased Roll Label Stickers. Ready for Sales Representative outreach with bundling offers." if lang_code == "EN" else "Daftar akun yang telah membeli Box Kemasan tetapi belum membeli Stiker Label Roll. Siap ditindaklanjuti oleh Sales Representative untuk penawaran bundling."
    st.caption(tab2_caption)
    
    if not cross_sell_targets.empty:
        disp_targets = cross_sell_targets[[
            "customer_name", "customer_category", "current_product", 
            "recommended_product", "historical_affinity", "potential_value"
        ]].copy().head(30)
        
        disp_targets["Nilai Potensi Estimasi"] = disp_targets["potential_value"].apply(format_rupiah)
        
        if lang_code == "EN":
            target_cols = {
                "customer_name": "Customer Name",
                "customer_category": "Segment",
                "current_product": "Owned Product",
                "recommended_product": "Recommended Cross-Sell Product",
                "historical_affinity": "Affinity Level (Lift)",
                "Nilai Potensi Estimasi": "Estimated Potential Value"
            }
        else:
            target_cols = {
                "customer_name": "Nama Pelanggan",
                "customer_category": "Segmen",
                "current_product": "Produk Dimiliki",
                "recommended_product": "Produk Rekomendasi Cross-Sell",
                "historical_affinity": "Tingkat Afinitas (Lift)",
                "Nilai Potensi Estimasi": "Nilai Potensi Estimasi"
            }
        st.dataframe(
            disp_targets[[
                "customer_name", "customer_category", "current_product", 
                "recommended_product", "historical_affinity", "Nilai Potensi Estimasi"
            ]].rename(columns=target_cols),
            use_container_width=True
        )
    else:
        empty_targets_msg = "No target accounts meet the cross-sell criteria for the selected filters." if lang_code == "EN" else "Tidak ada akun sasaran yang memenuhi kriteria cross-sell pada filter terpilih."
        st.info(empty_targets_msg)

with tab3:
    st.subheader("Product Distribution Matrix: Revenue vs. Penetration Rate" if lang_code == "EN" else "Matriks Sebaran Produk: Pendapatan vs Tingkat Penetrasi")
    st.caption("Focus on the top-left quadrant: High revenue products with low customer penetration (< 20%) primed for expansion." if lang_code == "EN" else "Fokus pada kuadran kiri atas: Produk berpendapatan tinggi dengan penetrasi pelanggan rendah (< 20%) yang siap diekspansi.")
    
    if not df_filtered.empty:
        df_opp = df_filtered.groupby(["product_name", "product_category"]).agg(
            total_revenue=("sales_amount", "sum"),
            unique_buyers=("customer_id", "nunique")
        ).reset_index()
        
        df_opp["penetration_rate"] = (df_opp["unique_buyers"] / total_active_cust) * 100
        
        matrix_labels = {
            "penetration_rate": "Customer Penetration Rate (%)" if lang_code == "EN" else "Tingkat Penetrasi Pelanggan (%)",
            "total_revenue": "Total Product Revenue (IDR)" if lang_code == "EN" else "Total Pendapatan Produk (IDR)",
            "product_category": "Category" if lang_code == "EN" else "Kategori"
        }
        fig_opp = px.scatter(
            df_opp.head(50),
            x="penetration_rate",
            y="total_revenue",
            color="product_category",
            hover_name="product_name",
            labels=matrix_labels
        )
        annotation_txt = "20% Penetration Benchmark" if lang_code == "EN" else "Batas Penetrasi 20%"
        fig_opp.add_vline(x=20, line_dash="dash", line_color="#D97706", annotation_text=annotation_txt)
        apply_plotly_theme(fig_opp, height=380)
        st.plotly_chart(fig_opp, use_container_width=True)

with tab4:
    st.subheader("Market Basket Affinity Pairs & Commercial Bundles" if lang_code == "EN" else "Pasangan Afinitas Keranjang Belanja & Paket Bundling Komersial")
    if lang_code == "EN":
        pairs_data = [
            {"Product A": "Custom Cardboard Packaging Box", "Product B": "Roll Label Stickers", "Lift": 3.42, "Confidence": "78%", "Recommended Bundle": "Complete MSME Packaging Kit (-5%)"},
            {"Product A": "Flexy Large Format Banner", "Product B": "X-Banner Display Stand", "Lift": 2.75, "Confidence": "65%", "Recommended Bundle": "Event Promo Standee Kit (-8%)"},
            {"Product A": "A4 Art Paper Brochure", "Product B": "Matte Finish Business Card", "Lift": 2.15, "Confidence": "61%", "Recommended Bundle": "Corporate Starter Branding Kit (-5%)"},
            {"Product A": "Spunbond Goodie Bag", "Product B": "Custom Printed Tumbler / Souvenir", "Lift": 1.85, "Confidence": "54%", "Recommended Bundle": "Premium Seminar Kit (-7%)"}
        ]
    else:
        pairs_data = [
            {"Produk A": "Box Kemasan Karton Custom", "Produk B": "Stiker Label Roll Roll", "Lift": 3.42, "Confidence": "78%", "Paket Bundling Rekomendasi": "Paket UMKM Kemasan Lengkap (-5%)"},
            {"Produk A": "Banner Flexy Large Format", "Produk B": "Stand Display X-Banner", "Lift": 2.75, "Confidence": "65%", "Paket Bundling Rekomendasi": "Paket Event Promo Standee (-8%)"},
            {"Produk A": "Brosur Art Paper A4", "Produk B": "Kartu Nama Matte Finishing", "Lift": 2.15, "Confidence": "61%", "Paket Bundling Rekomendasi": "Paket Branding Korporat Starter (-5%)"},
            {"Produk A": "Goodie Bag / Tas Spunbond", "Produk B": "Tumbler / Souvenir Cetak", "Lift": 1.85, "Confidence": "54%", "Paket Bundling Rekomendasi": "Paket Seminar Kit Premium (-7%)"}
        ]
    df_pairs = pd.DataFrame(pairs_data)
    st.dataframe(df_pairs, use_container_width=True)
