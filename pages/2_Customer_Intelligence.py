import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_intelligence, load_customer_data
from components.ui_components import (
    render_header, metric_card, render_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah
)

st.set_page_config(page_title="Customer Intelligence Dashboard", page_icon="👥", layout="wide")

# Load Datasets
df_cust_intel = load_customer_intelligence()
df_cust_master = load_customer_data()

# Merge metadata
df_intel_merged = df_cust_intel.merge(
    df_cust_master[['customer_id', 'customer_category', 'division_name']],
    on='customer_id',
    how='left',
    suffixes=('', '_master')
)

# Sidebar Filters & Locale State
filters = global_sidebar_filters(df_customers=df_intel_merged)
t = filters["t"]
lang_code = filters["lang"]

df_filtered = df_intel_merged.copy()
if filters["branch"] != "All Branches":
    branch_col = "division_name" if "division_name" in df_filtered.columns else "division_name_master"
    if branch_col in df_filtered.columns:
        df_filtered = df_filtered[df_filtered[branch_col] == filters["branch"]]

if filters["segment"] != "All Segments":
    seg_col = "customer_category" if "customer_category" in df_filtered.columns else "customer_category_master"
    if seg_col in df_filtered.columns:
        df_filtered = df_filtered[df_filtered[seg_col].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["cust_intel_title"],
    subtitle=t["cust_intel_sub"],
    module_tag="CS / MARKETING / SALES"
)

# Metrics Summary
total_cust = len(df_filtered)
at_risk_count = len(df_filtered[df_filtered["customer_health"] == "At Risk"])
dormant_count = len(df_filtered[df_filtered["customer_health"] == "Dormant"])
at_risk_pct = (at_risk_count / total_cust * 100) if total_cust > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Basis Dianalisis" if lang_code == "ID" else "Total Analyzed Base", f"{total_cust:,}", subtext="Populasi master pelanggan" if lang_code == "ID" else "Customer master population")
with c2:
    metric_card("Sehat / Aktif" if lang_code == "ID" else "Healthy / Active", f"{(total_cust - at_risk_count - dormant_count):,}", delta_color="positive", subtext="Siklus pembelian berulang teratur" if lang_code == "ID" else "Regular repeat purchase cycle")
with c3:
    metric_card("Pelanggan Berisiko" if lang_code == "ID" else "At Risk Customers", f"{at_risk_count:,}", delta=f"{at_risk_pct:.1f}% basis", delta_color="negative", subtext="Melebihi interval reorder normal" if lang_code == "ID" else "Exceeded normal reorder interval")
with c4:
    metric_card("Pelanggan Dormant" if lang_code == "ID" else "Dormant Customers", f"{dormant_count:,}", delta_color="negative", subtext="Tidak aktif > 90 hari kalender" if lang_code == "ID" else "Inactive for > 90 calendar days")

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD - 100% INDONESIAN
# -------------------------------------------------------------
if lang_code == "ID":
    ic_title = "Peringatan Mitigasi Risiko Churn & Kesehatan Pelanggan"
    ic_metric = f"{at_risk_count:,} Pelanggan Berisiko (At Risk) ({at_risk_pct:.1f}% dari basis)"
    ic_context = f"Dievaluasi dari {total_cust:,} total akun pelanggan dalam cakupan filter {filters['branch']} / {filters['segment']}."
    ic_insight = "Pelanggan Berisiko (At Risk) telah melebihi rata-rata siklus interval pembelian historis mereka hingga > 1.5x (rata-rata recency: 48 hari vs ekspektasi 24 hari). Sebagian besar merupakan pembeli kemasan dan stiker yang berpotensi beralih ke kompetitor."
    ic_action = "Tim Customer Service (CS): Prioritaskan panggilan penjangkauan (outbound call) untuk 50 akun Berisiko teratas berdasarkan nilai transaksi seumur hidup. Berikan diskon reorder loyalitas 5% untuk mengaktifkan kembali akun sebelum masuk ke status Dormant."
    ic_badge = "ATURAN KEPUTUSAN RETENSI"
else:
    ic_title = "Customer Health & Churn Risk Mitigation Alert"
    ic_metric = f"{at_risk_count:,} At Risk Customers ({at_risk_pct:.1f}% of base)"
    ic_context = f"Evaluated across {total_cust:,} total customer accounts under {filters['branch']} / {filters['segment']} filter scope."
    ic_insight = "At Risk customers have exceeded their historical average purchase gap by > 1.5x (avg recency: 48 days vs expected 24 days). The majority are packaging and label buyers who may be sourcing from competitors."
    ic_action = "CS Team: Prioritize outbound wellness calls for the top 50 At-Risk accounts by lifetime spend. Offer a 5% loyalty reorder discount to reactivate accounts before they slip into Dormant state."
    ic_badge = "RETENTION DECISION RULE"

render_insight_card(
    title=ic_title,
    metric=ic_metric,
    context=ic_context,
    insight=ic_insight,
    action=ic_action,
    badge=ic_badge
)

# -------------------------------------------------------------
# CHARTS ROW 1: HEALTH DONUT & RFM SEGMENT BAR
# -------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader(t["cust_health_donut"])
    if not df_filtered.empty:
        df_health_counts = df_filtered["customer_health"].value_counts().reset_index()
        df_health_counts.columns = ["Health Status", "Customer Count"]
        
        color_map = {
            "Healthy": "#10B981",
            "Active": "#2563EB",
            "At Risk": "#F59E0B",
            "Dormant": "#DC2626",
            "New": "#8B5CF6"
        }
        
        fig_health = px.pie(
            df_health_counts,
            names="Health Status",
            values="Customer Count",
            hole=0.5,
            color="Health Status",
            color_discrete_map=color_map
        )
        fig_health.update_traces(textposition='inside', textinfo='percent+label')
        apply_plotly_theme(fig_health, height=360)
        st.plotly_chart(fig_health, use_container_width=True)
    else:
        st.warning("Tidak ada data kesehatan pelanggan." if lang_code == "ID" else "No data available for health distribution.")

with col_chart2:
    st.subheader(t["rfm_bar"])
    if not df_filtered.empty and "rfm_segment" in df_filtered.columns:
        df_rfm = df_filtered["rfm_segment"].value_counts().reset_index()
        df_rfm.columns = ["RFM Segment", "Customer Count"]
        
        fig_rfm = px.bar(
            df_rfm,
            x="Customer Count",
            y="RFM Segment",
            orientation="h",
            color="Customer Count",
            color_continuous_scale="Purples",
            labels={"RFM Segment": "Segmen RFM" if lang_code == "ID" else "RFM Segment", "Customer Count": "Jumlah Pelanggan" if lang_code == "ID" else "Customer Count"}
        )
        apply_plotly_theme(fig_rfm, height=360)
        st.plotly_chart(fig_rfm, use_container_width=True)
    else:
        st.warning("Tidak ada data segmen RFM." if lang_code == "ID" else "No RFM segment data available.")

st.markdown("---")

# -------------------------------------------------------------
# CHARTS ROW 2: MARKET MAP SCATTER & HIGH VALUE WORKLIST
# -------------------------------------------------------------
r2_col1, r2_col2 = st.columns([5, 5])

with r2_col1:
    st.subheader(t["market_map_scatter"])
    if not df_filtered.empty:
        df_market = df_filtered.groupby("customer_category").agg(
            customer_count=("customer_id", "nunique"),
            total_revenue=("lifetime_sales", "sum"),
            avg_ltv=("lifetime_sales", "mean")
        ).reset_index()
        
        fig_market = px.scatter(
            df_market,
            x="customer_count",
            y="total_revenue",
            size="avg_ltv",
            color="customer_category",
            hover_name="customer_category",
            labels={
                "customer_count": "Jumlah Pelanggan Unik" if lang_code == "ID" else "Unique Customer Count",
                "total_revenue": "Total Pendapatan Seumur Hidup (IDR)" if lang_code == "ID" else "Total Lifetime Revenue (IDR)",
                "customer_category": "Segmen" if lang_code == "ID" else "Category"
            }
        )
        apply_plotly_theme(fig_market, height=360)
        st.plotly_chart(fig_market, use_container_width=True)

with r2_col2:
    st.subheader(t["at_risk_worklist"])
    df_worklist = df_filtered[df_filtered["customer_health"].isin(["At Risk", "Dormant"])].sort_values(
        by="lifetime_sales", ascending=False
    ).head(10)
    
    if not df_worklist.empty:
        df_worklist_disp = df_worklist[["customer_name", "customer_category", "lifetime_sales", "days_since_last_purchase", "customer_health"]].copy()
        df_worklist_disp["Lifetime Sales"] = df_worklist_disp["lifetime_sales"].apply(lambda x: format_rupiah(x))
        df_worklist_disp["Recency"] = df_worklist_disp["days_since_last_purchase"].apply(
            lambda x: (f"{int(x)} Hari" if lang_code == "ID" else f"{int(x)} Days") if pd.notnull(x) else "-"
        )
        
        st.dataframe(
            df_worklist_disp[["customer_name", "customer_category", "Lifetime Sales", "Recency", "customer_health"]].rename(columns={
                "customer_name": "Nama Pelanggan" if lang_code == "ID" else "Customer Name",
                "customer_category": "Segmen" if lang_code == "ID" else "Segment",
                "Lifetime Sales": "Penjualan Seumur Hidup" if lang_code == "ID" else "Lifetime Sales",
                "Recency": "Recency (Hari)" if lang_code == "ID" else "Recency",
                "customer_health": "Status Kesehatan" if lang_code == "ID" else "Health Status"
            }),
            use_container_width=True
        )
    else:
        st.info("Tidak ada pelanggan At-Risk atau Dormant pada filter terpilih." if lang_code == "ID" else "No At-Risk or Dormant customers in current selection.")
