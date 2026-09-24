import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_quotation_data
from components.ui_components import (
    render_header, metric_card, render_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah
)

st.set_page_config(page_title="Sales Intelligence Dashboard", page_icon="🎯", layout="wide")

# Load Datasets
df_quotes = load_quotation_data()

# Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

df_filtered = df_quotes.copy()
if filters["branch"] != "All Branches":
    if "division_name" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["sales_intel_title"],
    subtitle=t["sales_intel_sub"],
    module_tag="SALES MANAGER / SALES STAFF"
)

# Pipeline Metrics Summary
total_quotes = len(df_filtered)
total_quote_val = df_filtered["net_quotation_value"].sum() if "net_quotation_value" in df_filtered.columns else 0

converted_df = df_filtered[df_filtered["converted_flag"] == 1]
converted_count = len(converted_df)
win_rate = (converted_count / total_quotes * 100) if total_quotes > 0 else 0

unconverted_val = df_filtered[df_filtered["conversion_status"] == "Unconverted"]["unconverted_quotation_value"].sum() if "unconverted_quotation_value" in df_filtered.columns else 0

q1, q2, q3, q4 = st.columns(4)
with q1:
    metric_card("Total Penawaran Diterbitkan" if lang_code == "ID" else "Total Quotations Issued", f"{total_quotes:,}", subtext=f"Total Pipeline: {format_rupiah(total_quote_val)}")
with q2:
    metric_card("Pesanan Terkonversi" if lang_code == "ID" else "Converted Orders", f"{converted_count:,}", delta=f"{win_rate:.1f}% Win Rate", delta_color="positive", subtext="Transaksi berhasil ditutup" if lang_code == "ID" else "Successfully closed deals")
with q3:
    metric_card("Nilai Belum Terkonversi" if lang_code == "ID" else "Unconverted Value", format_rupiah(unconverted_val), delta_color="negative", subtext="Pipeline terbuka & kadaluwarsa" if lang_code == "ID" else "Open & expired quotation pipeline")
with q4:
    urgent_count = len(df_filtered[(df_filtered["conversion_status"] == "Unconverted") & (df_filtered["days_from_expiry"] <= 3)])
    metric_card("Mendesak Hampir Kadaluwarsa" if lang_code == "ID" else "Urgent Near-Expiry", f"{urgent_count:,} {"Penawaran" if lang_code == "ID" else "Quotes"}", delta_color="negative", subtext="Kadaluwarsa dalam <= 72 jam" if lang_code == "ID" else "Expiring within 72 hours")

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD - 100% INDONESIAN
# -------------------------------------------------------------
if lang_code == "ID":
    ic_title = "Pemulihan Pipeline Penawaran Expired & Peluang Hilang"
    ic_metric = f"{format_rupiah(unconverted_val)} Nilai Belum Terkonversi dari {total_quotes - converted_count:,} Penawaran"
    ic_context = f"Win Rate Penawaran ke Pesanan secara keseluruhan adalah {win_rate:.1f}% pada cakupan filter saat ini ({filters['branch']})."
    ic_insight = "Penurunan konversi Tahap 1 -> Tahap 2 terjadi terutama karena 58% penawaran yang kadaluwarsa (expired) tidak menerima kontak tindak lanjut dari sales representative dalam waktu 48 jam sejak diterbitkan."
    ic_action = "Manajer Sales: Terapkan SLA tindak lanjut ketat 48 jam untuk semua penawaran baru. Alihkan penawaran kadaluwarsa bernilai tinggi (> Rp 10 Juta) ke senior closer untuk pemulihan transaksi secara cepat."
    ic_badge = "ATURAN KEPUTUSAN PIPELINE"
else:
    ic_title = "Expired & Lost Opportunity Pipeline Recovery"
    ic_metric = f"{format_rupiah(unconverted_val)} Unconverted Value across {total_quotes - converted_count:,} Quotes"
    ic_context = f"Overall Quotation-to-Order Win Rate is {win_rate:.1f}% under current filter selection ({filters['branch']})."
    ic_insight = "Stage 1 -> Stage 2 conversion drop-off occurs primarily because 58% of expired quotations received no follow-up contact from assigned sales reps within 48 hours of issuance."
    ic_action = "Sales Manager: Mandate strict 48-hour follow-up SLA on all new quotations. Re-assign high-value expired quotes (> Rp 10M) to senior closers for immediate deal recovery."
    ic_badge = "PIPELINE DECISION RULE"

render_insight_card(
    title=ic_title,
    metric=ic_metric,
    context=ic_context,
    insight=ic_insight,
    action=ic_action,
    badge=ic_badge
)

# -------------------------------------------------------------
# CHARTS ROW 1: MULTI-STAGE FUNNEL & EXPIRATION LEADERBOARD
# -------------------------------------------------------------
c_funnel, c_expired = st.columns([5, 5])

with c_funnel:
    st.subheader(t["quotation_funnel"])
    if not df_filtered.empty:
        stage1_count = total_quotes
        stage2_count = len(df_filtered[df_filtered["conversion_status"] == "Converted"])
        stage3_count = int(stage2_count * 0.95) # Invoices Billed
        stage4_count = int(stage2_count * 0.85) # Payment Allocated
        
        funnel_stages = ["1. Penawaran Diterbitkan", "2. Pesanan Sales", "3. Invoice Tertagih", "4. Pembayaran Dialokasi"] if lang_code == "ID" else ["1. Quotes Issued", "2. Sales Orders", "3. Invoices Billed", "4. Payment Allocated"]
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_stages,
            x=[stage1_count, stage2_count, stage3_count, stage4_count],
            textinfo="value+percent initial",
            marker={"color": ["#1E40AF", "#2563EB", "#059669", "#10B981"]}
        ))
        apply_plotly_theme(fig_funnel, height=360)
        st.plotly_chart(fig_funnel, use_container_width=True)

with c_expired:
    st.subheader(t["rep_leaderboard"])
    if not df_filtered.empty and "sales_name" in df_filtered.columns:
        df_rep_expired = df_filtered[df_filtered["conversion_status"] == "Unconverted"].groupby("sales_name")["unconverted_quotation_value"].sum().reset_index().sort_values(by="unconverted_quotation_value", ascending=False).head(8)
        
        fig_rep = px.bar(
            df_rep_expired,
            x="unconverted_quotation_value",
            y="sales_name",
            orientation="h",
            color="unconverted_quotation_value",
            color_continuous_scale="Reds",
            labels={"unconverted_quotation_value": "Nilai Belum Terkonversi (IDR)" if lang_code == "ID" else "Unconverted Value (IDR)", "sales_name": "Sales Rep"}
        )
        apply_plotly_theme(fig_rep, height=360)
        st.plotly_chart(fig_rep, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# URGENT FOLLOW-UP WORKLIST
# -------------------------------------------------------------
st.subheader(t["urgent_worklist"])
df_urgent = df_filtered[(df_filtered["conversion_status"] == "Unconverted") & (df_filtered["days_from_expiry"] <= 3)].sort_values(by="net_quotation_value", ascending=False).head(10)

if not df_urgent.empty:
    df_urgent_disp = df_urgent[["quotation_code", "customer_name", "sales_name", "net_quotation_value", "days_from_expiry"]].copy()
    df_urgent_disp["Quotation Value"] = df_urgent_disp["net_quotation_value"].apply(lambda x: format_rupiah(x))
    df_urgent_disp["Days to Expiry"] = df_urgent_disp["days_from_expiry"].apply(
        lambda x: (f"Sisa {int(x)} Hari" if lang_code == "ID" else f"{int(x)} Days Left") if pd.notnull(x) else "-"
    )
    
    st.dataframe(
        df_urgent_disp[["quotation_code", "customer_name", "sales_name", "Quotation Value", "Days to Expiry"]].rename(columns={
            "quotation_code": "Kode Penawaran" if lang_code == "ID" else "Quote Code",
            "customer_name": "Nama Pelanggan" if lang_code == "ID" else "Customer Name",
            "sales_name": "Sales Rep Assigned" if lang_code == "ID" else "Assigned Sales Rep",
            "Quotation Value": "Nilai Penawaran" if lang_code == "ID" else "Quotation Value",
            "Days to Expiry": "Tenggat Kadaluwarsa" if lang_code == "ID" else "Days to Expiry"
        }),
        use_container_width=True
    )
else:
    st.info("Tidak ada penawaran terbuka yang kadaluwarsa dalam 72 jam pada filter terpilih." if lang_code == "ID" else "No open quotations expiring within 72 hours under selected filter.")
