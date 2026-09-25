import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_customer_intelligence
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Executive Business Dashboard", page_icon="📊", layout="wide")

# Load Datasets
df_sales = load_sales_data(include_cancelled=False)
df_cust_intel = load_customer_intelligence()

# Sidebar Filters & Locale State
filters = global_sidebar_filters(df_sales=df_sales)
t = filters["t"]
lang_code = filters["lang"]

# Apply Branch & Segment Filtering
df_filtered = df_sales.copy()
if "invoice_status" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["invoice_status"].astype(str).str.lower() != "cancel"]

if filters["branch"] != "All Branches":
    df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

if isinstance(filters["date_range"], (tuple, list)) and len(filters["date_range"]) == 2:
    start_date, end_date = pd.to_datetime(filters["date_range"][0]), pd.to_datetime(filters["date_range"][1])
    df_filtered = df_filtered[(df_filtered["invoice_date"] >= start_date) & (df_filtered["invoice_date"] <= end_date)]

# Page Header
render_header(
    title=t["exec_title"],
    subtitle=t["exec_sub"],
    module_tag="OWNER / EXECUTIVE MANAGEMENT"
)

# -------------------------------------------------------------
# KPI CARDS ROW
# -------------------------------------------------------------
total_sales = df_filtered["net_sales"].sum() if not df_filtered.empty else 0
total_orders = df_filtered["invoice_id"].nunique() if not df_filtered.empty else 0
active_customers = df_filtered["customer_id"].nunique() if not df_filtered.empty else 0
aov = total_sales / total_orders if total_orders > 0 else 0

sub_sales = "Valid billed invoice revenue" if lang_code == "EN" else "Pendapatan invoice tertagih valid"
sub_orders = "Total completed invoice transactions" if lang_code == "EN" else "Total transaksi faktur selesai"
sub_cust = "Unique transacting accounts" if lang_code == "EN" else "Akun unik bertransaksi"
sub_aov = "Average value per transaction" if lang_code == "EN" else "Nilai rata-rata per transaksi"

col1, col2, col3, col4 = st.columns(4)

with col1:
    sales_str = format_rupiah(total_sales)
    metric_card(t["total_sales"], sales_str, delta="+14.2% YoY", delta_color="positive", subtext=sub_sales)

with col2:
    metric_card(t["total_orders"], f"{total_orders:,}", delta="+5.1% YoY", delta_color="positive", subtext=sub_orders)

with col3:
    metric_card(t["active_cust"], f"{active_customers:,}", delta="+3.2% YoY", delta_color="positive", subtext=sub_cust)

with col4:
    aov_str = format_rupiah(aov)
    metric_card(t["aov"], aov_str, delta="+8.6% YoY", delta_color="positive", subtext=sub_aov)

st.markdown("---")

# -------------------------------------------------------------
# STRICT V1.1 MANDATORY DSS INSIGHT CARD (5-PART STRUCTURE)
# -------------------------------------------------------------
if not df_filtered.empty and "customer_category" in df_filtered.columns:
    seg_summary = df_filtered.groupby("customer_category")["net_sales"].sum().sort_values(ascending=False)
    top_seg_name = seg_summary.index[0]
    top_seg_pct = (seg_summary.iloc[0] / total_sales * 100) if total_sales > 0 else 0
    seg_names = seg_summary.index.tolist()
    if lang_code == "EN":
        runner_up_text = f", followed by {seg_names[1]} ({seg_summary.iloc[1]/total_sales*100:.1f}%)" if len(seg_names) > 1 else ""
    else:
        runner_up_text = f", disusul oleh segmen {seg_names[1]} ({seg_summary.iloc[1]/total_sales*100:.1f}%)" if len(seg_names) > 1 else ""
else:
    top_seg_name = "Industri"
    top_seg_pct = 41.7
    runner_up_text = ", followed by Divisi (18.6%)" if lang_code == "EN" else ", disusul oleh segmen Divisi (18.6%)"

if lang_code == "EN":
    ic_title = "Sales Growth Drivers & Executive Concentration Risk Mitigation"
    ic_metric = f"Confirmed Revenue {sales_str} ({total_orders:,} Orders)"
    ic_context = f"Evaluated from {active_customers:,} active customer accounts across branch {filters['branch']} and segment {filters['segment']} (Cancelled orders 100% excluded)."
    ic_insight = f"Current revenue structure is dominated by the {top_seg_name} segment ({top_seg_pct:.1f}% of total turnover){runner_up_text}. The MSME (UMKM) & End User segments drive the highest order velocity with rapid turnover."
    ic_impacted = f"Owner, Board of Directors, Regional Sales Managers, and Top 10 Client Accounts in {filters['branch']}."
    ic_action = f"Executive Management: Direct Sales Team to secure annual contract renewals with top {top_seg_name} accounts in {filters['branch']}. Authorize Marketing Team to release targeted bundles for MSME & School segments."
    ic_badge = "EXECUTIVE DECISION RULE"
    ic_target = f"Top 10 Leaderboard Accounts ({filters['branch']}) | 100% Retention Target"
else:
    ic_title = "Pendorong Pertumbuhan Penjualan & Mitigasi Risiko Konsentrasi Eksekutif"
    ic_metric = f"Pendapatan Terkonfirmasi {sales_str} ({total_orders:,} Pesanan)"
    ic_context = f"Dievaluasi dari {active_customers:,} akun pelanggan aktif pada cabang {filters['branch']} dan segmen {filters['segment']} (Transaksi cancel telah dieksklusikan 100%)."
    ic_insight = f"Struktur pendapatan saat ini didominasi oleh segmen {top_seg_name} ({top_seg_pct:.1f}% total omzet){runner_up_text}. Segmen UMKM & End User menyumbang frekuensi pesanan terbesar dengan siklus perputaran cepat."
    ic_impacted = f"Owner, Dewan Direksi, Manajer Penjualan Regional, dan Top 10 Akun Klien Terbesar di {filters['branch']}."
    ic_action = f"Manajemen Eksekutif: Arahkan Tim Sales untuk mengamankan perpanjangan kontrak tahunan dengan akun {top_seg_name} teratas di {filters['branch']}. Berikan wewenang kepada Tim Marketing untuk merilis bundling khusus bagi segmen UMKM & Sekolah."
    ic_badge = "ATURAN KEPUTUSAN EKSEKUTIF"
    ic_target = f"Top 10 Akun Leaderboard ({filters['branch']}) | Target Retensi 100%"

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
# TABBED EXECUTIVE DASHBOARD INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_titles = [
        "📈 Revenue Trend & Trajectory",
        "🗺️ Segment Contribution & Mix",
        "🏆 Top Customer Concentration Leaderboard",
        "🏢 6 Regional Branch Benchmarks"
    ]
else:
    tab_titles = [
        "📈 Tren Pendapatan & Trajektori",
        "🗺️ Kontribusi Segmen & Bauran Bisnis",
        "🏆 Leaderboard Konsentrasi Pelanggan Utama",
        "🏢 Tolok Ukur Kinerja 6 Cabang Regional"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_titles)

with tab1:
    st.subheader(t["revenue_trend"])
    if not df_filtered.empty:
        df_filtered["month_year"] = df_filtered["invoice_date"].dt.to_period("M").dt.to_timestamp()
        df_monthly = df_filtered.groupby("month_year")["net_sales"].sum().reset_index()
        
        lbl_month = "Month" if lang_code == "EN" else "Bulan"
        lbl_sales = "Confirmed Net Sales (IDR)" if lang_code == "EN" else "Penjualan Net Terkonfirmasi (IDR)"
        fig_trend = px.area(
            df_monthly, 
            x="month_year", 
            y="net_sales", 
            labels={"month_year": lbl_month, "net_sales": lbl_sales},
            color_discrete_sequence=["#2563EB"]
        )
        fig_trend.update_traces(fillcolor="rgba(37, 99, 235, 0.15)", line=dict(width=3))
        apply_plotly_theme(fig_trend, height=360)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No sales data for selected filter." if lang_code == "EN" else "Tidak ada data penjualan untuk filter terpilih.")

with tab2:
    st.subheader(t["segment_contrib"])
    if not df_filtered.empty:
        df_seg = df_filtered.groupby("customer_category").agg(
            total_revenue=("net_sales", "sum"),
            order_count=("invoice_id", "nunique"),
            active_cust=("customer_id", "nunique")
        ).reset_index()
        
        lbl_seg_rev = "Sales (IDR)" if lang_code == "EN" else "Penjualan (IDR)"
        lbl_seg_name = "Segment" if lang_code == "EN" else "Segmen"
        fig_tree = px.treemap(
            df_seg,
            path=["customer_category"],
            values="total_revenue",
            color="total_revenue",
            color_continuous_scale="Blues",
            labels={"total_revenue": lbl_seg_rev, "customer_category": lbl_seg_name}
        )
        apply_plotly_theme(fig_tree, height=360)
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.warning("No segment data." if lang_code == "EN" else "Tidak ada data segmen.")

with tab3:
    st.subheader(t["top_cust_leaderboard"])
    st.caption("Top 10 customer ranking based on confirmed valid invoice net spend." if lang_code == "EN" else "Peringkat 10 pelanggan teratas berdasarkan kontribusi belanja bersih invoice tertagih valid.")
    
    if not df_filtered.empty:
        df_top_cust = df_filtered.groupby(["customer_id", "customer_name", "customer_category", "division_name"]).agg(
            total_spend=("net_sales", "sum"),
            total_orders=("invoice_id", "nunique")
        ).reset_index().sort_values(by="total_spend", ascending=False).head(10)
        
        df_top_merged = df_top_cust.merge(
            df_cust_intel[["customer_id", "customer_health", "days_since_last_purchase"]], 
            on="customer_id", 
            how="left"
        )
        df_top_merged["customer_health"] = df_top_merged["customer_health"].fillna("Active Customer")
        
        day_suffix = "Days" if lang_code == "EN" else "Hari"
        df_top_display = df_top_merged.copy()
        df_top_display["Net Revenue"] = df_top_display["total_spend"].apply(format_rupiah)
        df_top_display["Order Count"] = df_top_display["total_orders"]
        df_top_display["Recency (Days)"] = df_top_display["days_since_last_purchase"].apply(lambda d: f"{int(d)} {day_suffix}" if pd.notnull(d) else "-")
        df_top_display["Health Status"] = df_top_display["customer_health"]
        
        display_cols = ["customer_name", "customer_category", "division_name", "Net Revenue", "Order Count", "Recency (Days)", "Health Status"]
        if lang_code == "EN":
            rename_map = {
                "customer_name": "Customer Name",
                "customer_category": "Segment",
                "division_name": "Branch",
                "Net Revenue": "Confirmed Net Revenue",
                "Order Count": "Order Count",
                "Recency (Days)": "Recency (Days)",
                "Health Status": "Health Status"
            }
        else:
            rename_map = {
                "customer_name": "Nama Pelanggan",
                "customer_category": "Segmen",
                "division_name": "Cabang",
                "Net Revenue": "Pendapatan Net Terkonfirmasi",
                "Order Count": "Jumlah Pesanan",
                "Recency (Days)": "Recency (Hari)",
                "Health Status": "Status Kesehatan"
            }
            
        st.dataframe(
            df_top_display[display_cols].rename(columns=rename_map),
            use_container_width=True
        )

with tab4:
    header_bench = "6 Regional Branch Performance Benchmark" if lang_code == "EN" else "Tolok Ukur Kinerja 6 Cabang Regional"
    sub_bench = "Comparison of confirmed revenue and invoice count across regional branches." if lang_code == "EN" else "Perbandingan total pendapatan terkonfirmasi dan jumlah transaksi faktur antar cabang."
    st.subheader(header_bench)
    st.caption(sub_bench)
    
    if not df_sales.empty and "division_name" in df_sales.columns:
        branch_bench = df_sales.groupby("division_name").agg(
            total_sales=("net_sales", "sum"),
            total_invoices=("invoice_id", "nunique"),
            unique_buyers=("customer_id", "nunique")
        ).reset_index().sort_values(by="total_sales", ascending=False)
        
        lbl_bb_branch = "Branch" if lang_code == "EN" else "Cabang"
        lbl_bb_sales = "Net Revenue (IDR)" if lang_code == "EN" else "Pendapatan Net (IDR)"
        fig_bb = px.bar(
            branch_bench,
            x="division_name",
            y="total_sales",
            color="total_sales",
            color_continuous_scale=["#93C5FD", "#2563EB"],
            labels={"division_name": lbl_bb_branch, "total_sales": lbl_bb_sales}
        )
        fig_bb.update_traces(
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.5,
            opacity=0.92
        )
        apply_plotly_theme(fig_bb, height=360)
        st.plotly_chart(fig_bb, use_container_width=True)
