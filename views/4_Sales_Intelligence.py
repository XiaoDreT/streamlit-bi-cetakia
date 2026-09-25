import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_quotation_data
from utils.intelligence_engine import rebuild_quotation_opportunity_metrics
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
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
    subtitle="Quotation Pipeline Audit, Open Opportunity Estimates, Drop-off Analysis & Salvage Worklist" if lang_code == "EN" else "Audit Pipeline Penawaran, Estimasi Peluang Terbuka, Analisis Drop-off & Worklist Penyelamatan",
    module_tag="SALES MANAGEMENT / COMMERCIAL"
)

# -------------------------------------------------------------
# STRICT OPPORTUNITY CALCULATIONS (BUSINESS LOGIC ENGINE)
# -------------------------------------------------------------
opp = rebuild_quotation_opportunity_metrics(df_filtered)

# 4 Key Decision Support KPI Cards
q1, q2, q3, q4 = st.columns(4)
with q1:
    kpi1_title = "Total Pipeline Value" if lang_code == "EN" else "Total Nilai Pipeline"
    kpi1_sub = f"{opp['total_count']:,} total quotations issued" if lang_code == "EN" else f"{opp['total_count']:,} total penawaran diterbitkan"
    metric_card(
        kpi1_title, 
        format_rupiah(opp["total_pipeline"]), 
        subtext=kpi1_sub
    )
with q2:
    kpi2_title = "Converted Value (Won)" if lang_code == "EN" else "Nilai Terkonversi (Won)"
    kpi2_sub = f"{opp['converted_count']:,} quotes successfully converted to orders" if lang_code == "EN" else f"{opp['converted_count']:,} penawaran sukses menjadi pesanan"
    metric_card(
        kpi2_title, 
        format_rupiah(opp["converted_val"]), 
        delta=f"{opp['win_rate']:.1f}% Win Rate", 
        delta_color="positive", 
        subtext=kpi2_sub
    )
with q3:
    kpi3_title = "Open Opportunities (Open Opp)" if lang_code == "EN" else "Peluang Terbuka (Open Opp)"
    kpi3_sub = f"{opp['open_opp_count']:,} active quotes (Draft/Sent/Accepted)" if lang_code == "EN" else f"{opp['open_opp_count']:,} penawaran aktif (Draft/Sent/Accepted)"
    metric_card(
        kpi3_title, 
        format_rupiah(opp["open_opp_val"]), 
        delta=f"{opp['open_opp_pct']:.1f}% pipeline", 
        delta_color="positive" if opp["open_opp_val"] > 0 else "negative", 
        subtext=kpi3_sub
    )
with q4:
    kpi4_title = "Lost Opportunities (Lost Opp)" if lang_code == "EN" else "Peluang Hilang (Lost Opp)"
    kpi4_sub = f"{opp['lost_opp_count']:,} Expired / Rejected quotes" if lang_code == "EN" else f"{opp['lost_opp_count']:,} penawaran Expired / Rejected"
    metric_card(
        kpi4_title, 
        format_rupiah(opp["lost_opp_val"]), 
        delta=f"{opp['lost_opp_pct']:.1f}% pipeline", 
        delta_color="negative", 
        subtext=kpi4_sub
    )

st.markdown("---")

# -------------------------------------------------------------
# STRICT V1.1 MANDATORY DSS INSIGHT CARD (5-PART STRUCTURE)
# -------------------------------------------------------------
if lang_code == "EN":
    ic_title = "Quotation Pipeline Recovery Strategy & Lost Opportunity Salvage"
    ic_metric = f"{format_rupiah(opp['lost_opp_val'])} Lost Opportunities ({opp['lost_opp_pct']:.1f}% Pipeline)"
    ic_context = f"Evaluated from {opp['total_count']:,} quotations worth {format_rupiah(opp['total_pipeline'])} across branch {filters['branch']} and segment {filters['segment']}."
    ic_insight = f"The largest pipeline drop-off occurs at the Expired stage, consuming {opp['lost_opp_pct']:.1f}% of total quotation value. Currently, there are {opp['open_opp_count']:,} open opportunities worth {format_rupiah(opp['open_opp_val'])} requiring proactive follow-up before expiring."
    ic_impacted = f"Sales Representative Team ({df_filtered['sales_name'].nunique() if 'sales_name' in df_filtered.columns else 'All'} sales), Branch Coordinators, and B2B Institutional & Industrial Clients."
    ic_action = "Sales Manager: Institute daily reviews for open opportunities > IDR 5M. Mandate 24-hour follow-up on quotations with <= 72 hours until expiration, and schedule reactivation for the 20 largest expired accounts."
    ic_badge = "SALES PIPELINE DECISION RULE"
    ic_target = f"{opp['urgent_count']:,} Urgent Quotes (<= 72 Hours) worth {format_rupiah(opp['urgent_val'])}"
else:
    ic_title = "Strategi Pemulihan Pipeline Penawaran & Penyelamatan Peluang Hilang"
    ic_metric = f"{format_rupiah(opp['lost_opp_val'])} Peluang Hilang ({opp['lost_opp_pct']:.1f}% Pipeline)"
    ic_context = f"Dievaluasi dari {opp['total_count']:,} penawaran senilai {format_rupiah(opp['total_pipeline'])} pada cakupan cabang {filters['branch']} dan segmen {filters['segment']}."
    ic_insight = f"Penurunan pipeline terbesar terjadi pada tahap penawaran kedaluwarsa (Expired) yang menyerap {opp['lost_opp_pct']:.1f}% total nilai penawaran. Saat ini terdapat {opp['open_opp_count']:,} peluang terbuka senilai {format_rupiah(opp['open_opp_val'])} yang memerlukan tindak lanjut aktif sebelum kedaluwarsa."
    ic_impacted = f"Tim Sales Representative ({df_filtered['sales_name'].nunique() if 'sales_name' in df_filtered.columns else 'All'} sales), Koordinator Cabang, dan Klien B2B Instansi & Industri."
    ic_action = "Manajer Sales: Terapkan peninjauan harian terhadap peluang terbuka > Rp 5 Juta. Wajibkan follow-up dalam 24 jam untuk penawaran bersisa tenggat <= 72 jam, serta jadwalkan reaktivasi pada 20 akun expired terbesar."
    ic_badge = "ATURAN KEPUTUSAN PIPELINE SALES"
    ic_target = f"{opp['urgent_count']:,} Penawaran Mendesak (<= 72 Jam) senilai {format_rupiah(opp['urgent_val'])}"

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
# TABBED DECISION SUPPORT INTERFACE (UX ENHANCEMENT)
# -------------------------------------------------------------
if lang_code == "EN":
    tab_labels = [
        "📊 Funnel Summary & Drop-off",
        "🎯 Sales Rep Performance & Win Rate",
        "⏳ Urgent Worklist (Expiry <= 72 Hours)",
        "📑 Quotation Ledger Exploration"
    ]
else:
    tab_labels = [
        "📊 Ringkasan Funnel & Drop-off",
        "🎯 Performa Sales Rep & Win Rate",
        "⏳ Worklist Mendesak (Tenggat <= 72 Jam)",
        "📑 Eksplorasi Data Penawaran"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

with tab1:
    col_f1, col_f2 = st.columns([6, 4])
    
    with col_f1:
        st.subheader("Quotation Conversion Funnel & Pipeline Drop-off" if lang_code == "EN" else "Funnel Konversi Penawaran & Drop-off Pipeline")
        
        # Calculate stages and drop-offs
        created_val = opp["total_pipeline"]
        created_cnt = opp["total_count"]
        
        conv_val = opp["converted_val"]
        conv_cnt = opp["converted_count"]
        
        open_val = opp["open_opp_val"]
        open_cnt = opp["open_opp_count"]
        
        lost_val = opp["lost_opp_val"]
        lost_cnt = opp["lost_opp_count"]
        
        if lang_code == "EN":
            funnel_labels = [
                f"1. Issued Quotes ({created_cnt:,} Quotes)",
                f"2. Converted / Closed Won ({conv_cnt:,} Quotes)",
                f"3. Open Opportunities / Active ({open_cnt:,} Quotes)",
                f"4. Lost Opportunities / Lost ({lost_cnt:,} Quotes)"
            ]
        else:
            funnel_labels = [
                f"1. Penawaran Diterbitkan ({created_cnt:,} Quotes)",
                f"2. Terkonversi / Closed Won ({conv_cnt:,} Quotes)",
                f"3. Peluang Terbuka / Active ({open_cnt:,} Quotes)",
                f"4. Peluang Hilang / Lost ({lost_cnt:,} Quotes)"
            ]
        
        funnel_vals = [created_val, conv_val, open_val, lost_val]
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels,
            x=funnel_vals,
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": ["#1E3A8A", "#10B981", "#3B82F6", "#EF4444"]}
        ))
        apply_plotly_theme(fig_funnel, height=360)
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col_f2:
        st.subheader("Opportunity Status Breakdown" if lang_code == "EN" else "Rincian Status Peluang")
        status_pie = df_filtered.groupby("quotation_status")["net_quotation_value"].sum().reset_index()
        fig_pie = px.pie(
            status_pie,
            names="quotation_status",
            values="net_quotation_value",
            hole=0.45,
            color="quotation_status",
            color_discrete_map={
                "accepted": "#10B981",
                "draft": "#3B82F6",
                "sent": "#8B5CF6",
                "expired": "#EF4444",
                "rejected": "#6B7280"
            }
        )
        apply_plotly_theme(fig_pie, height=360)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Unconverted Opportunity Value Ranking by Sales Representative" if lang_code == "EN" else "Peringkat Nilai Peluang Belum Terkonversi per Sales Representative")
    if not df_filtered.empty and "sales_name" in df_filtered.columns:
        rep_unconv = df_filtered[df_filtered["converted_flag"] == 0].groupby("sales_name").agg(
            lost_val=("net_quotation_value", "sum"),
            quote_count=("quotation_code", "count")
        ).reset_index().sort_values(by="lost_val", ascending=False).head(10)
        
        sales_axis = "Held / Lost Opportunity Value (IDR)" if lang_code == "EN" else "Nilai Peluang Tertahan / Hilang (IDR)"
        fig_rep = px.bar(
            rep_unconv,
            x="lost_val",
            y="sales_name",
            orientation="h",
            color="lost_val",
            color_continuous_scale=["#FCA5A5", "#DC2626"],
            labels={"lost_val": sales_axis, "sales_name": "Sales Representative"}
        )
        fig_rep.update_traces(
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.5,
            opacity=0.92
        )
        apply_plotly_theme(fig_rep, height=360)
        st.plotly_chart(fig_rep, use_container_width=True)
        
        expander_title = "🔍 View Full Sales Rep Win Rate Recap" if lang_code == "EN" else "🔍 Lihat Rekapitulasi Win Rate Lengkap per Sales Rep"
        with st.expander(expander_title):
            rep_perf = df_filtered.groupby("sales_name").agg(
                total_pipeline=("net_quotation_value", "sum"),
                total_quotes=("quotation_code", "count"),
                won_quotes=("converted_flag", "sum"),
                won_val=("net_quotation_value", lambda s: s[df_filtered.loc[s.index, "converted_flag"] == 1].sum())
            ).reset_index()
            rep_perf["win_rate"] = (rep_perf["won_quotes"] / rep_perf["total_quotes"] * 100).round(1)
            rep_perf["Pipeline Total"] = rep_perf["total_pipeline"].apply(format_rupiah)
            rep_perf["Nilai Won"] = rep_perf["won_val"].apply(format_rupiah)
            rep_perf["Win Rate (%)"] = rep_perf["win_rate"].apply(lambda w: f"{w:.1f}%")
            
            rep_cols = {
                "sales_name": "Sales Name" if lang_code == "EN" else "Nama Sales",
                "total_quotes": "Total Quotes" if lang_code == "EN" else "Total Penawaran",
                "won_quotes": "Won Quotes" if lang_code == "EN" else "Penawaran Won",
                "Pipeline Total": "Total Pipeline" if lang_code == "EN" else "Pipeline Total",
                "Nilai Won": "Won Value" if lang_code == "EN" else "Nilai Won"
            }
            st.dataframe(
                rep_perf[["sales_name", "total_quotes", "won_quotes", "Win Rate (%)", "Pipeline Total", "Nilai Won"]].rename(columns=rep_cols).sort_values(by="Win Rate (%)", ascending=False),
                use_container_width=True
            )

with tab3:
    urgent_header = f"Urgent Quotation Worklist - Expiry <= 72h ({opp['urgent_count']} Quotes)" if lang_code == "EN" else f"Daftar Kerja Penawaran Mendesak Tenggat <= 72 Jam ({opp['urgent_count']} Penawaran)"
    st.subheader(urgent_header)
    urgent_quotes = df_filtered[
        (df_filtered["converted_flag"] == 0) & 
        (df_filtered["quotation_status"].isin(["draft", "sent", "accepted"])) & 
        (df_filtered["days_from_expiry"] <= 3)
    ].sort_values(by="net_quotation_value", ascending=False)
    
    if not urgent_quotes.empty:
        disp_urgent = urgent_quotes[["quotation_code", "customer_name", "sales_name", "net_quotation_value", "days_from_expiry", "quotation_status"]].copy()
        disp_urgent["Nilai Penawaran"] = disp_urgent["net_quotation_value"].apply(format_rupiah)
        if lang_code == "EN":
            disp_urgent["Sisa Hari"] = disp_urgent["days_from_expiry"].apply(lambda d: f"{int(d)} Days Left" if pd.notnull(d) else "-")
            disp_urgent["Aksi Rekomendasi"] = "🚨 Priority Client Outreach (Immediate Follow-up)"
            urgent_rename = {
                "quotation_code": "Quote Code",
                "customer_name": "Customer Name",
                "sales_name": "Sales Rep",
                "Nilai Penawaran": "Quote Value",
                "Sisa Hari": "Days Left",
                "quotation_status": "Quote Status",
                "Aksi Rekomendasi": "Recommended Action"
            }
        else:
            disp_urgent["Sisa Hari"] = disp_urgent["days_from_expiry"].apply(lambda d: f"Sisa {int(d)} Hari" if pd.notnull(d) else "-")
            disp_urgent["Aksi Rekomendasi"] = "🚨 Prioritas Hubungi Klien Sekarang (Follow-up Segera)"
            urgent_rename = {
                "quotation_code": "Kode Penawaran",
                "customer_name": "Nama Pelanggan",
                "sales_name": "Sales Rep",
                "Nilai Penawaran": "Nilai Penawaran",
                "Sisa Hari": "Sisa Hari",
                "quotation_status": "Status Penawaran",
                "Aksi Rekomendasi": "Aksi Rekomendasi"
            }
        
        st.dataframe(
            disp_urgent[["quotation_code", "customer_name", "sales_name", "Nilai Penawaran", "Sisa Hari", "quotation_status", "Aksi Rekomendasi"]].rename(columns=urgent_rename),
            use_container_width=True
        )
    else:
        empty_urgent_msg = "✅ No open active quotations are within the 72-hour expiration threshold for the selected filters." if lang_code == "EN" else "✅ Tidak ada penawaran aktif terbuka yang berada dalam ambang batas kedaluwarsa 72 jam pada filter terpilih."
        st.info(empty_urgent_msg)

with tab4:
    st.subheader("Comprehensive Quotation Ledger Table" if lang_code == "EN" else "Tabel Ledger Penawaran Lengkap")
    st.caption("Search and review historical commercial quotations." if lang_code == "EN" else "Pencarian dan peninjauan riwayat penawaran komersial.")
    
    sample_disp = df_filtered[["quotation_code", "quotation_date", "customer_name", "division_name", "sales_name", "net_quotation_value", "quotation_status", "conversion_status"]].copy().head(50)
    sample_disp["Tanggal"] = sample_disp["quotation_date"].dt.strftime("%Y-%m-%d")
    sample_disp["Nilai Net"] = sample_disp["net_quotation_value"].apply(format_rupiah)
    
    ledger_rename = {
        "quotation_code": "Quote Code" if lang_code == "EN" else "Kode",
        "Tanggal": "Date" if lang_code == "EN" else "Tanggal",
        "customer_name": "Customer" if lang_code == "EN" else "Pelanggan",
        "division_name": "Branch" if lang_code == "EN" else "Cabang",
        "sales_name": "Sales Rep",
        "Nilai Net": "Net Value" if lang_code == "EN" else "Nilai Net",
        "quotation_status": "Status",
        "conversion_status": "Conversion Status" if lang_code == "EN" else "Status Konversi"
    }
    st.dataframe(
        sample_disp[["quotation_code", "Tanggal", "customer_name", "division_name", "sales_name", "Nilai Net", "quotation_status", "conversion_status"]].rename(columns=ledger_rename),
        use_container_width=True
    )
