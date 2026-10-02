import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import (
    load_finance_data,
    load_customer_payment_behavior,
    load_collection_data_quality_exceptions,
    load_aging_receivable_summary,
    load_finance_market_scope_summary,
    load_finance_segment_summary,
    load_finance_division_summary,
    load_payment_method_summary,
    load_finance_cohort_summary
)
from components.ui_components import (
    render_header,
    metric_card,
    render_business_insight_card,
    render_section_info,
    render_summary_strip,
    global_sidebar_filters,
    apply_plotly_theme,
    format_rupiah,
    format_data_value
)

st.set_page_config(
    page_title="Finance Intelligence — Cetakia BI DSS",
    page_icon="💳",
    layout="wide"
)

# -------------------------------------------------------------
# 1. LOAD DATASETS WITH STREAMLIT CACHING
# -------------------------------------------------------------
df_finance_raw = load_finance_data(include_internal=True)
df_cust_behavior = load_customer_payment_behavior()
df_exceptions = load_collection_data_quality_exceptions()
df_aging_master = load_aging_receivable_summary()
df_market_master = load_finance_market_scope_summary()
df_seg_master = load_finance_segment_summary()
df_div_master = load_finance_division_summary()
df_pm_master = load_payment_method_summary()
df_cohort_master = load_finance_cohort_summary()

# -------------------------------------------------------------
# 2. SIDEBAR FILTERS & LOCALE STATE
# -------------------------------------------------------------
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

# Additional Market Scope Filter for Finance Intelligence
st.sidebar.subheader("🏢 " + ("Cakupan Pasar (Market Scope)" if lang_code == "ID" else "Market Scope"))
scope_options_id = [
    "Semua Transaksi (Operasional Lengkap)",
    "Hanya Pelanggan Eksternal (Pasar)",
    "Hanya Divisi Internal (Antar Cabang)"
]
scope_options_en = [
    "All Transactions (Operational)",
    "External Customers Only (Market)",
    "Internal Division Only (Inter-Branch)"
]
scope_options = scope_options_id if lang_code == "ID" else scope_options_en
selected_scope = st.sidebar.radio(
    "Pilih Perspektif Data:" if lang_code == "ID" else "Select Data Perspective:",
    options=scope_options,
    index=0,
    key="fin_market_scope_select"
)

# Map selected scope to internal flag
if selected_scope in [scope_options[1]]:
    scope_filter = "External Customer"
elif selected_scope in [scope_options[2]]:
    scope_filter = "Internal Division"
else:
    scope_filter = "All"

# Apply Filters to Finance Invoices
df_finance = df_finance_raw.copy()

if filters["branch"] != "All Branches":
    if "division_name" in df_finance.columns:
        df_finance = df_finance[df_finance["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_finance.columns:
        df_finance = df_finance[df_finance["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

if scope_filter != "All" and "market_scope" in df_finance.columns:
    df_finance = df_finance[df_finance["market_scope"] == scope_filter]

# Date interval filtering on invoice_date
if filters.get("date_range") and len(filters["date_range"]) == 2:
    start_d, end_d = filters["date_range"]
    if "invoice_date" in df_finance.columns and df_finance["invoice_date"].notnull().any():
        df_finance = df_finance[
            (df_finance["invoice_date"].dt.date >= start_d) &
            (df_finance["invoice_date"].dt.date <= end_d)
        ]

# Apply Filters to Customer Behavior Dataset
df_cust = df_cust_behavior.copy()
if filters["branch"] != "All Branches" and "division_name" in df_cust.columns:
    df_cust = df_cust[df_cust["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments" and "customer_category" in df_cust.columns:
    df_cust = df_cust[df_cust["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

if scope_filter == "External Customer":
    df_cust = df_cust[df_cust["customer_category"] != "DIVISI"]
elif scope_filter == "Internal Division":
    df_cust = df_cust[df_cust["customer_category"] == "DIVISI"]

# Apply Filters to Exceptions Dataset
df_exc = df_exceptions.copy()
if filters["branch"] != "All Branches" and "division_name" in df_exc.columns:
    df_exc = df_exc[df_exc["division_name"] == filters["branch"]]
if filters["segment"] != "All Segments" and "customer_category" in df_exc.columns:
    df_exc = df_exc[df_exc["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# -------------------------------------------------------------
# 3. PAGE HEADER
# -------------------------------------------------------------
page_title = t.get("fin_intel_title", "Dashboard Intelijen Keuangan")
page_subtitle = (
    "Realisasi Kas Masuk, Pemantauan Umur Piutang (Aging), Perilaku Pembayaran Pelanggan & Prioritas Penagihan"
    if lang_code == "ID" else
    "Cash Conversion Realization, Aging Receivable Monitoring, Customer Payment Behavior & Collection Worklist"
)
render_header(title=page_title, subtitle=page_subtitle, module_tag="FINANCE & COLLECTION DSS")

# -------------------------------------------------------------
# 4. EXECUTIVE KPI CARDS (DECISION SUPPORT)
# -------------------------------------------------------------
total_invoices_count = len(df_finance)
total_billed = float(df_finance["invoice_amount_clean"].sum()) if total_invoices_count > 0 else 0.0
total_settled = float(df_finance["settled_amount_eda"].sum()) if total_invoices_count > 0 else 0.0
total_outstanding = float(df_finance["outstanding_eda"].sum()) if total_invoices_count > 0 else 0.0
total_overdue = float(df_finance["overdue_outstanding_eda"].sum()) if total_invoices_count > 0 else 0.0

collection_rate = (total_settled / total_billed * 100) if total_billed > 0 else 0.0
outstanding_pct = (total_outstanding / total_billed * 100) if total_billed > 0 else 0.0
overdue_ratio = (total_overdue / total_outstanding * 100) if total_outstanding > 0 else 0.0

k1, k2, k3, k4 = st.columns(4)

with k1:
    lbl_billed = "Total Tagihan Diterbitkan" if lang_code == "ID" else "Total Billed Invoices"
    sub_billed = (
        f"{total_invoices_count:,} faktur tagihan tercatat" if lang_code == "ID"
        else f"{total_invoices_count:,} invoices billed"
    )
    metric_card(title=lbl_billed, value=format_rupiah(total_billed), subtext=sub_billed)

with k2:
    lbl_settled = "Kas Nyata Berhasil Masuk" if lang_code == "ID" else "Cash Collected (Settled)"
    delta_settled = (
        f"{collection_rate:.1f}% Tingkat Realisasi Kas" if lang_code == "ID"
        else f"{collection_rate:.1f}% Collection Rate"
    )
    sub_settled = (
        "Uang kas riil yang sudah diterima kasir/bank" if lang_code == "ID"
        else "Authoritative cash collected into bank/cash"
    )
    metric_card(
        title=lbl_settled,
        value=format_rupiah(total_settled),
        delta=delta_settled,
        delta_color="positive" if collection_rate >= 50 else "negative",
        subtext=sub_settled
    )

with k3:
    lbl_out = "Total Sisa Piutang Berjalan" if lang_code == "ID" else "Total Outstanding Receivable"
    delta_out = (
        f"{outstanding_pct:.1f}% dari nilai tagihan" if lang_code == "ID"
        else f"{outstanding_pct:.1f}% of billed revenue"
    )
    sub_out = (
        "Nilai tagihan yang belum dibayar lunas" if lang_code == "ID"
        else "Unsettled invoice amount in portfolio"
    )
    metric_card(
        title=lbl_out,
        value=format_rupiah(total_outstanding),
        delta=delta_out,
        delta_color="negative" if outstanding_pct > 40 else "positive",
        subtext=sub_out
    )

with k4:
    lbl_over = "Piutang Lewat Jatuh Tempo" if lang_code == "ID" else "Overdue Receivables"
    delta_over = (
        f"{overdue_ratio:.1f}% dari sisa piutang" if lang_code == "ID"
        else f"{overdue_ratio:.1f}% of outstanding is overdue"
    )
    sub_over = (
        "Sudah melampaui batas tanggal jatuh tempo" if lang_code == "ID"
        else "Receivables past their agreed due date"
    )
    metric_card(
        title=lbl_over,
        value=format_rupiah(total_overdue),
        delta=delta_over,
        delta_color="negative",
        subtext=sub_over
    )

st.markdown("---")

# -------------------------------------------------------------
# 5. MANDATORY DSS BUSINESS INSIGHT CARD
# -------------------------------------------------------------
# Calculate 90+ days overdue for the insight card
overdue_90plus = float(df_finance[df_finance["aging_bucket"] == "90+ Days"]["outstanding_eda"].sum())
overdue_90plus_pct = (overdue_90plus / total_outstanding * 100) if total_outstanding > 0 else 0.0

if lang_code == "EN":
    ic_title = "Cash Flow Conversion Reality & 90+ Day Aging Receivable Escalation"
    ic_metric = f"{format_rupiah(total_overdue)} Overdue Receivables ({overdue_ratio:.1f}% of Outstanding, {format_rupiah(overdue_90plus)} in 90+ Days Bucket)"
    ic_context = f"Evaluated across {total_invoices_count:,} invoices worth {format_rupiah(total_billed)} for Branch '{filters['branch']}', Segment '{filters['segment']}', and Scope '{selected_scope}'."
    ic_insight = f"The primary financial challenge is the substantial gap between invoiced sales and actual cash collected (collection rate {collection_rate:.1f}%). Receivables are heavily concentrated in the INDUSTRI segment and internal DIVISI transfers, where over 54% of outstanding balances have aged past 90 days."
    ic_impacted = "Finance & Credit Control, Key Account Executives, Branch Managers, and Corporate Working Capital."
    ic_action = "Finance & Sales Management: Implement strict multi-tiered collection workflows. Isolate internal division flows from commercial KPI; require executive-level intervention and credit holds on 90+ day overdue accounts exceeding Rp 50 Million."
    ic_badge = "FINANCIAL DECISION SUPPORT"
    ic_target = f"{format_rupiah(overdue_90plus)} in 90+ Days Aging Bucket requiring structured collection escalation"
else:
    ic_title = "Realitas Konversi Kas & Eskalasi Penagihan Piutang Menunggak >90 Hari"
    ic_metric = f"{format_rupiah(total_overdue)} Piutang Lewat Jatuh Tempo ({overdue_ratio:.1f}% dari Piutang, {format_rupiah(overdue_90plus)} di Bucket >90 Hari)"
    ic_context = f"Dianalisis dari {total_invoices_count:,} invoice senilai {format_rupiah(total_billed)} pada Cabang '{filters['branch']}', Segmen '{filters['segment']}', dan Cakupan '{selected_scope}'."
    ic_insight = f"Tantangan finansial utama Cipta Grafika bukan pada minimnya pesanan, melainkan lebarnya jarak antara invoice diterbitkan dengan kas yang berhasil direalisasikan (kolektibilitas {collection_rate:.1f}%). Sebanyak 54,8% piutang telah menumpuk lebih dari 90 hari, didominasi oleh segmen INDUSTRI dan transaksi internal DIVISI."
    ic_impacted = "Tim Finance & Penagihan, Account Executive Segmen Industri, Manajer Cabang, dan Arus Kas Modal Kerja."
    ic_action = "Manajemen Keuangan & Penjualan: Terapkan SOP penagihan berjenjang. Pisahkan evaluasi piutang internal divisi agar tidak mendistorsi kinerja pasar; lakukan eskalasi langsung (holding order baru dan rekonsiliasi PO fisik) untuk akun menunggak >90 hari bernilai di atas Rp 50 Juta."
    ic_badge = "KEPUTUSAN FINANSIAL STRATEGIS"
    ic_target = f"{format_rupiah(overdue_90plus)} Piutang Kritis (>90 Hari) yang butuh penanganan khusus tim penagihan"

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
# 6. 5 TABBED FINANCE INTELLIGENCE INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_labels = [
        "⏳ Aging Receivables Analysis",
        "🏢 Segment & Branch Risk Exposure",
        "👥 Customer Payment Behavior",
        "🎯 Priority Collection Worklist",
        "🔍 Data Quality & Exception Audit"
    ]
else:
    tab_labels = [
        "⏳ Umur Piutang Usaha (Aging Receivables)",
        "🏢 Profil Risiko Segmen & Cabang",
        "👥 Pola & Perilaku Pembayaran Pelanggan",
        "🎯 Daftar Prioritas Penagihan (Worklist)",
        "🔍 Audit Kualitas Data & Pengecualian"
    ]

tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)

# =============================================================
# TAB 1: AGING RECEIVABLES ANALYSIS
# =============================================================
with tab1:
    render_section_info(
        title="Pemantauan Umur Piutang Usaha (Aging Receivables Analysis)" if lang_code == "ID" else "Aging Receivables Portfolio Monitoring",
        subtitle="Analisis struktur waktu keterlambatan pembayaran invoice sejak tanggal jatuh tempo" if lang_code == "ID" else "Structure of payment overdue duration since invoice due date",
        what_it_shows=(
            "Pengelompokan total tagihan berdasarkan umur keterlambatan: Sudah Lunas, Belum Jatuh Tempo, Jatuh Tempo Hari Ini, Menunggak 1-30 Hari, 31-60 Hari, 61-90 Hari, dan >90 Hari."
            if lang_code == "ID" else
            "Classification of billed invoices by overdue age buckets: Settled, Not Yet Due, Due Today, 1-30 Days, 31-60 Days, 61-90 Days, and 90+ Days."
        ),
        why_important=(
            "Semakin tua umur piutang (terutama di atas 90 hari), semakin tinggi risiko menjadi kredit macet (bad debt) dan semakin berat beban modal kerja untuk membiayai bahan baku cetak."
            if lang_code == "ID" else
            "As receivables age past 90 days, recovery probability drops sharply, locking up operational working capital needed for raw material replenishment."
        ),
        simple_insight=(
            f"Sebesar {format_rupiah(overdue_90plus)} ({overdue_90plus_pct:.1f}% dari piutang) berada di kelompok menunggak >90 hari. Ini adalah area kebocoran kas terbesar yang memerlukan eskalasi penagihan formal."
            if lang_code == "ID" else
            f"{format_rupiah(overdue_90plus)} ({overdue_90plus_pct:.1f}% of outstanding) sits in the 90+ day bucket, constituting the primary collection leak."
        ),
        icon="⏳"
    )

    # Aging Bucket Dynamic Calculation
    aging_order = ['Settled', 'Not Yet Due', 'Due Today', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
    aging_display_map_id = {
        'Settled': 'Sudah Lunas',
        'Not Yet Due': 'Belum Jatuh Tempo',
        'Due Today': 'Jatuh Tempo Hari Ini',
        '1-30 Days': 'Menunggak 1 - 30 Hari',
        '31-60 Days': 'Menunggak 31 - 60 Hari',
        '61-90 Days': 'Menunggak 61 - 90 Hari',
        '90+ Days': 'Menunggak > 90 Hari'
    }
    aging_display_map_en = {
        'Settled': 'Settled / Fully Paid',
        'Not Yet Due': 'Not Yet Due',
        'Due Today': 'Due Today',
        '1-30 Days': '1 - 30 Days Overdue',
        '31-60 Days': '31 - 60 Days Overdue',
        '61-90 Days': '61 - 90 Days Overdue',
        '90+ Days': '90+ Days Overdue'
    }
    disp_map = aging_display_map_id if lang_code == "ID" else aging_display_map_en

    aging_agg = df_finance.groupby("aging_bucket", observed=False).agg(
        invoices=("invoice_id", "nunique"),
        customers=("customer_id", "nunique"),
        outstanding=("outstanding_eda", "sum")
    ).reindex(aging_order).fillna(0.0).reset_index()

    aging_agg["bucket_label"] = aging_agg["aging_bucket"].map(disp_map).fillna(aging_agg["aging_bucket"])
    aging_agg["share_pct"] = (aging_agg["outstanding"] / total_outstanding * 100) if total_outstanding > 0 else 0.0

    # Summary Strip of Key Buckets
    strip_items = []
    bucket_colors = {
        'Not Yet Due': '#3B82F6',
        '1-30 Days': '#10B981',
        '31-60 Days': '#F59E0B',
        '61-90 Days': '#F97316',
        '90+ Days': '#EF4444'
    }
    for b_key in ['Not Yet Due', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days']:
        b_row = aging_agg[aging_agg["aging_bucket"] == b_key]
        if not b_row.empty:
            b_val = float(b_row["outstanding"].iloc[0])
            b_cnt = int(b_row["invoices"].iloc[0])
            b_pct = float(b_row["share_pct"].iloc[0])
            strip_items.append({
                "label": disp_map.get(b_key, b_key),
                "value": format_rupiah(b_val),
                "desc": f"{b_cnt:,} faktur ({b_pct:.1f}%)" if lang_code == "ID" else f"{b_cnt:,} invoices ({b_pct:.1f}%)",
                "color": bucket_colors.get(b_key, "#3B82F6")
            })
    render_summary_strip(strip_items)

    # 2 Visual Columns: Horizontal Bar Chart + Donut Composition
    c_chart1, c_chart2 = st.columns([1.5, 1])

    with c_chart1:
        st.subheader("📊 " + ("Distribusi Nominal Piutang per Kelompok Umur" if lang_code == "ID" else "Outstanding Receivables by Aging Bucket"))
        # Exclude 'Settled' for outstanding bar chart so only positive receivables are displayed
        aging_active = aging_agg[aging_agg["aging_bucket"] != "Settled"].copy()
        
        # Color mapping for buckets
        color_palette = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#F97316', '#EF4444']
        
        fig_aging = px.bar(
            aging_active,
            x="outstanding",
            y="bucket_label",
            orientation="h",
            text=aging_active["outstanding"].apply(format_rupiah),
            color="bucket_label",
            color_discrete_sequence=color_palette
        )
        fig_aging.update_traces(
            textposition="outside",
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>Sisa Piutang: %{x:,.0f} Rupiah<extra></extra>"
        )
        fig_aging.update_layout(
            xaxis_title="Nominal Piutang (Rupiah)" if lang_code == "ID" else "Outstanding Amount (IDR)",
            yaxis_title="",
            yaxis=dict(autorange="reversed")
        )
        apply_plotly_theme(fig_aging, height=360)
        st.plotly_chart(fig_aging, use_container_width=True)

    with c_chart2:
        st.subheader("🍩 " + ("Komposisi Piutang Sehat vs Kritis" if lang_code == "ID" else "Health Composition of Receivables"))
        # Categorize into 3 health groups
        not_due_val = float(aging_agg[aging_agg["aging_bucket"].isin(["Not Yet Due", "Due Today"])]["outstanding"].sum())
        mild_overdue = float(aging_agg[aging_agg["aging_bucket"].isin(["1-30 Days", "31-60 Days"])]["outstanding"].sum())
        severe_overdue = float(aging_agg[aging_agg["aging_bucket"].isin(["61-90 Days", "90+ Days"])]["outstanding"].sum())

        donut_labels = [
            "Normal / Belum Jatuh Tempo" if lang_code == "ID" else "Normal / Not Yet Due",
            "Overdue Ringan (1-60 Hari)" if lang_code == "ID" else "Mild Overdue (1-60 Days)",
            "Overdue Kritis (>60 Hari)" if lang_code == "ID" else "Critical Overdue (>60 Days)"
        ]
        donut_values = [not_due_val, mild_overdue, severe_overdue]
        donut_colors = ["#3B82F6", "#F59E0B", "#EF4444"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=donut_labels,
            values=donut_values,
            hole=0.55,
            marker=dict(colors=donut_colors),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Nominal: Rp %{value:,.0f}<br>Porsi: %{percent}<extra></extra>"
        )])
        fig_donut.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=20)
        )
        apply_plotly_theme(fig_donut, height=360)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Monthly Cohort Collection Progression Table & Trend
    st.subheader("📈 " + ("Tren Realisasi Kas per Bulan Penerbitan Invoice (Cohort)" if lang_code == "ID" else "Monthly Billed vs Collected Invoice Cohort Trend"))
    st.caption(
        "💡 Catatan Penting: Invoice pada bulan terbaru secara wajar memiliki tingkat pelunasan lebih rendah karena baru saja diterbitkan dan belum melewati tanggal jatuh tempo."
        if lang_code == "ID" else
        "💡 Note: Recent invoice cohorts naturally show lower settlement rates because they have had less time to mature compared to older invoices."
    )

    if "invoice_month" in df_finance.columns and df_finance["invoice_month"].notnull().any():
        cohort_agg = df_finance.groupby("invoice_month").agg(
            faktur=("invoice_id", "nunique"),
            tagihan=("invoice_amount_clean", "sum"),
            kas_masuk=("settled_amount_eda", "sum"),
            piutang=("outstanding_eda", "sum")
        ).reset_index().sort_values("invoice_month")
        
        cohort_agg["kolektibilitas_pct"] = np.where(
            cohort_agg["tagihan"] > 0,
            cohort_agg["kas_masuk"] / cohort_agg["tagihan"] * 100,
            0.0
        )

        fig_cohort = go.Figure()
        fig_cohort.add_trace(go.Bar(
            x=cohort_agg["invoice_month"],
            y=cohort_agg["tagihan"],
            name="Total Tagihan Diterbitkan" if lang_code == "ID" else "Billed Amount",
            marker_color="#94A3B8"
        ))
        fig_cohort.add_trace(go.Bar(
            x=cohort_agg["invoice_month"],
            y=cohort_agg["kas_masuk"],
            name="Kas Nyata Masuk (Settled)" if lang_code == "ID" else "Collected Cash",
            marker_color="#10B981"
        ))
        fig_cohort.add_trace(go.Scatter(
            x=cohort_agg["invoice_month"],
            y=cohort_agg["kolektibilitas_pct"],
            name="Kolektibilitas (%)" if lang_code == "ID" else "Collection Rate (%)",
            yaxis="y2",
            mode="lines+markers+text",
            text=[f"{v:.1f}%" for v in cohort_agg["kolektibilitas_pct"]],
            textposition="top center",
            line=dict(color="#3B82F6", width=3),
            marker=dict(size=7)
        ))
        fig_cohort.update_layout(
            barmode="group",
            yaxis=dict(title="Nominal Rupiah" if lang_code == "ID" else "Amount (IDR)"),
            yaxis2=dict(
                title="Tingkat Kolektibilitas (%)" if lang_code == "ID" else "Collection Rate (%)",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        apply_plotly_theme(fig_cohort, height=380)
        st.plotly_chart(fig_cohort, use_container_width=True)

# =============================================================
# TAB 2: SEGMENT & BRANCH RISK EXPOSURE
# =============================================================
with tab2:
    render_section_info(
        title="Profil Risiko Piutang per Segmen Pelanggan & Cabang Operasional" if lang_code == "ID" else "Receivable Exposure by Customer Segment & Branch",
        subtitle="Membedah sumber utama penumpukan piutang tanpa bias penilaian performa cabang" if lang_code == "ID" else "Deconstructing receivable concentration across customer segments and branch entities",
        what_it_shows=(
            "Perbandingan total tagihan, kas masuk, dan sisa piutang untuk setiap segmen pelanggan (Industri, UMKM, End User, Instansi, Sekolah, dsb.) serta cabang operasional."
            if lang_code == "ID" else
            "Comparison of billed revenue, collected cash, and outstanding balances across customer segments and branches."
        ),
        why_important=(
            "Masing-masing segmen memiliki budaya pembayaran yang berbeda. Segmen retail (End User/UMKM) membayar tunai di awal atau saat ambil barang, sedangkan segmen Industri/Instansi menggunakan term pembayaran korporat 30-90 hari dengan alur verifikasi berkas PO."
            if lang_code == "ID" else
            "Retail clients pay upfront or on pickup, whereas Corporate & Industrial clients transact on extended 30-90 day invoice credit terms requiring PO invoice approvals."
        ),
        simple_insight=(
            "Segmen INDUSTRI menyumbang Rp 7,66 Miliar (58,4%) dari seluruh piutang Cetakia, disusul akun internal DIVISI sebesar Rp 3,46 Miliar (26,4%). Kedua segmen ini mencakup 84,8% risiko piutang perusahaan."
            if lang_code == "ID" else
            "INDUSTRI accounts for Rp 7.66 Billion (58.4%) of outstanding receivables, followed by internal DIVISI transfers of Rp 3.46 Billion (26.4%). Together they represent 84.8% of exposure."
        ),
        icon="🏢"
    )

    col_seg1, col_seg2 = st.columns([1.5, 1])

    with col_seg1:
        st.subheader("🧩 " + ("Komparasi Tagihan, Kas Masuk & Piutang per Segmen" if lang_code == "ID" else "Segment Billed vs Settled vs Outstanding"))
        seg_agg = df_finance.groupby("customer_category").agg(
            tagihan=("invoice_amount_clean", "sum"),
            kas_masuk=("settled_amount_eda", "sum"),
            piutang=("outstanding_eda", "sum"),
            overdue=("overdue_outstanding_eda", "sum"),
            invoices=("invoice_id", "nunique"),
            customers=("customer_id", "nunique")
        ).reset_index().sort_values("piutang", ascending=False)
        
        seg_agg["kolektibilitas"] = np.where(seg_agg["tagihan"] > 0, seg_agg["kas_masuk"] / seg_agg["tagihan"] * 100, 0.0)

        fig_seg = go.Figure()
        fig_seg.add_trace(go.Bar(
            x=seg_agg["customer_category"],
            y=seg_agg["tagihan"],
            name="Total Tagihan (Billed)" if lang_code == "ID" else "Billed",
            marker_color="#94A3B8"
        ))
        fig_seg.add_trace(go.Bar(
            x=seg_agg["customer_category"],
            y=seg_agg["kas_masuk"],
            name="Kas Masuk (Settled)" if lang_code == "ID" else "Settled Cash",
            marker_color="#10B981"
        ))
        fig_seg.add_trace(go.Bar(
            x=seg_agg["customer_category"],
            y=seg_agg["piutang"],
            name="Sisa Piutang (Outstanding)" if lang_code == "ID" else "Outstanding",
            marker_color="#EF4444"
        ))
        fig_seg.update_layout(
            barmode="group",
            xaxis_title="Segmen Pelanggan" if lang_code == "ID" else "Customer Segment",
            yaxis_title="Nominal (Rupiah)" if lang_code == "ID" else "Amount (IDR)"
        )
        apply_plotly_theme(fig_seg, height=360)
        st.plotly_chart(fig_seg, use_container_width=True)

    with col_seg2:
        st.subheader("🍩 " + ("Pangsa Piutang per Segmen Pelanggan" if lang_code == "ID" else "Receivable Share by Segment"))
        fig_seg_pie = px.pie(
            seg_agg,
            names="customer_category",
            values="piutang",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_seg_pie.update_traces(
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Sisa Piutang: Rp %{value:,.0f}<br>Pangsa: %{percent}<extra></extra>"
        )
        apply_plotly_theme(fig_seg_pie, height=360)
        st.plotly_chart(fig_seg_pie, use_container_width=True)

    # Branch Analysis Section with Crucial Contextual Framing
    st.markdown("---")
    st.subheader("🏢 " + ("Kolektibilitas & Beban Piutang per Cabang Regional" if lang_code == "ID" else "Collection Rate & Receivable Burden by Regional Branch"))

    st.info(
        "📌 **Panduan Membaca bagi Manajemen / Direksi:**  \n"
        "Tingkat kolektibilitas cabang **tidak boleh langsung dijadikan ranking rapor baik/buruk**. "
        "Cabang seperti **Cipta Galuh** memegang order manufaktur B2B Industri dengan tempo pembayaran panjang, "
        "sedangkan **Cipta Graha** berperan sebagai pusat produksi utama yang mencatat tagihan transfer internal ke cabang lain (DIVISI). "
        "Sebaliknya, **Cipta Cianjur, Cipta Online, dan Cipta Purwakarta** didominasi pembeli ritel & UMKM yang pelunasannya langsung saat cetak selesai."
        if lang_code == "ID" else
        "📌 **Executive Reading Guidance:**  \n"
        "Branch collection rates should not be treated as a raw performance leaderboard. "
        "Cipta Galuh serves large industrial B2B clients with 90-day corporate terms, while Cipta Graha acts as the central manufacturing plant billing inter-branch orders (DIVISI). "
        "In contrast, Cianjur, Online, and Purwakarta serve retail and MSME customers paying immediately upon completion."
    )

    div_agg = df_finance.groupby("division_name").agg(
        tagihan=("invoice_amount_clean", "sum"),
        kas_masuk=("settled_amount_eda", "sum"),
        piutang=("outstanding_eda", "sum"),
        overdue=("overdue_outstanding_eda", "sum"),
        faktur=("invoice_id", "nunique")
    ).reset_index().sort_values("piutang", ascending=False)
    div_agg["kolektibilitas_pct"] = np.where(div_agg["tagihan"] > 0, div_agg["kas_masuk"] / div_agg["tagihan"] * 100, 0.0)

    c_b1, c_b2 = st.columns([1.2, 1])

    with c_b1:
        fig_div_bar = px.bar(
            div_agg,
            x="piutang",
            y="division_name",
            orientation="h",
            text=div_agg["piutang"].apply(format_rupiah),
            color="piutang",
            color_continuous_scale="Reds",
            title="Sisa Piutang Berjalan per Cabang" if lang_code == "ID" else "Outstanding Receivables by Branch"
        )
        fig_div_bar.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Sisa Piutang: Rp %{x:,.0f}<extra></extra>"
        )
        fig_div_bar.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title="Nominal Piutang (Rupiah)",
            coloraxis_showscale=False
        )
        apply_plotly_theme(fig_div_bar, height=340)
        st.plotly_chart(fig_div_bar, use_container_width=True)

    with c_b2:
        fig_div_rate = px.bar(
            div_agg.sort_values("kolektibilitas_pct", ascending=True),
            x="kolektibilitas_pct",
            y="division_name",
            orientation="h",
            text=div_agg.sort_values("kolektibilitas_pct", ascending=True)["kolektibilitas_pct"].apply(lambda x: f"{x:.1f}%"),
            color="kolektibilitas_pct",
            color_continuous_scale="Blues",
            title="Tingkat Realisasi Kas (%) per Cabang" if lang_code == "ID" else "Collection Rate (%) by Branch"
        )
        fig_div_rate.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Realisasi Kas: %{x:.1f}%<extra></extra>"
        )
        fig_div_rate.update_layout(
            xaxis=dict(range=[0, 115], title="Realisasi Kas (%)"),
            coloraxis_showscale=False
        )
        apply_plotly_theme(fig_div_rate, height=340)
        st.plotly_chart(fig_div_rate, use_container_width=True)

# =============================================================
# TAB 3: CUSTOMER PAYMENT BEHAVIOR
# =============================================================
with tab3:
    render_section_info(
        title="Pola & Perilaku Pembayaran Pelanggan (Payment Behavior Intelligence)" if lang_code == "ID" else "Customer Payment Behavior Intelligence",
        subtitle="Klasifikasi disiplin pembayaran pelanggan berdasarkan riwayat ketepatan waktu pelunasan" if lang_code == "ID" else "Customer payment discipline classification based on historical settlement timeliness",
        what_it_shows=(
            "Pemetaan 12.342 pelanggan ke dalam 4 profil perilaku: Pembayar Disiplin (Reliable Payer), Perlu Perhatian (Needs Attention), Risiko Tinggi / Macet (High Risk), dan Riwayat Terbatas (Insufficient History)."
            if lang_code == "ID" else
            "Mapping of 12,342 customers into 4 behavioral segments: Reliable Payer, Needs Attention, High Risk, and Insufficient History."
        ),
        why_important=(
            "Membantu tim Finance membedakan pelanggan yang terlambat sesekali dari pelanggan yang memiliki pola menunggak kronis, sehingga kebijakan kredit dan uang muka (DP) dapat diterapkan secara adil dan tepat sasaran."
            if lang_code == "ID" else
            "Helps Credit Control differentiate between occasional late payers and chronically delinquent accounts to set tailored credit policies and advance payment terms."
        ),
        simple_insight=(
            "Sebanyak 2.108 pelanggan terbukti disiplin membayar tepat waktu. Namun, 1.107 akun teridentifikasi Risiko Tinggi (High Risk) karena menunggak lebih dari 90 hari atau menahan lebih dari 50% nilai tagihannya."
            if lang_code == "ID" else
            "2,108 customers consistently pay reliably on time, while 1,107 accounts present High Risk with over 90-day delinquency or over 50% overdue balance."
        ),
        icon="👥"
    )

    # 4 Behavioral Category Stats
    beh_counts = df_cust["payment_behavior_segment"].value_counts()
    beh_outstanding = df_cust.groupby("payment_behavior_segment", observed=False)["outstanding_amount"].sum()

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        cnt_rel = beh_counts.get("Reliable Payer", 0)
        out_rel = beh_outstanding.get("Reliable Payer", 0.0)
        lbl_rel = "🌟 Pembayar Disiplin" if lang_code == "ID" else "🌟 Reliable Payer"
        sub_rel = f"{cnt_rel:,} akun (Sisa: {format_rupiah(out_rel)})"
        metric_card(title=lbl_rel, value=f"{cnt_rel:,}", delta="Disiplin Tinggi", delta_color="positive", subtext=sub_rel)

    with b2:
        cnt_att = beh_counts.get("Needs Attention", 0)
        out_att = beh_outstanding.get("Needs Attention", 0.0)
        lbl_att = "⚠️ Perlu Perhatian" if lang_code == "ID" else "⚠️ Needs Attention"
        sub_att = f"{cnt_att:,} akun (Sisa: {format_rupiah(out_att)})"
        metric_card(title=lbl_att, value=f"{cnt_att:,}", delta="Mulai Terlambat", delta_color="negative", subtext=sub_att)

    with b3:
        cnt_hr = beh_counts.get("High Risk", 0)
        out_hr = beh_outstanding.get("High Risk", 0.0)
        lbl_hr = "🚨 Risiko Tinggi (Macet)" if lang_code == "ID" else "🚨 High Risk Delinquent"
        sub_hr = f"{cnt_hr:,} akun (Sisa: {format_rupiah(out_hr)})"
        metric_card(title=lbl_hr, value=f"{cnt_hr:,}", delta="Overdue Kritis", delta_color="negative", subtext=sub_hr)

    with b4:
        cnt_ins = beh_counts.get("Insufficient History", 0)
        out_ins = beh_outstanding.get("Insufficient History", 0.0)
        lbl_ins = "📋 Riwayat Terbatas" if lang_code == "ID" else "📋 Insufficient History"
        sub_ins = f"{cnt_ins:,} akun (Sisa: {format_rupiah(out_ins)})"
        metric_card(title=lbl_ins, value=f"{cnt_ins:,}", subtext=sub_ins)

    st.markdown("---")

    col_b1, col_b2 = st.columns([1.2, 1])

    with col_b1:
        st.subheader("📊 " + ("Sebaran Piutang Berdasarkan Perilaku Pembayaran" if lang_code == "ID" else "Outstanding Receivables by Payment Behavior"))
        df_beh_agg = df_cust.groupby("payment_behavior_segment").agg(
            total_akun=("customer_id", "nunique"),
            total_piutang=("outstanding_amount", "sum"),
            total_overdue=("overdue_outstanding", "sum")
        ).reset_index().sort_values("total_piutang", ascending=False)

        beh_labels_map = {
            "High Risk": "🚨 Risiko Tinggi / Macet",
            "Needs Attention": "⚠️ Perlu Perhatian",
            "Reliable Payer": "🌟 Pembayar Disiplin",
            "Insufficient History": "📋 Riwayat Terbatas"
        }
        df_beh_agg["label_bersih"] = df_beh_agg["payment_behavior_segment"].map(beh_labels_map).fillna(df_beh_agg["payment_behavior_segment"])

        fig_beh = px.bar(
            df_beh_agg,
            x="total_piutang",
            y="label_bersih",
            orientation="h",
            text=df_beh_agg["total_piutang"].apply(format_rupiah),
            color="label_bersih",
            color_discrete_map={
                "🚨 Risiko Tinggi / Macet": "#EF4444",
                "⚠️ Perlu Perhatian": "#F59E0B",
                "🌟 Pembayar Disiplin": "#10B981",
                "📋 Riwayat Terbatas": "#94A3B8"
            }
        )
        fig_beh.update_traces(
            textposition="outside",
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>Total Piutang: Rp %{x:,.0f}<extra></extra>"
        )
        fig_beh.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title="Nominal Piutang (Rupiah)"
        )
        apply_plotly_theme(fig_beh, height=320)
        st.plotly_chart(fig_beh, use_container_width=True)

    with col_b2:
        st.subheader("⏱️ " + ("Ketepatan Waktu Pelunasan Invoice" if lang_code == "ID" else "Invoice Settlement Timeliness"))
        # Timeliness breakdown from core finance
        paid_invoices = df_finance[df_finance["invoice_status_norm"] == "paid"]
        on_time_invoices = len(paid_invoices[paid_invoices["paid_late_flag_eda"] == False])
        late_invoices = len(paid_invoices[paid_invoices["paid_late_flag_eda"] == True])
        
        pie_labels = [
            "Tepat Waktu / Sebelum Due Date" if lang_code == "ID" else "On Time / Early",
            "Terlambat Setelah Due Date" if lang_code == "ID" else "Late Payment"
        ]
        pie_vals = [on_time_invoices, late_invoices]
        pie_colors = ["#10B981", "#EF4444"]

        fig_timely = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_vals,
            hole=0.5,
            marker=dict(colors=pie_colors),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Jumlah Invoice: %{value:,}<br>Porsi: %{percent}<extra></extra>"
        )])
        apply_plotly_theme(fig_timely, height=320)
        st.plotly_chart(fig_timely, use_container_width=True)

    # Payment Methods Popularity
    st.subheader("💳 " + ("Metode Pembayaran Paling Sering Digunakan" if lang_code == "ID" else "Preferred Payment Channels & Gateways"))
    pm_filtered = df_finance[df_finance["payment_methods"].notnull() & (df_finance["payment_methods"] != "")]
    pm_counts = pm_filtered["payment_methods"].value_counts().head(10).reset_index()
    pm_counts.columns = ["payment_method", "invoice_count"]

    fig_pm = px.bar(
        pm_counts,
        x="invoice_count",
        y="payment_method",
        orientation="h",
        text=pm_counts["invoice_count"].apply(lambda x: f"{x:,} faktur"),
        color="invoice_count",
        color_continuous_scale="Viridis"
    )
    fig_pm.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Jumlah Transaksi: %{x:,}<extra></extra>"
    )
    fig_pm.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Jumlah Transaksi Invoice" if lang_code == "ID" else "Number of Invoices",
        yaxis_title="",
        coloraxis_showscale=False
    )
    apply_plotly_theme(fig_pm, height=340)
    st.plotly_chart(fig_pm, use_container_width=True)

# =============================================================
# TAB 4: PRIORITY COLLECTION WORKLIST
# =============================================================
with tab4:
    render_section_info(
        title="Daftar Kerja Prioritas Penagihan (Collection Action Worklist)" if lang_code == "ID" else "Operational Collection Action Worklist",
        subtitle="Daftar akun pelanggan dengan eksposur tunggakan tertinggi yang membutuhkan tindak lanjut segera" if lang_code == "ID" else "Actionable worklist of debtor accounts sorted by overdue exposure requiring immediate intervention",
        what_it_shows=(
            "Daftar akun teratas dengan sisa piutang dan overdue terbesar, dilengkapi status segmen perilaku dan rekomendasi tindakan penagihan konkret."
            if lang_code == "ID" else
            "Prioritized ledger of high-exposure debtor accounts complete with overdue age and recommended collection actions."
        ),
        why_important=(
            "Memberikan panduan operasional harian bagi staf Finance & Collection: akun mana yang harus ditelepon hari ini, akun mana yang harus dikirim Surat Peringatan (SP), dan akun mana yang harus ditahan pesanan barunya."
            if lang_code == "ID" else
            "Empowers daily credit control operations with specific accounts to call, demand letters to send, and accounts requiring new order credit blocks."
        ),
        simple_insight=(
            "10 pelanggan dengan piutang terbesar menyumbang miliaran rupiah piutang menunggak. Fokus penagihan intensif pada segelintir akun kunci ini akan langsung memulihkan mayoritas arus kas Cetakia."
            if lang_code == "ID" else
            "The top 10 debtors hold the vast majority of overdue value. Targeted collection on these key accounts delivers maximum cash recovery."
        ),
        icon="🎯"
    )

    # Filter Controls for Worklist
    wl_col1, wl_col2, wl_col3 = st.columns([1.5, 1, 1])

    with wl_col1:
        search_query = st.text_input(
            "🔍 " + ("Cari Nama Pelanggan:" if lang_code == "ID" else "Search Customer Name:"),
            placeholder="Ketik nama pelanggan / PT / CV...",
            key="worklist_search_input"
        )

    with wl_col2:
        risk_filter = st.selectbox(
            "Kategori Risiko:" if lang_code == "ID" else "Risk Category:",
            options=["Semua Kategori", "Risiko Tinggi (High Risk)", "Perlu Perhatian (Needs Attention)", "Pembayar Disiplin (Reliable)"] if lang_code == "ID"
            else ["All Categories", "High Risk", "Needs Attention", "Reliable Payer"],
            index=0,
            key="worklist_risk_filter"
        )

    with wl_col3:
        top_n = st.selectbox(
            "Tampilkan:" if lang_code == "ID" else "Show Top:",
            options=[10, 25, 50, 100, "Semua Data / All"],
            index=1,
            key="worklist_top_n"
        )

    # Filter Worklist Data
    df_wl = df_cust[df_cust["outstanding_amount"] > 0].copy()

    if search_query:
        df_wl = df_wl[df_wl["customer_name"].astype(str).str.lower().str.contains(search_query.lower())]

    if risk_filter in ["Risiko Tinggi (High Risk)", "High Risk"]:
        df_wl = df_wl[df_wl["payment_behavior_segment"] == "High Risk"]
    elif risk_filter in ["Perlu Perhatian (Needs Attention)", "Needs Attention"]:
        df_wl = df_wl[df_wl["payment_behavior_segment"] == "Needs Attention"]
    elif risk_filter in ["Pembayar Disiplin (Reliable)", "Reliable Payer"]:
        df_wl = df_wl[df_wl["payment_behavior_segment"] == "Reliable Payer"]

    df_wl = df_wl.sort_values(["overdue_outstanding", "outstanding_amount", "max_days_overdue"], ascending=False)

    if top_n != "Semua Data / All":
        df_wl_view = df_wl.head(int(top_n)).copy()
    else:
        df_wl_view = df_wl.copy()

    # Priority Metric Summary Strip
    total_wl_out = float(df_wl["outstanding_amount"].sum())
    total_wl_over = float(df_wl["overdue_outstanding"].sum())
    total_wl_accounts = len(df_wl)
    critical_90_count = len(df_wl[df_wl["max_days_overdue"] > 90])

    render_summary_strip([
        {
            "label": "Total Akun Berpiutang" if lang_code == "ID" else "Debtor Accounts",
            "value": f"{total_wl_accounts:,} Akun",
            "desc": "Memiliki sisa tagihan belum lunas",
            "color": "#3B82F6"
        },
        {
            "label": "Total Nilai Piutang" if lang_code == "ID" else "Total Receivable",
            "value": format_rupiah(total_wl_out),
            "desc": "Nilai potensi pemulihan kas",
            "color": "#10B981"
        },
        {
            "label": "Nilai Overdue Terancam" if lang_code == "ID" else "Overdue Exposure",
            "value": format_rupiah(total_wl_over),
            "desc": "Tagihan lewat tanggal jatuh tempo",
            "color": "#EF4444"
        },
        {
            "label": "Akun Menunggak >90 Hari" if lang_code == "ID" else "90+ Day Delinquent Accounts",
            "value": f"{critical_90_count:,} Akun",
            "desc": "Prioritas eskalasi penagihan kritis",
            "color": "#F97316"
        }
    ])

    # Top 10 Debtor Chart
    if len(df_wl) > 0:
        top10_chart_df = df_wl.head(10).sort_values("outstanding_amount", ascending=True)
        fig_top_deb = px.bar(
            top10_chart_df,
            x="outstanding_amount",
            y="customer_name",
            orientation="h",
            text=top10_chart_df["outstanding_amount"].apply(format_rupiah),
            color="overdue_outstanding",
            color_continuous_scale="Reds",
            title="10 Pelanggan dengan Piutang Tertinggi" if lang_code == "ID" else "Top 10 Outstanding Debtor Accounts"
        )
        fig_top_deb.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Total Piutang: Rp %{x:,.0f}<extra></extra>"
        )
        fig_top_deb.update_layout(
            xaxis_title="Nominal Piutang (Rupiah)",
            yaxis_title="",
            coloraxis_showscale=False
        )
        apply_plotly_theme(fig_top_deb, height=360)
        st.plotly_chart(fig_top_deb, use_container_width=True)

    # Action Recommendation Generator Function
    def assign_action_recommendation(row):
        seg = row.get("payment_behavior_segment", "")
        max_days = float(row.get("max_days_overdue", 0))
        out_amt = float(row.get("outstanding_amount", 0))
        cat = str(row.get("customer_category", "")).upper()
        
        if cat == "DIVISI":
            return "🔄 Rekonsiliasi Jurnal Transfer Antar-Cabang (Aliran Internal)"
        
        if max_days > 90 or seg == "High Risk":
            if out_amt >= 100000000:
                return "🚨 Tahan Order Baru (Hold Production) + Kunjungan Direksi & Legal SP3"
            elif out_amt >= 20000000:
                return "⚠️ Kirim Surat Peringatan (SP2) + Jadwalkan Pertemuan Finance & Sales"
            else:
                return "📞 Telepon Khusus Penagihan & Wajibkan Bayar Lunas Sebelum Cetak Ulang"
        elif seg == "Needs Attention":
            return "📱 Kirim Pengingat WhatsApp Resmi + Konfirmasi Rencana Tanggal Transfer"
        elif seg == "Reliable Payer":
            return "✅ Pelanggan Disiplin: Berikan Konfirmasi Tagihan Rutin via Email"
        else:
            return "ℹ️ Wajibkan Uang Muka (DP 50%) atau Pelunasan Sebelum Ambil Barang"

    df_wl_view["Rekomendasi Tindakan Bisnis"] = df_wl_view.apply(assign_action_recommendation, axis=1)

    # Build Clean Readable Table
    table_cols = [
        "customer_name",
        "customer_category",
        "division_name",
        "billed_amount",
        "outstanding_amount",
        "overdue_outstanding",
        "max_days_overdue",
        "payment_behavior_segment",
        "Rekomendasi Tindakan Bisnis"
    ]
    df_wl_display = df_wl_view[table_cols].copy()
    df_wl_display.columns = [
        "Nama Pelanggan",
        "Segmen",
        "Cabang",
        "Total Tagihan",
        "Sisa Piutang",
        "Piutang Overdue",
        "Telat Terlama (Hari)",
        "Status Perilaku",
        "Rekomendasi Tindakan Penagihan"
    ]

    # Format Currency for Display
    df_wl_display["Total Tagihan"] = df_wl_display["Total Tagihan"].apply(format_rupiah)
    df_wl_display["Sisa Piutang"] = df_wl_display["Sisa Piutang"].apply(format_rupiah)
    df_wl_display["Piutang Overdue"] = df_wl_display["Piutang Overdue"].apply(format_rupiah)
    df_wl_display["Telat Terlama (Hari)"] = df_wl_display["Telat Terlama (Hari)"].apply(lambda x: f"{int(round(float(x)))} Hari" if pd.notnull(x) else "-")

    st.dataframe(df_wl_display, use_container_width=True, hide_index=True)

    # Export Worklist CSV
    csv_data = df_wl_view.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 " + ("Unduh Daftar Kerja Penagihan (.CSV)" if lang_code == "ID" else "Download Collection Worklist (.CSV)"),
        data=csv_data,
        file_name="cetakia_collection_priority_worklist.csv",
        mime="text/csv"
    )

# =============================================================
# TAB 5: DATA QUALITY & EXCEPTION AUDIT
# =============================================================
with tab5:
    render_section_info(
        title="Audit Kualitas Data Finansial (Financial Data Quality & Exception Audit)" if lang_code == "ID" else "Financial Data Quality & Exception Audit",
        subtitle="Identifikasi 1.121 kasus anomali pencatatan transaksi kas dan tagihan untuk perbaikan operasional" if lang_code == "ID" else "Identification of 1,121 financial data quality exceptions to maintain authoritative decision accuracy",
        what_it_shows=(
            "Pemantauan 4 jenis pengecualian data: Tanggal Bayar Mendahului Invoice, Status Lunas Namun Masih Ada Sisa, Penerimaan Melebihi Nilai Tagihan (Overpayment), dan Invoice Batal yang Memiliki Receipt."
            if lang_code == "ID" else
            "Monitoring of 4 core financial exceptions: Payment before invoice date, Paid-status with remaining balance, Overpayment, and Cancelled invoices with active receipts."
        ),
        why_important=(
            "Pengecualian data tidak otomatis berarti korupsi atau fraud. Seringkali ini disebabkan oleh alur bisnis riil: uang muka (DP) sebelum invoice terbit, revisi invoice, atau pembulatan kasir. Memantau exception memastikan data BI tetap akurat dan akuntabel."
            if lang_code == "ID" else
            "Exceptions do not necessarily indicate error; they frequently arise from legitimate operational workflows like advance customer deposits, invoice amendments, or cashier rounding."
        ),
        simple_insight=(
            "Sebanyak 808 kasus adalah pembayaran mendahului invoice (DP/Uang Muka), dan 228 kasus adalah invoice berstatus 'paid' namun masih tercatat selisih sisa kecil. Rekonsiliasi rutin kasir akan meniadakan selisih ini."
            if lang_code == "ID" else
            "808 exceptions represent advance prepayments prior to final billing, while 228 reflect tiny residual allocations on paid invoices requiring simple cashier reconciliation."
        ),
        icon="🔍"
    )

    # Exception Counts
    exc_type_counts = df_exc["exception_type"].value_counts()
    
    cnt_early = exc_type_counts.get("Payment date earlier than invoice date", 0)
    cnt_paid_out = exc_type_counts.get("Invoice status PAID but still outstanding", 0)
    cnt_overpaid = exc_type_counts.get("Receipt exceeds invoice value", 0)
    cnt_cancel_rec = exc_type_counts.get("Cancelled invoice has receipt", 0)

    e1, e2, e3, e4 = st.columns(4)

    with e1:
        lbl_e1 = "⏰ Bayar Sebelum Invoice" if lang_code == "ID" else "⏰ Prepayment / Early"
        sub_e1 = "Uang muka (DP) diterima sebelum faktur terbit" if lang_code == "ID" else "Down payments prior to invoice"
        metric_card(title=lbl_e1, value=f"{cnt_early:,} Kasus", subtext=sub_e1)

    with e2:
        lbl_e2 = "⚠️ Status Lunas Ada Sisa" if lang_code == "ID" else "⚠️ Paid with Residual"
        sub_e2 = "Faktur 'paid' namun tercatat sisa selisih" if lang_code == "ID" else "Status paid with remaining balance"
        metric_card(title=lbl_e2, value=f"{cnt_paid_out:,} Kasus", delta_color="negative", subtext=sub_e2)

    with e3:
        lbl_e3 = "💸 Pembayaran Lebih (Over)" if lang_code == "ID" else "💸 Overpayment"
        sub_e3 = "Uang diterima melebihi nilai tagihan" if lang_code == "ID" else "Receipts exceed invoice amount"
        metric_card(title=lbl_e3, value=f"{cnt_overpaid:,} Kasus", delta_color="negative", subtext=sub_e3)

    with e4:
        lbl_e4 = "🚫 Batal Punya Receipt" if lang_code == "ID" else "🚫 Cancelled with Receipt"
        sub_e4 = "Invoice cancel namun tercatat kas masuk" if lang_code == "ID" else "Cancelled invoice with recorded cash"
        metric_card(title=lbl_e4, value=f"{cnt_cancel_rec:,} Kasus", delta_color="negative", subtext=sub_e4)

    st.markdown("---")

    # Interactive Exception Filter & Table
    st.subheader("📋 " + ("Daftar Detail Pengecualian Data Keuangan" if lang_code == "ID" else "Financial Data Quality Audit Log"))

    exc_filter_options = [
        "Semua Jenis Pengecualian" if lang_code == "ID" else "All Exception Types",
        "Payment date earlier than invoice date",
        "Invoice status PAID but still outstanding",
        "Receipt exceeds invoice value",
        "Cancelled invoice has receipt"
    ]
    selected_exc_filter = st.selectbox(
        "Filter Jenis Pengecualian:" if lang_code == "ID" else "Filter Exception Type:",
        options=exc_filter_options,
        index=0,
        key="exc_type_selector"
    )

    df_exc_view = df_exc.copy()
    if selected_exc_filter != exc_filter_options[0]:
        df_exc_view = df_exc_view[df_exc_view["exception_type"] == selected_exc_filter]

    # Readable Translation for Exception Types
    exc_type_trans = {
        "Payment date earlier than invoice date": "⏰ Tanggal Bayar Lebih Awal dari Invoice (DP / Pre-order)",
        "Invoice status PAID but still outstanding": "⚠️ Status Faktur PAID tapi Masih Tercatat Sisa Piutang",
        "Receipt exceeds invoice value": "💸 Penerimaan Kas Melebihi Nilai Tagihan (Overpayment)",
        "Cancelled invoice has receipt": "🚫 Faktur Dibatalkan (Cancel) Namun Memiliki Bukti Bayar"
    }

    df_exc_display = df_exc_view[[
        "invoice_code",
        "customer_name",
        "customer_category",
        "division_name",
        "invoice_date",
        "invoice_amount_clean",
        "settled_amount_eda",
        "outstanding_eda",
        "exception_type"
    ]].copy()

    df_exc_display["exception_type_readable"] = df_exc_display["exception_type"].map(exc_type_trans).fillna(df_exc_display["exception_type"])

    df_exc_display = df_exc_display[[
        "invoice_code",
        "customer_name",
        "customer_category",
        "division_name",
        "invoice_date",
        "invoice_amount_clean",
        "settled_amount_eda",
        "outstanding_eda",
        "exception_type_readable"
    ]]

    df_exc_display.columns = [
        "No. Invoice",
        "Nama Pelanggan",
        "Segmen",
        "Cabang",
        "Tanggal Invoice",
        "Nilai Tagihan",
        "Kas Masuk",
        "Sisa Piutang",
        "Jenis Pengecualian (Audit)"
    ]

    df_exc_display["Nilai Tagihan"] = df_exc_display["Nilai Tagihan"].apply(format_rupiah)
    df_exc_display["Kas Masuk"] = df_exc_display["Kas Masuk"].apply(format_rupiah)
    df_exc_display["Sisa Piutang"] = df_exc_display["Sisa Piutang"].apply(format_rupiah)
    df_exc_display["Tanggal Invoice"] = pd.to_datetime(df_exc_display["Tanggal Invoice"]).dt.strftime("%d %b %Y")

    st.dataframe(df_exc_display.head(200), use_container_width=True, hide_index=True)
    st.caption(
        f"Menampilkan {min(len(df_exc_display), 200)} dari total {len(df_exc_display)} kasus pengecualian data."
        if lang_code == "ID" else
        f"Displaying {min(len(df_exc_display), 200)} of {len(df_exc_display)} total exception records."
    )

    # Standard Operating Procedures & Guidance for Finance
    st.markdown("---")
    st.subheader("💡 " + ("Rekomendasi Standar Operasional Prosedur (SOP) Keuangan" if lang_code == "ID" else "Standard Operating Procedures (SOP) for Finance & Cashiers"))

    sop_col1, sop_col2 = st.columns(2)

    with sop_col1:
        st.markdown("""
        <div class="cetakia-card" style="padding: 18px;">
            <h4 style="color: #3B82F6; margin-top: 0;">1. Alur Uang Muka & Pre-order (DP)</h4>
            <p style="font-size: 13.5px; line-height: 1.6;">
                Untuk 808 transaksi di mana pembayaran diterima sebelum invoice final terbit:
                Pastikan kasir menggunakan modul <b>Down Payment (DP) Receipt</b> resmi dan mengaitkan nomor DP saat faktur final dicetak, sehingga tanggal receipt tidak dianggap anomali backdated.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cetakia-card" style="padding: 18px;">
            <h4 style="color: #F59E0B; margin-top: 0;">2. Rekonsiliasi Selisih Pembulatan Invoice Lunas</h4>
            <p style="font-size: 13.5px; line-height: 1.6;">
                Untuk 228 transaksi berstatus 'paid' namun tercatat sisa piutang kecil:
                Lakukan write-off selisih pembulatan (di bawah Rp 1.000) atau penyesuaian potongan diskon kasir pada akhir hari kerja (End-of-Day Closing).
            </p>
        </div>
        """, unsafe_allow_html=True)

    with sop_col2:
        st.markdown("""
        <div class="cetakia-card" style="padding: 18px;">
            <h4 style="color: #EF4444; margin-top: 0;">3. Penanganan Pembayaran Lebih (Overpayment)</h4>
            <p style="font-size: 13.5px; line-height: 1.6;">
                Untuk 57 transaksi dengan pembayaran melebihi nilai tagihan:
                Catat kelebihan dana sebesar Rp 6,01 Juta sebagai <b>Saldo Deposit Pelanggan (Customer Credit)</b> untuk pesanan berikutnya, atau lakukan proses transfer pengembalian dana (refund) resmi.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cetakia-card" style="padding: 18px;">
            <h4 style="color: #8B5CF6; margin-top: 0;">4. SOP Pembatalan Invoice yang Memiliki Bukti Bayar</h4>
            <p style="font-size: 13.5px; line-height: 1.6;">
                Untuk 28 invoice batal yang tercatat memiliki uang masuk:
                Wajibkan otorisasi Manajer Keuangan sebelum status diubah menjadi 'cancel'. Pastikan kwitansi pembayaran telah di-void atau dana telah dikembalikan dengan bukti transfer sah.
            </p>
        </div>
        """, unsafe_allow_html=True)
