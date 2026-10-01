import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_intelligence, load_customer_data
from utils.intelligence_engine import (
    classify_customer_health_8, assign_customer_value_category,
    compute_priority_score
)
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    render_section_info, render_summary_strip,
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

# Apply Customer 8-Segment Intelligence & Friendly Customer Value Classification
df_intel_merged["customer_segment_8"] = classify_customer_health_8(df_intel_merged)
df_intel_merged["customer_value_cat"] = assign_customer_value_category(df_intel_merged, lang="ID")
df_intel_merged["priority_score"] = compute_priority_score(df_intel_merged)

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
subtitle_text = "Analisis Perilaku Pelanggan, 8 Segmen Bisnis, Klasifikasi Nilai Belanja & Daftar Prioritas CS" if lang_code == "ID" else "Customer Behavioral Analysis, 8 Business Segments, Value Classification & CS Priority Worklist"
render_header(
    title=t["cust_intel_title"],
    subtitle=subtitle_text,
    module_tag="CUSTOMER INTELLIGENCE / RETENTION"
)

# -------------------------------------------------------------
# SUMMARY KPI CARDS (USER-ORIENTED METRICS)
# -------------------------------------------------------------
total_cust = len(df_filtered)
buyers_df = df_filtered[df_filtered["total_orders"] > 0]
purchasing_base = len(buyers_df)
prospect_count = total_cust - purchasing_base

# Active: <= 45 days; At Risk: 46 - 90 days; Dormant: > 90 days
active_count = len(buyers_df[buyers_df["days_since_last_purchase"] <= 45])
at_risk_count = len(buyers_df[(buyers_df["days_since_last_purchase"] > 45) & (buyers_df["days_since_last_purchase"] <= 90)])
dormant_count = len(buyers_df[buyers_df["days_since_last_purchase"] > 90])
at_risk_pct = (at_risk_count / purchasing_base * 100) if purchasing_base > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    lbl_act = "Pelanggan Aktif" if lang_code == "ID" else "Active Customers"
    sub_act = "Belanja dalam <= 45 hari terakhir" if lang_code == "ID" else "Purchased within <= 45 days"
    metric_card(lbl_act, f"{active_count:,}", delta_color="positive", subtext=sub_act)

with c2:
    lbl_risk = "Mulai Jarang Belanja" if lang_code == "ID" else "At-Risk Customers"
    delta_risk = f"{at_risk_pct:.1f}% basis pembeli" if lang_code == "ID" else f"{at_risk_pct:.1f}% buyer base"
    sub_risk = "Tidak belanja 46 - 90 hari (berisiko churn)" if lang_code == "ID" else "Inactive for 46 - 90 days"
    metric_card(lbl_risk, f"{at_risk_count:,}", delta=delta_risk, delta_color="negative", subtext=sub_risk)

with c3:
    lbl_dorm = "Pelanggan Pasif" if lang_code == "ID" else "Dormant Customers"
    sub_dorm = "Tidak belanja > 90 hari (perlu aktivasi)" if lang_code == "ID" else "Inactive for > 90 days"
    metric_card(lbl_dorm, f"{dormant_count:,}", delta_color="negative", subtext=sub_dorm)

with c4:
    lbl_prospect = "Prospek Belum Transaksi" if lang_code == "ID" else "Unconverted Prospects"
    sub_prospect = "Akun terdaftar tanpa histori pesanan" if lang_code == "ID" else "Registered accounts with 0 orders"
    metric_card(lbl_prospect, f"{prospect_count:,}", subtext=sub_prospect)

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD (DECISION SUPPORT)
# -------------------------------------------------------------
high_val_risk = len(buyers_df[(buyers_df["customer_segment_8"] == "At Risk High Value")])
high_prio_count = len(buyers_df[buyers_df["priority_score"] >= 70])

if lang_code == "EN":
    ic_badge = "CS RETENTION DECISION SUPPORT"
    ic_title = "Customer Churn Risk Alert & High-Value Account Retention Priority"
    ic_metric = f"{at_risk_count:,} At-Risk Customers ({high_val_risk:,} High-Value Accounts)"
    ic_context = f"Evaluated from {purchasing_base:,} active buyer accounts across branch '{filters['branch']}' and segment '{filters['segment']}'."
    ic_insight = f"There are {high_val_risk:,} high-value accounts that have not placed an order in over 60 days. These accounts represent substantial lifetime revenue and are vulnerable to competitor poaching if not engaged."
    ic_impacted = f"Customer Service Outbound, Regional Sales Account Executives, and {high_val_risk:,} Key Accounts."
    ic_action = "CS & Sales Team: Focus immediate personal outreach on the High-Value At-Risk Worklist. Inquire regarding recent printing satisfaction and offer tailored retention incentives."
    ic_target = f"{high_prio_count:,} Priority Contact Accounts (Score >= 70)"
else:
    ic_badge = "KEPUTUSAN RETENSI PELANGGAN"
    ic_title = "Peringatan Risiko Churn & Prioritas Penyelamatan Pelanggan Bernilai Tinggi"
    ic_metric = f"{at_risk_count:,} Pelanggan Mulai Jarang Belanja ({high_val_risk:,} Akun Bernilai Tinggi)"
    ic_context = f"Dianalisis dari {purchasing_base:,} akun yang memiliki riwayat transaksi di cabang '{filters['branch']}' dan segmen '{filters['segment']}'."
    ic_insight = f"Terdapat {high_val_risk:,} akun bernilai tinggi (At Risk High Value) yang belum bertransaksi selama lebih dari 60 hari. Kelompok ini menyumbang nilai belanja kumulatif yang signifikan dan berisiko beralih ke kompetitor jika tidak segera dihubungi."
    ic_impacted = f"Tim Customer Service Outbound, Account Executive Cabang {filters['branch']}, serta {high_val_risk:,} Akun Kunci."
    ic_action = "Tim CS & Sales: Segera hubungi akun pada Daftar Kerja Prioritas Kontak di bawah. Tanyakan kepuasan cetak terakhir dan berikan penawaran khusus atau bebas biaya kirim untuk pesanan berikutnya."
    ic_target = f"{high_prio_count:,} Akun Prioritas Kontak (Skor >= 70)"

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
# TABBED CUSTOMER INTELLIGENCE INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_titles = [
        "👥 8-Segment Customer Health & Value",
        "📋 CS Outbound Priority Worklist",
        "🌐 Segment Market Value Distribution",
        "📊 Customer Loyalty & Activity Status"
    ]
else:
    tab_titles = [
        "👥 Segmentasi Perilaku & Nilai Pelanggan",
        "📋 Daftar Kerja Prioritas Kontak CS",
        "🌐 Sebaran Nilai Pasar per Segmen",
        "📊 Status Loyalitas & Keaktifan Belanja"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_titles)

# -------------------------------------------------------------
# TAB 1: 8 KATEGORI SEGMENTASI & DISTRIBUSI NILAI PELANGGAN
# -------------------------------------------------------------
with tab1:
    if lang_code == "EN":
        render_section_info(
            title="Customer Behavioral Segmentation (8 Operational Categories) & Value Distribution",
            subtitle="Mapping the customer portfolio into 8 clear operational categories easily understood by all business stakeholders.",
            what_it_shows="Customer counts across 8 behavioral segments (Champion, At Risk, Regular, etc.) and customer value tiers (Very High, High, Medium, Low).",
            why_important="Helps management and CS tailor strategies: whom to reward, whom to rescue, and whom to grow.",
            simple_insight="Commercial focus divides into 4 action quadrants: (1) <b>High Value</b>: Champion & High Value Low Frequency; (2) <b>Retention Priority</b>: At Risk High Value; (3) <b>Upside Potential</b>: Cross-Sell & Frequent Small Buyer; (4) <b>Inactive</b>: Dormant."
        )
    else:
        render_section_info(
            title="Segmentasi Perilaku Pelanggan (8 Kategori Bisnis) & Distribusi Nilai",
            subtitle="Memetakan portofolio pelanggan ke dalam 8 kategori operasional yang mudah dipahami orang awam.",
            what_it_shows="Jumlah pelanggan di setiap segmen perilaku (Champion, At Risk, Regular, dsb.) dan sebaran nilai belanja (Sangat Tinggi, Tinggi, Menengah, Rendah).",
            why_important="Membantu manajemen dan CS membedakan strategi perlakuan: siapa yang harus dirawat, siapa yang harus diselamatkan, dan siapa yang berpotensi dikembangkan.",
            simple_insight="Fokus bisnis terbagi 4 kuadran aksi: (1) <b>Bernilai Tinggi</b>: Champion & High Value Low Frequency; (2) <b>Perlu Dipertahankan</b>: At Risk High Value; (3) <b>Potensi Berkembang</b>: Cross-Sell & Frequent Small Buyer; (4) <b>Mulai Pasif</b>: Dormant."
        )
    
    col_s1, col_s2 = st.columns([6, 4])
    
    with col_s1:
        st.subheader("Distribusi 8 Segmen Perilaku Pelanggan" if lang_code == "ID" else "8-Segment Customer Distribution")
        seg8_counts = buyers_df["customer_segment_8"].value_counts().reset_index()
        lbl_seg_col = "Segmen" if lang_code == "ID" else "Segment"
        lbl_cnt_col = "Jumlah Pelanggan" if lang_code == "ID" else "Customer Accounts"
        seg8_counts.columns = [lbl_seg_col, lbl_cnt_col]
        
        # Color mapping for business clarity
        color_seg8 = {
            "Champion / Key Account": "#10B981",          # Green - Top
            "Regular Customer": "#3B82F6",                # Blue - Consistent
            "Cross-Sell Potential": "#06B6D4",            # Cyan - Upside
            "High Value Low Frequency": "#8B5CF6",        # Purple - Big basket
            "Frequent Small Buyer": "#6366F1",            # Indigo - High velocity
            "New / Recent Buyer": "#14B8A6",              # Teal - New
            "At Risk High Value": "#F59E0B",              # Amber - Urgent retention
            "Dormant / Low Value": "#94A3B8"              # Slate - Inactive
        }
        
        fig_seg8 = px.bar(
            seg8_counts.sort_values(by=lbl_cnt_col, ascending=True),
            x=lbl_cnt_col,
            y=lbl_seg_col,
            orientation="h",
            color=lbl_seg_col,
            color_discrete_map=color_seg8,
            text=lbl_cnt_col
        )
        fig_seg8.update_traces(
            textposition="outside",
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.2
        )
        apply_plotly_theme(fig_seg8, height=390)
        st.plotly_chart(fig_seg8, use_container_width=True)
        
    with col_s2:
        st.subheader("Distribusi Nilai Pelanggan" if lang_code == "ID" else "Customer Value Distribution")
        val_counts = buyers_df["customer_value_cat"].value_counts().reset_index()
        lbl_vcat_col = "Kategori Nilai" if lang_code == "ID" else "Value Category"
        lbl_vcnt_col = "Jumlah Akun" if lang_code == "ID" else "Accounts"
        val_counts.columns = [lbl_vcat_col, lbl_vcnt_col]
        
        color_val = {
            "Customer Bernilai Sangat Tinggi": "#10B981",
            "Customer Bernilai Tinggi": "#3B82F6",
            "Customer Bernilai Menengah": "#F59E0B",
            "Customer Bernilai Rendah": "#94A3B8",
            "Very High Value Customer": "#10B981",
            "High Value Customer": "#3B82F6",
            "Medium Value Customer": "#F59E0B",
            "Low Value Customer": "#94A3B8"
        }
        
        fig_val = px.pie(
            val_counts,
            names=lbl_vcat_col,
            values=lbl_vcnt_col,
            hole=0.45,
            color=lbl_vcat_col,
            color_discrete_map=color_val
        )
        fig_val.update_traces(textposition='inside', textinfo='percent+label')
        apply_plotly_theme(fig_val, height=390)
        st.plotly_chart(fig_val, use_container_width=True)

    # 4 Quadrant Business Meaning Narrative
    st.markdown(f"### {'🧭 Panduan Makna Bisnis Portofolio Pelanggan' if lang_code == 'ID' else '🧭 Customer Portfolio Strategic Business Guide'}")
    q1, q2, q3, q4 = st.columns(4)
    acct_lbl = "Akun" if lang_code == "ID" else "Accounts"
    with q1:
        champ_c = len(buyers_df[buyers_df["customer_segment_8"].isin(["Champion / Key Account", "High Value Low Frequency"])])
        if lang_code == "EN":
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #10B981; padding: 14px;">
                <div style="color: #10B981; font-weight: 700; font-size: 13px;">💎 HIGH-VALUE CUSTOMERS</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{champ_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">Champion & High Value Low Frequency. Deliver greatest margins. Focus: Nurture relationship and grant priority production queue.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #10B981; padding: 14px;">
                <div style="color: #10B981; font-weight: 700; font-size: 13px;">💎 PELANGGAN BERNILAI TINGGI</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{champ_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">Champion & High Value Low Frequency. Menopang margin terbesar. Fokus: Jaga hubungan dan berikan prioritas antrean produksi.</div>
            </div>
            """, unsafe_allow_html=True)
    with q2:
        risk_c = len(buyers_df[buyers_df["customer_segment_8"] == "At Risk High Value"])
        if lang_code == "EN":
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #F59E0B; padding: 14px;">
                <div style="color: #F59E0B; font-weight: 700; font-size: 13px;">🚨 RETENTION PRIORITY</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{risk_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">At Risk High Value. Heavy spenders who have delayed orders (> 60 days). Top priority for CS Outbound outreach!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #F59E0B; padding: 14px;">
                <div style="color: #F59E0B; font-weight: 700; font-size: 13px;">🚨 PERLU DIPERTAHANKAN</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{risk_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">At Risk High Value. Berbelanja banyak di masa lalu namun mulai pasif (> 60 hari). Prioritas utama panggilan CS Outbound!</div>
            </div>
            """, unsafe_allow_html=True)
    with q3:
        pot_c = len(buyers_df[buyers_df["customer_segment_8"].isin(["Cross-Sell Potential", "Frequent Small Buyer"])])
        if lang_code == "EN":
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #06B6D4; padding: 14px;">
                <div style="color: #06B6D4; font-weight: 700; font-size: 13px;">🚀 GROWTH POTENTIAL</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{pot_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">Cross-Sell & Frequent Small Buyer. High velocity, smaller baskets. Upsell potential through packaged bundles.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #06B6D4; padding: 14px;">
                <div style="color: #06B6D4; font-weight: 700; font-size: 13px;">🚀 POTENSI DIKEMBANGKAN</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{pot_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">Cross-Sell & Frequent Small Buyer. Sering belanja dengan nilai kecil. Potensial dinaikkan AOV-nya melalui bundling.</div>
            </div>
            """, unsafe_allow_html=True)
    with q4:
        dorm_c = len(buyers_df[buyers_df["customer_segment_8"] == "Dormant / Low Value"])
        if lang_code == "EN":
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #94A3B8; padding: 14px;">
                <div style="color: #94A3B8; font-weight: 700; font-size: 13px;">💤 INACTIVE / DORMANT</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{dorm_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">Dormant / Low Value. Inactive > 90 days. Reach via automated seasonal email/WhatsApp broadcast vouchers.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cetakia-card" style="border-top: 4px solid #94A3B8; padding: 14px;">
                <div style="color: #94A3B8; font-weight: 700; font-size: 13px;">💤 MULAI PASIF</div>
                <div style="font-size: 20px; font-weight: 800; margin: 4px 0;">{dorm_c:,} {acct_lbl}</div>
                <div style="font-size: 12px; opacity: 0.85;">Dormant / Low Value. Tidak bertransaksi > 90 hari. Jangkau melalui broadcast WhatsApp promosi otomatis berkala.</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 2: DAFTAR KERJA PRIORITAS KONTAK CS (WORKLIST)
# -------------------------------------------------------------
with tab2:
    if lang_code == "EN":
        render_section_info(
            title="Customer Service Outbound Priority Contact Worklist",
            subtitle="Prioritized contact queue for the CS & retention team based on customer value and churn risk.",
            what_it_shows="Customer name, segment, value classification, lifetime spend (LTV), days since last purchase, and priority score (0 - 100).",
            why_important="Eliminates CS confusion: specifies exactly which accounts must be called today and explains why each account is worth retaining.",
            simple_insight="Accounts with top priority scores (>= 70) are high-value buyers whose normal buying cycle is overdue. Reach them immediately to prevent competitor switching."
        )
    else:
        render_section_info(
            title="Daftar Kerja Prioritas Kontak Customer Service (CS Outbound)",
            subtitle="Daftar pelanggan yang diprioritaskan untuk dihubungi oleh tim CS berdasarkan nilai akun dan risiko churn.",
            what_it_shows="Nama pelanggan, segmen, klasifikasi nilai, total belanja seumur hidup, kapan terakhir belanja, dan skor prioritas (0 - 100).",
            why_important="Menghilangkan kebingungan tim CS: siapa yang harus ditelepon hari ini dan mengapa pelanggan tersebut penting untuk diselamatkan.",
            simple_insight="Akun dengan skor prioritas tertinggi (>= 70) adalah pelanggan bernilai tinggi yang siklus belanjanya terlewat. Kontak mereka segera untuk mencegah perpindahan ke percetakan kompetitor."
        )
    
    # Priority Summary Badges
    prio_top = buyers_df[buyers_df["priority_score"] >= 70]
    if lang_code == "EN":
        prio_strip = [
            {"label": "Total in Worklist", "value": f"{len(buyers_df):,} Accounts", "desc": "All active buying customer accounts", "color": "#3B82F6"},
            {"label": "Urgent Priority (Score >= 70)", "value": f"{len(prio_top):,} Accounts", "desc": "Mandatory CS outreach within 24h", "color": "#EF4444"},
            {"label": "At-Risk High-Value Accounts", "value": f"{high_val_risk:,} Accounts", "desc": "Top spenders with delayed orders", "color": "#F59E0B"},
            {"label": "Average Priority Score", "value": f"{buyers_df['priority_score'].mean():.0f} / 100", "desc": "Portfolio contact urgency index", "color": "#10B981"}
        ]
    else:
        prio_strip = [
            {"label": "Total Masuk Worklist", "value": f"{len(buyers_df):,} Akun", "desc": "Seluruh akun pelanggan aktif bertransaksi", "color": "#3B82F6"},
            {"label": "Prioritas Mendesak (Skor >= 70)", "value": f"{len(prio_top):,} Akun", "desc": "Wajib dihubungi CS dalam 24 jam", "color": "#EF4444"},
            {"label": "Akun Bernilai Tinggi Berisiko", "value": f"{high_val_risk:,} Akun", "desc": "Mantan pembeli besar yang belum kembali", "color": "#F59E0B"},
            {"label": "Rata-rata Skor Prioritas", "value": f"{buyers_df['priority_score'].mean():.0f} / 100", "desc": "Indeks urgensi kontak portofolio", "color": "#10B981"}
        ]
    render_summary_strip(prio_strip)
    
    col_w1, col_w2 = st.columns([5, 5])
    with col_w1:
        if lang_code == "EN":
            val_filter_opts = [
                "All Value Categories",
                "Customer Bernilai Sangat Tinggi",
                "Customer Bernilai Tinggi",
                "Customer Bernilai Menengah",
                "Customer Bernilai Rendah"
            ]
            lbl_val_s = "Filter by Customer Value Tier:"
        else:
            val_filter_opts = [
                "Semua Kategori Nilai",
                "Customer Bernilai Sangat Tinggi",
                "Customer Bernilai Tinggi",
                "Customer Bernilai Menengah",
                "Customer Bernilai Rendah"
            ]
            lbl_val_s = "Saring Berdasarkan Nilai Pelanggan:"
        sel_val_filter = st.selectbox(lbl_val_s, options=val_filter_opts, index=0)
    with col_w2:
        all_seg_str = "All Behavioral Segments" if lang_code == "EN" else "Semua Segmen Perilaku"
        seg_filter_opts = [all_seg_str] + list(color_seg8.keys())
        lbl_seg_s = "Filter by Behavioral Segment:" if lang_code == "EN" else "Saring Berdasarkan Segmen Perilaku:"
        sel_seg_filter = st.selectbox(lbl_seg_s, options=seg_filter_opts, index=0)
        
    worklist_df = buyers_df.copy()
    if sel_val_filter not in ["Semua Kategori Nilai", "All Value Categories"]:
        worklist_df = worklist_df[worklist_df["customer_value_cat"] == sel_val_filter]
    if sel_seg_filter not in ["Semua Segmen Perilaku", "All Behavioral Segments"]:
        worklist_df = worklist_df[worklist_df["customer_segment_8"] == sel_seg_filter]
        
    top_contacts = worklist_df.sort_values(by="priority_score", ascending=False).head(30)
    
    if not top_contacts.empty:
        disp_contacts = top_contacts[[
            "customer_name", "customer_category", "customer_segment_8", "customer_value_cat",
            "lifetime_sales", "days_since_last_purchase", "priority_score"
        ]].copy()
        
        disp_contacts["Total Belanja (LTV)"] = disp_contacts["lifetime_sales"].apply(format_rupiah)
        days_str = "days ago" if lang_code == "EN" else "hari lalu"
        just_now_str = "Just now" if lang_code == "EN" else "Baru saja"
        disp_contacts["Terakhir Belanja"] = disp_contacts["days_since_last_purchase"].apply(
            lambda d: f"{int(d)} {days_str}" if pd.notnull(d) else just_now_str
        )
        disp_contacts["Skor Prioritas"] = disp_contacts["priority_score"].apply(lambda s: f"{s} / 100")
        
        if lang_code == "EN":
            rename_wl = {
                "customer_name": "Customer Name",
                "customer_category": "Segment",
                "customer_segment_8": "Behavioral Status",
                "customer_value_cat": "Customer Value",
                "Total Belanja (LTV)": "Lifetime Value (LTV)",
                "Terakhir Belanja": "Last Purchase",
                "Skor Prioritas": "Contact Urgency"
            }
        else:
            rename_wl = {
                "customer_name": "Nama Pelanggan",
                "customer_category": "Segmen",
                "customer_segment_8": "Status Perilaku",
                "customer_value_cat": "Nilai Pelanggan",
                "Total Belanja (LTV)": "Total Belanja (LTV)",
                "Terakhir Belanja": "Terakhir Belanja",
                "Skor Prioritas": "Urgensi Kontak"
            }
        
        st.dataframe(
            disp_contacts[["customer_name", "customer_category", "customer_segment_8", "customer_value_cat", "Total Belanja (LTV)", "Terakhir Belanja", "Skor Prioritas"]].rename(columns=rename_wl).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Tidak ada pelanggan yang memenuhi kriteria filter worklist saat ini." if lang_code == "ID" else "No customers match the current worklist filter.")

# -------------------------------------------------------------
# TAB 3: MATRIKS SEBARAN NILAI PASAR (GROUPED / RANKING BAR CHART)
# -------------------------------------------------------------
with tab3:
    if lang_code == "EN":
        render_section_info(
            title="Customer Segment Market Value Distribution",
            subtitle="Comprehensive comparison between total net revenue, average order value (AOV), and transacting customer counts.",
            what_it_shows="Bar charts and summary tables highlighting confirmed net revenue vs customer account base across market segments.",
            why_important="Prevents volume bias: segments with the largest account base (like End Users) do not necessarily generate the highest revenue compared to the Industrial segment.",
            simple_insight="<b>Industrial & Division</b> segments yield the highest average transaction values per order. <b>End User & MSME</b> segments deliver the highest transaction volume."
        )
    else:
        render_section_info(
            title="Sebaran Nilai Pasar per Segmen Pelanggan",
            subtitle="Perbandingan komprehensif antara total pendapatan, rata-rata nilai pesanan (AOV), dan jumlah pelanggan bertransaksi.",
            what_it_shows="Grafik batang dan tabel kinerja yang memperlihatkan kontribusi uang nyata vs jumlah pelanggan dari setiap segmen pasar.",
            why_important="Menghindari bias: segmen dengan pelanggan terbanyak (seperti End User) belum tentu menyumbang pendapatan terbesar dibanding segmen Industri.",
            simple_insight="Segmen <b>Industri & Divisi</b> menyumbang nilai transaksi rata-rata tertinggi per pesanan. Segmen <b>End User & UMKM</b> menyumbang volume transaksi terbesar."
        )
    
    if not buyers_df.empty:
        df_market = buyers_df.groupby("customer_category").agg(
            customer_count=("customer_id", "nunique"),
            total_revenue=("lifetime_sales", "sum"),
            avg_aov=("average_order_value", "mean")
        ).reset_index().sort_values(by="total_revenue", ascending=False)
        
        col_m1, col_m2 = st.columns([6, 4])
        with col_m1:
            st.markdown(f"**{'Perbandingan Total Pendapatan per Segmen' if lang_code == 'ID' else 'Total Revenue Comparison by Segment'}**")
            lbl_mkt_cat = "Segmen Pelanggan" if lang_code == "ID" else "Customer Segment"
            lbl_mkt_rev = "Total Pendapatan (IDR)" if lang_code == "ID" else "Total Revenue (IDR)"
            fig_mkt_bar = px.bar(
                df_market,
                x="customer_category",
                y="total_revenue",
                color="total_revenue",
                text=df_market["total_revenue"].apply(lambda v: format_rupiah(v)),
                color_continuous_scale=["#93C5FD", "#2563EB"],
                labels={"customer_category": lbl_mkt_cat, "total_revenue": lbl_mkt_rev}
            )
            fig_mkt_bar.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_mkt_bar, height=360)
            st.plotly_chart(fig_mkt_bar, use_container_width=True)
            
        with col_m2:
            st.markdown(f"**{'Rata-rata Nilai Belanja (AOV) per Segmen' if lang_code == 'ID' else 'Average Order Value (AOV) by Segment'}**")
            lbl_mkt_aov = "Rata-rata AOV (IDR)" if lang_code == "ID" else "Average AOV (IDR)"
            fig_aov_bar = px.bar(
                df_market.sort_values(by="avg_aov", ascending=False),
                x="customer_category",
                y="avg_aov",
                color="avg_aov",
                text=df_market.sort_values(by="avg_aov", ascending=False)["avg_aov"].apply(lambda a: format_rupiah(a)),
                color_continuous_scale=["#C7D2FE", "#4F46E5"],
                labels={"customer_category": lbl_mkt_cat, "avg_aov": lbl_mkt_aov}
            )
            fig_aov_bar.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_aov_bar, height=360)
            st.plotly_chart(fig_aov_bar, use_container_width=True)
            
        # Clean Table Summary
        st.markdown(f"**{'Tabel Rangkuman Sebaran Nilai Pasar' if lang_code == 'ID' else 'Market Value Distribution Summary Table'}**")
        df_market_disp = df_market.copy()
        df_market_disp["Total Pendapatan"] = df_market_disp["total_revenue"].apply(format_rupiah)
        df_market_disp["Rata-rata Belanja (AOV)"] = df_market_disp["avg_aov"].apply(format_rupiah)
        acct_unit = "akun" if lang_code == "ID" else "accounts"
        df_market_disp["Jumlah Pelanggan"] = df_market_disp["customer_count"].apply(lambda c: f"{c:,} {acct_unit}")
        
        if lang_code == "EN":
            rename_mkt = {
                "customer_category": "Customer Segment",
                "Jumlah Pelanggan": "Buying Customer Base",
                "Total Pendapatan": "Total Net Revenue",
                "Rata-rata Belanja (AOV)": "Average Order Value"
            }
        else:
            rename_mkt = {
                "customer_category": "Segmen Pelanggan",
                "Jumlah Pelanggan": "Basis Pelanggan Pembeli",
                "Total Pendapatan": "Total Pendapatan Net",
                "Rata-rata Belanja (AOV)": "Rata-rata Nilai Pesanan"
            }
        st.dataframe(
            df_market_disp[["customer_category", "Jumlah Pelanggan", "Total Pendapatan", "Rata-rata Belanja (AOV)"]].rename(columns=rename_mkt).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

# -------------------------------------------------------------
# TAB 4: DISTRIBUSI SEGMEN RFM & KEDALAMAN RETENSI
# -------------------------------------------------------------
with tab4:
    if lang_code == "EN":
        render_section_info(
            title="Customer Loyalty & Purchase Recency Distribution (RFM)",
            subtitle="Analyzes how frequently and how recently customer accounts place print orders with Cetakia.",
            what_it_shows="Proportions of customer accounts across segments: Active & Loyal, At Risk of Churn, and Requiring Reactivation.",
            why_important="Detects shifts from active to dormant status in advance so commercial teams can intervene before accounts permanently defect.",
            simple_insight="<b>High Value Loyal</b> and <b>Active Customer</b> groups underpin stable cashflow, while <b>Low Engagement / Dormant</b> accounts require automated win-back voucher incentives."
        )
    else:
        render_section_info(
            title="Distribusi Status Loyalitas & Keaktifan Belanja (RFM)",
            subtitle="Analisis seberapa sering dan seberapa baru pelanggan melakukan pemesanan di Cetakia.",
            what_it_shows="Proporsi pelanggan dalam kelompok: Aktif & Loyal, Berisiko Churn, dan Perlu Reaktivasi.",
            why_important="Mendeteksi tren pergeseran pelanggan dari aktif menjadi pasif sehingga tim penjualan dapat segera melakukan intervensi sebelum pelanggan berhenti berbelanja.",
            simple_insight="Kelompok <b>High Value Loyal</b> dan <b>Active Customer</b> menyumbang stabilitas transaksi, sedangkan kelompok <b>Low Engagement / Dormant</b> membutuhkan insentif kupon win-back."
        )
    
    if not buyers_df.empty and "rfm_segment" in buyers_df.columns:
        df_rfm = buyers_df["rfm_segment"].value_counts().reset_index()
        lbl_rfm_col = "Segmen RFM" if lang_code == "ID" else "RFM Segment"
        lbl_rfm_cnt = "Jumlah Pelanggan" if lang_code == "ID" else "Customer Accounts"
        df_rfm.columns = [lbl_rfm_col, lbl_rfm_cnt]
        
        if lang_code == "EN":
            rfm_friendly_map = {
                "High Value Loyal": "Active & Loyal (High Value)",
                "Active Customer": "Regular Active Customer",
                "At Risk": "Declining Frequency (At Risk)",
                "Low Engagement": "Requires Reactivation (Dormant)"
            }
        else:
            rfm_friendly_map = {
                "High Value Loyal": "Aktif & Loyal (High Value)",
                "Active Customer": "Pelanggan Aktif Teratur",
                "At Risk": "Mulai Jarang Belanja (At Risk)",
                "Low Engagement": "Perlu Reaktivasi (Dormant)"
            }
        df_rfm["Label Ramah"] = df_rfm[lbl_rfm_col].map(rfm_friendly_map).fillna(df_rfm[lbl_rfm_col])
        tot_rfm = df_rfm[lbl_rfm_cnt].sum()
        df_rfm["Persentase"] = (df_rfm[lbl_rfm_cnt] / tot_rfm * 100).round(1)
        
        col_r1, col_r2 = st.columns([6, 4])
        with col_r1:
            rfm_colors = {
                "Aktif & Loyal (High Value)": "#10B981",
                "Pelanggan Aktif Teratur": "#3B82F6",
                "Mulai Jarang Belanja (At Risk)": "#F59E0B",
                "Perlu Reaktivasi (Dormant)": "#94A3B8",
                "Active & Loyal (High Value)": "#10B981",
                "Regular Active Customer": "#3B82F6",
                "Declining Frequency (At Risk)": "#F59E0B",
                "Requires Reactivation (Dormant)": "#94A3B8"
            }
            lbl_rfm_x = "Jumlah Akun Pelanggan" if lang_code == "ID" else "Customer Accounts"
            lbl_rfm_y = "Status Loyalitas" if lang_code == "ID" else "Loyalty Status"
            fig_rfm = px.bar(
                df_rfm.sort_values(by=lbl_rfm_cnt, ascending=True),
                x=lbl_rfm_cnt,
                y="Label Ramah",
                orientation="h",
                color="Label Ramah",
                text=df_rfm.sort_values(by=lbl_rfm_cnt, ascending=True)["Persentase"].apply(lambda p: f" {p:.1f}%"),
                color_discrete_map=rfm_colors,
                labels={lbl_rfm_cnt: lbl_rfm_x, "Label Ramah": lbl_rfm_y}
            )
            fig_rfm.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_rfm, height=340)
            st.plotly_chart(fig_rfm, use_container_width=True)
            
        with col_r2:
            if lang_code == "EN":
                card_r2 = """
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #10B981; font-size: 13px;">🌟 Active & Loyal Customers</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Accounts with consistent order frequency and basket value. Recognize with loyalty rewards and priority queueing.
                    </div>
                </div>
                
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #F59E0B; font-size: 13px;">⚠️ Declining Frequency (At-Risk)</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Exceeded normal buying cycle. CS team should proactively follow up to check upcoming printing projects.
                    </div>
                </div>
                
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #94A3B8; font-size: 13px;">📩 Requires Win-Back Reactivation</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Prolonged inactivity (> 90 days). Re-engage with automated email/WhatsApp promotional voucher campaigns.
                    </div>
                </div>
                """
            else:
                card_r2 = """
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #10B981; font-size: 13px;">🌟 Pelanggan Aktif & Loyal</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Pelanggan dengan frekuensi dan nilai belanja konsisten. Berikan apresiasi loyalty point dan penanganan prioritas.
                    </div>
                </div>
                
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #F59E0B; font-size: 13px;">⚠️ Pelanggan Mulai Jarang Belanja</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Melewati siklus belanja reguler. Perlu dihubungi tim CS untuk menanyakan kebutuhan cetak mendatang.
                    </div>
                </div>
                
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-weight: 700; color: #94A3B8; font-size: 13px;">📩 Pelanggan Perlu Reaktivasi</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Lama tidak bertransaksi. Reaktivasi menggunakan email newsletter atau promo voucher diskon cetak.
                    </div>
                </div>
                """
            st.markdown(card_r2, unsafe_allow_html=True)
