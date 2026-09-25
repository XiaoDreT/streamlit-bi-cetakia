import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_intelligence, load_customer_data
from utils.intelligence_engine import (
    classify_customer_health, assign_customer_value_tier, 
    compute_priority_score
)
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
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

# Apply Customer Health & Value Tier Engine
df_intel_merged["customer_health"] = df_intel_merged.apply(classify_customer_health, axis=1)
df_intel_merged["value_tier"] = df_intel_merged.apply(assign_customer_value_tier, axis=1)
df_intel_merged["priority_score"] = df_intel_merged.apply(compute_priority_score, axis=1)

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
# Page Header
subtitle_text = "4-Status Customer Health Segmentation, Tier A/B/C Value Classification & CS Priority Score" if lang_code == "EN" else "Segmentasi Kesehatan Pelanggan 4-Status, Klasifikasi Nilai Tier A/B/C & Skor Prioritas CS"
render_header(
    title=t["cust_intel_title"],
    subtitle=subtitle_text,
    module_tag="CUSTOMER SUCCESS / RETENTION"
)

# -------------------------------------------------------------
# STRICT 4-STATUS HEALTH METRICS
# -------------------------------------------------------------
total_cust = len(df_filtered)
never_bought_count = len(df_filtered[df_filtered["customer_health"] == "Never Purchased"])
active_count = len(df_filtered[df_filtered["customer_health"] == "Active Customer"])
at_risk_count = len(df_filtered[df_filtered["customer_health"] == "At Risk"])
dormant_count = len(df_filtered[df_filtered["customer_health"] == "Dormant"])

purchasing_base = total_cust - never_bought_count
at_risk_pct = (at_risk_count / purchasing_base * 100) if purchasing_base > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    lbl_act = "Active Customers" if lang_code == "EN" else "Pelanggan Aktif"
    sub_act = "Regular transactions within <= 45 days" if lang_code == "EN" else "Transaksi teratur dalam <= 45 hari"
    metric_card(
        lbl_act, 
        f"{active_count:,}", 
        delta_color="positive", 
        subtext=sub_act
    )
with c2:
    lbl_risk = "At-Risk Customers" if lang_code == "EN" else "Pelanggan Berisiko (At Risk)"
    delta_risk = f"{at_risk_pct:.1f}% buying base" if lang_code == "EN" else f"{at_risk_pct:.1f}% basis pembeli"
    sub_risk = "Exceeded normal cycle (46 - 90 days)" if lang_code == "EN" else "Melebihi siklus normal (46 - 90 hari)"
    metric_card(
        lbl_risk, 
        f"{at_risk_count:,}", 
        delta=delta_risk, 
        delta_color="negative", 
        subtext=sub_risk
    )
with c3:
    lbl_dorm = "Dormant Customers" if lang_code == "EN" else "Pelanggan Dormant"
    sub_dorm = "No transactions in > 90 calendar days" if lang_code == "EN" else "Tidak ada transaksi > 90 hari kalender"
    metric_card(
        lbl_dorm, 
        f"{dormant_count:,}", 
        delta_color="negative", 
        subtext=sub_dorm
    )
with c4:
    lbl_never = "Never Purchased" if lang_code == "EN" else "Belum Pernah Transaksi"
    sub_never = "Registered accounts with no invoice history" if lang_code == "EN" else "Akun terdaftar tanpa histori invoice"
    metric_card(
        lbl_never, 
        f"{never_bought_count:,}", 
        subtext=sub_never
    )

st.markdown("---")

# -------------------------------------------------------------
# STRICT V1.1 MANDATORY DSS INSIGHT CARD
# -------------------------------------------------------------
at_risk_tier_a = len(df_filtered[(df_filtered['customer_health'] == 'At Risk') & (df_filtered['value_tier'].str.contains('Tier A'))])
high_prio_count = len(df_filtered[df_filtered['priority_score'] >= 70])

if lang_code == "EN":
    ic_badge = "CS RETENTION DECISION RULE"
    ic_title = "Churn Risk Mitigation & High-Value Account Prioritization Alert"
    ic_metric = f"{at_risk_count:,} At-Risk Customers ({at_risk_pct:.1f}% of transacting base)"
    ic_context = f"Analyzed from {total_cust:,} accounts ({purchasing_base:,} with purchasing history) within {filters['branch']} and {filters['segment']}."
    ic_insight = "At-risk customers have exceeded their normal purchasing cycles by 1.5x - 2.5x. This group contains Tier A (High Value) accounts that will become Dormant or defect to competitors without immediate intervention."
    ic_impacted = f"Outbound Customer Service Team, Account Executives at {filters['branch']}, and {at_risk_tier_a:,} at-risk Tier A accounts."
    ic_action = "CS Team: Immediately use the Priority Contact Worklist below to execute personal calls for accounts with priority score >= 70 within 24 hours offering 5% retention incentives."
    ic_target = f"{high_prio_count:,} High Priority Accounts (Score >= 70)"
else:
    ic_badge = "ATURAN KEPUTUSAN RETENSI CS"
    ic_title = "Peringatan Mitigasi Risiko Churn & Prioritisasi Akun Bernilai Tinggi"
    ic_metric = f"{at_risk_count:,} Pelanggan Berisiko ({at_risk_pct:.1f}% dari basis bertransaksi)"
    ic_context = f"Dianalisis dari {total_cust:,} akun ({purchasing_base:,} akun memiliki riwayat belanja) pada cakupan {filters['branch']} dan {filters['segment']}."
    ic_insight = "Pelanggan berisiko (At Risk) telah melewati siklus pembelian normal mereka hingga 1.5x - 2.5x. Dari kelompok ini, terdapat akun Tier A (High Value) yang jika tidak segera dihubungi akan berpindah status menjadi Dormant atau beralih ke percetakan kompetitor."
    ic_impacted = f"Tim Customer Service Outbound, Account Executive Cabang {filters['branch']}, serta {at_risk_tier_a:,} akun Tier A yang berisiko."
    ic_action = "Tim CS: Segera gunakan Daftar Kerja Prioritas Kontak (Worklist) di bawah untuk mengeksekusi panggilan personal pada akun skor prioritas >= 70 dalam 24 jam dengan penawaran voucher retensi 5%."
    ic_target = f"{high_prio_count:,} Akun Prioritas Tinggi (Skor >= 70)"

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
# TABBED DECISION SUPPORT INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_titles = [
        "🍩 Health Radar & Tier Segmentation",
        "📋 Priority Contact CS Worklist",
        "🌐 Market Value Distribution Matrix",
        "📊 RFM Analysis & Retention Depth"
    ]
else:
    tab_titles = [
        "🍩 Radar Kesehatan & Segmentasi Tier",
        "📋 Daftar Kerja Prioritas Kontak CS (Worklist)",
        "🌐 Matriks Sebaran Nilai Pasar",
        "📊 Analisis RFM & Kedalaman Retensi"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_titles)

with tab1:
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        hdr_health = "Customer Health Status Distribution (4 Categories)" if lang_code == "EN" else "Distribusi Status Kesehatan Pelanggan (4 Kategori)"
        st.subheader(hdr_health)
        df_health_counts = df_filtered["customer_health"].value_counts().reset_index()
        col_health = "Health Status" if lang_code == "EN" else "Status Kesehatan"
        col_count = "Customer Count" if lang_code == "EN" else "Jumlah Pelanggan"
        df_health_counts.columns = [col_health, col_count]
        
        color_map = {
            "Active Customer": "#3B82F6",
            "At Risk": "#F59E0B",
            "Dormant": "#EF4444",
            "Never Purchased": "#8B5CF6"
        }
        
        fig_health = px.pie(
            df_health_counts,
            names=col_health,
            values=col_count,
            hole=0.45,
            color=col_health,
            color_discrete_map=color_map
        )
        fig_health.update_traces(textposition='inside', textinfo='percent+label')
        apply_plotly_theme(fig_health, height=360)
        st.plotly_chart(fig_health, use_container_width=True)
        
    with col_h2:
        hdr_tier = "Customer Value Tier Distribution (Tier A / B / C)" if lang_code == "EN" else "Distribusi Nilai Pelanggan (Tier A / B / C)"
        st.subheader(hdr_tier)
        df_tier_counts = df_filtered[df_filtered["customer_health"] != "Never Purchased"]["value_tier"].value_counts().reset_index()
        col_tier = "Value Tier"
        col_tier_cnt = "Account Count" if lang_code == "EN" else "Jumlah Akun"
        df_tier_counts.columns = [col_tier, col_tier_cnt]
        
        fig_tier = px.bar(
            df_tier_counts,
            x=col_tier_cnt,
            y=col_tier,
            orientation="h",
            color=col_tier,
            color_discrete_map={
                "Tier A (High Value)": "#10B981",
                "Tier B (Medium Value)": "#3B82F6",
                "Tier C (Low Value)": "#6B7280"
            }
        )
        fig_tier.update_traces(marker_line_color="rgba(255, 255, 255, 0.7)", marker_line_width=1.5, opacity=0.92)
        apply_plotly_theme(fig_tier, height=360)
        st.plotly_chart(fig_tier, use_container_width=True)

with tab2:
    hdr_worklist = "📋 Outbound Customer Service Priority Contact Worklist" if lang_code == "EN" else "📋 Daftar Kerja Prioritas Kontak Customer Service (CS Outbound)"
    cap_worklist = "Ranked by Priority Score (Formula: Customer Value + Recency Risk + Transaction Frequency). Answers: 'Who should CS contact first?'" if lang_code == "EN" else "Diurutkan berdasarkan Skor Prioritas (Formula: Nilai Pelanggan + Risiko Recency + Frekuensi Transaksi). Menjawab langsung: 'Siapa yang harus dihubungi CS terlebih dahulu?'"
    st.subheader(hdr_worklist)
    st.caption(cap_worklist)
    
    worklist_df = df_filtered[df_filtered["customer_health"] != "Never Purchased"].copy()
    
    col_w1, col_w2 = st.columns([4, 6])
    with col_w1:
        lbl_ftier = "Filter Value Tier:" if lang_code == "EN" else "Filter Tier Nilai:"
        tier_filter = st.multiselect(
            lbl_ftier, 
            options=["Tier A (High Value)", "Tier B (Medium Value)", "Tier C (Low Value)"],
            default=["Tier A (High Value)", "Tier B (Medium Value)"]
        )
    with col_w2:
        lbl_fhealth = "Filter Health Status:" if lang_code == "EN" else "Filter Status Kesehatan:"
        health_filter = st.multiselect(
            lbl_fhealth, 
            options=["At Risk", "Dormant", "Active Customer"],
            default=["At Risk", "Dormant"]
        )
        
    if tier_filter:
        worklist_df = worklist_df[worklist_df["value_tier"].isin(tier_filter)]
    if health_filter:
        worklist_df = worklist_df[worklist_df["customer_health"].isin(health_filter)]
        
    top_contacts = worklist_df.sort_values(by="priority_score", ascending=False).head(20)
    
    if not top_contacts.empty:
        disp_contacts = top_contacts[[
            "customer_name", "customer_category", "value_tier", "lifetime_sales", 
            "days_since_last_purchase", "customer_health", "priority_score"
        ]].copy()
        
        lbl_ltv = "Lifetime Spend (LTV)" if lang_code == "EN" else "Total Belanja (LTV)"
        lbl_rec = "Recency"
        lbl_action = "CS Recommended Action" if lang_code == "EN" else "Rekomendasi Tindakan CS"
        day_suffix = "Days" if lang_code == "EN" else "Hari"
        
        disp_contacts[lbl_ltv] = disp_contacts["lifetime_sales"].apply(format_rupiah)
        disp_contacts[lbl_rec] = disp_contacts["days_since_last_purchase"].apply(lambda d: f"{int(d)} {day_suffix}" if pd.notnull(d) else "-")
        
        if lang_code == "EN":
            disp_contacts[lbl_action] = disp_contacts.apply(
                lambda r: "🚨 Call Immediately (24h SLA) + 5% Retention Discount" if r["priority_score"] >= 75 
                else ("⚠️ WA Check-in + Free Delivery Offer" if r["priority_score"] >= 50 else "📩 Include in Broadcast Email"),
                axis=1
            )
            rename_wl = {
                "customer_name": "Customer Name",
                "customer_category": "Segment",
                "value_tier": "Value Tier",
                "customer_health": "Status",
                "priority_score": "Priority Score (0-100)"
            }
        else:
            disp_contacts[lbl_action] = disp_contacts.apply(
                lambda r: "🚨 Telepon Segera (SLA 24 Jam) + Diskon Retensi 5%" if r["priority_score"] >= 75 
                else ("⚠️ WA Check-in + Penawaran Free Delivery" if r["priority_score"] >= 50 else "📩 Sertakan dalam Broadcast Email"),
                axis=1
            )
            rename_wl = {
                "customer_name": "Nama Pelanggan",
                "customer_category": "Segmen",
                "value_tier": "Tier Nilai",
                "customer_health": "Status",
                "priority_score": "Skor Prioritas (0-100)"
            }
        
        st.dataframe(
            disp_contacts[[
                "customer_name", "customer_category", "value_tier", lbl_ltv, 
                lbl_rec, "customer_health", "priority_score", lbl_action
            ]].rename(columns=rename_wl),
            use_container_width=True
        )
    else:
        st.info("No customers currently match the worklist filter criteria." if lang_code == "EN" else "Tidak ada pelanggan yang memenuhi kriteria filter worklist saat ini.")

with tab3:
    hdr_mkt = "Market Opportunity Map: Lifetime Value (LTV) vs Recency" if lang_code == "EN" else "Matriks Sebaran Nilai Pasar per Segmen"
    st.subheader(hdr_mkt)
    if not df_filtered.empty:
        df_market = df_filtered[df_filtered["customer_health"] != "Never Purchased"].groupby("customer_category").agg(
            customer_count=("customer_id", "nunique"),
            total_revenue=("lifetime_sales", "sum"),
            avg_ltv=("lifetime_sales", "mean")
        ).reset_index()
        
        lbl_cc = "Transacting Customer Count" if lang_code == "EN" else "Jumlah Pelanggan Bertransaksi"
        lbl_tr = "Total Confirmed Revenue (IDR)" if lang_code == "EN" else "Total Pendapatan Terkonfirmasi (IDR)"
        lbl_sc = "Segment" if lang_code == "EN" else "Segmen"
        fig_market = px.scatter(
            df_market,
            x="customer_count",
            y="total_revenue",
            size="avg_ltv",
            color="customer_category",
            hover_name="customer_category",
            labels={
                "customer_count": lbl_cc,
                "total_revenue": lbl_tr,
                "customer_category": lbl_sc
            }
        )
        apply_plotly_theme(fig_market, height=360)
        st.plotly_chart(fig_market, use_container_width=True)

with tab4:
    hdr_rfm = "Customer RFM Segment Distribution" if lang_code == "EN" else "Distribusi Segmen RFM Pelanggan"
    st.subheader(hdr_rfm)
    if not df_filtered.empty and "rfm_segment" in df_filtered.columns:
        df_rfm = df_filtered[df_filtered["customer_health"] != "Never Purchased"]["rfm_segment"].value_counts().reset_index()
        col_rfm_name = "RFM Segment" if lang_code == "EN" else "Segmen RFM"
        col_rfm_cnt = "Customer Count" if lang_code == "EN" else "Jumlah Pelanggan"
        df_rfm.columns = [col_rfm_name, col_rfm_cnt]
        
        rfm_colors = {
            "High Value Loyal": "#10B981",
            "Active Customer": "#2563EB",
            "At Risk": "#F59E0B",
            "Dormant": "#94A3B8"
        }
        fig_rfm = px.bar(
            df_rfm,
            x=col_rfm_cnt,
            y=col_rfm_name,
            orientation="h",
            color=col_rfm_name,
            color_discrete_map=rfm_colors,
            labels={col_rfm_name: col_rfm_name, col_rfm_cnt: col_rfm_cnt}
        )
        fig_rfm.update_traces(
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.5,
            opacity=0.92
        )
        apply_plotly_theme(fig_rfm, height=360)
        st.plotly_chart(fig_rfm, use_container_width=True)
