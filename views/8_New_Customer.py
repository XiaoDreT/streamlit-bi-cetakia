import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_new_customer_master
from utils.intelligence_engine import (
    compute_new_customer_kpis,
    compute_new_customer_trend,
    compute_new_customer_category_growth,
    compute_new_customer_division_matrix,
    compute_new_customer_growth_drivers,
    compute_new_customer_declining_segments,
    generate_new_customer_insights,
    compute_cetakia_realtime_acquisition_stats
)
from components.ui_components import (
    render_header,
    render_cetakia_hero_card,
    metric_card,
    render_business_insight_card,
    render_section_info,
    render_summary_strip,
    global_sidebar_filters,
    apply_plotly_theme
)

st.set_page_config(
    page_title="New Customer — Cetakia BI DSS",
    page_icon="🌱",
    layout="wide"
)

# -------------------------------------------------------------
# 1. LOAD MASTER DATASET (CACHED FROM new_customer_eda.csv)
# -------------------------------------------------------------
try:
    df_customer_master = load_new_customer_master()
except Exception as e:
    st.error(f"Data New Customer belum dapat dimuat: {e}. Silakan periksa file dataset new_customer_eda.csv.")
    st.stop()

# -------------------------------------------------------------
# 2. GLOBAL SIDEBAR FILTERS & LOCALE STATE
# -------------------------------------------------------------
# Uses standard global sidebar filters: "Pilih Cabang" and "Segmen Pelanggan"
filters = global_sidebar_filters(df_customers=df_customer_master)
t = filters["t"]
lang_code = filters.get("lang", "ID")
is_en = (lang_code == "EN")

selected_branch = filters.get("branch", "All Branches")
selected_segment = filters.get("segment", "All Segments")

# Normalized filter values
norm_division = None if selected_branch in ["All Branches", "Semua Cabang"] else selected_branch
norm_category = None if selected_segment in ["All Segments", "Semua Segmen"] else selected_segment

# Reference timestamp from latest data
active_cust = df_customer_master[df_customer_master["customer_deleted_at"].isna()].copy()
latest_data_dt = active_cust["created_at_jakarta"].max()
if pd.notna(latest_data_dt):
    dt_obj = pd.to_datetime(latest_data_dt)
    month_str = dt_obj.strftime("%b") if is_en else dt_obj.strftime("%b")
    latest_data_str = f"{dt_obj.strftime('%d')} {month_str} {dt_obj.strftime('%Y %H:%M')}"
else:
    latest_data_str = "26 Oct 2026 13:43" if is_en else "26 Okt 2026 13:43"

# -------------------------------------------------------------
# 3. PAGE HEADER & ACTIVE GLOBAL SCOPE STRIP
# -------------------------------------------------------------
sub_header = (
    "Monitor new customer acquisition growth by period, customer category, and division (integrated with Cetakia API)."
    if is_en
    else "Pantau pertumbuhan customer baru berdasarkan periode, kategori customer, dan divisi (terintegrasi dengan Cetakia API)."
)
render_header(
    title="New Customer",
    subtitle=sub_header,
    module_tag="CETAKIA ACQUISITION & BI DSS" if is_en else "AKUISISI CETAKIA & BI DSS"
)

# Active Global Scope Strip (Informs user that sidebar filters control the scope)
lbl_scope_branch = "Branch / Division" if is_en else "Cabang / Divisi"
lbl_scope_segment = "Customer Segment" if is_en else "Segmen Pelanggan"
lbl_scope_hint = "Change anytime via sidebar 'Select Branch'" if is_en else "Ubah kapan saja via sidebar 'Pilih Cabang'"
lbl_source = "Data Source" if is_en else "Sumber Data"

display_branch_name = "All Branches" if (norm_division is None and is_en) else ("Semua Cabang" if norm_division is None else norm_division)
display_segment_name = "All Segments" if (norm_category is None and is_en) else ("Semua Segmen" if norm_category is None else norm_category)

st.markdown(f"""
<div style="background-color: var(--secondary-background-color, rgba(128,128,128,0.06)); 
            border: 1px solid rgba(156,163,175,0.22); 
            border-radius: 10px; padding: 12px 18px; margin-bottom: 20px;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 13.5px;">
        <span>🏢 <b>{lbl_scope_branch}:</b> <span style="color: #38BDF8; font-weight: 700;">{display_branch_name}</span></span>
        <span style="opacity: 0.3;">|</span>
        <span>👥 <b>{lbl_scope_segment}:</b> <span style="color: #38BDF8; font-weight: 700;">{display_segment_name}</span></span>
        <span style="opacity: 0.3;">|</span>
        <span style="color: #94A3B8; font-size: 12px;"><i>({lbl_scope_hint})</i></span>
    </div>
    <div style="color: #10B981; font-size: 12px; font-weight: 600;">
        ⚡ {lbl_source}: Cetakia Master Dataset ({latest_data_str} WIB)
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. CETAKIA REALTIME HERO STAT CARDS (SISTEM CETAKIA)
# -------------------------------------------------------------
# Compute Cetakia Realtime API Stats (automatically filtered by global branch & segment)
cetakia_stats = compute_cetakia_realtime_acquisition_stats(
    df=df_customer_master,
    division=norm_division,
    category=norm_category
)

title_sec_hero = "⚡ Cetakia New Customer Acquisition Stats (Cetakia System)" if is_en else "⚡ Statistik Akuisisi New Customer (Sistem Cetakia)"
caption_sec_hero = (
    "Real-time Cetakia customer acquisition cards computed in accordance with Cetakia-API `getNewCustomersStats` endpoint."
    if is_en
    else "Visualisasi kartu akuisisi customer Cetakia yang dihitung real-time sesuai endpoint `getNewCustomersStats` dari Cetakia-API."
)
st.markdown(f"### {title_sec_hero}")
st.caption(caption_sec_hero)

col_hero1, col_hero2, col_hero3, col_hero4 = st.columns(4)

unit_label_str = "new accounts" if is_en else "akun baru"
last_30_prefix_str = "Last 30 Days:" if is_en else "30 Hari Terakhir:"
total_prefix_str = "Total:"

with col_hero1:
    render_cetakia_hero_card(
        title="NEW CUSTOMERS (3 DAYS)",
        new_accounts=cetakia_stats["last_3_days"],
        growth_pct=cetakia_stats["growth_3"],
        prev_accounts=cetakia_stats["previous_3_days"],
        prev_label="prev 3 days" if is_en else "3 hari lalu",
        last_30_days=cetakia_stats["last_30_days"],
        total_customers=cetakia_stats["total_customers"],
        highlight_color="#10B981",
        unit_label=unit_label_str,
        last_30_prefix=last_30_prefix_str,
        total_prefix=total_prefix_str
    )

with col_hero2:
    render_cetakia_hero_card(
        title="NEW CUSTOMERS (7 DAYS)",
        new_accounts=cetakia_stats["last_7_days"],
        growth_pct=cetakia_stats["growth_7"],
        prev_accounts=cetakia_stats["previous_7_days"],
        prev_label="prev 7 days" if is_en else "7 hari lalu",
        last_30_days=cetakia_stats["last_30_days"],
        total_customers=cetakia_stats["total_customers"],
        highlight_color="#3B82F6",
        unit_label=unit_label_str,
        last_30_prefix=last_30_prefix_str,
        total_prefix=total_prefix_str
    )

with col_hero3:
    render_cetakia_hero_card(
        title="NEW CUSTOMERS (30 DAYS)",
        new_accounts=cetakia_stats["last_30_days"],
        growth_pct=cetakia_stats["growth_30"],
        prev_accounts=cetakia_stats["previous_30_days"],
        prev_label="prev 30 days" if is_en else "30 hari lalu",
        last_30_days=cetakia_stats["last_30_days"],
        total_customers=cetakia_stats["total_customers"],
        highlight_color="#F59E0B",
        unit_label=unit_label_str,
        last_30_prefix=last_30_prefix_str,
        total_prefix=total_prefix_str
    )

with col_hero4:
    top_cat = cetakia_stats["top_category"]
    top_cnt = cetakia_stats["top_category_count"]
    top_pct = cetakia_stats["top_category_pct"]
    top_div = cetakia_stats["top_division"]
    
    top_cat_title = "TOP CATEGORY (30 DAYS)" if is_en else "TOP KATEGORI (30 HARI)"
    top_cat_sub = f"+{top_cnt:,} accounts ({top_pct:.1f}% share)" if is_en else f"+{top_cnt:,} akun ({top_pct:.1f}% pangsa)"
    top_div_lbl = "Top Branch:" if is_en else "Cabang Terbesar:"
    
    card_top_html = f"""<div class="cetakia-stat-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <span style="color: #94A3B8; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;">
        {top_cat_title}
    </span>
    <div style="background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 8px; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; color: #3B82F6;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
            <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
    </div>
</div>
<div style="display: flex; align-items: baseline; margin-bottom: 4px;">
    <span style="color: #FFFFFF; font-size: 24px; font-weight: 800; font-family: Inter, sans-serif; letter-spacing: -0.5px;">
        {top_cat}
    </span>
</div>
<div style="font-size: 13.5px; font-weight: 600; display: flex; align-items: center; gap: 4px; margin-bottom: 14px;">
    <span style="color: #10B981; font-weight: 700;">
        {top_cat_sub}
    </span>
</div>
<div style="border-top: 1px solid rgba(148, 163, 184, 0.15); margin: 14px 0 10px 0;"></div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
    <div style="color: #94A3B8; display: flex; align-items: center; gap: 6px;">
        <span>{top_div_lbl} <b style="color: #F1F5F9; font-weight: 700;">{top_div}</b></span>
    </div>
    <div style="color: #10B981; font-weight: 700;">
        LEADER
    </div>
</div>
</div>"""
    st.markdown(card_top_html, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# 5. USER-FRIENDLY PERIOD RANGE SELECTION (CETAKIA STYLE)
# -------------------------------------------------------------
# Reference dates based on dataset
max_valid_date = df_customer_master["new_customer_valid_date"].max()
min_valid_date = df_customer_master["new_customer_valid_date"].min()

title_sec_period = "📊 Dynamic Period Analysis (BI Decision Support)" if is_en else "📊 Analisis Periode Dinamis (BI Decision Support)"
caption_sec_period = (
    "Select an analysis period to inspect acquisition velocity, balanced baseline comparisons, category spread, and branch contributions."
    if is_en
    else "Pilih rentang tanggal untuk menganalisis laju pertumbuhan, perbandingan periode setara, sebaran kategori, dan kontribusi cabang."
)
st.markdown(f"### {title_sec_period}")
st.caption(caption_sec_period)

# Period Range Container matching Image 4 from Cetakia system
period_pills_options = (
    ["Today", "This Week", "This Month", "Last Month", "This Year", "Last Year", "Custom"]
    if is_en
    else ["Hari Ini", "Minggu Ini", "Bulan Ini", "Bulan Lalu", "Tahun Ini", "Tahun Lalu", "Kustom"]
)
default_pill = "This Month" if is_en else "Bulan Ini"

st.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 15px; font-weight: 700; color: #38BDF8;">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
    </svg>
    <span>{"Period Range" if is_en else "Rentang Periode"}</span>
</div>
""", unsafe_allow_html=True)

selected_pill = st.pills(
    label="Period Range Pills",
    options=period_pills_options,
    default=default_pill,
    label_visibility="collapsed",
    key="nc_period_range_pills"
)
if not selected_pill:
    selected_pill = default_pill

# Compute start_date and end_date based on selected pill
is_custom = selected_pill in ["Custom", "Kustom"]

if selected_pill in ["Today", "Hari Ini"]:
    bi_start = max_valid_date
    bi_end = max_valid_date
elif selected_pill in ["This Week", "Minggu Ini"]:
    bi_start = max_valid_date - datetime.timedelta(days=6)
    bi_end = max_valid_date
elif selected_pill in ["This Month", "Bulan Ini"]:
    bi_start = datetime.date(2026, 10, 1)
    bi_end = max_valid_date
elif selected_pill in ["Last Month", "Bulan Lalu"]:
    bi_start = datetime.date(2026, 9, 1)
    bi_end = datetime.date(2026, 9, 30)
elif selected_pill in ["This Year", "Tahun Ini"]:
    bi_start = datetime.date(2026, 1, 1)
    bi_end = max_valid_date
elif selected_pill in ["Last Year", "Tahun Lalu"]:
    bi_start = datetime.date(2025, 1, 1)
    bi_end = datetime.date(2025, 12, 31)
else:
    bi_start = datetime.date(2026, 9, 29)
    bi_end = max_valid_date

# If Custom is chosen, display clean date input
if is_custom:
    custom_col, _ = st.columns([1.5, 2.5])
    with custom_col:
        custom_range = st.date_input(
            "Pilih Rentang Tanggal Mulai & Akhir:" if not is_en else "Select Custom Start & End Date:",
            value=(bi_start, bi_end),
            min_value=datetime.date(2025, 1, 1),
            max_value=datetime.date(2026, 12, 31),
            key="nc_custom_date_input"
        )
        if isinstance(custom_range, (tuple, list)) and len(custom_range) == 2:
            bi_start, bi_end = custom_range

# -------------------------------------------------------------
# 6. COMPUTE PERIOD KPIS & BALANCED COMPARISON
# -------------------------------------------------------------
bi_kpis = compute_new_customer_kpis(
    df=df_customer_master,
    start_date=bi_start,
    end_date=bi_end,
    division=norm_division,
    category=norm_category
)

df_curr = bi_kpis["df_curr"]
df_prev = bi_kpis["df_prev"]
period_days = bi_kpis["period_days"]
prev_start = bi_kpis["prev_start_date"]
prev_end = bi_kpis["prev_end_date"]

# Period Context Banner & Partial Day indicator
is_partial = (bi_end >= datetime.date.today())
now_wib = datetime.datetime.now().strftime("%H:%M")

c_stat1, c_stat2 = st.columns([3, 2])
with c_stat1:
    lbl_sel_period = "Selected Period (Valid Date +2 Days):" if is_en else "Periode Terpilih (Tanggal Sah Valid +2 Hari):"
    lbl_comp_period = "Balanced Comparison Period:" if is_en else "Periode Pembanding Seimbang:"
    lbl_days = "days" if is_en else "hari"
    lbl_equiv = "days equivalent" if is_en else "hari setara"
    
    st.info(
        f"📅 **{lbl_sel_period}** `{bi_start.strftime('%d %b %Y')}` — `{bi_end.strftime('%d %b %Y')}` (**{period_days} {lbl_days}**)  \n"
        f"⚖️ **{lbl_comp_period}** `{prev_start.strftime('%d %b %Y')}` — `{prev_end.strftime('%d %b %Y')}` (**{period_days} {lbl_equiv}**)"
    )

with c_stat2:
    if is_partial:
        warn_msg = f"⚠️ **Includes Partial Day:** Period includes today which is still in progress (data up to {now_wib} WIB)." if is_en else f"⚠️ **Mencakup Hari Ini:** Periode mencakup hari ini yang masih berjalan (data s/d pukul {now_wib} WIB)."
        st.warning(warn_msg)
    else:
        succ_msg = "✅ **Completed Period:** The selected period represents 100% completed operational days." if is_en else "✅ **Periode Selesai:** Periode yang dipilih merupakan hari operasional yang telah selesai 100%."
        st.success(succ_msg)

# 5 Executive KPI Cards
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    metric_card(
        title="NEW CUSTOMERS",
        value=f"{bi_kpis['curr_count']:,}",
        delta=None,
        subtext="New accounts in period" if is_en else "Customer di periode terpilih"
    )
with k2:
    delta_lbl = "vs Previous Period" if is_en else "vs Periode Lalu"
    metric_card(
        title="GROWTH %",
        value=bi_kpis["growth_display"],
        delta=delta_lbl if bi_kpis["prev_count"] > 0 else ("New Base" if is_en else "Basis Baru"),
        delta_color=bi_kpis["delta_color"],
        subtext=f"Status: {bi_kpis['status']}"
    )
with k3:
    metric_card(
        title="PREVIOUS PERIOD",
        value=f"{bi_kpis['prev_count']:,}",
        delta=None,
        subtext=f"{period_days} {'days comparison' if is_en else 'hari pembanding'}"
    )
with k4:
    net_val = bi_kpis["net_growth"]
    unit_cust = "customers" if is_en else "customer"
    metric_card(
        title="NET CUSTOMER GROWTH",
        value=f"{net_val:+d} {unit_cust}",
        delta=None,
        subtext="Real volume change" if is_en else "Pertambahan volume riil"
    )
with k5:
    top_c_name = bi_kpis["top_category"]
    top_c_pct = bi_kpis["top_category_pct"]
    contrib_lbl = "contribution" if is_en else "kontribusi"
    metric_card(
        title="TOP CATEGORY",
        value=top_c_name,
        delta=f"{top_c_pct:.1f}% {contrib_lbl}" if bi_kpis["curr_count"] > 0 else None,
        delta_color="positive",
        subtext="Largest contributor" if is_en else "Kontributor terbesar"
    )

st.markdown("---")

# -------------------------------------------------------------
# 7. SECTION 1: TREND LINE CHART (DYNAMIC GRANULARITY)
# -------------------------------------------------------------
trend_df, granularity = compute_new_customer_trend(df_curr, df_prev, bi_start, bi_end)

if is_en:
    sec1_title = f"New Customer Acquisition Trend ({granularity} Aggregation)"
    sec1_sub = "Monitoring new customer intake velocity over time."
    sec1_what = f"New customer volume per {granularity.lower()} across the selected active period."
    sec1_why = "Identifies seasonal patterns, promotional spikes, or operational weekend dips."
    sec1_insight = "A steady upward trajectory indicates healthy customer acquisition pace."
else:
    sec1_title = f"Tren Akuisisi New Customer (Agregasi {granularity})"
    sec1_sub = "Memantau perkembangan laju penambahan customer baru dari waktu ke waktu."
    sec1_what = f"Volume New Customer per {granularity.lower()} pada periode aktif yang dipilih."
    sec1_why = "Mengidentifikasi pola musiman (peak season), lonjakan promo, atau penurunan di hari libur."
    sec1_insight = "Pola yang menanjak konsisten menandakan laju perolehan customer yang sehat."

render_section_info(
    title=sec1_title,
    subtitle=sec1_sub,
    what_it_shows=sec1_what,
    why_important=sec1_why,
    simple_insight=sec1_insight,
    icon="📈",
    lang_code=lang_code
)

if not trend_df.empty:
    fig_trend = px.line(
        trend_df,
        x="date_label",
        y="new_customers",
        markers=True,
        labels={
            "date_label": "Date" if is_en else "Tanggal",
            "new_customers": "New Customers" if is_en else "Customer Baru"
        }
    )
    fig_trend.update_traces(
        line=dict(color="#10B981", width=3),
        marker=dict(size=7, color="#059669", line=dict(width=1.5, color="#FFFFFF")),
        hovertemplate="<b>%{x}</b><br>New Customers: <b>%{y:,} " + ("accounts" if is_en else "akun") + "</b><extra></extra>"
    )
    apply_plotly_theme(fig_trend, height=320)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.caption("No trend data available for this filter." if is_en else "Tidak ada data tren untuk filter periode ini.")

st.markdown("---")

# -------------------------------------------------------------
# 8. SECTION 2: CATEGORY LEADERBOARD & CONTRIBUTION (DONUT)
# -------------------------------------------------------------
col_bar, col_donut = st.columns([1.3, 1.0])
cat_growth_df = compute_new_customer_category_growth(df_curr, df_prev)

with col_bar:
    if is_en:
        sec2_bar_title = "New Customers by Customer Category"
        sec2_bar_sub = "Which categories generate the highest number of new customers?"
        sec2_bar_what = "Ranked new customer volume per category (sorted largest to smallest)."
        sec2_bar_why = "Guides management in allocating sales channels and segment marketing."
        sec2_bar_insight = "The top category serves as the core growth engine."
    else:
        sec2_bar_title = "Customer Baru per Kategori Pelanggan"
        sec2_bar_sub = "Kategori mana yang paling banyak menyumbang customer baru?"
        sec2_bar_what = "Peringkat jumlah customer baru per kategori (diurutkan terbesar ke terkecil)."
        sec2_bar_why = "Membantu manajemen menentukan prioritas sales channel dan promosi segmen."
        sec2_bar_insight = "Kategori di puncak merupakan lokomotif penarik pertumbuhan customer."

    render_section_info(
        title=sec2_bar_title,
        subtitle=sec2_bar_sub,
        what_it_shows=sec2_bar_what,
        why_important=sec2_bar_why,
        simple_insight=sec2_bar_insight,
        icon="📊",
        lang_code=lang_code
    )
    
    if not cat_growth_df.empty and cat_growth_df["current"].sum() > 0:
        bar_df = cat_growth_df.sort_values(by="current", ascending=True)
        fig_cat = px.bar(
            bar_df,
            x="current",
            y="category_name",
            orientation="h",
            text="current",
            labels={
                "current": "New Customers" if is_en else "Jumlah Customer Baru",
                "category_name": "Customer Category" if is_en else "Kategori Customer"
            },
            color="current",
            color_continuous_scale=["#6EE7B7", "#059669"]
        )
        fig_cat.update_traces(
            textposition="outside",
            texttemplate="<b>%{text:,}</b>",
            hovertemplate="<b>%{y}</b><br>New Customers: <b>%{x:,}</b><extra></extra>"
        )
        fig_cat.update_layout(coloraxis_showscale=False)
        apply_plotly_theme(fig_cat, height=330)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.caption("No customer data per category." if is_en else "Belum ada data customer per kategori.")

with col_donut:
    if is_en:
        sec2_pie_title = "Contribution Share & Concentration Risk"
        sec2_pie_sub = "How heavily does acquisition rely on specific categories?"
        sec2_pie_what = "Percentage share of each customer category relative to total intake."
        sec2_pie_why = "Detects risk of over-reliance on a single retail customer segment."
        sec2_pie_insight = "If Top 2 Categories exceed 70%, B2B and commercial diversification is recommended."
    else:
        sec2_pie_title = "Distribusi & Konsentrasi Kontribusi"
        sec2_pie_sub = "Seberapa besar ketergantungan terhadap kategori tertentu?"
        sec2_pie_what = "Pangsa persentase kontribusi masing-masing kategori terhadap total New Customer."
        sec2_pie_why = "Mendeteksi risiko konsentrasi berlebih pada segmen ritel perorangan tunggal."
        sec2_pie_insight = "Jika Top 2 Kategori > 70%, diperlukan upaya diversifikasi ke kategori B2B/Industri."

    render_section_info(
        title=sec2_pie_title,
        subtitle=sec2_pie_sub,
        what_it_shows=sec2_pie_what,
        why_important=sec2_pie_why,
        simple_insight=sec2_pie_insight,
        icon="🍩",
        lang_code=lang_code
    )
    
    if not cat_growth_df.empty and cat_growth_df["current"].sum() > 0:
        valid_cats = cat_growth_df[cat_growth_df["current"] > 0]
        fig_pie = px.pie(
            valid_cats,
            names="category_name",
            values="current",
            hole=0.45,
            color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6", "#EC4899", "#64748B", "#14B8A6"]
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Volume: %{value:,} accounts (%{percent})<extra></extra>" if is_en else "<b>%{label}</b><br>Volume: %{value:,} akun (%{percent})<extra></extra>"
        )
        apply_plotly_theme(fig_pie, height=330)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        top2_share = cat_growth_df["contribution_pct"].head(2).sum()
        if top2_share >= 70.0:
            top_names = " & ".join(cat_growth_df["category_name"].head(2).tolist())
            warn_conc = (
                f"⚠️ **Concentration Alert ({top2_share:.1f}%):** Acquisition portfolio relies heavily on **{top_names}**."
                if is_en
                else f"⚠️ **Peringatan Konsentrasi ({top2_share:.1f}%):** Portofolio akuisisi sangat bergantung pada **{top_names}**."
            )
            st.warning(warn_conc)
    else:
        st.caption("No contribution data." if is_en else "Belum ada data kontribusi.")

st.markdown("---")

# -------------------------------------------------------------
# 9. SECTION 3: GROWTH BY CUSTOMER CATEGORY (TABLE & STATUS)
# -------------------------------------------------------------
if not cat_growth_df.empty:
    top_gainers = cat_growth_df[cat_growth_df["net_change"] > 0].sort_values(by="net_change", ascending=False)
    top_losers = cat_growth_df[cat_growth_df["net_change"] < 0].sort_values(by="net_change", ascending=True)

    g_name = top_gainers.iloc[0]["category_name"] if not top_gainers.empty else None
    g_net = int(top_gainers.iloc[0]["net_change"]) if not top_gainers.empty else 0
    g_pct = top_gainers.iloc[0]["growth_display_en" if is_en else "growth_display_id"] if not top_gainers.empty else "0.0%"

    l_name = top_losers.iloc[0]["category_name"] if not top_losers.empty else None
    l_net = int(top_losers.iloc[0]["net_change"]) if not top_losers.empty else 0
    l_pct = top_losers.iloc[0]["growth_display_en" if is_en else "growth_display_id"] if not top_losers.empty else "0.0%"

    top_share_cat = cat_growth_df.sort_values(by="current", ascending=False).iloc[0]

    if is_en:
        sec3_title = "Category Growth Dynamics (Growth by Category)"
        sec3_sub = "Direct evaluation of new customer intake between periods to understand business momentum."
        sec3_what = "Real changes in customer count (+/- accounts), growth rate, portfolio share, and business status."
        sec3_why = "Ensures management focuses on real customer gains/losses rather than being misled by percentages on small samples."
        if g_name and l_name:
            sec3_insight = f"🟢 <b>Top Driver:</b> <b>{g_name}</b> added the most real accounts (<b>+{g_net:,} customers</b> / {g_pct}).<br>⚠️ <b>Key Concern:</b> <b>{l_name}</b> lost <b>{l_net:,} customers</b> ({l_pct}), representing the largest volume contraction."
        elif g_name:
            sec3_insight = f"🟢 <b>Positive Momentum:</b> All categories expanded, led by <b>{g_name}</b> (+{g_net:,} customers)."
        elif l_name:
            sec3_insight = f"⚠️ <b>Contraction Warning:</b> All categories saw declining intake, with <b>{l_name}</b> dropping {l_net:,} customers."
        else:
            sec3_insight = "Customer intake across all categories remained stable compared to the baseline period."
    else:
        sec3_title = "Dinamika Pertumbuhan per Kategori Pelanggan"
        sec3_sub = "Evaluasi perbandingan perolehan customer baru periode ini vs periode lalu secara transparan dan mudah dipahami."
        sec3_what = "Perubahan riil jumlah customer baru (+/- orang), persentase pertumbuhan, pangsa pasar, dan evaluasi bisnis di tiap kategori."
        sec3_why = "Memastikan manajemen tidak terkecoh oleh persentase semata; mengetahui pasti kategori mana yang menopang pertumbuhan vs mana yang kehilangan pelanggan terbanyak."
        if g_name and l_name:
            sec3_insight = f"🟢 <b>Pendorong Utama:</b> Kategori <b>{g_name}</b> melonjak paling tinggi (<b>+{g_net:,} customer</b> / {g_pct}).<br>⚠️ <b>Perhatian Khusus:</b> Kategori <b>{l_name}</b> berkurang <b>{l_net:,} customer</b> ({l_pct}) — merupakan kehilangan volume terbesar yang perlu dievaluasi."
        elif g_name:
            sec3_insight = f"🟢 <b>Pertumbuhan Menyeluruh:</b> Seluruh kategori mencatatkan penambahan customer baru, dipimpin oleh <b>{g_name}</b> (+{g_net:,} customer)."
        elif l_name:
            sec3_insight = f"⚠️ <b>Peringatan Penurunan:</b> Seluruh kategori mengalami penurunan, kontraksi terbesar dialami oleh <b>{l_name}</b> ({l_net:,} customer)."
        else:
            sec3_insight = "Seluruh kategori mempertahankan volume perolehan customer baru yang relatif stabil."

    render_section_info(
        title=sec3_title,
        subtitle=sec3_sub,
        what_it_shows=sec3_what,
        why_important=sec3_why,
        simple_insight=sec3_insight,
        icon="⚖️",
        lang_code=lang_code
    )

    # 1. Executive Summary Strip
    n_growing = len(cat_growth_df[cat_growth_df["net_change"] > 0])
    n_declining = len(cat_growth_df[cat_growth_df["net_change"] < 0])
    n_stable = len(cat_growth_df[cat_growth_df["net_change"] == 0])

    strip_items = [
        {
            "label": "Pendorong Pertumbuhan Terbesar" if not is_en else "Top Growth Driver",
            "value": f"{g_name} (+{g_net:,})" if g_name else "-",
            "desc": f"Laju {g_pct} vs periode lalu" if g_name else ("Tidak ada kenaikan positif" if not is_en else "No positive gain"),
            "color": "#10B981"
        },
        {
            "label": "Penurunan Volume Terbanyak" if not is_en else "Largest Real Drop",
            "value": f"{l_name} ({l_net:,})" if l_name else "-",
            "desc": f"Laju {l_pct} vs periode lalu" if l_name else ("Seluruh kategori stabil/tumbuh" if not is_en else "All categories stable/up"),
            "color": "#EF4444"
        },
        {
            "label": "Kategori Paling Dominan" if not is_en else "Dominant Category",
            "value": f"{top_share_cat['category_name']} ({top_share_cat['current']:,})",
            "desc": f"Menyumbang {top_share_cat['contribution_pct']:.1f}% total customer baru" if not is_en else f"Accounts for {top_share_cat['contribution_pct']:.1f}% of new intake",
            "color": "#3B82F6"
        },
        {
            "label": "Dinamika Portofolio" if not is_en else "Portfolio Movement",
            "value": f"{n_growing} Tumbuh · {n_declining} Turun" if not is_en else f"{n_growing} Up · {n_declining} Down",
            "desc": f"{n_stable} stabil dari {len(cat_growth_df)} kategori" if not is_en else f"{n_stable} stable out of {len(cat_growth_df)} categories",
            "color": "#8B5CF6"
        }
    ]
    render_summary_strip(strip_items)

    # 2. Visual Diverging Bar Chart (Real Customer Volume Changes)
    chart_df = cat_growth_df.sort_values(by="net_change", ascending=True).copy()
    bar_colors = ["#10B981" if x > 0 else ("#EF4444" if x < 0 else "#9CA3AF") for x in chart_df["net_change"]]
    bar_texts = [
        f"+{x:,} customer ({p})" if x > 0 else (f"{x:,} customer ({p})" if x < 0 else f"0 customer ({p})")
        for x, p in zip(chart_df["net_change"], chart_df["growth_display_en" if is_en else "growth_display_id"])
    ]

    fig_div = go.Figure(go.Bar(
        x=chart_df["net_change"],
        y=chart_df["category_name"],
        orientation="h",
        marker_color=bar_colors,
        text=bar_texts,
        textposition="outside",
        cliponaxis=False,
        customdata=chart_df[[
            "previous",
            "current",
            "growth_display_en" if is_en else "growth_display_id",
            "status_en" if is_en else "status_id",
            "contribution_pct",
            "desc_en" if is_en else "desc_id"
        ]].values,
        hovertemplate=(
            "<b>Kategori: %{y}</b><br>"
            "Perubahan Bersih: <b>%{x:+d} Customer Baru</b><br>"
            "Periode Lalu: <b>%{customdata[0]:,}</b> → Periode Ini: <b>%{customdata[1]:,}</b><br>"
            "Laju Pertumbuhan: <b>%{customdata[2]}</b><br>"
            "Status Bisnis: <b>%{customdata[3]}</b><br>"
            "Pangsa Portofolio: <b>%{customdata[4]:.1f}%</b><br>"
            "Makna: <i>%{customdata[5]}</i><extra></extra>"
        ) if not is_en else (
            "<b>Category: %{y}</b><br>"
            "Net Change: <b>%{x:+d} New Customers</b><br>"
            "Previous: <b>%{customdata[0]:,}</b> → Current: <b>%{customdata[1]:,}</b><br>"
            "Growth Rate: <b>%{customdata[2]}</b><br>"
            "Business Status: <b>%{customdata[3]}</b><br>"
            "Portfolio Share: <b>%{customdata[4]:.1f}%</b><br>"
            "Meaning: <i>%{customdata[5]}</i><extra></extra>"
        )
    ))

    fig_div.add_vline(x=0, line_dash="solid", line_color="rgba(156, 163, 175, 0.4)", line_width=1.5)
    fig_div.update_layout(
        xaxis=dict(
            title="Penambahan / Pengurangan Riil (Customer Baru)" if not is_en else "Net Customer Intake (+/- Accounts)",
            zeroline=False,
            showgrid=True,
            gridcolor="rgba(156, 163, 175, 0.15)"
        ),
        yaxis=dict(
            title=None,
            showgrid=False
        ),
        margin=dict(l=10, r=40, t=10, b=10)
    )
    apply_plotly_theme(fig_div, height=max(320, len(chart_df) * 44))

    st.markdown(
        "##### 📊 Visual Perubahan Riil Customer Baru (+/- Orang)"
        if not is_en
        else "##### 📊 Visual Real Customer Volume Change (+/- Accounts)"
    )
    st.caption(
        "Batang **hijau ke kanan** menandakan kategori bertumbuh. Batang **merah ke kiri** menandakan kategori yang mengalami penurunan pelanggan."
        if not is_en
        else "Green bars extending right indicate customer gains. Red bars extending left indicate customer losses."
    )
    st.plotly_chart(fig_div, use_container_width=True)

    # 3. Plain Language Business Interpretation Guide
    guide_point1 = (
        f"Kenaikan pada <b>{g_name} (+{g_net:,} customer)</b> memberikan dampak pertumbuhan operasional yang sangat riil. Sebaliknya, penurunan pada <b>{l_name} ({l_net:,} customer)</b> adalah kehilangan volume terbesar periode ini meskipun persentasenya terlihat moderat ({l_pct}), karena {l_name} mencakup {top_share_cat['contribution_pct']:.1f}% basis pelanggan Cetakia."
        if (g_name and l_name)
        else ("Fokuskan pemantauan pada perubahan angka riil (+/- customer) untuk mengukur dampak langsung ke kapasitas operasional." if not is_en else "Focus on real customer volume (+/- accounts) to evaluate operational capacity impact.")
    )

    low_base_list = cat_growth_df[cat_growth_df["is_low_base"]]["category_name"].tolist()
    low_base_str = ", ".join(low_base_list) if low_base_list else ("DIVISI" if not is_en else "DIVISION")
    guide_point2 = (
        f"Kategori seperti <b>{low_base_str}</b> memiliki jumlah dasar sangat sedikit (< 5 customer). Penurunan atau kenaikan 1-2 orang sudah menghasilkan persentase ekstrim (-100% atau +66.7%). Ini adalah <i>fluktuasi wajar basis kecil</i> dan bukan krisis operasional."
        if not is_en
        else f"Categories such as <b>{low_base_str}</b> have very small baselines (< 5 accounts). Shifts of 1-2 people generate extreme percentages; these are normal baseline variations rather than operational issues."
    )

    guide_point3 = (
        f"Prioritaskan evaluasi saluran promosi & follow-up pada <b>{l_name if l_name else 'kategori yang menurun'}</b> dan kategori penunjang (seperti <b>UMKM</b>) untuk mencegah berlanjutnya penurunan volume, sembari mereplikasi pola sukses <b>{g_name if g_name else 'kategori unggulan'}</b> ke cabang-cabang lainnya."
        if not is_en
        else f"Prioritize marketing audits on <b>{l_name if l_name else 'declining segments'}</b> and <b>SME</b> to prevent further volume leakage, while standardizing sales playbooks from <b>{g_name if g_name else 'lead categories'}</b> across all branches."
    )

    st.markdown(f"""
<div style="background-color: var(--secondary-background-color, rgba(128,128,128,0.06)); border: 1px solid rgba(156,163,175,0.25); border-left: 4px solid #10B981; border-radius: 8px; padding: 14px 18px; margin-top: 4px; margin-bottom: 22px;">
    <div style="font-weight: 700; font-size: 14.5px; color: #10B981; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
        💡 <span>{'Panduan Membaca Angka untuk Manajemen & Orang Awam' if not is_en else 'Executive & Layman Interpretation Guide'}</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; font-size: 13px; line-height: 1.55;">
        <div>
            <div style="font-weight: 700; color: #3B82F6; margin-bottom: 4px;">{'1. Jangan Terkecoh Persentase Semata' if not is_en else '1. Real Volume Outweighs Percentages'}</div>
            <span>{guide_point1}</span>
        </div>
        <div>
            <div style="font-weight: 700; color: #F59E0B; margin-bottom: 4px;">{'2. Memahami Fluktuasi Basis Kecil (<5)' if not is_en else '2. Understanding Low Base Fluctuations'}</div>
            <span>{guide_point2}</span>
        </div>
        <div>
            <div style="font-weight: 700; color: #10B981; margin-bottom: 4px;">{'3. Prioritas Tindakan Nyata' if not is_en else '3. Priority Action Areas'}</div>
            <span>{guide_point3}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # 4. Detailed Data Table with Humanized Columns & Status
    st.markdown(
        "##### 📋 Rincian Lengkap & Status Kinerja Tiap Kategori"
        if not is_en
        else "##### 📋 Detailed Breakdown & Performance Status per Category"
    )

    c_sort, _ = st.columns([3, 2])
    with c_sort:
        sort_opts = (
            [
                "Dampak Perubahan Riil (Paling Berdampak)",
                "Volume Saat Ini (Terbanyak)",
                "Pertumbuhan Tertinggi (%)",
                "Penurunan Terbesar (Net Drop)"
            ]
            if not is_en
            else [
                "Impactful Real Change (Absolute Net)",
                "Current Volume (Highest)",
                "Highest Growth (%)",
                "Largest Drop (Net Contraction)"
            ]
        )
        sort_opt = st.radio(
            "Urutkan Tabel Berdasarkan:" if not is_en else "Sort Table By:",
            options=sort_opts,
            horizontal=True,
            key="nc_tbl_sort_radio"
        )

    tbl_data = cat_growth_df.copy()
    if "Dampak Perubahan Riil" in sort_opt or "Impactful Real Change" in sort_opt:
        tbl_data["_abs_net"] = tbl_data["net_change"].abs()
        tbl_data = tbl_data.sort_values(by=["_abs_net", "current"], ascending=[False, False])
    elif "Pertumbuhan Tertinggi" in sort_opt or "Highest Growth" in sort_opt:
        tbl_data["_sort_key"] = tbl_data["growth_pct"].fillna(-999)
        tbl_data = tbl_data.sort_values(by="_sort_key", ascending=False)
    elif "Penurunan Terbesar" in sort_opt or "Largest Drop" in sort_opt:
        tbl_data = tbl_data.sort_values(by="net_change", ascending=True)
    else: # Volume Saat Ini
        tbl_data = tbl_data.sort_values(by="current", ascending=False)

    col_names = {
        "Kategori": "Category" if is_en else "Kategori Pelanggan",
        "Lalu": "Previous Period" if is_en else "Periode Lalu",
        "Kini": "Current Period" if is_en else "Periode Ini",
        "Perubahan": "Net Change" if is_en else "Perubahan Riil (Net)",
        "Laju Growth": "Growth %" if is_en else "Laju Pertumbuhan (%)",
        "Porsi": "Share %" if is_en else "Pangsa Kontribusi",
        "Status": "Business Status" if is_en else "Status Bisnis",
        "Makna": "Business Takeaway" if is_en else "Makna Bisnis & Rekomendasi"
    }

    formatted_table = pd.DataFrame({
        col_names["Kategori"]: tbl_data["category_name"],
        col_names["Lalu"]: tbl_data["previous"].apply(lambda v: f"{v:,} customer" if not is_en else f"{v:,} accounts"),
        col_names["Kini"]: tbl_data["current"].apply(lambda v: f"{v:,} customer" if not is_en else f"{v:,} accounts"),
        col_names["Perubahan"]: tbl_data["net_change"].apply(lambda v: f"{v:+d} customer" if not is_en else f"{v:+d} accounts"),
        col_names["Laju Growth"]: tbl_data["growth_display_en" if is_en else "growth_display_id"],
        col_names["Porsi"]: tbl_data["contribution_pct"].apply(lambda v: f"{v:.1f}%"),
        col_names["Status"]: tbl_data["status_en" if is_en else "status_id"],
        col_names["Makna"]: tbl_data["desc_en" if is_en else "desc_id"]
    })

    st.dataframe(formatted_table, use_container_width=True, hide_index=True)
    st.caption(
        "💡 *Status bisnis menggabungkan perubahan angka riil (+/- customer) dan persentase agar evaluasi tetap adil bagi kategori bervolume besar maupun kategori skala kecil (<5 customer).*"
        if not is_en
        else "💡 *Business status accounts for both absolute volume change and percentage to ensure balanced evaluations for large categories and low baselines alike.*"
    )
else:
    st.caption("No category growth data available." if is_en else "Belum ada data pertumbuhan kategori untuk filter ini.")

st.markdown("---")

# -------------------------------------------------------------
# 10. SECTION 4: DIVISION × CATEGORY — USER-FRIENDLY STACKED BAR CHART
# (Replacing Heatmap as requested by user for non-technical clarity)
# -------------------------------------------------------------
if is_en:
    sec4_title = "New Customers by Division & Category (Stacked Bar)"
    sec4_sub = "Mapping branch performance and customer category mix across all Cipta Grafika branches."
    sec4_what = "Stacked bar chart visualizing total customer acquisition per branch broken down by customer category."
    sec4_why = "Instantly reveals which branches lead in acquisition and which customer segments drive them, without confusing matrix heatmaps."
    sec4_insight = "Total bar height shows overall volume leadership; color layers reveal customer portfolio composition."
else:
    sec4_title = "Sebaran Customer Baru per Cabang & Kategori (Bar Bertumpuk)"
    sec4_sub = "Memetakan kontribusi cabang dan komposisi segmen customer di setiap cabang Cipta Grafika."
    sec4_what = "Grafik batang bertumpuk yang memperlihatkan total akuisisi customer tiap cabang sekaligus proporsi kategori pelanggannya."
    sec4_why = "Melihat cabang mana yang paling aktif mengakuisisi pelanggan dan segmen apa yang dominan di cabang tersebut tanpa grafik rumit."
    sec4_insight = "Tinggi total batang menunjukkan cabang terkuat; susunan warna menunjukkan komposisi segmen pelanggannya."

render_section_info(
    title=sec4_title,
    subtitle=sec4_sub,
    what_it_shows=sec4_what,
    why_important=sec4_why,
    simple_insight=sec4_insight,
    icon="🏢",
    lang_code=lang_code
)

if not df_curr.empty:
    # Group by division and category
    div_cat_df = (
        df_curr.groupby(["division_name", "category_name"])["customer_id"]
        .nunique()
        .reset_index(name="new_customers")
    )
    
    # Calculate division totals for ordering
    div_totals = div_cat_df.groupby("division_name")["new_customers"].sum().sort_values(ascending=False)
    cat_totals = div_cat_df.groupby("category_name")["new_customers"].sum().sort_values(ascending=False)
    
    # Interactive view mode toggle
    c_view_opt, _ = st.columns([2.5, 2.5])
    with c_view_opt:
        stack_view_opts = (
            ["🏢 Grouped by Branch (Stacked by Category)", "👥 Grouped by Category (Stacked by Branch)"]
            if is_en
            else ["🏢 Dikelompokkan per Cabang (Stacked per Kategori)", "👥 Dikelompokkan per Kategori (Stacked per Cabang)"]
        )
        selected_stack_view = st.radio(
            "Tampilan Grafik:" if not is_en else "Chart View:",
            options=stack_view_opts,
            horizontal=True,
            key="nc_stack_view_toggle"
        )
    
    palette = ["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#64748B", "#F97316"]

    if "Cabang" in selected_stack_view or "Branch" in selected_stack_view:
        # X: Division, Color: Category
        fig_stack = px.bar(
            div_cat_df,
            x="division_name",
            y="new_customers",
            color="category_name",
            category_orders={"division_name": div_totals.index.tolist()},
            labels={
                "division_name": "Branch / Division" if is_en else "Cabang / Divisi",
                "new_customers": "New Customers" if is_en else "Customer Baru",
                "category_name": "Category" if is_en else "Kategori"
            },
            color_discrete_sequence=palette
        )
        fig_stack.update_layout(
            barmode="stack",
            legend_title_text="Customer Category" if is_en else "Kategori Customer",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_stack.update_traces(
            hovertemplate="<b>%{x}</b><br>Kategori: <b>%{fullData.name}</b><br>New Customers: <b>%{y:,}</b><extra></extra>" if not is_en else "<b>%{x}</b><br>Category: <b>%{fullData.name}</b><br>New Customers: <b>%{y:,}</b><extra></extra>"
        )
    else:
        # X: Category, Color: Division
        fig_stack = px.bar(
            div_cat_df,
            x="category_name",
            y="new_customers",
            color="division_name",
            category_orders={"category_name": cat_totals.index.tolist()},
            labels={
                "category_name": "Customer Category" if is_en else "Kategori Customer",
                "new_customers": "New Customers" if is_en else "Customer Baru",
                "division_name": "Branch / Division" if is_en else "Cabang / Divisi"
            },
            color_discrete_sequence=palette
        )
        fig_stack.update_layout(
            barmode="stack",
            legend_title_text="Branch" if is_en else "Cabang",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_stack.update_traces(
            hovertemplate="<b>%{x}</b><br>Cabang: <b>%{fullData.name}</b><br>New Customers: <b>%{y:,}</b><extra></extra>" if not is_en else "<b>%{x}</b><br>Branch: <b>%{fullData.name}</b><br>New Customers: <b>%{y:,}</b><extra></extra>"
        )
        
    apply_plotly_theme(fig_stack, height=360)
    st.plotly_chart(fig_stack, use_container_width=True)

    # Clean expander for exact cross-tabulation table
    matrix_df = compute_new_customer_division_matrix(df_curr)
    exp_title = "🔍 View Detailed Cross-Tabulation Table (Division × Category Numbers)" if is_en else "🔍 Lihat Rincian Tabel Angka (Cross-Tabulation Divisi × Kategori)"
    with st.expander(exp_title, expanded=False):
        st.dataframe(matrix_df.style.format("{:,}"), use_container_width=True)
else:
    st.caption("No data for current filter selection." if is_en else "Belum ada data untuk filter saat ini.")

st.markdown("---")

# -------------------------------------------------------------
# 11. SECTION 5: GROWTH DRIVERS & NEEDS ATTENTION
# -------------------------------------------------------------
col_drv, col_dec = st.columns(2)
drivers_df = compute_new_customer_growth_drivers(df_curr, df_prev, top_n=6)
declining_df = compute_new_customer_declining_segments(df_curr, df_prev, top_n=5)

with col_drv:
    st.markdown("#### 🚀 Top Growth Drivers" if is_en else "#### 🚀 Pendorong Pertumbuhan Utama (Top Growth Drivers)")
    st.caption(
        "Ranked **Division × Category** pairings with the highest customer surge (sorted by **Net Change DESC**)."
        if is_en
        else "Peringkat kombinasi **Divisi × Kategori** dengan penambahan customer baru terbesar (diurutkan berdasarkan **Net Change DESC**)."
    )
    
    if not drivers_df.empty:
        drv_tbl = pd.DataFrame({
            ("Division" if is_en else "Divisi"): drivers_df["division_name"],
            ("Category" if is_en else "Kategori"): drivers_df["category_name"],
            ("Previous" if is_en else "Lalu"): drivers_df["previous"].apply(lambda v: f"{v:,}"),
            ("Current" if is_en else "Kini"): drivers_df["current"].apply(lambda v: f"{v:,}"),
            ("Net Change" if is_en else "Net Penambahan"): drivers_df["net_change"].apply(lambda v: f"+{v:,}"),
            ("Growth Rate" if is_en else "Laju Growth"): drivers_df["growth_display"]
        })
        st.dataframe(drv_tbl, use_container_width=True, hide_index=True)
    else:
        st.info("No division pairings recorded positive additions for this filter." if is_en else "Tidak ada kombinasi cabang yang mencatatkan penambahan positif pada filter ini.")

with col_dec:
    st.markdown("#### ⚠️ Needs Attention (Declining Segments)" if is_en else "#### ⚠️ Area Perhatian (Needs Attention)")
    st.caption(
        "Customer categories experiencing **contraction in new customer intake** compared to the baseline period."
        if is_en
        else "Kategori pelanggan yang mengalami **kontraksi/penurunan volume customer baru** dibandingkan periode sebelumnya."
    )
    
    if not declining_df.empty:
        dec_tbl = pd.DataFrame({
            ("Category" if is_en else "Kategori"): declining_df["category_name"],
            ("Previous" if is_en else "Lalu"): declining_df["previous"].apply(lambda v: f"{v:,}"),
            ("Current" if is_en else "Kini"): declining_df["current"].apply(lambda v: f"{v:,}"),
            ("Contraction" if is_en else "Penurunan"): declining_df["net_change"].apply(lambda v: f"{v:,}"),
            ("Growth %" if is_en else "Growth %"): declining_df["growth_display"],
            ("Impacted Branch" if is_en else "Cabang Terdampak"): declining_df["most_impacted_division"]
        })
        st.dataframe(dec_tbl, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 No customer categories experienced decline in this period!" if is_en else "🎉 Tidak ada kategori customer yang mengalami penurunan pada periode ini!")

st.markdown("---")

# -------------------------------------------------------------
# 12. SECTION 6: BUSINESS INSIGHTS & RECOMMENDED ACTIONS (DSS)
# -------------------------------------------------------------
title_ins_sec = "💡 Business Insights & Actionable Decision Support" if is_en else "💡 Business Insights & Rekomendasi Keputusan Bisnis"
caption_ins_sec = (
    "Standardized Business Evaluation Format: **OBSERVED METRIC → ROOT CAUSE INSIGHT → RECOMMENDED ACTION WORKFLOW**"
    if is_en
    else "Format Evaluasi Bisnis Terstandar: **TEMUAN → MAKNA BISNIS → RECOMMENDED ACTION WORKFLOW**"
)
st.subheader(title_ins_sec)
st.caption(caption_ins_sec)

matrix_for_insights = compute_new_customer_division_matrix(df_curr)
dynamic_insights = generate_new_customer_insights(
    kpis=bi_kpis,
    cat_growth=cat_growth_df,
    drivers=drivers_df,
    declining=declining_df,
    matrix=matrix_for_insights,
    lang=lang_code
)

if dynamic_insights:
    for ins in dynamic_insights:
        render_business_insight_card(
            title=ins["title"],
            metric=ins["metric"],
            context=ins["context"],
            insight=ins["insight"],
            who_impacted=ins["who_impacted"],
            action=ins["action"],
            badge=ins["badge"]
        )
else:
    st.caption("No analytical insights could be extracted for the current filter." if is_en else "Belum ada insight analitis yang dapat diekstrak untuk filter periode saat ini.")

# Footer data integrity
st.markdown("---")
f1, f2, f3 = st.columns(3)
with f1:
    st.caption("📌 **Cetakia Business Definition:** `New Customer Valid Date = Registration Date + 2 Days`" if is_en else "📌 **Definisi Bisnis Cetakia:** `New Customer Valid Date = Registration Date + 2 Hari`")
with f2:
    st.caption("🛡️ **Data Hygiene:** Calculation basis `COUNT(DISTINCT customer_id)`" if is_en else "🛡️ **Data Hygiene:** Basis perhitungan `COUNT(DISTINCT customer_id)`")
with f3:
    st.caption("⚡ **Data Mode:** Master Historical Customer Dataset Cetakia BI (`new_customer_eda.csv`)" if is_en else "⚡ **Mode Data:** Master Historical Customer Dataset Cetakia BI (`new_customer_eda.csv`)")
