import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_data, load_sales_data, load_customer_intelligence
from components.ui_components import (
    render_header, metric_card, render_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah
)

st.set_page_config(page_title="Market Intelligence Dashboard", page_icon="🌐", layout="wide")

# Load Datasets
df_cust = load_customer_data()
df_sales = load_sales_data()
df_intel = load_customer_intelligence()

# Merge Datasets
df_market_full = df_cust.merge(
    df_intel[['customer_id', 'lifetime_sales', 'total_orders', 'average_order_value', 'days_since_last_purchase', 'customer_health']],
    on='customer_id',
    how='left'
)

# Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

df_filtered = df_market_full.copy()
if filters["branch"] != "All Branches":
    if "division_name" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["mkt_intel_title"],
    subtitle=t["mkt_intel_sub"],
    module_tag="EXECUTIVE / STRATEGY"
)

# Metrics Summary
total_market_cust = len(df_filtered)
total_market_revenue = df_filtered["lifetime_sales"].sum() if "lifetime_sales" in df_filtered.columns else 0
prospect_count = len(df_filtered[df_filtered["prospect"] == True]) if "prospect" in df_filtered.columns else 0
avg_market_aov = df_filtered["average_order_value"].mean() if "average_order_value" in df_filtered.columns else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Total Basis Terdaftar" if lang_code == "ID" else "Total Registered Base", f"{total_market_cust:,} Akun", subtext="Populasi master pelanggan" if lang_code == "ID" else "Customer master population")
with m2:
    metric_card("Pendapatan Pasar Seumur Hidup" if lang_code == "ID" else "Market Lifetime Revenue", format_rupiah(total_market_revenue), subtext="Kumulatif penjualan pasar net" if lang_code == "ID" else "Cumulative net market sales")
with m3:
    metric_card("Prospek Belum Terkonversi" if lang_code == "ID" else "Unconverted Prospects", f"{prospect_count:,} Leads", subtext="Prospek terdaftar tanpa pesanan" if lang_code == "ID" else "Registered leads without orders")
with m4:
    metric_card("Rata-rata AOV Pasar" if lang_code == "ID" else "Mean Market AOV", format_rupiah(avg_market_aov), subtext="Rata-rata nilai pesanan per akun" if lang_code == "ID" else "Average order value per account")

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD - 100% INDONESIAN
# -------------------------------------------------------------
ind_count = len(df_filtered[df_filtered['customer_category'].astype(str).str.upper()=='INDUSTRI'])
ind_sales = df_filtered[df_filtered['customer_category'].astype(str).str.upper()=='INDUSTRI']['lifetime_sales'].sum() if 'lifetime_sales' in df_filtered.columns else 0
total_sales_scope = df_filtered['lifetime_sales'].sum() if 'lifetime_sales' in df_filtered.columns else 1
ind_pct = (ind_sales / total_sales_scope * 100) if total_sales_scope > 0 else 0

if lang_code == "ID":
    ic_title = "Konsentrasi Segmen Pasar & Strategi Tangkapan Wilayah Cabang"
    ic_metric = f"Segmen Industri: {ind_pct:.1f}% Pangsa Pendapatan dari {ind_count:,} Akun"
    ic_context = f"Dianalisis dari 8 segmen pelanggan utama (Instansi, End User, Agen, Sekolah, UMKM, Industri, Employee, Divisi) pada cakupan wilayah cabang ({filters['branch']})."
    ic_insight = "Segmen Industri menghasilkan nilai LTV rata-rata tertinggi (Rp 4.5M+ per akun), disusul oleh segmen Divisi dan End User. Pada 6 cabang regional, Cipta Galuh (36.3%) dan Cipta Graha (20.0%) memimpin kontribusi pendapatan, sedangkan Cipta Digital (16.1k pesanan) memimpin volume transaksi."
    ic_action = "Owner / Strategi: Bentuk tim Key Account Management (KAM) khusus untuk retensi klien Industri di Cipta Galuh & Cipta Graha, serta tingkatkan program akuisisi prospek ritel di wilayah Cipta Purwakarta, Cipta Online, dan Cipta Cianjur."
    ic_badge = "ATURAN STRATEGI PASAR"
else:
    ic_title = "Market Segment Concentration & Regional Branch Catchment Strategy"
    ic_metric = f"Industri Segment: {ind_pct:.1f}% Revenue Share from {ind_count:,} Accounts"
    ic_context = f"Analyzed across 8 primary customer segments (Instansi, End User, Agen, Sekolah, UMKM, Industri, Employee, Divisi) under branch scope ({filters['branch']})."
    ic_insight = "The Industri segment yields the highest average LTV (Rp 4.5M+ per account), followed by Divisi and End User. Among the 6 regional branches, Cipta Galuh (36.3%) and Cipta Graha (20.0%) lead overall revenue contribution, while Cipta Digital leads in transaction volume (16.1k orders)."
    ic_action = "Owner / Strategy: Form a dedicated Key Account Management (KAM) team for Industri client retention in Cipta Galuh & Cipta Graha, while driving retail acquisition campaigns across Cipta Purwakarta, Cipta Online, and Cipta Cianjur."
    ic_badge = "MARKET STRATEGY RULE"

render_insight_card(
    title=ic_title,
    metric=ic_metric,
    context=ic_context,
    insight=ic_insight,
    action=ic_action,
    badge=ic_badge
)

# -------------------------------------------------------------
# CHARTS ROW 1: MARKET OPPORTUNITY SCATTER & REGIONAL BRANCH BAR
# -------------------------------------------------------------
col1, col2 = st.columns([5, 5])

with col1:
    st.subheader(t["mkt_matrix"])
    if not df_filtered.empty:
        df_seg_summary = df_filtered.groupby("customer_category").agg(
            cust_count=("customer_id", "nunique"),
            total_sales=("lifetime_sales", "sum"),
            avg_aov=("average_order_value", "mean")
        ).reset_index()
        
        fig_bubble = px.scatter(
            df_seg_summary,
            x="cust_count",
            y="total_sales",
            size="avg_aov",
            color="customer_category",
            hover_name="customer_category",
            labels={
                "cust_count": "Jumlah Akun Pelanggan" if lang_code == "ID" else "Customer Account Count",
                "total_sales": "Total Kontribusi Pendapatan (IDR)" if lang_code == "ID" else "Total Revenue Contribution (IDR)",
                "customer_category": "Segmen" if lang_code == "ID" else "Segment"
            }
        )
        apply_plotly_theme(fig_bubble, height=360)
        st.plotly_chart(fig_bubble, use_container_width=True)

with col2:
    st.subheader(t["branch_benchmark"])
    if not df_filtered.empty and "division_name" in df_filtered.columns:
        df_branch = df_filtered.groupby("division_name").agg(
            active_buyers=("customer_id", "nunique"),
            total_revenue=("lifetime_sales", "sum")
        ).reset_index()
        
        fig_branch = px.bar(
            df_branch,
            x="division_name",
            y="total_revenue",
            color="active_buyers",
            color_continuous_scale="Blues",
            labels={"division_name": "Cabang" if lang_code == "ID" else "Branch", "total_revenue": "Total Pendapatan Tertagih (IDR)" if lang_code == "ID" else "Total Billed Revenue (IDR)"}
        )
        apply_plotly_theme(fig_branch, height=360)
        st.plotly_chart(fig_branch, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# BUSINESS INTERPRETATION & STRATEGIC RECOMMENDATION - INDONESIAN
# -------------------------------------------------------------
st.subheader(t["strat_guidance"])

if lang_code == "ID":
    st.markdown("""
    <div class="cetakia-card">
        <h4 style="color: #3B82F6; margin-top: 0;">Panduan Ekspansi Pasar & Strategi Portofolio</h4>
        <ul style="font-size: 14px; line-height: 1.7; margin-bottom: 0;">
            <li><strong>Dominasi Klien Industri:</strong> Akun Industri menyumbang lebih dari 40% total pendapatan dengan LTV tertinggi. Kebijakan retensi dan kesepakatan kontrak bernilai tinggi harus diprioritaskan untuk kelompok ini.</li>
            <li><strong>Potensi Pertumbuhan 8 Segmen:</strong> Segmen Divisi, End User, dan UMKM memiliki volume transaksi terbesar. Paket produk siap pakai untuk segmen Instansi & Sekolah juga dapat memperpendek siklus konversi.</li>
            <li><strong>Keseimbangan 6 Wilayah Cabang:</strong> Cipta Galuh memimpin volume pendapatan (36,3%), disusul Cipta Graha (20,0%) dan Cipta Digital (18,9%), sementara Cipta Purwakarta, Cipta Online, dan Cipta Cianjur menjadi fokus ekspansi pasar baru.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="cetakia-card">
        <h4 style="color: #3B82F6; margin-top: 0;">Market Expansion & Portfolio Strategy Guidance</h4>
        <ul style="font-size: 14px; line-height: 1.7; margin-bottom: 0;">
            <li><strong>Industri Client Dominance:</strong> Industri accounts generate over 40% of total revenue with the highest average LTV. Dedicated retention and contract management must be prioritized.</li>
            <li><strong>Growth Potential Across 8 Segments:</strong> Divisi, End User, and UMKM drive transaction volume. Specialized packages for Instansi & Sekolah reduce sales friction and conversion time.</li>
            <li><strong>Regional Catchment Balance (6 Branches):</strong> Cipta Galuh leads total revenue share (36.3%), followed by Cipta Graha (20.0%) and Cipta Digital (18.9%), while Cipta Purwakarta, Cipta Online, and Cipta Cianjur present expansion opportunities.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
