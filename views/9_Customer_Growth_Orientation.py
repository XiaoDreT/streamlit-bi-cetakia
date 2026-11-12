import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_customer_growth_data
from utils.intelligence_engine import (
    compute_cgr_period_summary,
    compute_cgr_monthly_breakdown,
    compute_cgr_by_dimension
)
from components.ui_components import (
    render_header,
    metric_card,
    render_section_info,
    render_summary_strip,
    render_layman_summary_box,
    render_business_insight_card,
    global_sidebar_filters,
    apply_plotly_theme
)

st.set_page_config(
    page_title="Customer Growth Orientation — Cetakia BI DSS",
    page_icon="🚀",
    layout="wide"
)

# -------------------------------------------------------------
# 1. LOAD DATASET (data/data_customer.csv — External Customers Only)
# -------------------------------------------------------------
try:
    df_customers = load_customer_growth_data()
    # Exclude internal company division accounts ('DIVISI') so CGR focuses 100% on external customers
    if "category_name" in df_customers.columns:
        df_customers = df_customers[df_customers["category_name"].astype(str).str.upper() != "DIVISI"].copy()
except Exception as e:
    st.error(f"Gagal memuat dataset data/data_customer.csv: {e}")
    st.stop()

# -------------------------------------------------------------
# 2. GLOBAL SIDEBAR FILTERS & LOCALE STATE
# -------------------------------------------------------------
filters = global_sidebar_filters(df_customers=df_customers)
t = filters["t"]
lang_code = filters.get("lang", "ID")
is_en = (lang_code == "EN")

selected_branch = filters.get("branch", "All Branches")
selected_segment = filters.get("segment", "All Segments")

norm_division = None if selected_branch in ["All Branches", "Semua Cabang"] else selected_branch
norm_category = None if selected_segment in ["All Segments", "Semua Segmen"] else selected_segment

# Latest timestamp from data_customer.csv
latest_dt = df_customers["created_at_jakarta"].max()
if pd.notna(latest_dt):
    dt_obj = pd.to_datetime(latest_dt)
    latest_data_str = dt_obj.strftime("%d %b %Y %H:%M")
else:
    latest_data_str = "12 Nov 2026 08:47"

# -------------------------------------------------------------
# 3. PAGE HEADER & SCOPE BANNER
# -------------------------------------------------------------
render_header(
    title="Customer Growth Orientation",
    subtitle=(
        "Customer Growth Rate (CGR) Analytics based on Initial Customer Base, New Customer Intake, Churn & Ending Base — presented with layman-friendly Stacked Bar & Donut visuals."
        if is_en
        else "Analisa Pertumbuhan Pelanggan (Customer Growth Rate / CGR) berbasis Pelanggan Awal, Pelanggan Baru, Pelanggan Berhenti (Churn) & Pelanggan Akhir — disajikan dengan grafik Bar Stack & Donat yang mudah dipahami semua kalangan."
    ),
    module_tag="SENIOR DATA ANALYST · CGR ORIENTATION" if is_en else "ANALISA PERTUMBUHAN PELANGGAN · CGR"
)

display_branch_name = "All Branches (6 Divisions)" if (norm_division is None and is_en) else ("Semua Cabang (6 Divisi)" if norm_division is None else norm_division)
display_segment_name = "All External Segments (7 Categories · Excl. Internal Divisi)" if (norm_category is None and is_en) else ("Semua Segmen Eksternal (7 Kategori · Tanpa Divisi Internal)" if norm_category is None else norm_category)

st.markdown(f"""
<div style="background-color: var(--secondary-background-color, rgba(128,128,128,0.06)); 
            border: 1px solid rgba(156,163,175,0.22); 
            border-radius: 10px; padding: 12px 18px; margin-bottom: 18px;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 13.5px;">
        <span>🏢 <b>{"Branch Scope" if is_en else "Cakupan Cabang"}:</b> <span style="color: #38BDF8; font-weight: 700;">{display_branch_name}</span></span>
        <span style="opacity: 0.3;">|</span>
        <span>👥 <b>{"Customer Segment" if is_en else "Segmen Pelanggan"}:</b> <span style="color: #38BDF8; font-weight: 700;">{display_segment_name}</span></span>
        <span style="opacity: 0.3;">|</span>
        <span style="color: #94A3B8; font-size: 12px;"><i>({"Filter via left sidebar anytime" if is_en else "Ubah filter cabang/segmen kapan saja melalui menu di sebelah kiri"})</i></span>
    </div>
    <div style="color: #10B981; font-size: 12px; font-weight: 600;">
        📂 {"Source" if is_en else "Sumber Data Eksternal"}: data/data_customer.csv ({len(df_customers):,} {"external records" if is_en else "pelanggan eksternal"} · s/d {latest_data_str})
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. PERIOD & FORMULA CONTROL BAR
# -------------------------------------------------------------
st.markdown(
    "### 🎛️ Pilih Periode Analisa & Basis Tanggal Customer Growth"
    if not is_en
    else "### 🎛️ Select Analysis Period & Customer Growth Date Basis"
)

ctrl_col1, ctrl_col2 = st.columns([2.6, 1.4])

with ctrl_col1:
    period_options = (
        [
            "Full Year 2026 (Jan – Nov 2026)",
            "October 2026 (Last Full Month)",
            "September 2026",
            "August 2026",
            "Q3 2026 (Jul – Sep 2026)",
            "Q2 2026 (Apr – Jun 2026)",
            "Last 30 Days",
            "November 2026 (Month-to-Date)",
            "Custom Date Range"
        ]
        if is_en
        else [
            "Sepanjang Tahun 2026 (Jan – Nov 2026)",
            "Oktober 2026 (Bulan Penuh Terakhir)",
            "September 2026",
            "Agustus 2026",
            "Kuartal 3 / Q3 2026 (Jul – Sep)",
            "Kuartal 2 / Q2 2026 (Apr – Jun)",
            "30 Hari Terakhir",
            "November 2026 (Bulan Berjalan)",
            "Rentang Tanggal Kustom"
        ]
    )
    selected_period_opt = st.pills(
        label="Pilih Periode Analisa" if not is_en else "Select Period",
        options=period_options,
        default=period_options[0],
        label_visibility="collapsed",
        key="cgr_period_pills"
    )
    if not selected_period_opt:
        selected_period_opt = period_options[0]

with ctrl_col2:
    date_basis_opts = (
        ["Registration Date (registration_date)", "Valid Date +2 Days (new_customer_valid_date)"]
        if is_en
        else ["Tanggal Pendaftaran (registration_date)", "Tanggal Sah +2 Hari (new_customer_valid_date)"]
    )
    selected_basis_lbl = st.radio(
        "Acuan Tanggal Pelanggan:" if not is_en else "Customer Date Reference:",
        options=date_basis_opts,
        horizontal=True,
        key="cgr_date_basis_radio"
    )
    date_basis_col = "new_customer_valid_date" if "new_customer_valid_date" in selected_basis_lbl else "registration_date"

max_dt_in_col = df_customers[date_basis_col].max()
min_dt_in_col = df_customers[date_basis_col].min()

# Map selected pill to start_date and end_date
if "Oktober 2026" in selected_period_opt or "October 2026" in selected_period_opt:
    p_start, p_end = datetime.date(2026, 10, 1), datetime.date(2026, 10, 31)
elif "September 2026" in selected_period_opt:
    p_start, p_end = datetime.date(2026, 9, 1), datetime.date(2026, 9, 30)
elif "Agustus 2026" in selected_period_opt or "August 2026" in selected_period_opt:
    p_start, p_end = datetime.date(2026, 8, 1), datetime.date(2026, 8, 31)
elif "Q3 2026" in selected_period_opt:
    p_start, p_end = datetime.date(2026, 7, 1), datetime.date(2026, 9, 30)
elif "Q2 2026" in selected_period_opt:
    p_start, p_end = datetime.date(2026, 4, 1), datetime.date(2026, 6, 30)
elif "30" in selected_period_opt:
    p_end = max_dt_in_col
    p_start = p_end - datetime.timedelta(days=29)
elif "November 2026" in selected_period_opt:
    p_start, p_end = datetime.date(2026, 11, 1), max_dt_in_col
elif "Kustom" in selected_period_opt or "Custom" in selected_period_opt:
    c_d1, _ = st.columns([1.6, 2.4])
    with c_d1:
        custom_dates = st.date_input(
            "Pilih Tanggal Mulai & Tanggal Akhir:" if not is_en else "Select Start & End Date:",
            value=(datetime.date(2026, 10, 1), datetime.date(2026, 10, 31)),
            min_value=min_dt_in_col,
            max_value=max_dt_in_col,
            key="cgr_custom_dates"
        )
        if isinstance(custom_dates, (tuple, list)) and len(custom_dates) == 2:
            p_start, p_end = custom_dates
        else:
            p_start, p_end = datetime.date(2026, 10, 1), datetime.date(2026, 10, 31)
else:
    # Full Year 2026
    p_start, p_end = min_dt_in_col, max_dt_in_col

# -------------------------------------------------------------
# 5. COMPUTE CGR METRICS FOR SELECTED PERIOD
# -------------------------------------------------------------
cgr_summary = compute_cgr_period_summary(
    df=df_customers,
    start_date=p_start,
    end_date=p_end,
    division=norm_division,
    category=norm_category,
    date_basis=date_basis_col
)

awal_cnt = cgr_summary["pelanggan_awal"]
baru_cnt = cgr_summary["pelanggan_baru"]
churn_cnt = cgr_summary["pelanggan_churn"]
churn_del_cnt = cgr_summary["churn_deleted"]
churn_inact_cnt = cgr_summary["churn_inactive"]
akhir_cnt = cgr_summary["pelanggan_akhir"]
net_cnt = cgr_summary["net_growth"]
cgr_net_pct = cgr_summary["cgr_net_pct"]
cgr_rumus1_pct = cgr_summary["cgr_rumus1_pct"]
prev_baru_cnt = cgr_summary["prev_baru"]
diff_baru_pop = cgr_summary["diff_baru_pop"]
pop_baru_pct = cgr_summary["pop_baru_pct"]
is_fy_base = cgr_summary["is_full_year_baseline"]
eff_start = cgr_summary["eff_start_date"]
eff_end = cgr_summary["eff_end_date"]

# -------------------------------------------------------------
# 6. FORMULA EXPLAINER & STEP-BY-STEP VISUAL CALCULATOR
# -------------------------------------------------------------
if is_fy_base:
    base_note_id = (
        f"📌 <b>Catatan Data-Oriented (Penting):</b> Pada tanggal <b>5–8 Januari 2026</b> terdapat proses <b>Migrasi Database Awal</b> sebanyak <b>{awal_cnt:,} pelanggan eksisting</b> dari seluruh cabang ke sistem Cetakia. "
        f"Sebagai Data Analyst, angka <b>{awal_cnt:,} pelanggan</b> tersebut ditetapkan sebagai <b>Jumlah Pelanggan Awal Periode</b> (agar pembagi tidak nol dan tidak mendistorsi analisa), sedangkan <b>{baru_cnt:,} pelanggan</b> yang mendaftar mulai <b>9 Januari s/d {eff_end.strftime('%d %b %Y')}</b> dihitung sebagai <b>Pelanggan Baru Didapat</b>."
    )
    base_note_en = (
        f"📌 <b>Data-Oriented Note (Crucial):</b> On <b>Jan 5–8, 2026</b>, an initial bulk database migration onboarded <b>{awal_cnt:,} existing customers</b> into Cetakia. "
        f"This <b>{awal_cnt:,} account base</b> serves as the <b>Initial Period Customers (Pelanggan Awal Periode)</b>, while the <b>{baru_cnt:,} accounts</b> registered from <b>Jan 9 to {eff_end.strftime('%d %b %Y')}</b> represent <b>New Customers Acquired (Pelanggan Baru Didapat)</b>."
    )
else:
    base_note_id = (
        f"📅 <b>Periode Analisa Aktif:</b> <code>{eff_start.strftime('%d %b %Y')}</code> s/d <code>{eff_end.strftime('%d %b %Y')}</code> ({cgr_summary['period_days']} hari). "
        f"<b>Pelanggan Awal Periode ({awal_cnt:,} akun)</b> adalah seluruh pelanggan aktif yang sudah terdaftar sebelum <code>{eff_start.strftime('%d %b %Y')}</code>."
    )
    base_note_en = (
        f"📅 <b>Active Analysis Period:</b> <code>{eff_start.strftime('%d %b %Y')}</code> to <code>{eff_end.strftime('%d %b %Y')}</code> ({cgr_summary['period_days']} days). "
        f"<b>Initial Period Customers ({awal_cnt:,} accounts)</b> are all active customers registered prior to <code>{eff_start.strftime('%d %b %Y')}</code>."
    )

avg_daily_period = round(baru_cnt / max(1, cgr_summary["period_days"]), 1)

st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(30, 64, 175, 0.10) 0%, rgba(16, 185, 129, 0.10) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
    <div style="font-size: 16px; font-weight: 800; color: #3B82F6; margin-bottom: 8px;">
        🧮 {"Rumus Customer Growth Rate (CGR) & Pedoman Keputusan Bisnis" if not is_en else "Customer Growth Rate (CGR) Formula & Business Decision Guide"}
    </div>
    <div style="font-size: 13px; margin-bottom: 14px; line-height: 1.55; opacity: 0.92;">
        {base_note_en if is_en else base_note_id}
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
        <div style="background-color: var(--secondary-background-color, rgba(17,24,39,0.5)); border: 1px solid rgba(16, 185, 129, 0.4); border-left: 5px solid #10B981; border-radius: 10px; padding: 14px 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                {"Perhitungan Aktual Customer Growth Rate (CGR)" if not is_en else "Actual Customer Growth Rate (CGR) Calculation"}
            </div>
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px; opacity: 0.9;">
                <code>CGR = ((Pelanggan Baru − Pelanggan Berhenti) / Pelanggan Awal) × 100%</code>
            </div>
            <div style="font-size: 13.5px; margin-bottom: 6px;">
                <code>CGR = (({baru_cnt:,} − {churn_cnt:,}) / {awal_cnt:,}) × 100%</code> = <b style="color: #10B981; font-size: 20px;">+{cgr_net_pct:.2f}%</b>
            </div>
            <div style="font-size: 12px; opacity: 0.85; line-height: 1.45;">
                {"💡 <b>Makna Bagi Pengambil Keputusan:</b> Menunjukkan berapa persen <b>pertambahan bersih basis pelanggan eksternal kita</b> dari awal periode ke akhir periode setelah dikurangi akun yang berhenti/dihapus." if not is_en else "💡 <b>Decision Meaning:</b> Measures the <b>net percentage expansion of our external customer base</b> from the start to the end of the period after subtracting churn."}
            </div>
        </div>
        <div style="background-color: var(--secondary-background-color, rgba(17,24,39,0.5)); border: 1px solid rgba(59, 130, 246, 0.4); border-left: 5px solid #3B82F6; border-radius: 10px; padding: 14px 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #3B82F6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                {"Kecepatan Akuisisi & Indikator Keputusan Manajemen" if not is_en else "Acquisition Velocity & Management Decision Benchmark"}
            </div>
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px; opacity: 0.9;">
                <code>Laju Harian = {baru_cnt:,} Pelanggan Baru ÷ {cgr_summary['period_days']} Hari</code>
            </div>
            <div style="font-size: 13.5px; margin-bottom: 6px;">
                {"Rata-rata Penambahan:" if not is_en else "Average Daily Intake:"} <b style="color: #38BDF8; font-size: 20px;">+{avg_daily_period:.1f} {"pelanggan/hari" if not is_en else "customers/day"}</b>
            </div>
            <div style="font-size: 12px; opacity: 0.85; line-height: 1.45;">
                {"🎯 <b>Panduan Keputusan:</b> Jika laju akuisisi <b>≥ 30 pelanggan/hari (CGR bulanan ≥ +4%)</b> fokuskan CS mengonversi akun baru menjadi repeat order; jika <b>&lt; 28 pelanggan/hari</b> segera aktifkan kampanye promo cabang &amp; kemitraan AGEN/UMKM." if not is_en else "🎯 <b>Decision Guide:</b> When daily intake is <b>≥ 30/day (monthly CGR ≥ +4%)</b> focus CS on repeat-order onboarding; when <b>&lt; 28/day</b> activate branch promos &amp; AGEN/SME outreach."}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 6 Executive KPI Cards showing every single variable in the formula
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    metric_card(
        title="PELANGGAN AWAL" if not is_en else "INITIAL CUSTOMERS",
        value=f"{awal_cnt:,}",
        delta="Basis Awal (100%)" if not is_en else "Starting Base",
        delta_color="positive",
        subtext="Jumlah di awal periode" if not is_en else "Customers at period start"
    )
with k2:
    metric_card(
        title="+ PELANGGAN BARU" if not is_en else "+ NEW CUSTOMERS",
        value=f"+{baru_cnt:,}",
        delta=f"{pop_baru_pct:+.1f}% vs periode lalu" if (not is_en and prev_baru_cnt > 0) else (f"{pop_baru_pct:+.1f}% vs prev period" if prev_baru_cnt > 0 else "Akuisisi Baru"),
        delta_color="positive" if diff_baru_pop >= 0 else "negative",
        subtext="Pelanggan baru didapat" if not is_en else "New customers acquired"
    )
with k3:
    metric_card(
        title="- BERHENTI (CHURN)" if not is_en else "- CHURNED / LEFT",
        value=f"{churn_cnt:,}",
        delta=f"{churn_del_cnt} dihapus · {churn_inact_cnt} nonaktif" if not is_en else f"{churn_del_cnt} del · {churn_inact_cnt} inact",
        delta_color="positive" if churn_cnt == 0 else "negative",
        subtext="Keluar / tidak aktif" if not is_en else "Deleted or inactive accounts"
    )
with k4:
    metric_card(
        title="= PELANGGAN AKHIR" if not is_en else "= ENDING CUSTOMERS",
        value=f"{akhir_cnt:,}",
        delta=f"+{net_cnt:,} bersih" if not is_en else f"+{net_cnt:,} net",
        delta_color="positive" if net_cnt >= 0 else "negative",
        subtext="Awal + Baru − Churn" if not is_en else "Initial + New − Churn"
    )
with k5:
    metric_card(
        title="CGR (BARU - CHURN)" if not is_en else "NET CGR %",
        value=f"+{cgr_net_pct:.2f}%",
        delta="Pertumbuhan Basis" if not is_en else "Base Expansion",
        delta_color="positive" if cgr_net_pct >= 0 else "negative",
        subtext="(Baru − Churn) / Awal" if not is_en else "(New − Churn) / Initial"
    )
with k6:
    metric_card(
        title="RATA-RATA BARU / HARI" if not is_en else "AVG NEW / DAY",
        value=f"+{avg_daily_period:.1f}",
        delta=f"{cgr_summary['period_days']} hari aktif" if not is_en else f"{cgr_summary['period_days']} active days",
        delta_color="positive",
        subtext="Kecepatan akuisisi harian" if not is_en else "Daily acquisition speed"
    )

# Layman summary for Section 0 (Overall Formula Summary)
render_layman_summary_box(
    title="Gambaran Umum Pertumbuhan Pelanggan (CGR)" if not is_en else "Overall Customer Growth (CGR) Snapshot",
    plain_summary=(
        f"Pada awal periode ini, kita memiliki <b>{awal_cnt:,} pelanggan eksternal</b>. Selama periode berjalan ({cgr_summary['period_days']} hari), masuk tambahan <b>+{baru_cnt:,} pelanggan baru</b> (rata-rata <b>+{avg_daily_period:.1f} pelanggan baru per hari</b>) dan hanya ada <b>{churn_cnt:,} akun yang berhenti/dihapus</b>, sehingga total pelanggan aktif di akhir periode naik menjadi <b>{akhir_cnt:,} pelanggan</b>."
        if not is_en
        else f"At the start of this period, we had <b>{awal_cnt:,} external customers</b>. Over {cgr_summary['period_days']} days, we gained <b>+{baru_cnt:,} new customers</b> (averaging <b>+{avg_daily_period:.1f} new customers/day</b>) and lost only <b>{churn_cnt:,} accounts</b> to churn, bringing our ending active base to <b>{akhir_cnt:,} customers</b>."
    ),
    key_takeaway=(
        f"Jumlah pelanggan eksternal kita tumbuh bersih sebesar <b>+{cgr_net_pct:.2f}%</b> (bertambah <b>+{net_cnt:,} pelanggan baru bersih</b>). Artinya, kran pendaftaran pelanggan baru mengalir kencang (~{avg_daily_period:.0f} akun/hari) dan hampir tidak ada akun pelanggan yang keluar."
        if not is_en
        else f"Our external customer base expanded by a net <b>+{cgr_net_pct:.2f}%</b> (adding <b>+{net_cnt:,} net customers</b>), driven by a steady intake of ~{avg_daily_period:.0f} new accounts/day and virtually zero churn."
    ),
    recommended_action=(
        "Fokuskan tim sales dan CS untuk memastikan pelanggan yang baru terdaftar segera melakukan transaksi berulang (repeat order), serta jaga kecepatan akuisisi di atas 30 pelanggan baru/hari."
        if not is_en
        else "Focus sales and CS teams on converting newly registered accounts into repeat buyers while maintaining daily acquisition above 30 new accounts/day."
    ),
    formula_note=(
        f"<code>CGR = ({baru_cnt:,} Baru − {churn_cnt:,} Churn) ÷ {awal_cnt:,} Awal × 100% = +{cgr_net_pct:.2f}%</code>  |  <code>Rata-rata Harian = +{avg_daily_period:.1f} pelanggan baru/hari</code>"
    ),
    lang_code=lang_code,
    accent_color="#10B981"
)

st.markdown("---")

# -------------------------------------------------------------
# 7. INSIGHT 1: STACKED BAR CHART — MONTHLY CUSTOMER BASE EXPANSION
# -------------------------------------------------------------
monthly_df = compute_cgr_monthly_breakdown(
    df=df_customers,
    division=norm_division,
    category=norm_category,
    date_basis=date_basis_col
)

render_section_info(
    title=(
        "Insight 1: Grafik Bar Bertumpuk (Bar Stack) Pertumbuhan Pelanggan Bulanan (Jan – Nov 2026)"
        if not is_en
        else "Insight 1: Monthly Customer Growth Stacked Bar Chart (Jan – Nov 2026)"
    ),
    subtitle=(
        "Visualisasi Bar Stack yang memperlihatkan bagaimana tumpukan Pelanggan Awal + Pelanggan Baru membentuk Pelanggan Akhir di setiap bulan."
        if not is_en
        else "Stacked Bar visualization showing how Initial Customers + New Customers stack up to form Ending Customers each month."
    ),
    what_it_shows=(
        "Tumpukan batang biru (Pelanggan Awal Bulan) dan batang hijau (Pelanggan Baru Bulan Tersebut) beserta angka persentase CGR setiap bulannya."
        if not is_en
        else "Stacked blue bars (Initial Monthly Base) and green bars (New Monthly Customers) along with monthly CGR percentages."
    ),
    why_important=(
        "User dapat langsung melihat bahwa tangga pelanggan Cipta Grafika terus naik setiap bulan tanpa pernah menyusut."
        if not is_en
        else "Anyone can immediately see that Cipta Grafika's customer staircase climbs steadily every single month without shrinking."
    ),
    simple_insight=(
        "Semakin tinggi total batang, semakin besar total pelanggan kita; semakin tebal lapisan warna hijau di atasnya, semakin banyak pelanggan baru yang masuk di bulan itu."
        if not is_en
        else "The taller the overall bar, the larger our customer base; the thicker the green layer on top, the more new customers joined that month."
    ),
    icon="📊",
    lang_code=lang_code
)

if not monthly_df.empty:
    tab_m_stack1, tab_m_stack2, tab_m_stack3 = st.tabs([
        "📊 Bar Stack: Pelanggan Awal + Pelanggan Baru (Kumulatif CGR)" if not is_en else "📊 Stacked Bar: Initial Base + New Customers (Cumulative CGR)",
        "🏢 Bar Stack: Pelanggan Baru Bulanan per Cabang" if not is_en else "🏢 Stacked Bar: Monthly New Customers by Branch",
        "👥 Bar Stack: Pelanggan Baru Bulanan per Kategori" if not is_en else "👥 Stacked Bar: Monthly New Customers by Category"
    ])

    month_col_lbl = "month_label_en" if is_en else "month_label_id"
    ym_to_label = dict(zip(monthly_df["year_month"], monthly_df[month_col_lbl]))
    ym_to_cgr = dict(zip(monthly_df["year_month"], monthly_df["cgr_net_pct"]))
    ym_to_baru = dict(zip(monthly_df["year_month"], monthly_df["pelanggan_baru"]))
    ordered_month_labels = monthly_df[month_col_lbl].tolist()

    with tab_m_stack1:
        fig_m_stack = go.Figure()

        fig_m_stack.add_trace(go.Bar(
            x=monthly_df[month_col_lbl],
            y=monthly_df["pelanggan_awal"],
            name="Pelanggan Awal Periode (Basis Lama)" if not is_en else "Initial Customers (Existing Base)",
            marker_color="#3B82F6",
            text=monthly_df["pelanggan_awal"].apply(lambda v: f"{v:,}"),
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=11, color="#FFFFFF"),
            hovertemplate=(
                "<b>%{x}</b><br>Pelanggan Awal Bulan: <b>%{y:,} pelanggan</b><extra></extra>"
                if not is_en else
                "<b>%{x}</b><br>Initial Base: <b>%{y:,} customers</b><extra></extra>"
            )
        ))

        fig_m_stack.add_trace(go.Bar(
            x=monthly_df[month_col_lbl],
            y=monthly_df["pelanggan_baru"],
            name="+ Pelanggan Baru Didapat" if not is_en else "+ New Customers Acquired",
            marker_color="#10B981",
            customdata=monthly_df[["pelanggan_awal", "pelanggan_akhir", "pelanggan_churn", "cgr_net_pct", "avg_daily_new"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Pelanggan Awal: <b>%{customdata[0]:,}</b><br>"
                "+ Pelanggan Baru: <b>+%{y:,}</b> (~%{customdata[4]:.1f}/hari)<br>"
                "- Pelanggan Berhenti (Churn): <b>%{customdata[2]:,}</b><br>"
                "= Pelanggan Akhir: <b>%{customdata[1]:,}</b><br>"
                "CGR (Baru−Churn)/Awal: <b>+%{customdata[3]:.2f}%</b><extra></extra>"
                if not is_en else
                "<b>%{x}</b><br>"
                "Initial Base: <b>%{customdata[0]:,}</b><br>"
                "+ New Customers: <b>+%{y:,}</b> (~%{customdata[4]:.1f}/day)<br>"
                "- Churned Customers: <b>%{customdata[2]:,}</b><br>"
                "= Ending Base: <b>%{customdata[1]:,}</b><br>"
                "Net CGR %: <b>+%{customdata[3]:.2f}%</b><extra></extra>"
            )
        ))

        if monthly_df["pelanggan_churn"].sum() > 0:
            fig_m_stack.add_trace(go.Bar(
                x=monthly_df[month_col_lbl],
                y=monthly_df["pelanggan_churn"],
                name="- Pelanggan Berhenti (Churn)" if not is_en else "- Churned Customers",
                marker_color="#EF4444",
                hovertemplate="<b>%{x}</b><br>Pelanggan Berhenti (Churn): <b>%{y:,} akun</b><extra></extra>"
            ))

        # Add explicit top-of-bar annotations for EVERY month so no bar ever hides its +New & CGR% label
        for _, m_row in monthly_df.iterrows():
            bar_top_y = float(m_row["pelanggan_awal"] + m_row["pelanggan_baru"] + m_row["pelanggan_churn"])
            baru_val = int(m_row["pelanggan_baru"])
            cgr_val = float(m_row["cgr_net_pct"])
            ann_text = (
                f"<b>+{baru_val:,} Baru</b><br><span style='color:#10B981;'>(CGR +{cgr_val:.2f}%)</span>"
                if not is_en
                else f"<b>+{baru_val:,} New</b><br><span style='color:#10B981;'>(CGR +{cgr_val:.2f}%)</span>"
            )
            fig_m_stack.add_annotation(
                x=m_row[month_col_lbl],
                y=bar_top_y,
                text=ann_text,
                showarrow=False,
                yanchor="bottom",
                yshift=5,
                align="center",
                font=dict(size=11, color="#F8FAFC")
            )

        max_y = (monthly_df["pelanggan_awal"] + monthly_df["pelanggan_baru"] + monthly_df["pelanggan_churn"]).max() if not monthly_df.empty else 25000
        apply_plotly_theme(fig_m_stack, height=460)
        fig_m_stack.update_layout(
            barmode="stack",
            yaxis=dict(
                title="Total Populasi Pelanggan (Akun)" if not is_en else "Total Customer Base (Accounts)",
                range=[0, max_y * 1.22]
            ),
            xaxis=dict(
                title=None,
                type="category",
                categoryorder="array",
                categoryarray=ordered_month_labels
            ),
            margin=dict(t=50, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_m_stack, use_container_width=True)

        st.markdown(
            "##### 🔢 Tabel Data Riil Pertumbuhan Pelanggan Bulanan & Rumus CGR (Jan – Nov 2026)"
            if not is_en
            else "##### 🔢 Real Data Table: Monthly Customer Growth & CGR Formula (Jan – Nov 2026)"
        )
        m_tbl_tab1 = pd.DataFrame({
            ("Bulan" if not is_en else "Month"): monthly_df[month_col_lbl],
            ("Pelanggan Awal" if not is_en else "Initial Customers"): monthly_df["pelanggan_awal"].apply(lambda v: f"{v:,}"),
            ("+ Pelanggan Baru" if not is_en else "+ New Customers"): monthly_df["pelanggan_baru"].apply(lambda v: f"+{v:,}"),
            ("- Berhenti (Churn)" if not is_en else "- Churned"): monthly_df["pelanggan_churn"].apply(lambda v: f"{v:,}"),
            ("= Pelanggan Akhir" if not is_en else "= Ending Customers"): monthly_df["pelanggan_akhir"].apply(lambda v: f"{v:,}"),
            ("CGR (Baru-Churn)/Awal" if not is_en else "Net CGR %"): monthly_df["cgr_net_pct"].apply(lambda v: f"+{v:.2f}%"),
            ("Rata-rata Baru / Hari" if not is_en else "Avg New / Day"): monthly_df["avg_daily_new"].apply(lambda v: f"+{v:.1f} akun/hari" if not is_en else f"+{v:.1f}/day"),
            ("Perubahan Baru vs Bulan Lalu" if not is_en else "MoM New Intake Change"): monthly_df["mom_disp_en" if is_en else "mom_disp_id"]
        })
        st.dataframe(m_tbl_tab1, use_container_width=True, hide_index=True)

    # Prepare filtered organic data (> init_cutoff) for monthly stacked breakdown by branch & category
    init_cutoff_dt = datetime.date(2026, 1, 8) if date_basis_col == "registration_date" else datetime.date(2026, 1, 10)
    df_org_monthly = cgr_summary["df_filtered"].copy()
    df_org_monthly = df_org_monthly[df_org_monthly[date_basis_col] > init_cutoff_dt].copy()
    df_org_monthly["ym_str"] = pd.to_datetime(df_org_monthly[date_basis_col]).dt.strftime("%Y-%m")
    df_org_monthly["month_lbl"] = df_org_monthly["ym_str"].map(ym_to_label).fillna(df_org_monthly["ym_str"])

    palette_vivid = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#F97316", "#64748B"]

    with tab_m_stack2:
        if not df_org_monthly.empty:
            div_view_mode = st.radio(
                "Mode Representasi Angka pada Bar Stack Cabang:" if not is_en else "Branch Stacked Bar Display Mode:",
                options=[
                    "📊 Jumlah Pelanggan Baru Riil (Volume + Total & % CGR)" if not is_en else "📊 Real New Customer Volume (+ Total & CGR %)",
                    "📐 Proporsi 100% per Bulan (Angka Riil + % Porsi Cabang)" if not is_en else "📐 100% Monthly Proportion (Real Count + % Share)"
                ],
                horizontal=True,
                key="cgr_tab2_div_mode"
            )
            is_div_100 = "100%" in div_view_mode

            m_div_df = (
                df_org_monthly.groupby(["ym_str", "month_lbl", "division_name"])["customer_id"]
                .nunique()
                .reset_index(name="new_customers")
            )
            m_div_df["month_total"] = m_div_df.groupby("ym_str")["new_customers"].transform("sum")
            m_div_df["share_pct"] = (m_div_df["new_customers"] / m_div_df["month_total"].replace(0, np.nan) * 100.0).fillna(0.0)
            m_div_df["cgr_pct"] = m_div_df["ym_str"].map(ym_to_cgr).fillna(0.0)

            div_order_list = (
                m_div_df.groupby("division_name")["new_customers"]
                .sum()
                .sort_values(ascending=False)
                .index.tolist()
            )
            if is_div_100:
                m_div_df["bar_text"] = m_div_df.apply(
                    lambda r: f"+{int(r['new_customers']):,} ({r['share_pct']:.0f}%)" if r["share_pct"] >= 6.0 else "",
                    axis=1
                )
                y_div_col = "share_pct"
            else:
                m_div_df["bar_text"] = m_div_df["new_customers"].apply(lambda v: f"+{v:,}" if v >= 55 else "")
                y_div_col = "new_customers"

            fig_m_div = px.bar(
                m_div_df,
                x="month_lbl",
                y=y_div_col,
                color="division_name",
                text="bar_text",
                category_orders={
                    "month_lbl": ordered_month_labels,
                    "division_name": div_order_list
                },
                custom_data=["division_name", "new_customers", "share_pct", "month_total", "cgr_pct"],
                labels={
                    "month_lbl": "Bulan" if not is_en else "Month",
                    y_div_col: (
                        ("Porsi Cabang (%)" if is_div_100 else "Pelanggan Baru Didapat (Akun Riil)")
                        if not is_en
                        else ("Branch Share (%)" if is_div_100 else "New Customers Acquired (Real Count)")
                    ),
                    "division_name": "Cabang" if not is_en else "Branch"
                },
                color_discrete_sequence=palette_vivid
            )
            fig_m_div.update_traces(
                textposition="inside",
                insidetextanchor="middle",
                textangle=0,
                constraintext="none",
                textfont=dict(size=11, color="#FFFFFF"),
                hovertemplate=(
                    "<b>%{x} — %{customdata[0]}</b><br>"
                    "Penambahan Pelanggan Baru: <b>+%{customdata[1]:,} pelanggan</b><br>"
                    "Porsi Cabang di Bulan Ini: <b>%{customdata[2]:.1f}%</b> (dari total +%{customdata[3]:,} baru)<br>"
                    "CGR Total Bulan Ini: <b>+%{customdata[4]:.2f}%</b><extra></extra>"
                    if not is_en else
                    "<b>%{x} — %{customdata[0]}</b><br>"
                    "New Customers Added: <b>+%{customdata[1]:,} accounts</b><br>"
                    "Branch Share This Month: <b>%{customdata[2]:.1f}%</b> (of +%{customdata[3]:,} total new)<br>"
                    "Monthly Total CGR: <b>+%{customdata[4]:.2f}%</b><extra></extra>"
                )
            )

            # Add top-of-bar annotations showing Total New Customers + CGR % for every month
            month_div_totals = m_div_df.groupby(["ym_str", "month_lbl"], as_index=False)["new_customers"].sum()
            for _, mt_row in month_div_totals.iterrows():
                ym_k = mt_row["ym_str"]
                m_lbl = mt_row["month_lbl"]
                tot_v = int(mt_row["new_customers"])
                cgr_v = float(ym_to_cgr.get(ym_k, 0.0))
                ann_div_txt = (
                    f"<b>+{tot_v:,} Baru</b><br><span style='color:#10B981;'>(CGR +{cgr_v:.2f}%)</span>"
                    if not is_en
                    else f"<b>+{tot_v:,} New</b><br><span style='color:#10B981;'>(CGR +{cgr_v:.2f}%)</span>"
                )
                fig_m_div.add_annotation(
                    x=m_lbl,
                    y=100.0 if is_div_100 else tot_v,
                    text=ann_div_txt,
                    showarrow=False,
                    yanchor="bottom",
                    yshift=5,
                    align="center",
                    font=dict(size=11, color="#F8FAFC")
                )

            max_div_m_y = 100.0 if is_div_100 else (month_div_totals["new_customers"].max() if not month_div_totals.empty else 2200)
            apply_plotly_theme(fig_m_div, height=480)
            fig_m_div.update_layout(
                barmode="stack",
                yaxis=dict(
                    title=(
                        ("Proporsi Pelanggan Baru per Cabang (%)" if is_div_100 else "Pelanggan Baru Didapat (Akun)")
                        if not is_en
                        else ("New Customer Share by Branch (%)" if is_div_100 else "New Customers Acquired (Accounts)")
                    ),
                    range=[0, max_div_m_y * 1.22]
                ),
                xaxis=dict(
                    title=None,
                    type="category",
                    categoryorder="array",
                    categoryarray=ordered_month_labels
                ),
                margin=dict(t=55, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_m_div, use_container_width=True)

            # Display Real Numbers Matrix Table (Cabang x Bulan) directly below the chart for 100% clarity
            st.markdown(
                "##### 🔢 Tabel Data Riil Penambahan Pelanggan Baru Bulanan per Cabang (Jan – Nov 2026)"
                if not is_en
                else "##### 🔢 Real Data Table: Monthly New Customers Added by Branch (Jan – Nov 2026)"
            )
            piv_div = m_div_df.pivot_table(
                index="division_name",
                columns="ym_str",
                values="new_customers",
                aggfunc="sum",
                fill_value=0
            ).reindex(div_order_list)

            ym_cols_sorted = sorted(piv_div.columns.tolist())
            piv_div_disp = pd.DataFrame()
            piv_div_disp["Cabang / Divisi" if not is_en else "Branch / Division"] = piv_div.index

            for ym_c in ym_cols_sorted:
                col_header = ym_to_label.get(ym_c, ym_c).replace(" (Berjalan)", "*").replace(" (MTD)", "*")
                piv_div_disp[col_header] = [f"+{int(v):,}" for v in piv_div[ym_c].values]

            row_totals_div = piv_div[ym_cols_sorted].sum(axis=1)
            grand_total_div = max(1, int(row_totals_div.sum()))
            piv_div_disp["Total Baru" if not is_en else "Total New"] = [f"+{int(v):,}" for v in row_totals_div.values]
            piv_div_disp["Porsi (%)" if not is_en else "Share (%)"] = [f"{(v / grand_total_div * 100.0):.1f}%" for v in row_totals_div.values]

            # Append Summary Rows: Total Pelanggan Baru & % CGR Bulanan
            tot_row_div = {"Cabang / Divisi" if not is_en else "Branch / Division": "TOTAL PELANGGAN BARU" if not is_en else "TOTAL NEW CUSTOMERS"}
            cgr_row_div = {"Cabang / Divisi" if not is_en else "Branch / Division": "PERSENTASE CGR BULANAN (%)" if not is_en else "MONTHLY CGR (%)"}
            for ym_c in ym_cols_sorted:
                col_header = ym_to_label.get(ym_c, ym_c).replace(" (Berjalan)", "*").replace(" (MTD)", "*")
                m_sum_v = int(piv_div[ym_c].sum())
                tot_row_div[col_header] = f"+{m_sum_v:,}"
                cgr_row_div[col_header] = f"+{ym_to_cgr.get(ym_c, 0.0):.2f}%"
            tot_row_div["Total Baru" if not is_en else "Total New"] = f"+{int(row_totals_div.sum()):,}"
            tot_row_div["Porsi (%)" if not is_en else "Share (%)"] = "100.0%"
            cgr_row_div["Total Baru" if not is_en else "Total New"] = f"+{cgr_net_pct:.2f}% (CGR)"
            cgr_row_div["Porsi (%)" if not is_en else "Share (%)"] = "—"

            piv_div_disp = pd.concat([piv_div_disp, pd.DataFrame([tot_row_div, cgr_row_div])], ignore_index=True)
            st.dataframe(piv_div_disp, use_container_width=True, hide_index=True)

    with tab_m_stack3:
        if not df_org_monthly.empty:
            cat_view_mode = st.radio(
                "Mode Representasi Angka pada Bar Stack Kategori:" if not is_en else "Category Stacked Bar Display Mode:",
                options=[
                    "📊 Jumlah Pelanggan Baru Riil (Volume + Total & % CGR)" if not is_en else "📊 Real New Customer Volume (+ Total & CGR %)",
                    "📐 Proporsi 100% per Bulan (Angka Riil + % Porsi Kategori)" if not is_en else "📐 100% Monthly Proportion (Real Count + % Share)"
                ],
                horizontal=True,
                key="cgr_tab3_cat_mode"
            )
            is_cat_100 = "100%" in cat_view_mode

            m_cat_df = (
                df_org_monthly.groupby(["ym_str", "month_lbl", "category_name"])["customer_id"]
                .nunique()
                .reset_index(name="new_customers")
            )
            m_cat_df["month_total"] = m_cat_df.groupby("ym_str")["new_customers"].transform("sum")
            m_cat_df["share_pct"] = (m_cat_df["new_customers"] / m_cat_df["month_total"].replace(0, np.nan) * 100.0).fillna(0.0)
            m_cat_df["cgr_pct"] = m_cat_df["ym_str"].map(ym_to_cgr).fillna(0.0)

            cat_order_list = (
                m_cat_df.groupby("category_name")["new_customers"]
                .sum()
                .sort_values(ascending=False)
                .index.tolist()
            )
            if is_cat_100:
                m_cat_df["bar_text"] = m_cat_df.apply(
                    lambda r: f"+{int(r['new_customers']):,} ({r['share_pct']:.0f}%)" if r["share_pct"] >= 6.0 else "",
                    axis=1
                )
                y_cat_col = "share_pct"
            else:
                m_cat_df["bar_text"] = m_cat_df["new_customers"].apply(lambda v: f"+{v:,}" if v >= 55 else "")
                y_cat_col = "new_customers"

            fig_m_cat = px.bar(
                m_cat_df,
                x="month_lbl",
                y=y_cat_col,
                color="category_name",
                text="bar_text",
                category_orders={
                    "month_lbl": ordered_month_labels,
                    "category_name": cat_order_list
                },
                custom_data=["category_name", "new_customers", "share_pct", "month_total", "cgr_pct"],
                labels={
                    "month_lbl": "Bulan" if not is_en else "Month",
                    y_cat_col: (
                        ("Porsi Kategori (%)" if is_cat_100 else "Pelanggan Baru Didapat (Akun Riil)")
                        if not is_en
                        else ("Category Share (%)" if is_cat_100 else "New Customers Acquired (Real Count)")
                    ),
                    "category_name": "Kategori Pelanggan" if not is_en else "Customer Category"
                },
                color_discrete_sequence=palette_vivid
            )
            fig_m_cat.update_traces(
                textposition="inside",
                insidetextanchor="middle",
                textangle=0,
                constraintext="none",
                textfont=dict(size=11, color="#FFFFFF"),
                hovertemplate=(
                    "<b>%{x} — %{customdata[0]}</b><br>"
                    "Penambahan Pelanggan Baru: <b>+%{customdata[1]:,} pelanggan</b><br>"
                    "Porsi Kategori di Bulan Ini: <b>%{customdata[2]:.1f}%</b> (dari total +%{customdata[3]:,} baru)<br>"
                    "CGR Total Bulan Ini: <b>+%{customdata[4]:.2f}%</b><extra></extra>"
                    if not is_en else
                    "<b>%{x} — %{customdata[0]}</b><br>"
                    "New Customers Added: <b>+%{customdata[1]:,} accounts</b><br>"
                    "Category Share This Month: <b>%{customdata[2]:.1f}%</b> (of +%{customdata[3]:,} total new)<br>"
                    "Monthly Total CGR: <b>+%{customdata[4]:.2f}%</b><extra></extra>"
                )
            )

            # Add top-of-bar annotations showing Total New Customers + CGR % for every month
            month_cat_totals = m_cat_df.groupby(["ym_str", "month_lbl"], as_index=False)["new_customers"].sum()
            for _, mt_row in month_cat_totals.iterrows():
                ym_k = mt_row["ym_str"]
                m_lbl = mt_row["month_lbl"]
                tot_v = int(mt_row["new_customers"])
                cgr_v = float(ym_to_cgr.get(ym_k, 0.0))
                ann_cat_txt = (
                    f"<b>+{tot_v:,} Baru</b><br><span style='color:#10B981;'>(CGR +{cgr_v:.2f}%)</span>"
                    if not is_en
                    else f"<b>+{tot_v:,} New</b><br><span style='color:#10B981;'>(CGR +{cgr_v:.2f}%)</span>"
                )
                fig_m_cat.add_annotation(
                    x=m_lbl,
                    y=100.0 if is_cat_100 else tot_v,
                    text=ann_cat_txt,
                    showarrow=False,
                    yanchor="bottom",
                    yshift=5,
                    align="center",
                    font=dict(size=11, color="#F8FAFC")
                )

            max_cat_m_y = 100.0 if is_cat_100 else (month_cat_totals["new_customers"].max() if not month_cat_totals.empty else 2200)
            apply_plotly_theme(fig_m_cat, height=480)
            fig_m_cat.update_layout(
                barmode="stack",
                yaxis=dict(
                    title=(
                        ("Proporsi Pelanggan Baru per Kategori (%)" if is_cat_100 else "Pelanggan Baru Didapat (Akun)")
                        if not is_en
                        else ("New Customer Share by Category (%)" if is_cat_100 else "New Customers Acquired (Accounts)")
                    ),
                    range=[0, max_cat_m_y * 1.22]
                ),
                xaxis=dict(
                    title=None,
                    type="category",
                    categoryorder="array",
                    categoryarray=ordered_month_labels
                ),
                margin=dict(t=55, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_m_cat, use_container_width=True)

            # Display Real Numbers Matrix Table (Kategori x Bulan) directly below the chart for 100% clarity
            st.markdown(
                "##### 🔢 Tabel Data Riil Penambahan Pelanggan Baru Bulanan per Kategori (Jan – Nov 2026)"
                if not is_en
                else "##### 🔢 Real Data Table: Monthly New Customers Added by Category (Jan – Nov 2026)"
            )
            piv_cat = m_cat_df.pivot_table(
                index="category_name",
                columns="ym_str",
                values="new_customers",
                aggfunc="sum",
                fill_value=0
            ).reindex(cat_order_list)

            ym_cols_sorted_c = sorted(piv_cat.columns.tolist())
            piv_cat_disp = pd.DataFrame()
            piv_cat_disp["Kategori Pelanggan" if not is_en else "Customer Category"] = piv_cat.index

            for ym_c in ym_cols_sorted_c:
                col_header = ym_to_label.get(ym_c, ym_c).replace(" (Berjalan)", "*").replace(" (MTD)", "*")
                piv_cat_disp[col_header] = [f"+{int(v):,}" if int(v) > 0 else "0" for v in piv_cat[ym_c].values]

            row_totals_cat = piv_cat[ym_cols_sorted_c].sum(axis=1)
            grand_total_cat = max(1, int(row_totals_cat.sum()))
            piv_cat_disp["Total Baru" if not is_en else "Total New"] = [f"+{int(v):,}" for v in row_totals_cat.values]
            piv_cat_disp["Porsi (%)" if not is_en else "Share (%)"] = [f"{(v / grand_total_cat * 100.0):.1f}%" for v in row_totals_cat.values]

            # Append Summary Rows: Total Pelanggan Baru & % CGR Bulanan
            tot_row_cat = {"Kategori Pelanggan" if not is_en else "Customer Category": "TOTAL PELANGGAN BARU" if not is_en else "TOTAL NEW CUSTOMERS"}
            cgr_row_cat = {"Kategori Pelanggan" if not is_en else "Customer Category": "PERSENTASE CGR BULANAN (%)" if not is_en else "MONTHLY CGR (%)"}
            for ym_c in ym_cols_sorted_c:
                col_header = ym_to_label.get(ym_c, ym_c).replace(" (Berjalan)", "*").replace(" (MTD)", "*")
                m_sum_v = int(piv_cat[ym_c].sum())
                tot_row_cat[col_header] = f"+{m_sum_v:,}"
                cgr_row_cat[col_header] = f"+{ym_to_cgr.get(ym_c, 0.0):.2f}%"
            tot_row_cat["Total Baru" if not is_en else "Total New"] = f"+{int(row_totals_cat.sum()):,}"
            tot_row_cat["Porsi (%)" if not is_en else "Share (%)"] = "100.0%"
            cgr_row_cat["Total Baru" if not is_en else "Total New"] = f"+{cgr_net_pct:.2f}% (CGR)"
            cgr_row_cat["Porsi (%)" if not is_en else "Share (%)"] = "—"

            piv_cat_disp = pd.concat([piv_cat_disp, pd.DataFrame([tot_row_cat, cgr_row_cat])], ignore_index=True)
            st.dataframe(piv_cat_disp, use_container_width=True, hide_index=True)

    # Compute highlights from monthly_df for Layman Summary
    completed_months = monthly_df[monthly_df["year_month"] < "2026-11"]
    best_m_row = completed_months.sort_values(by="cgr_net_pct", ascending=False).iloc[0] if not completed_months.empty else monthly_df.iloc[0]
    organic_months = completed_months[completed_months["year_month"] >= "2026-03"]
    best_org_row = organic_months.sort_values(by="cgr_net_pct", ascending=False).iloc[0] if not organic_months.empty else best_m_row
    latest_full_row = completed_months.iloc[-1] if not completed_months.empty else monthly_df.iloc[-1]

    render_layman_summary_box(
        title="Tren Pertumbuhan Basis Pelanggan Bulanan" if not is_en else "Monthly Customer Base Expansion Trend",
        plain_summary=(
            f"Dari grafik batang bertumpuk (Bar Stack) di atas, terlihat jumlah pelanggan kita naik tanpa henti dari <b>{monthly_df.iloc[0]['pelanggan_awal']:,} pelanggan</b> di awal Januari menjadi <b>{monthly_df.iloc[-1]['pelanggan_akhir']:,} pelanggan</b> di bulan November. "
            f"Lonjakan tertinggi terjadi pada <b>{best_m_row['month_label_id']}</b> (CGR <b>+{best_m_row['cgr_net_pct']:.2f}%</b> / +{best_m_row['pelanggan_baru']:,} akun, didorong penambahan basis cabang Cianjur), sedangkan untuk pertumbuhan murni harian tertinggi terjadi di <b>{best_org_row['month_label_id']}</b> (CGR <b>+{best_org_row['cgr_net_pct']:.2f}%</b> / +{best_org_row['pelanggan_baru']:,} pelanggan baru)."
            if not is_en
            else f"The Stacked Bar chart shows our customer base climbing steadily from <b>{monthly_df.iloc[0]['pelanggan_awal']:,} accounts</b> in early January to <b>{monthly_df.iloc[-1]['pelanggan_akhir']:,} accounts</b> in November. "
                 f"Peak growth occurred in <b>{best_m_row['month_label_en']}</b> (CGR <b>+{best_m_row['cgr_net_pct']:.2f}%</b>), while the strongest pure organic month was <b>{best_org_row['month_label_en']}</b> (CGR <b>+{best_org_row['cgr_net_pct']:.2f}%</b> / +{best_org_row['pelanggan_baru']:,} new accounts)."
        ),
        key_takeaway=(
            f"Pada bulan penuh terakhir (<b>{latest_full_row['month_label_id']}</b>), pertumbuhan pelanggan kita kembali menguat ke <b>+{latest_full_row['cgr_net_pct']:.2f}%</b> (<b>+{latest_full_row['pelanggan_baru']:,} pelanggan baru</b>, naik dibandingkan bulan September yang berjumlah 805 pelanggan). Ini menandakan daya tarik akuisisi Cipta Grafika sedang berada di jalur positif menjelang akhir tahun."
            if not is_en
            else f"In the most recent completed month (<b>{latest_full_row['month_label_en']}</b>), CGR rebounded to <b>+{latest_full_row['cgr_net_pct']:.2f}%</b> (<b>+{latest_full_row['pelanggan_baru']:,} new customers</b>, up from September's 805). This signals positive momentum heading into year-end."
        ),
        recommended_action=(
            "Pertahankan ritme promosi akuisisi minimal 850–1.000 pelanggan baru per bulan seperti di bulan April–Mei dan Oktober agar target pertumbuhan tahunan di atas 70% tercapai dengan mudah."
            if not is_en
            else "Maintain acquisition momentum at 850–1,000+ new customers per month (as achieved in Apr–May and Oct) to easily surpass 70% annual customer growth."
        ),
        formula_note=(
            "Setiap batang = <code>Pelanggan Awal Bulan (Biru) + Pelanggan Baru Bulan Itu (Hijau) − Pelanggan Berhenti (Merah) = Pelanggan Akhir Bulan</code>."
            if not is_en
            else "Each stacked bar = <code>Initial Monthly Base (Blue) + New Monthly Intake (Green) − Churned (Red) = Ending Monthly Base</code>."
        ),
        lang_code=lang_code,
        accent_color="#3B82F6"
    )

st.markdown("---")

# -------------------------------------------------------------
# 8. INSIGHT 2: DONUT CHARTS — PROPORTION OF CUSTOMER GROWTH SOURCES
# -------------------------------------------------------------
cat_cgr_df = compute_cgr_by_dimension(
    df=df_customers,
    group_col="category_name",
    start_date=p_start,
    end_date=p_end,
    division=norm_division,
    category=norm_category,
    date_basis=date_basis_col
)

div_cgr_df = compute_cgr_by_dimension(
    df=df_customers,
    group_col="division_name",
    start_date=p_start,
    end_date=p_end,
    division=norm_division,
    category=norm_category,
    date_basis=date_basis_col
)

render_section_info(
    title=(
        "Insight 2: Grafik Donat (Donut Chart) Proporsi Sumber Pertumbuhan Pelanggan"
        if not is_en
        else "Insight 2: Donut Charts — Customer Growth Source Proportions"
    ),
    subtitle=(
        "Membantu User memahami porsi kue pertumbuhan pelanggan: berasal dari segmen mana, cabang mana, dan bagaimana komposisi akhir pelanggan kita."
        if not is_en
        else "Helps anyone visualize the customer growth pie: which segments and branches drive new customers, and how our ending customer base is composed."
    ),
    what_it_shows=(
        "3 Grafik Donat: (1) Porsi Pelanggan Baru per Kategori, (2) Porsi Pelanggan Baru per Cabang, dan (3) Komposisi Pelanggan Akhir Periode (Pelanggan Lama Bertahan vs Pelanggan Baru)."
        if not is_en
        else "3 Donut Charts: (1) New Customers by Category, (2) New Customers by Branch, and (3) Ending Base Composition (Retained Base vs New Intake)."
    ),
    why_important=(
        "Grafik donat sangat mudah dibaca siapa saja untuk melihat siapa penyumbang terbesar dan apakah kita terlalu bergantung pada satu kelompok pelanggan saja."
        if not is_en
        else "Donut charts make it effortless to spot the largest contributors and check if growth relies too heavily on a single segment or branch."
    ),
    simple_insight=(
        "Potongan donat paling besar menunjukkan penyumbang utama pertumbuhan pelanggan Cipta Grafika pada periode ini."
        if not is_en
        else "The largest slice of the donut reveals the primary engine of Cipta Grafika's customer growth in this period."
    ),
    icon="🍩",
    lang_code=lang_code
)

donut_col1, donut_col2, donut_col3 = st.columns(3)

with donut_col1:
    st.markdown(
        "##### 🍩 1. Porsi Pelanggan Baru per Kategori"
        if not is_en
        else "##### 🍩 1. New Customers by Category"
    )
    if not cat_cgr_df.empty and cat_cgr_df["pelanggan_baru"].sum() > 0:
        valid_cat_donut = cat_cgr_df[cat_cgr_df["pelanggan_baru"] > 0]
        fig_d_cat = px.pie(
            valid_cat_donut,
            names="group_name",
            values="pelanggan_baru",
            hole=0.48,
            color_discrete_sequence=palette_vivid
        )
        fig_d_cat.update_traces(
            textinfo="percent+label",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Pelanggan Baru: <b>%{value:,} akun (%{percent})</b><extra></extra>"
        )
        apply_plotly_theme(fig_d_cat, height=320)
        fig_d_cat.update_layout(showlegend=False, margin=dict(t=15, b=15, l=15, r=15))
        st.plotly_chart(fig_d_cat, use_container_width=True)
    else:
        st.caption("Tidak ada data pelanggan baru." if not is_en else "No new customer data.")

with donut_col2:
    st.markdown(
        "##### 🍩 2. Porsi Pelanggan Baru per Cabang"
        if not is_en
        else "##### 🍩 2. New Customers by Branch"
    )
    if not div_cgr_df.empty and div_cgr_df["pelanggan_baru"].sum() > 0:
        valid_div_donut = div_cgr_df[div_cgr_df["pelanggan_baru"] > 0]
        fig_d_div = px.pie(
            valid_div_donut,
            names="group_name",
            values="pelanggan_baru",
            hole=0.48,
            color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"]
        )
        fig_d_div.update_traces(
            textinfo="percent+label",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Pelanggan Baru: <b>%{value:,} akun (%{percent})</b><extra></extra>"
        )
        apply_plotly_theme(fig_d_div, height=320)
        fig_d_div.update_layout(showlegend=False, margin=dict(t=15, b=15, l=15, r=15))
        st.plotly_chart(fig_d_div, use_container_width=True)
    else:
        st.caption("Tidak ada data cabang." if not is_en else "No branch data.")

with donut_col3:
    st.markdown(
        "##### 🍩 3. Komposisi Populasi Akhir Periode"
        if not is_en
        else "##### 🍩 3. Ending Customer Base Mix"
    )
    retained_base = max(0, awal_cnt - churn_cnt)
    comp_df = pd.DataFrame({
        "Komponen": (
            ["Pelanggan Awal Bertahan", "Pelanggan Baru Didapat", "Pelanggan Berhenti (Churn)"]
            if not is_en
            else ["Retained Initial Base", "New Customers Acquired", "Churned / Left"]
        ),
        "Jumlah": [retained_base, baru_cnt, churn_cnt]
    })
    comp_df = comp_df[comp_df["Jumlah"] > 0]
    if not comp_df.empty:
        fig_d_comp = px.pie(
            comp_df,
            names="Komponen",
            values="Jumlah",
            hole=0.48,
            color="Komponen",
            color_discrete_map={
                "Pelanggan Awal Bertahan": "#3B82F6",
                "Retained Initial Base": "#3B82F6",
                "Pelanggan Baru Didapat": "#10B981",
                "New Customers Acquired": "#10B981",
                "Pelanggan Berhenti (Churn)": "#EF4444",
                "Churned / Left": "#EF4444"
            }
        )
        fig_d_comp.update_traces(
            textinfo="percent+label",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Jumlah: <b>%{value:,} pelanggan (%{percent})</b><extra></extra>"
        )
        apply_plotly_theme(fig_d_comp, height=320)
        fig_d_comp.update_layout(showlegend=False, margin=dict(t=15, b=15, l=15, r=15))
        st.plotly_chart(fig_d_comp, use_container_width=True)

# Layman summary for Insight 2 (Donut Charts)
if not cat_cgr_df.empty and not div_cgr_df.empty and baru_cnt > 0:
    top_cat_row = cat_cgr_df.iloc[0]
    sec_cat_row = cat_cgr_df.iloc[1] if len(cat_cgr_df) > 1 else top_cat_row
    top_div_row = div_cgr_df.iloc[0]
    sec_div_row = div_cgr_df.iloc[1] if len(div_cgr_df) > 1 else top_div_row
    new_share_in_end = (baru_cnt / max(1, akhir_cnt)) * 100.0

    render_layman_summary_box(
        title="Proporsi Sumber Pertumbuhan Pelanggan (Donut Chart)" if not is_en else "Customer Growth Source Proportions (Donut Chart)",
        plain_summary=(
            f"Dari <b>{baru_cnt:,} pelanggan baru</b> yang masuk pada periode ini, porsi terbesar berasal dari segmen <b>{top_cat_row['group_name']}</b> sebanyak <b>{top_cat_row['pelanggan_baru']:,} akun ({top_cat_row['share_baru_pct']:.1f}%)</b>, disusul oleh <b>{sec_cat_row['group_name']}</b> sebanyak <b>{sec_cat_row['pelanggan_baru']:,} akun ({sec_cat_row['share_baru_pct']:.1f}%)</b>. "
            f"Dari sisi cabang, penyumbang terbesar adalah <b>{top_div_row['group_name']} ({top_div_row['share_baru_pct']:.1f}%)</b> dan <b>{sec_div_row['group_name']} ({sec_div_row['share_baru_pct']:.1f}%)</b>."
            if not is_en
            else f"Out of <b>{baru_cnt:,} new customers</b> acquired in this period, the largest slice comes from <b>{top_cat_row['group_name']}</b> with <b>{top_cat_row['pelanggan_baru']:,} accounts ({top_cat_row['share_baru_pct']:.1f}%)</b>, followed by <b>{sec_cat_row['group_name']} ({sec_cat_row['share_baru_pct']:.1f}%)</b>. "
                 f"By branch, <b>{top_div_row['group_name']} ({top_div_row['share_baru_pct']:.1f}%)</b> and <b>{sec_div_row['group_name']} ({sec_div_row['share_baru_pct']:.1f}%)</b> lead intake."
        ),
        key_takeaway=(
            f"Donat ke-3 memperlihatkan bahwa dari total <b>{akhir_cnt:,} pelanggan akhir periode</b>, sebesar <b>{new_share_in_end:.1f}% adalah wajah-wajah pelanggan baru</b> yang didapat pada periode ini, sedangkan <b>{100 - new_share_in_end:.1f}% adalah pelanggan lama yang tetap bertahan</b>. Namun, karena <b>{top_cat_row['group_name']}</b> mendominasi lebih dari separuh pelanggan baru, bisnis perlu terus mendorong segmen <b>UMKM, AGEN, dan INSTANSI</b> agar kue pertumbuhan semakin seimbang."
            if not is_en
            else f"The 3rd donut reveals that out of <b>{akhir_cnt:,} ending customers</b>, <b>{new_share_in_end:.1f}% are newly acquired accounts</b> from this period while <b>{100 - new_share_in_end:.1f}% are retained existing customers</b>. Since <b>{top_cat_row['group_name']}</b> accounts for over half of new intake, expanding B2B segments (UMKM, AGEN, INSTANSI) will balance portfolio risk."
        ),
        recommended_action=(
            f"Jadikan metode penerimaan pelanggan di <b>{top_div_row['group_name']}</b> sebagai contoh bagi cabang lain, dan buat paket promosi khusus untuk segmen <b>{sec_cat_row['group_name']}</b> agar kontribusinya semakin membesar."
            if not is_en
            else f"Replicate the onboarding workflow of <b>{top_div_row['group_name']}</b> across smaller branches, and launch targeted bundles for <b>{sec_cat_row['group_name']}</b> to diversify growth."
        ),
        formula_note=(
            f"Total Kue Donat 3 = <code>PelangganAkhir ({akhir_cnt:,}) = Pelanggan Awal Bertahan ({retained_base:,}) + Pelanggan Baru ({baru_cnt:,})</code>."
        ),
        lang_code=lang_code,
        accent_color="#F59E0B"
    )

st.markdown("---")

# -------------------------------------------------------------
# 9. INSIGHT 3: STACKED BAR CHART — CROSS-ANALYSIS OF BRANCH × CATEGORY
# -------------------------------------------------------------
render_section_info(
    title=(
        "Insight 3: Grafik Bar Bertumpuk (Bar Stack) Pertumbuhan Silang Cabang × Kategori Pelanggan"
        if not is_en
        else "Insight 3: Cross-Dimensional Stacked Bar — Branch × Customer Category Growth"
    ),
    subtitle=(
        "Membedah isi perut pertumbuhan setiap cabang: segmen pelanggan apa yang paling banyak masuk di masing-masing cabang?"
        if not is_en
        else "Dissecting each branch's growth composition: which customer segments drive growth inside each branch?"
    ),
    what_it_shows=(
        "Grafik Bar Stack yang bisa dilihat dalam Angka Jumlah Pelanggan (Volume) maupun Proporsi Persentase (100% Bar Stack) per Cabang dan per Kategori."
        if not is_en
        else "Stacked Bar chart viewable by Absolute Customer Volume or 100% Relative Share across Branches and Categories."
    ),
    why_important=(
        "Memudahkan User membandingkan karakter tiap cabang (misal cabang mana yang kuat di UMKM vs cabang mana yang kuat di AGEN atau END USER)."
        if not is_en
        else "Makes it easy for non-technical users to compare the DNA of each branch (e.g., which branch excels in UMKM vs AGEN or END USER)."
    ),
    simple_insight=(
        "Pilih '100% Proporsi Segmen' untuk melihat perbandingan persentase isi segmen di tiap cabang secara sejajar."
        if not is_en
        else "Toggle '100% Relative Proportion' to compare segment mix across branches on an equal 100% scale."
    ),
    icon="🏢",
    lang_code=lang_code
)

df_baru_period = cgr_summary["df_baru"]
df_akhir_period = cgr_summary["df_filtered"]
df_akhir_active = df_akhir_period[(~df_akhir_period["is_churned"]) & (df_akhir_period[date_basis_col] <= eff_end)]

if not df_baru_period.empty:
    sc1, sc2, sc3 = st.columns([1.5, 1.5, 1.2])
    with sc1:
        stack_metric_mode = st.radio(
            "Data yang Ditampilkan:" if not is_en else "Metric to Display:",
            options=[
                "Pelanggan Baru Didapat (Periode Ini)" if not is_en else "New Customers Acquired (Current Period)",
                "Total Pelanggan Aktif Akhir Periode" if not is_en else "Total Ending Active Customers"
            ],
            horizontal=True,
            key="cgr_stack_metric_mode"
        )
    with sc2:
        stack_orient_mode = st.radio(
            "Kelompok Sumbu Utama:" if not is_en else "Primary Axis Grouping:",
            options=[
                "Per Cabang (Ditumpuk per Kategori)" if not is_en else "By Branch (Stacked by Category)",
                "Per Kategori (Ditumpuk per Cabang)" if not is_en else "By Category (Stacked by Branch)"
            ],
            horizontal=True,
            key="cgr_stack_orient_mode"
        )
    with sc3:
        stack_norm_mode = st.radio(
            "Mode Tumpukan Bar:" if not is_en else "Stacking Mode:",
            options=[
                "Jumlah Angka (Volume)" if not is_en else "Volume (Count)",
                "100% Proporsi (%)" if not is_en else "100% Share (%)"
            ],
            horizontal=True,
            key="cgr_stack_norm_mode"
        )

    source_stack_df = df_baru_period if ("Baru" in stack_metric_mode or "New" in stack_metric_mode) else df_akhir_active
    cross_df = (
        source_stack_df.groupby(["division_name", "category_name"])["customer_id"]
        .nunique()
        .reset_index(name="customer_count")
    )

    is_100_pct = ("100%" in stack_norm_mode)
    by_branch_axis = ("Per Cabang" in stack_orient_mode or "By Branch" in stack_orient_mode)

    if by_branch_axis:
        totals_order = cross_df.groupby("division_name")["customer_count"].sum().sort_values(ascending=False).index.tolist()
        cross_df["group_total"] = cross_df.groupby("division_name")["customer_count"].transform("sum")
        cross_df["pct_share"] = (cross_df["customer_count"] / cross_df["group_total"] * 100.0).round(1)
        y_col = "pct_share" if is_100_pct else "customer_count"

        fig_cross = px.bar(
            cross_df,
            x="division_name",
            y=y_col,
            color="category_name",
            category_orders={"division_name": totals_order},
            text=cross_df["pct_share"].apply(lambda v: f"{v:.1f}%" if v >= 6 else "") if is_100_pct else cross_df["customer_count"].apply(lambda v: f"{v:,}" if v >= 30 else ""),
            labels={
                "division_name": "Cabang / Divisi" if not is_en else "Branch / Division",
                y_col: ("Proporsi Kategori (%)" if is_100_pct else "Jumlah Pelanggan") if not is_en else ("Category Share (%)" if is_100_pct else "Customer Count"),
                "category_name": "Kategori Pelanggan" if not is_en else "Customer Category"
            },
            color_discrete_sequence=palette_vivid,
            custom_data=["customer_count", "pct_share", "group_total"]
        )
        fig_cross.update_traces(
            hovertemplate=(
                "<b>%{x} — %{fullData.name}</b><br>"
                "Jumlah Pelanggan: <b>%{customdata[0]:,} akun</b><br>"
                "Porsi di Cabang Ini: <b>%{customdata[1]:.1f}%</b> (dari total %{customdata[2]:,})<extra></extra>"
            )
        )
    else:
        totals_order = cross_df.groupby("category_name")["customer_count"].sum().sort_values(ascending=False).index.tolist()
        cross_df["group_total"] = cross_df.groupby("category_name")["customer_count"].transform("sum")
        cross_df["pct_share"] = (cross_df["customer_count"] / cross_df["group_total"] * 100.0).round(1)
        y_col = "pct_share" if is_100_pct else "customer_count"

        fig_cross = px.bar(
            cross_df,
            x="category_name",
            y=y_col,
            color="division_name",
            category_orders={"category_name": totals_order},
            text=cross_df["pct_share"].apply(lambda v: f"{v:.1f}%" if v >= 8 else "") if is_100_pct else cross_df["customer_count"].apply(lambda v: f"{v:,}" if v >= 30 else ""),
            labels={
                "category_name": "Kategori Pelanggan" if not is_en else "Customer Category",
                y_col: ("Proporsi Cabang (%)" if is_100_pct else "Jumlah Pelanggan") if not is_en else ("Branch Share (%)" if is_100_pct else "Customer Count"),
                "division_name": "Cabang / Divisi" if not is_en else "Branch / Division"
            },
            color_discrete_sequence=palette_vivid,
            custom_data=["customer_count", "pct_share", "group_total"]
        )
        fig_cross.update_traces(
            hovertemplate=(
                "<b>%{x} — %{fullData.name}</b><br>"
                "Jumlah Pelanggan: <b>%{customdata[0]:,} akun</b><br>"
                "Porsi di Kategori Ini: <b>%{customdata[1]:.1f}%</b> (dari total %{customdata[2]:,})<extra></extra>"
            )
        )

    apply_plotly_theme(fig_cross, height=420)
    fig_cross.update_layout(barmode="stack")
    st.plotly_chart(fig_cross, use_container_width=True)

    # Identify top branch x category pair for layman summary
    top_pair = cross_df.sort_values(by="customer_count", ascending=False).iloc[0]
    non_enduser_df = cross_df[cross_df["category_name"] != "END USER"].sort_values(by="customer_count", ascending=False)
    top_b2b_pair = non_enduser_df.iloc[0] if not non_enduser_df.empty else top_pair

    render_layman_summary_box(
        title="Sebaran Pertumbuhan Cabang & Segmen (Bar Stack)" if not is_en else "Branch × Segment Stacked Bar Insights",
        plain_summary=(
            f"Grafik batang bertumpuk (Bar Stack) di atas memperlihatkan bahwa kombinasi terkuat ada pada cabang <b>{top_pair['division_name']}</b> untuk kategori <b>{top_pair['category_name']}</b> sebanyak <b>{top_pair['customer_count']:,} pelanggan ({top_pair['pct_share']:.1f}% dari cabang tersebut)</b>. "
            f"Sementara untuk segmen non-perorangan (usaha/kemitraan), kantong pertumbuhan terbesar berada di <b>{top_b2b_pair['division_name']} — kategori {top_b2b_pair['category_name']} ({top_b2b_pair['customer_count']:,} pelanggan)</b>."
            if not is_en
            else f"The Stacked Bar chart shows the strongest overall combination is <b>{top_pair['division_name']} × {top_pair['category_name']}</b> with <b>{top_pair['customer_count']:,} accounts ({top_pair['pct_share']:.1f}% share)</b>. "
                 f"Among business/partnership segments (excluding End User), the largest pocket of growth is <b>{top_b2b_pair['division_name']} × {top_b2b_pair['category_name']} ({top_b2b_pair['customer_count']:,} accounts)</b>."
        ),
        key_takeaway=(
            "Setiap cabang memiliki kekuatan segmen yang berbeda: <b>Cipta Digital</b> sangat unggul dalam menjaring pelaku <b>UMKM & END USER</b>, sedangkan <b>Cipta Purwakarta, Cipta Digital, dan Cipta Graha</b> menjadi motor penggerak baru bagi segmen <b>AGEN</b> di kuartal terakhir."
            if not is_en
            else "Each branch exhibits distinct segment strengths: <b>Cipta Digital</b> excels at capturing <b>UMKM & END USER</b> accounts, while <b>Cipta Purwakarta, Cipta Digital, and Cipta Graha</b> have become major engines for <b>AGEN</b> resellers in recent months."
        ),
        recommended_action=(
            "Gunakan tombol '100% Proporsi (%)' di atas grafik untuk melihat cabang mana yang porsi UMKM atau AGEN-nya masih tipis, lalu terapkan program akuisisi kemitraan dari cabang terkuat ke cabang tersebut."
            if not is_en
            else "Use the '100% Share (%)' toggle above the chart to spot branches with thin UMKM or AGEN slices, then roll out proven reseller/SME acquisition programs to those branches."
        ),
        lang_code=lang_code,
        accent_color="#8B5CF6"
    )

st.markdown("---")

# -------------------------------------------------------------
# 10. INSIGHT 4: CGR COMPARISON BY SEGMENT & BRANCH (STACKED BAR + TABLE)
# -------------------------------------------------------------
render_section_info(
    title=(
        "Insight 4: Perbandingan Customer Growth Rate (CGR %) Antar-Kategori & Antar-Cabang"
        if not is_en
        else "Insight 4: Customer Growth Rate (CGR %) Comparison by Category & Branch"
    ),
    subtitle=(
        "Mengukur laju persentase pertumbuhan CGR = ((Pelanggan Baru - Churn) / Pelanggan Awal) × 100% di setiap segmen dan cabang."
        if not is_en
        else "Comparing CGR % = ((New Customers - Churn) / Initial Customers) × 100% across every customer category and branch."
    ),
    what_it_shows=(
        "Perbandingan Bar Stack (Pelanggan Awal + Pelanggan Baru) beserta peringkat CGR (%) dan tabel rincian rumus untuk setiap Kategori & Cabang."
        if not is_en
        else "Stacked Bar comparison (Initial Base + New Intake) alongside CGR (%) rankings and complete formula breakdown tables."
    ),
    why_important=(
        "Segmen dengan jumlah pelanggan awal kecil bisa tumbuh ratusan persen (CGR tinggi), sedangkan segmen besar tumbuh stabil namun menyumbang jumlah orang terbanyak."
        if not is_en
        else "Smaller initial segments can post triple-digit CGR %, while large core segments grow at a steady percentage but contribute the most absolute customers."
    ),
    simple_insight=(
        "Lihat kedua sisi sekaligus: Persentase CGR (%) menunjukkan kecepatan ekspansi, sedangkan Jumlah Pelanggan Baru menunjukkan besarnya volume yang didapat."
        if not is_en
        else "Look at both sides together: CGR % shows expansion speed, while New Customer Volume shows absolute scale."
    ),
    icon="📈",
    lang_code=lang_code
)

col_cgr_cat, col_cgr_div = st.columns(2)

with col_cgr_cat:
    st.markdown(
        "##### 👥 Pertumbuhan Basis per Kategori Pelanggan (Awal + Baru & CGR %)"
        if not is_en
        else "##### 👥 Customer Base Growth by Category (Initial + New & CGR %)"
    )
    if not cat_cgr_df.empty:
        cat_plot_df = cat_cgr_df.sort_values(by="pelanggan_akhir", ascending=True).copy()
        fig_cgr_cat = go.Figure()
        fig_cgr_cat.add_trace(go.Bar(
            y=cat_plot_df["group_name"],
            x=cat_plot_df["pelanggan_awal"],
            name="Pelanggan Awal" if not is_en else "Initial Base",
            orientation="h",
            marker_color="#3B82F6",
            hovertemplate="<b>%{y}</b><br>Pelanggan Awal: <b>%{x:,}</b><extra></extra>"
        ))
        cat_bar_labels = [
            f"+{b:,} Baru (CGR +{c:.1f}%)" if not is_en else f"+{b:,} New (CGR +{c:.1f}%)"
            for b, c in zip(cat_plot_df["pelanggan_baru"], cat_plot_df["cgr_net_pct"])
        ]
        fig_cgr_cat.add_trace(go.Bar(
            y=cat_plot_df["group_name"],
            x=cat_plot_df["pelanggan_baru"],
            name="+ Pelanggan Baru" if not is_en else "+ New Customers",
            orientation="h",
            marker_color="#10B981",
            text=cat_bar_labels,
            textposition="outside",
            cliponaxis=False,
            customdata=cat_plot_df[["pelanggan_awal", "pelanggan_akhir", "cgr_net_pct", "share_baru_pct"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Pelanggan Awal: <b>%{customdata[0]:,}</b><br>"
                "+ Pelanggan Baru: <b>+%{x:,}</b> (%{customdata[3]:.1f}% dari total baru)<br>"
                "= Pelanggan Akhir: <b>%{customdata[1]:,}</b><br>"
                "CGR (Baru−Churn)/Awal: <b>+%{customdata[2]:.2f}%</b><extra></extra>"
            )
        ))
        max_cat_x = cat_plot_df["pelanggan_akhir"].max() if not cat_plot_df.empty else 15000
        apply_plotly_theme(fig_cgr_cat, height=380)
        fig_cgr_cat.update_layout(
            barmode="stack",
            xaxis=dict(title="Jumlah Pelanggan" if not is_en else "Customers", range=[0, max_cat_x * 1.32]),
            yaxis=dict(title=None),
            margin=dict(r=110, t=35, b=20, l=10)
        )
        st.plotly_chart(fig_cgr_cat, use_container_width=True)

with col_cgr_div:
    st.markdown(
        "##### 🏢 Pertumbuhan Basis per Cabang (Awal + Baru & CGR %)"
        if not is_en
        else "##### 🏢 Customer Base Growth by Branch (Initial + New & CGR %)"
    )
    if not div_cgr_df.empty:
        div_plot_df = div_cgr_df.sort_values(by="pelanggan_akhir", ascending=True).copy()
        fig_cgr_div = go.Figure()
        fig_cgr_div.add_trace(go.Bar(
            y=div_plot_df["group_name"],
            x=div_plot_df["pelanggan_awal"],
            name="Pelanggan Awal" if not is_en else "Initial Base",
            orientation="h",
            marker_color="#6366F1",
            hovertemplate="<b>%{y}</b><br>Pelanggan Awal: <b>%{x:,}</b><extra></extra>"
        ))
        div_bar_labels = [
            f"+{b:,} Baru (CGR +{c:.1f}%)" if not is_en else f"+{b:,} New (CGR +{c:.1f}%)"
            for b, c in zip(div_plot_df["pelanggan_baru"], div_plot_df["cgr_net_pct"])
        ]
        fig_cgr_div.add_trace(go.Bar(
            y=div_plot_df["group_name"],
            x=div_plot_df["pelanggan_baru"],
            name="+ Pelanggan Baru" if not is_en else "+ New Customers",
            orientation="h",
            marker_color="#10B981",
            text=div_bar_labels,
            textposition="outside",
            cliponaxis=False,
            customdata=div_plot_df[["pelanggan_awal", "pelanggan_akhir", "cgr_net_pct", "share_baru_pct"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Pelanggan Awal: <b>%{customdata[0]:,}</b><br>"
                "+ Pelanggan Baru: <b>+%{x:,}</b> (%{customdata[3]:.1f}% dari total baru)<br>"
                "= Pelanggan Akhir: <b>%{customdata[1]:,}</b><br>"
                "CGR (Baru−Churn)/Awal: <b>+%{customdata[2]:.2f}%</b><extra></extra>"
            )
        ))
        max_div_x = div_plot_df["pelanggan_akhir"].max() if not div_plot_df.empty else 8000
        apply_plotly_theme(fig_cgr_div, height=380)
        fig_cgr_div.update_layout(
            barmode="stack",
            xaxis=dict(title="Jumlah Pelanggan" if not is_en else "Customers", range=[0, max_div_x * 1.32]),
            yaxis=dict(title=None),
            margin=dict(r=110, t=35, b=20, l=10)
        )
        st.plotly_chart(fig_cgr_div, use_container_width=True)

# Detailed CGR Formula Tables by Category & Branch
st.caption(
    "💡 **Cara Membaca Tabel di Bawah:** Setiap baris memperlihatkan langkah perhitungan CGR secara berurutan dari kiri ke kanan: **`Pelanggan Awal` + `Pelanggan Baru` − `Churn` = `Pelanggan Akhir`**, di mana **`Pertumbuhan Bersih (Baru − Churn)` dibagi `Pelanggan Awal` × 100% = `Hasil CGR (%)`**."
    if not is_en
    else "💡 **How to Read the Table Below:** Each row shows the step-by-step CGR calculation from left to right: **`Initial Base` + `New Customers` − `Churn` = `Ending Base`**, where **`Net Growth (New − Churn)` ÷ `Initial Base` × 100% = `CGR (%)`**."
)

tab_tbl_cat, tab_tbl_div = st.tabs([
    "📋 Tabel Rincian Rumus CGR per Kategori Pelanggan" if not is_en else "📋 CGR Formula Breakdown Table by Category",
    "📋 Tabel Rincian Rumus CGR per Cabang (Divisi)" if not is_en else "📋 CGR Formula Breakdown Table by Branch"
])

with tab_tbl_cat:
    if not cat_cgr_df.empty:
        disp_cat_tbl = pd.DataFrame({
            ("Kategori Pelanggan" if not is_en else "Category"): cat_cgr_df["group_name"],
            ("Pelanggan Awal" if not is_en else "Initial Base"): cat_cgr_df["pelanggan_awal"].apply(lambda v: f"{v:,}"),
            ("+ Pelanggan Baru" if not is_en else "+ New Customers"): cat_cgr_df["pelanggan_baru"].apply(lambda v: f"+{v:,}"),
            ("- Berhenti (Churn)" if not is_en else "- Churn"): cat_cgr_df["pelanggan_churn"].apply(lambda v: f"{v:,}"),
            ("Pertumbuhan Bersih (Baru - Churn)" if not is_en else "Net Growth (New - Churn)"): cat_cgr_df["net_growth"].apply(lambda v: f"+{v:,}" if v >= 0 else f"{v:,}"),
            ("= Pelanggan Akhir" if not is_en else "= Ending Base"): cat_cgr_df["pelanggan_akhir"].apply(lambda v: f"{v:,}"),
            ("Hasil CGR (%)" if not is_en else "CGR Result (%)"): cat_cgr_df["cgr_net_pct"].apply(lambda v: f"+{v:.2f}%"),
            ("Rata-rata Baru / Hari" if not is_en else "Avg New / Day"): cat_cgr_df["avg_daily_new"].apply(lambda v: f"+{v:.1f}/hari" if not is_en else f"+{v:.1f}/day"),
            ("Status Pertumbuhan" if not is_en else "Growth Status"): cat_cgr_df["status_en" if is_en else "status_id"]
        })
        tot_cat_row = pd.DataFrame([{
            ("Kategori Pelanggan" if not is_en else "Category"): "TOTAL KESELURUHAN (7 KATEGORI)" if not is_en else "TOTAL (7 EXTERNAL CATEGORIES)",
            ("Pelanggan Awal" if not is_en else "Initial Base"): f"{awal_cnt:,}",
            ("+ Pelanggan Baru" if not is_en else "+ New Customers"): f"+{baru_cnt:,}",
            ("- Berhenti (Churn)" if not is_en else "- Churn"): f"{churn_cnt:,}",
            ("Pertumbuhan Bersih (Baru - Churn)" if not is_en else "Net Growth (New - Churn)"): f"+{net_cnt:,}",
            ("= Pelanggan Akhir" if not is_en else "= Ending Base"): f"{akhir_cnt:,}",
            ("Hasil CGR (%)" if not is_en else "CGR Result (%)"): f"+{cgr_net_pct:.2f}%",
            ("Rata-rata Baru / Hari" if not is_en else "Avg New / Day"): f"+{avg_daily_period:.1f}/hari" if not is_en else f"+{avg_daily_period:.1f}/day",
            ("Status Pertumbuhan" if not is_en else "Growth Status"): "🎯 Rata-rata CGR Perusahaan" if not is_en else "🎯 Company CGR Benchmark"
        }])
        disp_cat_tbl = pd.concat([disp_cat_tbl, tot_cat_row], ignore_index=True)
        st.dataframe(disp_cat_tbl, use_container_width=True, hide_index=True)

with tab_tbl_div:
    if not div_cgr_df.empty:
        disp_div_tbl = pd.DataFrame({
            ("Cabang / Divisi" if not is_en else "Branch / Division"): div_cgr_df["group_name"],
            ("Pelanggan Awal" if not is_en else "Initial Base"): div_cgr_df["pelanggan_awal"].apply(lambda v: f"{v:,}"),
            ("+ Pelanggan Baru" if not is_en else "+ New Customers"): div_cgr_df["pelanggan_baru"].apply(lambda v: f"+{v:,}"),
            ("- Berhenti (Churn)" if not is_en else "- Churn"): div_cgr_df["pelanggan_churn"].apply(lambda v: f"{v:,}"),
            ("Pertumbuhan Bersih (Baru - Churn)" if not is_en else "Net Growth (New - Churn)"): div_cgr_df["net_growth"].apply(lambda v: f"+{v:,}" if v >= 0 else f"{v:,}"),
            ("= Pelanggan Akhir" if not is_en else "= Ending Base"): div_cgr_df["pelanggan_akhir"].apply(lambda v: f"{v:,}"),
            ("Hasil CGR (%)" if not is_en else "CGR Result (%)"): div_cgr_df["cgr_net_pct"].apply(lambda v: f"+{v:.2f}%"),
            ("Rata-rata Baru / Hari" if not is_en else "Avg New / Day"): div_cgr_df["avg_daily_new"].apply(lambda v: f"+{v:.1f}/hari" if not is_en else f"+{v:.1f}/day"),
            ("Status Pertumbuhan" if not is_en else "Growth Status"): div_cgr_df["status_en" if is_en else "status_id"]
        })
        tot_div_row = pd.DataFrame([{
            ("Cabang / Divisi" if not is_en else "Branch / Division"): "TOTAL KESELURUHAN (6 CABANG)" if not is_en else "TOTAL (6 BRANCHES)",
            ("Pelanggan Awal" if not is_en else "Initial Base"): f"{awal_cnt:,}",
            ("+ Pelanggan Baru" if not is_en else "+ New Customers"): f"+{baru_cnt:,}",
            ("- Berhenti (Churn)" if not is_en else "- Churn"): f"{churn_cnt:,}",
            ("Pertumbuhan Bersih (Baru - Churn)" if not is_en else "Net Growth (New - Churn)"): f"+{net_cnt:,}",
            ("= Pelanggan Akhir" if not is_en else "= Ending Base"): f"{akhir_cnt:,}",
            ("Hasil CGR (%)" if not is_en else "CGR Result (%)"): f"+{cgr_net_pct:.2f}%",
            ("Rata-rata Baru / Hari" if not is_en else "Avg New / Day"): f"+{avg_daily_period:.1f}/hari" if not is_en else f"+{avg_daily_period:.1f}/day",
            ("Status Pertumbuhan" if not is_en else "Growth Status"): "🎯 Rata-rata CGR Perusahaan" if not is_en else "🎯 Company CGR Benchmark"
        }])
        disp_div_tbl = pd.concat([disp_div_tbl, tot_div_row], ignore_index=True)
        st.dataframe(disp_div_tbl, use_container_width=True, hide_index=True)

if not cat_cgr_df.empty and not div_cgr_df.empty:
    fastest_cat = cat_cgr_df.sort_values(by="cgr_net_pct", ascending=False).iloc[0]
    largest_cat = cat_cgr_df.sort_values(by="pelanggan_baru", ascending=False).iloc[0]
    fastest_div = div_cgr_df.sort_values(by="cgr_net_pct", ascending=False).iloc[0]
    largest_div = div_cgr_df.sort_values(by="pelanggan_baru", ascending=False).iloc[0]

    render_layman_summary_box(
        title="Perbandingan CGR Antar-Kategori & Antar-Cabang" if not is_en else "Category & Branch CGR Comparison",
        plain_summary=(
            f"Secara persentase CGR, kategori yang tumbuh paling pesat terhadap basis awalnya adalah <b>{fastest_cat['group_name']}</b> dengan CGR <b>+{fastest_cat['cgr_net_pct']:.2f}%</b> (dari {fastest_cat['pelanggan_awal']:,} menjadi {fastest_cat['pelanggan_akhir']:,} pelanggan), sedangkan secara jumlah orang terbanyak dipimpin oleh <b>{largest_cat['group_name']}</b> (<b>+{largest_cat['pelanggan_baru']:,} pelanggan baru</b> / CGR +{largest_cat['cgr_net_pct']:.2f}%). "
            f"Untuk cabang, laju CGR tertinggi dicapai oleh <b>{fastest_div['group_name']} (+{fastest_div['cgr_net_pct']:.2f}%)</b> dan volume pelanggan baru terbesar disumbang oleh <b>{largest_div['group_name']} (+{largest_div['pelanggan_baru']:,} pelanggan)</b>."
            if not is_en
            else f"By percentage CGR, the fastest-growing category relative to its starting base is <b>{fastest_cat['group_name']}</b> at <b>+{fastest_cat['cgr_net_pct']:.2f}%</b> ({fastest_cat['pelanggan_awal']:,} → {fastest_cat['pelanggan_akhir']:,}), while in sheer volume <b>{largest_cat['group_name']}</b> leads with <b>+{largest_cat['pelanggan_baru']:,} new accounts</b> (CGR +{largest_cat['cgr_net_pct']:.2f}%). "
                 f"Among branches, <b>{fastest_div['group_name']} (+{fastest_div['cgr_net_pct']:.2f}%)</b> posts the highest CGR % while <b>{largest_div['group_name']} (+{largest_div['pelanggan_baru']:,} accounts)</b> contributes the largest volume."
        ),
        key_takeaway=(
            "Data bulanan terbaru (September–November 2026) juga menyingkap pergeseran menarik: pendaftaran kategori <b>AGEN</b> melonjak tajam (dari 5 akun di Agustus → 193 di September → 283 di Oktober → 98 hanya dalam 12 hari pertama November, terutama di Cipta Purwakarta, Digital, dan Graha), sedangkan pendaftaran baru <b>UMKM</b> di Cipta Digital melambat dari 200+ akun/bulan menjadi ~64 akun/bulan."
            if not is_en
            else "Recent monthly data (Sep–Nov 2026) reveals an important structural shift: <b>AGEN</b> registrations surged dramatically (from 5 in Aug → 193 in Sep → 283 in Oct → 98 in just the first 12 days of Nov, led by Purwakarta, Digital, and Graha), whereas new <b>UMKM</b> intake at Cipta Digital slowed from 200+/month to ~64/month."
        ),
        recommended_action=(
            "Pertahankan momentum rekrutmen kemitraan <b>AGEN</b> yang sedang naik daun, sembari mengaktifkan kembali kampanye akuisisi <b>UMKM</b> dan <b>INSTANSI</b> agar semua mesin pertumbuhan berjalan beriringan."
            if not is_en
            else "Sustain the surging <b>AGEN</b> reseller momentum while reactivating local <b>UMKM</b> and <b>INSTANSI</b> outreach campaigns so all growth engines fire simultaneously."
        ),
        lang_code=lang_code,
        accent_color="#10B981"
    )

st.markdown("---")

# -------------------------------------------------------------
# 11. INSIGHT 5: CHURN / INACTIVE & WIN-BACK ACTION AUDIT (DONUT + BAR STACK)
# -------------------------------------------------------------
df_all_scope = cgr_summary["df_filtered"]
all_churn_df = df_all_scope[df_all_scope["is_churned"]].copy()
del_scope_cnt = int(df_all_scope["is_deleted_customer"].sum())
inact_scope_cnt = int((df_all_scope["inactive"] & (~df_all_scope["is_deleted_customer"])).sum())
total_churn_scope = del_scope_cnt + inact_scope_cnt

render_section_info(
    title=(
        "Insight 5: Fokus Pelanggan Berhenti (Churn: Dihapus vs Non-Aktif) & Peluang Re-Aktivasi"
        if not is_en
        else "Insight 5: Churned Customer Focus (Deleted vs Inactive) & Re-Activation Opportunities"
    ),
    subtitle=(
        "Berfokus penuh pada akun pelanggan yang Dihapus (Deleted) dan Non-Aktif (Inactive) untuk mengidentifikasi pelanggan potensial yang bisa diaktifkan kembali (Win-Back)."
        if not is_en
        else "Strictly focuses on Deleted and Inactive accounts to identify high-potential customers that can be re-activated (Win-Back)."
    ),
    what_it_shows=(
        "Grafik Donat proporsi khusus akun berhenti (Dihapus vs Non-Aktif), Grafik Bar Stack sebaran per cabang & kategori, serta Tabel Rencana Tindakan (Action Plan) per akun."
        if not is_en
        else "Donut chart of Churned accounts (Deleted vs Inactive), Stacked Bar breakdown by branch & category, and an account-level Action Plan table."
    ),
    why_important=(
        "Menghilangkan data akun aktif (yang mencapai ~100%) dari grafik ini membuat perhatian manajemen langsung tertuju pada akun yang bermasalah/non-aktif agar segera diambil keputusan tindak lanjut."
        if not is_en
        else "Excluding active accounts (~100%) focuses management attention directly on churned/inactive accounts that require immediate follow-up decisions."
    ),
    simple_insight=(
        f"Terdapat {total_churn_scope:,} akun berhenti pada cakupan ini: {del_scope_cnt:,} akun berstatus Dihapus (Deleted) dan {inact_scope_cnt:,} akun berstatus Non-Aktif (Inactive) yang dapat dievaluasi untuk re-aktivasi."
        if not is_en
        else f"There are {total_churn_scope:,} churned accounts in this scope: {del_scope_cnt:,} Deleted accounts and {inact_scope_cnt:,} Inactive accounts that can be evaluated for win-back."
    ),
    icon="🎯",
    lang_code=lang_code
)

ch_col1, ch_col2 = st.columns([1.0, 1.3])

with ch_col1:
    st.markdown(
        "##### 🍩 Proporsi Akun Pelanggan Berhenti (Dihapus vs Non-Aktif)"
        if not is_en
        else "##### 🍩 Churned Customer Account Proportion (Deleted vs Inactive)"
    )
    del_total_cnt = int(df_all_scope["is_deleted_customer"].sum())
    inact_total_cnt = int((df_all_scope["inactive"] & (~df_all_scope["is_deleted_customer"])).sum())

    status_pie_df = pd.DataFrame({
        "Status": (
            [
                f"Dihapus / Deleted ({del_total_cnt:,} Akun)",
                f"Non-Aktif / Inactive ({inact_total_cnt:,} Akun)"
            ]
            if not is_en
            else [
                f"Deleted ({del_total_cnt:,} Accounts)",
                f"Inactive ({inact_total_cnt:,} Accounts)"
            ]
        ),
        "Count": [del_total_cnt, inact_total_cnt]
    })
    status_pie_df = status_pie_df[status_pie_df["Count"] > 0]

    if not status_pie_df.empty:
        fig_ch_donut = px.pie(
            status_pie_df,
            names="Status",
            values="Count",
            hole=0.52,
            color="Status",
            color_discrete_map={
                f"Dihapus / Deleted ({del_total_cnt:,} Akun)": "#EF4444",
                f"Deleted ({del_total_cnt:,} Accounts)": "#EF4444",
                f"Non-Aktif / Inactive ({inact_total_cnt:,} Akun)": "#F59E0B",
                f"Inactive ({inact_total_cnt:,} Accounts)": "#F59E0B"
            }
        )
        fig_ch_donut.update_traces(
            textinfo="label+percent",
            textposition="inside",
            insidetextfont=dict(size=12, color="#FFFFFF"),
            hovertemplate="<b>%{label}</b><br>Jumlah: <b>%{value:,} akun (%{percent})</b><extra></extra>"
        )
        center_lbl = (
            f"<b>{del_total_cnt + inact_total_cnt:,} Akun</b><br><span style='font-size:11px;color:#94A3B8;'>Total Churn</span>"
            if not is_en
            else f"<b>{del_total_cnt + inact_total_cnt:,} Accts</b><br><span style='font-size:11px;color:#94A3B8;'>Total Churn</span>"
        )
        apply_plotly_theme(fig_ch_donut, height=340)
        fig_ch_donut.update_layout(
            showlegend=True,
            margin=dict(t=25, b=20, l=15, r=15),
            annotations=[dict(text=center_lbl, x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig_ch_donut, use_container_width=True)
    else:
        st.success("Tidak ada akun dihapus atau non-aktif pada cakupan filter ini." if not is_en else "No deleted or inactive accounts in this filter scope.")

with ch_col2:
    st.markdown(
        "##### 📊 Bar Stack Sebaran Akun Berhenti (Deleted vs Inactive) per Cabang & Kategori"
        if not is_en
        else "##### 📊 Stacked Bar of Churned Accounts (Deleted vs Inactive) by Branch & Category"
    )
    if not all_churn_df.empty:
        all_churn_df["churn_type"] = np.where(
            all_churn_df["is_deleted_customer"],
            "Dihapus (Deleted)" if not is_en else "Deleted Account",
            "Non-Aktif (Inactive)" if not is_en else "Inactive Account"
        )
        churn_stack = (
            all_churn_df.groupby(["division_name", "category_name", "churn_type"])["customer_id"]
            .nunique()
            .reset_index(name="churn_count")
        )
        churn_stack["bar_label"] = churn_stack.apply(
            lambda r: f"{int(r['churn_count'])} ({r['category_name']})", axis=1
        )
        fig_ch_bar = px.bar(
            churn_stack,
            x="division_name",
            y="churn_count",
            color="category_name",
            pattern_shape="churn_type",
            text="bar_label",
            labels={
                "division_name": "Cabang" if not is_en else "Branch",
                "churn_count": "Jumlah Akun Berhenti" if not is_en else "Churned Accounts",
                "category_name": "Kategori" if not is_en else "Category",
                "churn_type": "Status Berhenti" if not is_en else "Churn Status"
            },
            color_discrete_sequence=["#EF4444", "#F59E0B", "#3B82F6", "#8B5CF6", "#10B981"]
        )
        fig_ch_bar.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=11, color="#FFFFFF")
        )
        apply_plotly_theme(fig_ch_bar, height=340)
        fig_ch_bar.update_layout(barmode="stack", margin=dict(t=25, b=20, l=15, r=15))
        st.plotly_chart(fig_ch_bar, use_container_width=True)
    else:
        st.success("Tidak ada akun yang tercatat berhenti/dihapus pada cakupan filter ini." if not is_en else "No churned/deleted accounts recorded in this filter scope.")

if not all_churn_df.empty:
    st.markdown(
        f"##### 📋 Daftar Akun Pelanggan Berhenti / Non-Aktif ({len(all_churn_df)} Akun) & Rekomendasi Tindakan (Win-Back / Audit)"
        if not is_en
        else f"##### 📋 Churned / Inactive Customer Accounts ({len(all_churn_df)} Accounts) & Recommended Win-Back Actions"
    )

    def _classify_churn_action(row):
        cname = str(row.get("customer_name", "")).lower()
        cat = str(row.get("category_name", "")).upper()
        div = str(row.get("division_name", ""))
        is_del = bool(row.get("is_deleted_customer", False))

        if "test" in cname or "testing" in cname:
            return (
                "🧹 Akun Uji Coba (Testing) — Abaikan dari target sales & bersihkan dari produksi"
                if not is_en
                else "🧹 System Test Account — Exclude from sales follow-up & clean from production"
            )
        if not is_del:
            return (
                f"🎯 Prioritas Win-Back (Non-Aktif) — Hubungi kembali prospek {cat} ini melalui tim Sales/CS {div} untuk re-aktivasi pesanan"
                if not is_en
                else f"🎯 Win-Back Priority (Inactive) — Re-engage this {cat} account via {div} Sales/CS team to reactivate orders"
            )
        return (
            f"⚠️ Audit & Akuisisi Ulang (Dihapus) — Cek alasan penghapusan di {div}; jika bukan akun duplikat, jadikan target penawaran ulang ({cat})"
            if not is_en
            else f"⚠️ Audit & Re-Acquire (Deleted) — Verify deletion reason at {div}; if not a duplicate, re-engage as a {cat} lead"
        )

    churn_disp = pd.DataFrame({
        ("Kode Pelanggan" if not is_en else "Customer Code"): all_churn_df["customer_code"],
        ("Nama Pelanggan" if not is_en else "Customer Name"): all_churn_df["customer_name"],
        ("Cabang" if not is_en else "Branch"): all_churn_df["division_name"],
        ("Kategori" if not is_en else "Category"): all_churn_df["category_name"],
        ("Tanggal Registrasi" if not is_en else "Registration Date"): all_churn_df["registration_date"].astype(str),
        ("Tanggal Berhenti / Dihapus" if not is_en else "Churn / Deleted Date"): all_churn_df["churn_date"].astype(str),
        ("Status Akun" if not is_en else "Account Status"): np.where(
            all_churn_df["is_deleted_customer"],
            "Dihapus (Deleted)" if not is_en else "Deleted",
            "Non-Aktif (Inactive)" if not is_en else "Inactive"
        ),
        ("Diagnosa & Keputusan Tindak Lanjut" if not is_en else "Diagnosis & Follow-Up Decision"): all_churn_df.apply(_classify_churn_action, axis=1)
    })
    st.dataframe(churn_disp, use_container_width=True, hide_index=True)

render_layman_summary_box(
    title="Keputusan Tindak Lanjut atas Pelanggan Berhenti (Deleted vs Inactive)" if not is_en else "Follow-Up Decisions on Churned Customers (Deleted vs Inactive)",
    plain_summary=(
        f"Dengan menghilangkan akun aktif dari grafik donat di atas, kini terlihat jelas komposisi <b>{len(all_churn_df):,} akun pelanggan yang berhenti</b>: terdiri dari <b>{del_total_cnt:,} akun berstatus Dihapus (Deleted / {del_total_cnt / max(1, len(all_churn_df)) * 100:.1f}%)</b> dan <b>{inact_total_cnt:,} akun berstatus Non-Aktif (Inactive / {inact_total_cnt / max(1, len(all_churn_df)) * 100:.1f}%)</b>."
        if not is_en
        else f"By removing active accounts from the donut chart above, we clearly see the breakdown of the <b>{len(all_churn_df):,} churned accounts</b>: <b>{del_total_cnt:,} Deleted accounts ({del_total_cnt / max(1, len(all_churn_df)) * 100:.1f}%)</b> and <b>{inact_total_cnt:,} Inactive accounts ({inact_total_cnt / max(1, len(all_churn_df)) * 100:.1f}%)</b>."
    ),
    key_takeaway=(
        "Dari bedah daftar akun di atas, <b>2 akun Non-Aktif adalah pelanggan riil potensial</b> (termasuk korporasi <i>PT. China State Construction Overseas</i> di segmen INDUSTRI – Cipta Digital dan <i>jihan PT LKI</i> di Cipta Galuh), serta <b>2 akun Dihapus di Cipta Online juga merupakan entitas riil</b> (<i>Universitas Ciputra Makassar</i> di segmen INSTANSI dan <i>Annisa Azizah</i>), sedangkan <b>2 akun lainnya di Cipta Graha hanyalah akun uji coba (testing)</b>."
        if not is_en
        else "Inspecting the account list reveals that <b>2 Inactive accounts are real potential customers</b> (including corporate account <i>PT. China State Construction Overseas</i> in INDUSTRI – Cipta Digital and <i>jihan PT LKI</i> in Cipta Galuh), and <b>2 Deleted accounts at Cipta Online are real entities</b> (<i>Universitas Ciputra Makassar</i> in INSTANSI and <i>Annisa Azizah</i>), while the remaining <b>2 accounts at Cipta Graha are merely system test entries</b>."
    ),
    recommended_action=(
        "1) Tugaskan tim Sales B2B Cipta Digital & Cipta Galuh untuk menghubungi kembali 2 akun <b>Non-Aktif (Inactive)</b> agar kembali bertransaksi (Win-Back). 2) Tugaskan CS Cipta Online memverifikasi apakah <i>Universitas Ciputra Makassar</i> dihapus karena duplikat akun; jika belum terlayani, segera hubungi kembali sebagai prospek Instansi."
        if not is_en
        else "1) Assign B2B Sales at Cipta Digital & Cipta Galuh to re-engage the 2 <b>Inactive</b> accounts for win-back. 2) Have Cipta Online CS verify whether <i>Universitas Ciputra Makassar</i> was deleted due to duplication; if unserved, follow up immediately as an Institutional lead."
    ),
    lang_code=lang_code,
    accent_color="#EF4444"
)

st.markdown("---")

# -------------------------------------------------------------
# 12. FOOTER DATA INTEGRITY & METHODOLOGY NOTES
# -------------------------------------------------------------
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    st.caption(
        "🧮 **Formula CGR:** `((Pelanggan Baru - Pelanggan Berhenti) / Pelanggan Awal) × 100%`"
        if not is_en
        else "🧮 **CGR Formula:** `((New Customers - Churned Customers) / Initial Customers) × 100%`"
    )
with f_col2:
    st.caption(
        "🎯 **Acuan Keputusan:** `≥ 30 Baru/Hari (CGR ≥ +4%/bln) = Akselerasi Kuat`"
        if not is_en
        else "🎯 **Decision Benchmark:** `≥ 30 New/Day (CGR ≥ +4%/mo) = Strong Acceleration`"
    )
with f_col3:
    st.caption(
        f"📂 **Sumber Data Pelanggan Eksternal:** `data/data_customer.csv` ({len(df_customers):,} Akun Eksternal · 7 Kategori tanpa Divisi Internal · per {latest_data_str})"
        if not is_en
        else f"📂 **External Master Data Source:** `data/data_customer.csv` ({len(df_customers):,} External Accounts · 7 Categories excl. Divisi · as of {latest_data_str})"
    )

