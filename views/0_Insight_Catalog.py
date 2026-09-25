import importlib
import streamlit as st
import components.ui_components
importlib.reload(components.ui_components)
from components.ui_components import (
    render_header, global_sidebar_filters, TRANSLATIONS
)

st.set_page_config(
    page_title="Insight Catalog — Cetakia BI DSS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Global Filters & Get Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

# Render Landing Header
render_header(
    title=t["app_title"],
    subtitle=t["app_subtitle"],
    module_tag="CETAKIA DSS V1.1"
)

if lang_code == "ID":
    philosophy_title = "🚀 Filosofi Sistem Pendukung Keputusan Bisnis (DSS V1.1)"
    philosophy_desc = "Dashboard BI tradisional hanya menjawab <em>\"Berapa total pendapatannya?\"</em>. <strong>Cetakia BI V1.1</strong> dirancang sebagai <strong>Stricter Business Decision Support System (DSS)</strong> berorientasi tindakan untuk <strong>Cipta Grafika</strong>. Setiap metrik dan visualisasi secara mutlak mengikuti formula: <strong>Metrik + Konteks + Insight + Entitas Terdampak + Rekomendasi Tindakan Bisnis</strong>."
    pill1 = "1. METRIK"
    pill2 = "2. KONTEKS"
    pill3 = "3. INSIGHT"
    pill3_title = "Akar Penyebab"
    pill4 = "4. TERDAMPAK"
    pill5 = "5. TINDAKAN"
    s1_desc = "Metrik teramati & deviasi"
    s2_desc = "Konteks rasio & baseline riil"
    s3_desc = "Akar penyebab & diagnosis"
    s4_desc = "Akun/lini produk terdampak"
    s5_desc = "Rekomendasi tindakan & SLA"
    mod_header = "📌 Modul Decision Support System V1.1"
    target_owner = "Target: Owner, Direksi & Manajemen Eksekutif"
    target_cs_mkt = "Target: Manajer CS, Lead Retention & Marketing"
    target_cs_sales = "Target: Account Executive, CS Team & Sales"
    target_sales_mgr = "Target: Manajer Penjualan & Lead Komersial"
    target_mkt_prod = "Target: Product Manager, Merchandising & Marketing"
    target_owner_strat = "Target: Owner, Direktur Strategi & Ekspansi Bisnis"
    exec_desc = "Kesehatan makro bisnis, pendapatan bersih riil (eksklusi invoice cancel), dekomposisi Repeat vs New, benchmark 6 cabang regional, dan mitigasi risiko konsentrasi top customer."
    cust_intel_desc = "Klasifikasi 4 status kesehatan pelanggan (Never Purchased, Active, At Risk, Dormant), Value Tier (A/B/C), Priority Score (0-100), dan High Priority Worklist operasional CS."
    cust_360_desc = "Profil akun tunggal 360°, Customer Value Tier, Customer Journey Stage, Next Best Action Engine berbasis rule otomatis, dan riwayat ledger faktur valid."
    sales_intel_desc = "Rekonstruksi quotation funnel: Total Pipeline (Rp 27,1M), Converted (Rp 3,63M), Open Opportunity (Rp 2,18M), Lost Opportunity (Rp 21,3M), analisis drop-off %, dan worklist urgent 72 jam."
    prod_intel_desc = "Mix kategori produk, matriks High Revenue/Low Penetration, affinity basket analysis (Lift, Support, Confidence), dan Actionable Cross-Sell Target List (Kemasan tanpa Stiker)."
    mkt_intel_desc = "Matriks Peluang Pasar 4 Kuadran (Strategic, Growth, Retention, Development), kontribusi 8 segmen pelanggan, catchment 6 cabang, dan strategi alokasi sumber daya."
    info_nav = "👈 **Gunakan menu navigasi sidebar di sebelah kiri untuk membuka modul dashboard DSS V1.1.**"
else:
    philosophy_title = "🚀 Business Decision Support Philosophy (DSS V1.1)"
    philosophy_desc = "Traditional BI dashboards only answer <em>\"What is the revenue?\"</em>. <strong>Cetakia BI V1.1</strong> is engineered as an actionable, <strong>Stricter Business Decision Support System (DSS)</strong> for <strong>Cipta Grafika</strong>. Every metric and chart strictly enforces: <strong>Metric + Context + Insight + Who is Impacted + Recommended Action</strong>."
    pill1 = "1. METRIC"
    pill2 = "2. CONTEXT"
    pill3 = "3. INSIGHT"
    pill3_title = "Root Cause"
    pill4 = "4. IMPACTED"
    pill5 = "5. ACTION"
    s1_desc = "Observed metric & delta"
    s2_desc = "Context ratio & baseline"
    s3_desc = "Root cause & diagnosis"
    s4_desc = "Impacted accounts/products"
    s5_desc = "Assigned action & target SLA"
    mod_header = "📌 Available DSS V1.1 Modules"
    target_owner = "Target: Owner, Executive Management"
    target_cs_mkt = "Target: CS Manager, Retention & Marketing Lead"
    target_cs_sales = "Target: Account Executive, CS Team & Sales"
    target_sales_mgr = "Target: Sales Manager, Commercial Operations"
    target_mkt_prod = "Target: Product Manager, Merchandising & Marketing"
    target_owner_strat = "Target: Owner, Strategy & Business Dev"
    exec_desc = "Macro enterprise health, net confirmed revenue (cancelled orders excluded), Repeat vs New breakdown, 6 regional branch benchmarks, and top customer concentration risk mitigation."
    cust_intel_desc = "Strict 4-state customer health (Never Purchased, Active, At Risk, Dormant), Value Tier (A/B/C), Priority Score (0-100), and High Priority CS Retention Worklist."
    cust_360_desc = "Customer 360 single view, Value Tier badge, Customer Journey stage, automated rule-based Next Best Action Engine, and confirmed transaction ledger."
    sales_intel_desc = "Rebuilt quotation funnel: Total Pipeline (Rp 27.1B), Converted (Rp 3.63B), Open Pipeline (Rp 2.18B), Lost Pipeline (Rp 21.3B), drop-off % per stage, and urgent 72-hour worklist."
    prod_intel_desc = "Product category mix, High Revenue/Low Penetration matrix, market basket affinity pairs (Lift, Support, Confidence), and Actionable Cross-Sell Target List (Packaging buyers without Stickers)."
    mkt_intel_desc = "4-Quadrant Market Opportunity Matrix (Strategic, Growth, Retention, Development), 8 segment contributions, regional branch catchments, and resource allocation playbook."
    info_nav = "👈 **Select any module from the sidebar navigation menu to launch the DSS V1.1 dashboard.**"

# System Philosophy Banner
st.markdown(f"""
<div class="cetakia-card">
    <h3 style="color: #3B82F6; margin-top: 0;">{philosophy_title}</h3>
    <p style="font-size: 15px; line-height: 1.6;">
        {philosophy_desc}
    </p>
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 20px;">
        <div style="background-color: rgba(37, 99, 235, 0.12); border-top: 4px solid #2563EB; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #3B82F6;">{pill1}</div>
            <div style="color: #3B82F6; font-size: 14px; font-weight: 700; margin: 4px 0;">{t['what_happened']}</div>
            <div style="font-size: 12px; opacity: 0.9;">{s1_desc}</div>
        </div>
        <div style="background-color: rgba(217, 119, 6, 0.12); border-top: 4px solid #D97706; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #F59E0B;">{pill2}</div>
            <div style="color: #F59E0B; font-size: 14px; font-weight: 700; margin: 4px 0;">{t['context_baseline']}</div>
            <div style="font-size: 12px; opacity: 0.9;">{s2_desc}</div>
        </div>
        <div style="background-color: rgba(139, 92, 246, 0.12); border-top: 4px solid #8B5CF6; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #A78BFA;">{pill3}</div>
            <div style="color: #A78BFA; font-size: 14px; font-weight: 700; margin: 4px 0;">{pill3_title}</div>
            <div style="font-size: 12px; opacity: 0.9;">{s3_desc}</div>
        </div>
        <div style="background-color: rgba(219, 39, 119, 0.12); border-top: 4px solid #DB2777; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #EC4899;">{pill4}</div>
            <div style="color: #EC4899; font-size: 14px; font-weight: 700; margin: 4px 0;">{t['why_who']}</div>
            <div style="font-size: 12px; opacity: 0.9;">{s4_desc}</div>
        </div>
        <div style="background-color: rgba(22, 163, 74, 0.12); border-top: 4px solid #16A34A; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #10B981;">{pill5}</div>
            <div style="color: #10B981; font-size: 14px; font-weight: 700; margin: 4px 0;">{t['recommended_action']}</div>
            <div style="font-size: 12px; opacity: 0.9;">{s5_desc}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.subheader(mod_header)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="cetakia-metric-card">
        <h4 style="color: #3B82F6; margin-top: 0;">📊 {t['exec_title']}</h4>
        <p style="font-size: 13px;">{exec_desc}</p>
        <p style="color: #3B82F6; font-weight: 600; font-size: 13px;">{target_owner}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="cetakia-metric-card">
        <h4 style="color: #3B82F6; margin-top: 0;">👥 {t['cust_intel_title']}</h4>
        <p style="font-size: 13px;">{cust_intel_desc}</p>
        <p style="color: #3B82F6; font-weight: 600; font-size: 13px;">{target_cs_mkt}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="cetakia-metric-card">
        <h4 style="color: #3B82F6; margin-top: 0;">👤 {t['cust_360_title']}</h4>
        <p style="font-size: 13px;">{cust_360_desc}</p>
        <p style="color: #3B82F6; font-weight: 600; font-size: 13px;">{target_cs_sales}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="cetakia-metric-card">
        <h4 style="color: #3B82F6; margin-top: 0;">🎯 {t['sales_intel_title']}</h4>
        <p style="font-size: 13px;">{sales_intel_desc}</p>
        <p style="color: #3B82F6; font-weight: 600; font-size: 13px;">{target_sales_mgr}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="cetakia-metric-card">
        <h4 style="color: #3B82F6; margin-top: 0;">📦 {t['prod_intel_title']}</h4>
        <p style="font-size: 13px;">{prod_intel_desc}</p>
        <p style="color: #3B82F6; font-weight: 600; font-size: 13px;">{target_mkt_prod}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="cetakia-metric-card">
        <h4 style="color: #3B82F6; margin-top: 0;">🌐 {t['mkt_intel_title']}</h4>
        <p style="font-size: 13px;">{mkt_intel_desc}</p>
        <p style="color: #3B82F6; font-weight: 600; font-size: 13px;">{target_owner_strat}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.info(info_nav)
