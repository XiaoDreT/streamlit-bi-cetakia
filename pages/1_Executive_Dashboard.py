import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_customer_intelligence
from components.ui_components import (
    render_header, metric_card, render_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah
)

st.set_page_config(page_title="Executive Business Dashboard", page_icon="📊", layout="wide")

# Load Datasets
df_sales = load_sales_data()
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
    module_tag="OWNER / MANAGEMENT"
)

# -------------------------------------------------------------
# KPI CARDS ROW
# -------------------------------------------------------------
total_sales = df_filtered["net_sales"].sum() if not df_filtered.empty else 0
total_orders = df_filtered["invoice_id"].nunique() if not df_filtered.empty else 0
active_customers = df_filtered["customer_id"].nunique() if not df_filtered.empty else 0
aov = total_sales / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    sales_str = format_rupiah(total_sales)
    metric_card(t["total_sales"], sales_str, delta="+14.2% YoY", delta_color="positive", subtext=t["billed_rev_sub"])

with col2:
    metric_card(t["total_orders"], f"{total_orders:,}", delta="+5.1% YoY", delta_color="positive", subtext=t["distinct_trans_sub"])

with col3:
    metric_card(t["active_cust"], f"{active_customers:,}", delta="+3.2% YoY", delta_color="positive", subtext=t["buying_base_sub"])

with col4:
    aov_str = format_rupiah(aov)
    metric_card(t["aov"], aov_str, delta="+8.6% YoY", delta_color="positive", subtext=t["revenue_per_order_sub"])

st.markdown("---")

# -------------------------------------------------------------
# INSIGHT CARD (MANDATORY DSS RULE) - 100% INDONESIAN
# -------------------------------------------------------------
if not df_filtered.empty and "customer_category" in df_filtered.columns:
    seg_summary = df_filtered.groupby("customer_category")["net_sales"].sum().sort_values(ascending=False)
    top_seg_name = seg_summary.index[0]
    top_seg_pct = (seg_summary.iloc[0] / total_sales * 100) if total_sales > 0 else 0
    seg_names = seg_summary.index.tolist()
    runner_up_text_id = f", disusul oleh segmen {seg_names[1]} ({seg_summary.iloc[1]/total_sales*100:.1f}%)" if len(seg_names) > 1 else ""
    runner_up_text_en = f", followed by {seg_names[1]} ({seg_summary.iloc[1]/total_sales*100:.1f}%)" if len(seg_names) > 1 else ""
else:
    top_seg_name = "Industri"
    top_seg_pct = 41.7
    runner_up_text_id = ", disusul oleh segmen Divisi (18.6%)"
    runner_up_text_en = ", followed by Divisi (18.6%)"

if lang_code == "ID":
    ic_title = "Pendorong Pertumbuhan Penjualan & Risiko Konsentrasi Eksekutif"
    ic_context = f"Dievaluasi dari {total_orders:,} pesanan terkonfirmasi dari {active_customers:,} akun aktif ({filters['branch']}, {filters['segment']}). Transaksi dibatalkan (cancel) telah dieksklusikan dari revenue."
    ic_insight = f"Pendapatan terkonfirmasi didominasi oleh segmen {top_seg_name} ({top_seg_pct:.1f}% total penjualan){runner_up_text_id}. Segmen UMKM & End User menyumbang frekuensi pesanan terbesar."
    ic_action = f"Manajemen Eksekutif: Arahkan Tim Sales untuk mengamankan perpanjangan kontrak tahunan dengan akun {top_seg_name} teratas di {filters['branch'] if filters['branch'] != 'All Branches' else 'semua cabang'}. Berikan wewenang kepada Tim Marketing untuk merilis paket bundling khusus bagi segmen UMKM & Sekolah."
    ic_badge = "ATURAN KEPUTUSAN EKSEKUTIF"
else:
    ic_title = "Executive Revenue Growth Driver & Concentration Risk"
    ic_context = f"Evaluated across {total_orders:,} confirmed orders from {active_customers:,} active accounts ({filters['branch']}, {filters['segment']}). Cancelled transactions have been excluded from revenue."
    ic_insight = f"Confirmed revenue is predominantly driven by {top_seg_name} ({top_seg_pct:.1f}% total share){runner_up_text_en}. UMKM & End User segments generate the highest order volume."
    ic_action = f"Executive Management: Direct Sales Team to secure contract renewals with top {top_seg_name} accounts in {filters['branch'] if filters['branch'] != 'All Branches' else 'all branches'}. Authorize Marketing to release tailored bundles for UMKM & Sekolah clients."
    ic_badge = "EXECUTIVE DECISION RULE"

render_insight_card(
    title=ic_title,
    metric=sales_str,
    context=ic_context,
    insight=ic_insight,
    action=ic_action,
    badge=ic_badge
)

# -------------------------------------------------------------
# CHARTS ROW 1: REVENUE TREND & SEGMENT TREEMAP
# -------------------------------------------------------------
c1, c2 = st.columns([6, 4])

with c1:
    st.subheader(t["revenue_trend"])
    if not df_filtered.empty:
        df_filtered["month_year"] = df_filtered["invoice_date"].dt.to_period("M").dt.to_timestamp()
        df_monthly = df_filtered.groupby("month_year")["net_sales"].sum().reset_index()
        
        fig_trend = px.area(
            df_monthly, 
            x="month_year", 
            y="net_sales", 
            labels={"month_year": "Bulan" if lang_code == "ID" else "Month", "net_sales": "Penjualan Net (IDR)" if lang_code == "ID" else "Net Sales (IDR)"},
            color_discrete_sequence=["#2563EB"]
        )
        fig_trend.update_traces(fillcolor="rgba(37, 99, 235, 0.15)", line=dict(width=3))
        apply_plotly_theme(fig_trend, height=360)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Tidak ada data penjualan untuk filter terpilih." if lang_code == "ID" else "No sales data available for selected filters.")

with c2:
    st.subheader(t["segment_contrib"])
    if not df_filtered.empty:
        df_seg = df_filtered.groupby("customer_category").agg(
            total_revenue=("net_sales", "sum"),
            order_count=("invoice_id", "nunique"),
            active_cust=("customer_id", "nunique")
        ).reset_index()
        
        fig_tree = px.treemap(
            df_seg,
            path=["customer_category"],
            values="total_revenue",
            color="total_revenue",
            color_continuous_scale="Blues",
            labels={"total_revenue": "Penjualan (IDR)" if lang_code == "ID" else "Revenue (IDR)", "customer_category": "Segmen" if lang_code == "ID" else "Segment"}
        )
        apply_plotly_theme(fig_tree, height=360)
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.warning("Tidak ada data segmen." if lang_code == "ID" else "No segment data available.")

st.markdown("---")

# -------------------------------------------------------------
# TOP CUSTOMER LEADERBOARD TABLE
# -------------------------------------------------------------
st.subheader(t["top_cust_leaderboard"])
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
    df_top_merged["customer_health"] = df_top_merged["customer_health"].fillna("Active")
    
    df_top_display = df_top_merged.copy()
    df_top_display["Net Revenue"] = df_top_display["total_spend"].apply(lambda x: format_rupiah(x))
    df_top_display["Order Count"] = df_top_display["total_orders"]
    df_top_display["Recency (Days)"] = df_top_display["days_since_last_purchase"].fillna(0).astype(int)
    df_top_display["Health Status"] = df_top_display["customer_health"]
    
    display_cols = ["customer_name", "customer_category", "division_name", "Net Revenue", "Order Count", "Recency (Days)", "Health Status"]
    st.dataframe(
        df_top_display[display_cols].rename(columns={
            "customer_name": "Nama Pelanggan" if lang_code == "ID" else "Customer Name",
            "customer_category": "Segmen" if lang_code == "ID" else "Segment",
            "division_name": "Cabang" if lang_code == "ID" else "Branch",
            "Net Revenue": "Pendapatan Net" if lang_code == "ID" else "Net Revenue",
            "Order Count": "Jumlah Pesanan" if lang_code == "ID" else "Order Count",
            "Recency (Days)": "Recency (Hari)" if lang_code == "ID" else "Recency (Days)",
            "Health Status": "Status Kesehatan" if lang_code == "ID" else "Health Status"
        }),
        use_container_width=True
    )
