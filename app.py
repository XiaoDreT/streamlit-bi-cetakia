import importlib
import streamlit as st
import components.ui_components
importlib.reload(components.ui_components)
from components.ui_components import (
    inject_custom_css, render_header, global_sidebar_filters, 
    TRANSLATIONS
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
    module_tag="CETAKIA DSS V1"
)

if lang_code == "ID":
    philosophy_title = "🚀 Filosofi Sistem Pendukung Keputusan Bisnis"
    philosophy_desc = "Dashboard BI tradisional hanya menjawab <em>\"Berapa total pendapatannya?\"</em>. <strong>Cetakia BI</strong> dirancang sebagai <strong>Sistem Pendukung Keputusan (Decision Support System / DSS)</strong> berorientasi pelanggan untuk <strong>Cipta Grafika</strong>. Setiap metrik terhubung langsung dengan analisis penyebab utama, entitas yang terdampak, serta tindakan operasional yang nyata."
    s1_desc = "Metrik teramati & perbandingan baseline"
    s2_desc = "Pendorong utama & rincian segmen"
    s3_desc = "ID pelanggan, sales rep, lini produk"
    s4_desc = "Alur kerja tindakan & target SLA"
    mod_header = "📌 Modul Dashboard yang Tersedia"
    target_owner = "Target Pengguna: Owner, Manajemen Eksekutif"
    target_cs_mkt = "Target Pengguna: Manajer CS, Lead Marketing"
    target_cs_sales = "Target Pengguna: CS Representative, Sales AE"
    target_sales_mgr = "Target Pengguna: Manajer Sales, Lead Komersial"
    target_mkt_prod = "Target Pengguna: Manajer Marketing, Lead Kategori"
    target_owner_strat = "Target Pengguna: Owner, Direktur Strategi"
    exec_desc = "Kesehatan bisnis makro, tren penjualan & pesanan, sumber pendapatan berulang vs baru, benchmark 6 cabang (Cipta Graha, Cipta Digital, Cipta Galuh, Cipta Cianjur, Cipta Purwakarta, Cipta Online), dan risiko konsentrasi pelanggan utama."
    cust_intel_desc = "Radar kesehatan pelanggan (Healthy, Active, At Risk, Dormant), distribusi loyalitas RFM, daftar kerja retensi nilai tinggi, dan heatmap retensi kohort."
    cust_360_desc = "Profil akun tunggal, total belanja seumur hidup, interval kecepatan pembelian, mix kategori produk, kepatuhan finansial, dan pemicu cross-sell."
    sales_intel_desc = "Funnel konversi penawaran multi-tahap, leaderboard peluang expired yang hilang, win rate salesperson, dan peringatan kedaluwarsa 72 jam."
    prod_intel_desc = "Mix pendapatan kategori, matriks peluang Pendapatan Tinggi/Penetrasi Rendah, pasangan co-purchase keranjang belanja (Support, Lift), paket bundle komersial."
    mkt_intel_desc = "Pangsa 8 segmen pasar (Instansi, End User, Agen, Sekolah, UMKM, Industri, Employee, Divisi), catchment 6 cabang regional, kecepatan akuisisi pelanggan, kerapatan kluster industri."
    info_nav = "👈 **Gunakan menu navigasi sidebar di sebelah kiri untuk membuka modul dashboard.**"
else:
    philosophy_title = "🚀 Business Decision Support Philosophy"
    philosophy_desc = "Traditional BI dashboards only answer <em>\"What is the revenue?\"</em>. <strong>Cetakia BI</strong> is designed as a customer-oriented <strong>Decision Support System (DSS)</strong> for <strong>Cipta Grafika</strong>. Every metric is tied to root-cause insights, affected entities, and concrete operational actions."
    s1_desc = "Observed metric & baseline comparison"
    s2_desc = "Root-cause driver & segment breakdown"
    s3_desc = "Customer IDs, sales reps, product lines"
    s4_desc = "Assigned business workflow & target SLA"
    mod_header = "📌 Available Dashboard Modules"
    target_owner = "Target Users: Owner, Executive Management"
    target_cs_mkt = "Target Users: CS Manager, Marketing Lead"
    target_cs_sales = "Target Users: CS Representative, Sales AE"
    target_sales_mgr = "Target Users: Sales Manager, Commercial Lead"
    target_mkt_prod = "Target Users: Marketing Manager, Category Lead"
    target_owner_strat = "Target Users: Owner, Strategy Director"
    exec_desc = "Macro business health, sales & order trends, repeat vs new revenue sources, 6 branch benchmarks (Cipta Graha, Cipta Digital, Cipta Galuh, Cipta Cianjur, Cipta Purwakarta, Cipta Online), and top customer risk exposure."
    cust_intel_desc = "Customer health radar (Healthy, Active, At Risk, Dormant), RFM loyalty distribution, high-value retention worklist, cohort retention heatmap."
    cust_360_desc = "Single-account profile, lifetime observed spend, purchase velocity gap, preferred product basket, financial compliance, and cross-sell triggers."
    sales_intel_desc = "Multi-stage quotation conversion funnel, expired lost opportunity leaderboard, salesperson win rates, and urgent 72-hour expiry alerts."
    prod_intel_desc = "Category revenue mix, High Revenue/Low Penetration opportunity matrix, co-purchase basket affinity pairs (Support, Lift), commercial bundles."
    mkt_intel_desc = "Market segment share across 8 segments (Instansi, End User, Agen, Sekolah, UMKM, Industri, Employee, Divisi), 6 regional branch catchment, customer acquisition speed, industry cluster density."
    info_nav = "👈 **Select any module from the sidebar navigation menu to launch the dashboard.**"

# System Philosophy Banner
st.markdown(f"""
<div class="cetakia-card">
    <h3 style="color: #3B82F6; margin-top: 0;">{philosophy_title}</h3>
    <p style="font-size: 15px; line-height: 1.6;">
        {philosophy_desc}
    </p>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 20px;">
        <div style="background-color: rgba(37, 99, 235, 0.12); border-top: 4px solid #2563EB; border-radius: 8px; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #3B82F6;">STEP 1</div>
            <div style="color: #3B82F6; font-size: 15px; font-weight: 700; margin: 4px 0;">{t['what_happened']}</div>
            <div style="font-size: 13px; opacity: 0.9;">{s1_desc}</div>
        </div>
        <div style="background-color: rgba(217, 119, 6, 0.12); border-top: 4px solid #D97706; border-radius: 8px; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #F59E0B;">STEP 2</div>
            <div style="color: #F59E0B; font-size: 15px; font-weight: 700; margin: 4px 0;">{t['context_baseline']}</div>
            <div style="font-size: 13px; opacity: 0.9;">{s2_desc}</div>
        </div>
        <div style="background-color: rgba(219, 39, 119, 0.12); border-top: 4px solid #DB2777; border-radius: 8px; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #EC4899;">STEP 3</div>
            <div style="color: #EC4899; font-size: 15px; font-weight: 700; margin: 4px 0;">{t['why_who']}</div>
            <div style="font-size: 13px; opacity: 0.9;">{s3_desc}</div>
        </div>
        <div style="background-color: rgba(22, 163, 74, 0.12); border-top: 4px solid #16A34A; border-radius: 8px; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #10B981;">STEP 4</div>
            <div style="color: #10B981; font-size: 15px; font-weight: 700; margin: 4px 0;">{t['recommended_action']}</div>
            <div style="font-size: 13px; opacity: 0.9;">{s4_desc}</div>
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
