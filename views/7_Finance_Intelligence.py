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
    ic_insight = f"The primary financial challenge is the substantial gap between invoiced sales and actual cash collected (collection rate {collection_rate:.1f}%). Receivables are heavily concentrated in the INDUSTRI segment and internal DIVISI transfers, where over {overdue_90plus_pct:.1f}% of outstanding balances have aged past 90 days."
    ic_impacted = "Finance & Credit Control, Key Account Executives, Branch Managers, and Corporate Working Capital."
    ic_action = "Finance & Sales Management: Implement strict multi-tiered collection workflows. Isolate internal division flows from commercial KPI; require executive-level intervention and credit holds on 90+ day overdue accounts exceeding Rp 50 Million."
    ic_badge = "FINANCIAL DECISION SUPPORT"
    ic_target = f"{format_rupiah(overdue_90plus)} in 90+ Days Aging Bucket requiring structured collection escalation"
else:
    ic_title = "Realitas Konversi Kas & Eskalasi Penagihan Piutang Menunggak >90 Hari"
    ic_metric = f"{format_rupiah(total_overdue)} Piutang Lewat Jatuh Tempo ({overdue_ratio:.1f}% dari Piutang, {format_rupiah(overdue_90plus)} di Bucket >90 Hari)"
    ic_context = f"Dianalisis dari {total_invoices_count:,} invoice senilai {format_rupiah(total_billed)} pada Cabang '{filters['branch']}', Segmen '{filters['segment']}', dan Cakupan '{selected_scope}'."
    ic_insight = f"Tantangan finansial utama Cipta Grafika bukan pada minimnya pesanan, melainkan lebarnya jarak antara invoice diterbitkan dengan kas yang berhasil direalisasikan (kolektibilitas {collection_rate:.1f}%). Sebanyak {overdue_90plus_pct:.1f}% piutang telah menumpuk lebih dari 90 hari, didominasi oleh segmen INDUSTRI dan transaksi internal DIVISI."
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
    st.subheader("📈 " + ("Metode 1: Pelacakan Kohor Faktur (Efektivitas Penagihan & Risiko Piutang)" if lang_code == "ID" else "Method 1: Invoice Cohort Tracking (Collection Rate & Credit Quality)"))
    st.caption(
        "💡 Catatan Metodologi Kohor: Melacak realisasi kas berdasarkan bulan penerbitan invoice. Kas Masuk (Settled) secara matematis selalu ≤ Nilai Tagihan (Billed) karena faktur tidak dapat lunas melebihi 100% nilainya. Invoice bulan terbaru secara wajar memiliki tingkat pelunasan lebih rendah karena baru saja diterbitkan dan belum melewati tanggal jatuh tempo."
        if lang_code == "ID" else
        "💡 Cohort Methodology Note: Tracks cash realization by invoice issuance month. Settled Cash mathematically cannot exceed Billed Amount (capped at 100%). Recent invoice cohorts naturally show lower settlement rates because they have had less time to mature."
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

        with st.expander(
            "💡 Penjelasan Metodologi: Mengapa Kas Nyata Masuk (Settled) Selalu ≤ Tagihan Diterbitkan? (Beda Kohor vs Kas Kalender)"
            if lang_code == "ID" else
            "💡 Methodology Note: Why Settled Cash is Always ≤ Billed Amount (Cohort vs Calendar Cash Inflow)"
        ):
            if lang_code == "ID":
                st.markdown("""
                **Memahami Perbedaan Visualisasi Kohor (Streamlit) vs Laporan Penerimaan Kas Kalender (ERP/cetakia.com):**
                
                1. **Pendekatan Kohor Penerbitan Invoice (*Invoice Cohort Tracking* di Grafik Ini):**
                   - Sumbu waktu **bukan** tanggal penerimaan uang, melainkan **bulan penerbitan faktur (`invoice_month`)**.
                   - Batang hijau (*Kas Nyata Masuk / Settled*) melacak: *Dari seluruh faktur yang diterbitkan pada bulan tersebut, berapa banyak nominalnya yang sudah berhasil dilunasi hingga hari ini?*
                   - Secara kaidah matematika dan audit EDA: `settled_amount = min(paid_amount, invoice_amount)`. Pelunasan sebuah faktur **tidak pernah boleh melebihi 100% nilai fakturnya sendiri**. Maka secara absolut, Kas Nyata Masuk selalu **≤** Total Tagihan Diterbitkan. Selisihnya merupakan sisa piutang berjalan (*outstanding*).
                
                2. **Mengapa pada Grafik Arus Kas Kalender ERP (cetakia.com) Penerimaan (*Receipts*) Bisa Lebih Besar dari Penjualan (*Sales*)?**
                   - Pada grafik kalender kas (seperti di *cetakia.com* pada bulan April, Mei, dan Oktober), batang hijau adalah **Total Uang Masuk ke Rekening/Kasir pada Bulan Tersebut** (berdasarkan `payment_date`), sedangkan batang biru adalah **Total Penjualan Baru yang Diterbitkan pada Bulan Tersebut** (berdasarkan `invoice_date`).
                   - **Pelunasan Lintas Periode (*Lagged Collection*):** Ketika pelanggan dengan termin tempo 30–90 hari (seperti segmen Industri/Instansi) melunasi faktur-faktur besar dari bulan sebelumnya (misal faktur Februari & Maret baru ditransfer di bulan April/Mei), uang tunai riil yang masuk di bulan tersebut menjadi sangat tinggi, bahkan melampaui penjualan baru bulan itu.
                   - **Awal Bulan Berjalan (Contoh: Oktober):** Di awal bulan berjalan, penjualan baru baru tercatat sedikit (misal 1–3 hari pertama), namun kasir/bank terus menerima pembayaran pelunasan piutang jatuh tempo bulan-bulan sebelumnya, sehingga *Receipts > Sales* secara alami dan valid secara arus kas riil.
                """)
            else:
                st.markdown("""
                **Understanding the Difference: Cohort Visualization (Streamlit) vs. Calendar Cash Receipts (ERP/cetakia.com):**
                
                1. **Invoice Cohort Tracking (This Chart):**
                   - The time axis is the **invoice issue month (`invoice_month`)**, NOT the payment date.
                   - The green bar (*Collected Cash / Settled*) tracks: *Out of the total invoices issued in that cohort month, how much has been settled to date?*
                   - By EDA mathematical constraint: `settled_amount = min(paid_amount, invoice_amount)`. An invoice settlement cannot exceed 100% of its face value. Therefore, settled cash is always **≤** billed amount.
                
                2. **Why Can Receipts Exceed Sales on ERP Calendar Cash Trend (cetakia.com)?**
                   - On ERP calendar cash flow charts (e.g. April, May, October on *cetakia.com*), Receipts represent **actual cash collected in that calendar month** (by `payment_date`), while Sales represent **invoices issued in that calendar month** (by `invoice_date`).
                   - **Cross-Period Receivable Collections:** When clients on credit terms pay down large backlogged invoices from prior months, the actual cash deposited in the bank during that month can easily surpass newly issued sales invoices.
                   - **Early Month Phenomenon (e.g. October):** In the first few days of a month, new sales have just begun accumulating, but historical collections flow in continuously, causing Receipts to naturally exceed Sales.
                """)

    # =========================================================
    # METHOD 2: CALENDAR CASH FLOW AR TREND (CETAKIA ERP MODEL)
    # =========================================================
    st.markdown("---")
    st.subheader("🏦 " + ("Metode 2: Tren Arus Kas Kalender — Penjualan Baru vs. Realisasi Kas Masuk (Model ERP Cetakia)" if lang_code == "ID" else "Method 2: Calendar Cash Flow Trend — New Sales vs. Actual Cash Inflow (Cetakia ERP Model)"))
    
    st.caption(
        "💡 **Mengapa Grafik Ini Dihadirkan?** Berbeda dari metode Kohor di atas yang mengikat uang ke faktur lahirnya, grafik Arus Kas Kalender ini mencatat **uang tunai riil yang masuk rekening/kasir pada bulan berjalan** (berdasarkan `payment_date`) berbanding **penjualan baru** (berdasarkan `invoice_date`). Pada model kalender ini, **Penerimaan (Receipts) SANGAT WAJAR & VALID melampaui Penjualan (Sales)** ketika kasir menerima pencairan pelunasan piutang tempo bulan-bulan sebelumnya."
        if lang_code == "ID" else
        "💡 **Why This Chart Exists:** Unlike the Cohort method which attributes cash back to the invoice issuance month, this Calendar Cash Flow chart captures **actual cash deposited into bank/cashier in that calendar month** (by payment date) vs **newly issued sales invoices** (by invoice date). Under this calendar model, **Receipts CAN NATURALLY & VALIDLY EXCEED Sales** when clients settle large backlogged invoices from prior months."
    )

    if "invoice_date" in df_finance.columns and "last_payment_date" in df_finance.columns:
        df_fin_cal = df_finance.copy()
        df_fin_cal["inv_m"] = df_fin_cal["invoice_date"].dt.strftime("%Y-%m")
        df_fin_cal["pay_m"] = df_fin_cal["last_payment_date"].dt.strftime("%Y-%m")
        
        cal_sales_series = df_fin_cal.groupby("inv_m")["invoice_amount_clean"].sum()
        cal_inv_counts = df_fin_cal.groupby("inv_m")["invoice_id"].nunique()
        
        valid_pay = df_fin_cal[df_fin_cal["pay_m"].notnull()]
        cal_rec_series = valid_pay.groupby("pay_m")["paid_raw_clean"].sum()
        cal_pay_counts = valid_pay.groupby("pay_m")["invoice_id"].nunique()
        
        # Use active sales months to ensure relevant operational scope
        active_cal_months = sorted(list(set(cal_sales_series.index)))
        if not active_cal_months:
            active_cal_months = sorted(list(set(cal_rec_series.index)))
            
        cal_df = pd.DataFrame(index=active_cal_months)
        cal_df["month"] = cal_df.index
        cal_df["sales"] = cal_df["month"].map(cal_sales_series).fillna(0.0)
        cal_df["receipts"] = cal_df["month"].map(cal_rec_series).fillna(0.0)
        cal_df["inv_count"] = cal_df["month"].map(cal_inv_counts).fillna(0).astype(int)
        cal_df["pay_count"] = cal_df["month"].map(cal_pay_counts).fillna(0).astype(int)
        
        cal_df["net_cash"] = cal_df["receipts"] - cal_df["sales"]
        cal_df["ratio_pct"] = np.where(cal_df["sales"] > 0, (cal_df["receipts"] / cal_df["sales"]) * 100, 0.0)

        if not cal_df.empty and (cal_df["sales"].sum() > 0 or cal_df["receipts"].sum() > 0):
            # Calendar Cash Flow Summary Strip
            tot_cal_sales = float(cal_df["sales"].sum())
            tot_cal_rec = float(cal_df["receipts"].sum())
            tot_cal_net = tot_cal_rec - tot_cal_sales
            surplus_count = int((cal_df["net_cash"] > 0).sum())
            
            peak_row = cal_df.loc[cal_df["receipts"].idxmax()]
            peak_m = peak_row["month"]
            peak_rec_val = float(peak_row["receipts"])
            
            strip_cal = [
                {
                    "label": "Total Penjualan Baru" if lang_code == "ID" else "Total New Sales Billed",
                    "value": format_rupiah(tot_cal_sales),
                    "desc": f"{cal_df['inv_count'].sum():,} faktur terbit" if lang_code == "ID" else f"{cal_df['inv_count'].sum():,} invoices billed",
                    "color": "#3B82F6"
                },
                {
                    "label": "Total Kas Riil Masuk" if lang_code == "ID" else "Total Realized Receipts",
                    "value": format_rupiah(tot_cal_rec),
                    "desc": f"{cal_df['pay_count'].sum():,} pembayaran disetor" if lang_code == "ID" else f"{cal_df['pay_count'].sum():,} payments deposited",
                    "color": "#10B981"
                },
                {
                    "label": "Net Arus Kas Kalender" if lang_code == "ID" else "Net Cash Balance",
                    "value": (f"+{format_rupiah(tot_cal_net)}" if tot_cal_net >= 0 else format_rupiah(tot_cal_net)),
                    "desc": ("Surplus kas riil (+Rp)" if tot_cal_net >= 0 else "Defisit kas kalender (-Rp)") if lang_code == "ID" else ("Net Cash Surplus" if tot_cal_net >= 0 else "Net Cash Deficit"),
                    "color": "#10B981" if tot_cal_net >= 0 else "#EF4444"
                },
                {
                    "label": "Penerimaan Kas Puncak" if lang_code == "ID" else "Peak Cash Inflow Month",
                    "value": f"{peak_m}",
                    "desc": f"{format_rupiah(peak_rec_val)} ({surplus_count} bln surplus)" if lang_code == "ID" else f"{format_rupiah(peak_rec_val)} ({surplus_count} surplus mos)",
                    "color": "#F59E0B"
                }
            ]
            render_summary_strip(strip_cal)

            # Secondary Axis Switcher
            c_sel1, c_sel2 = st.columns([2, 1])
            with c_sel1:
                axis_opt = st.radio(
                    "Pilih Metrik Indikator (Sumbu Kanan):" if lang_code == "ID" else "Secondary Axis Indicator:",
                    options=[
                        "Selisih Bersih Kas (Receipts − Sales dalam Rupiah)" if lang_code == "ID" else "Net Cash Difference (Receipts − Sales in IDR)",
                        "Rasio Kas Masuk vs Penjualan (%)" if lang_code == "ID" else "Cash-to-Sales Ratio (%)"
                    ],
                    horizontal=True,
                    key="cal_cash_axis_mode"
                )

            # Build Custom Hover Data for Unambiguous Clarity
            custom_sales_cal = []
            custom_rec_cal = []
            
            for _, r in cal_df.iterrows():
                net_val = r["net_cash"]
                net_str = f"+Rp {net_val:,.0f}" if net_val >= 0 else f"-Rp {abs(net_val):,.0f}"
                is_surplus = net_val > 0
                
                if lang_code == "ID":
                    status_lbl = "Surplus Kas (Receipts > Sales)" if is_surplus else "Defisit Kalender (Sales > Receipts)"
                    reason_desc = (
                        "Pencairan pelunasan piutang tempo bulan-bulan sebelumnya cair masif."
                        if is_surplus else
                        "Penjualan baru bertempo kredit belum memasuki tanggal jatuh tempo."
                    )
                else:
                    status_lbl = "Cash Surplus (Receipts > Sales)" if is_surplus else "Calendar Deficit (Sales > Receipts)"
                    reason_desc = (
                        "Heavy collections of past backlogged invoices deposited."
                        if is_surplus else
                        "Recent credit sales remain within customer credit terms."
                    )
                    
                custom_sales_cal.append([r["receipts"], net_str, r["ratio_pct"], status_lbl, reason_desc])
                custom_rec_cal.append([r["sales"], net_str, r["ratio_pct"], status_lbl, reason_desc])

            fig_cal = go.Figure()
            
            # Trace 1: Sales Bar (Invoice Date)
            fig_cal.add_trace(go.Bar(
                x=cal_df["month"],
                y=cal_df["sales"],
                name="Penjualan Baru (Invoice Date)" if lang_code == "ID" else "New Sales (Invoice Date)",
                marker_color="#3B82F6",
                customdata=custom_sales_cal,
                hovertemplate=(
                    "<b>Bulan: %{x}</b><br>" +
                    ("Penjualan Baru: Rp %{y:,.0f}<br>" if lang_code == "ID" else "New Invoiced Sales: Rp %{y:,.0f}<br>") +
                    ("Kas Masuk Riil: Rp %{customdata[0]:,.0f}<br>" if lang_code == "ID" else "Actual Cash Receipts: Rp %{customdata[0]:,.0f}<br>") +
                    ("Selisih Kas: %{customdata[1]}<br>" if lang_code == "ID" else "Net Cash Delta: %{customdata[1]}<br>") +
                    ("Rasio Kas/Sales: %{customdata[2]:.1f}%<extra></extra>" if lang_code == "ID" else "Cash/Sales Ratio: %{customdata[2]:.1f}%<extra></extra>")
                )
            ))
            
            # Trace 2: Receipts Bar (Payment Date)
            fig_cal.add_trace(go.Bar(
                x=cal_df["month"],
                y=cal_df["receipts"],
                name="Kas Riil Masuk (Payment Date)" if lang_code == "ID" else "Actual Receipts (Payment Date)",
                marker_color="#10B981",
                customdata=custom_rec_cal,
                hovertemplate=(
                    "<b>Bulan: %{x}</b><br>" +
                    ("Kas Masuk Riil: Rp %{y:,.0f}<br>" if lang_code == "ID" else "Actual Cash Receipts: Rp %{y:,.0f}<br>") +
                    ("Penjualan Baru: Rp %{customdata[0]:,.0f}<br>" if lang_code == "ID" else "New Invoiced Sales: Rp %{customdata[0]:,.0f}<br>") +
                    ("Selisih Kas: %{customdata[1]}<br>" if lang_code == "ID" else "Net Cash Delta: %{customdata[1]}<br>") +
                    ("Status: <b>%{customdata[3]}</b><br>" if lang_code == "ID" else "Status: <b>%{customdata[3]}</b><br>") +
                    ("💡 <i>%{customdata[4]}</i><extra></extra>" if lang_code == "ID" else "💡 <i>%{customdata[4]}</i><extra></extra>")
                )
            ))
            
            # Trace 3: Secondary Axis Indicator
            is_net_mode = "Selisih" in axis_opt or "Difference" in axis_opt
            if is_net_mode:
                fig_cal.add_trace(go.Scatter(
                    x=cal_df["month"],
                    y=cal_df["net_cash"],
                    name="Net Arus Kas (Receipts − Sales)" if lang_code == "ID" else "Net Cash Flow (Receipts − Sales)",
                    yaxis="y2",
                    mode="lines+markers+text",
                    text=[(f"+Rp {v/1e6:.1f}M" if v >= 0 else f"-Rp {abs(v)/1e6:.1f}M") for v in cal_df["net_cash"]],
                    textposition="top center",
                    textfont=dict(size=10, color="#F59E0B"),
                    line=dict(color="#F59E0B", width=2.5),
                    marker=dict(size=8, symbol="diamond")
                ))
                fig_cal.add_hline(
                    y=0,
                    line_dash="dot",
                    line_color="rgba(148, 163, 184, 0.7)",
                    yref="y2",
                    annotation_text="Net Zero (Receipts = Sales)",
                    annotation_position="bottom left",
                    annotation_font_size=10
                )
                y2_title = "Net Arus Kas (Rupiah)" if lang_code == "ID" else "Net Cash Inflow (IDR)"
            else:
                fig_cal.add_trace(go.Scatter(
                    x=cal_df["month"],
                    y=cal_df["ratio_pct"],
                    name="Rasio Kas Masuk (%)" if lang_code == "ID" else "Cash Coverage Ratio (%)",
                    yaxis="y2",
                    mode="lines+markers+text",
                    text=[f"{v:.0f}%" for v in cal_df["ratio_pct"]],
                    textposition="top center",
                    textfont=dict(size=10, color="#F59E0B"),
                    line=dict(color="#F59E0B", width=2.5),
                    marker=dict(size=8, symbol="diamond")
                ))
                fig_cal.add_hline(
                    y=100,
                    line_dash="dash",
                    line_color="rgba(239, 68, 68, 0.7)",
                    yref="y2",
                    annotation_text="100% (Receipts = Sales)",
                    annotation_position="top left",
                    annotation_font_size=10
                )
                y2_title = "Rasio Kas Masuk vs Penjualan (%)" if lang_code == "ID" else "Cash Inflow Ratio (%)"
            
            fig_cal.update_layout(
                barmode="group",
                yaxis=dict(title="Nominal Rupiah (Sales & Receipts)" if lang_code == "ID" else "Amount (IDR)"),
                yaxis2=dict(
                    title=y2_title,
                    overlaying="y",
                    side="right"
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            apply_plotly_theme(fig_cal, height=400)
            st.plotly_chart(fig_cal, use_container_width=True)

            # Collapsible Data Table for Monthly Reconciliation Audit
            with st.expander(
                "📋 Tabel Rekonsiliasi & Audit Arus Kas Kalender per Bulan (Audit Detil)"
                if lang_code == "ID" else
                "📋 Monthly Calendar Cash Flow Reconciliation Table (Detailed Audit)"
            ):
                table_display = pd.DataFrame({
                    "Bulan Kalender" if lang_code == "ID" else "Calendar Month": cal_df["month"],
                    "Penjualan Baru (Sales)" if lang_code == "ID" else "New Sales (Billed)": cal_df["sales"].apply(format_rupiah),
                    "Kas Masuk Riil (Receipts)" if lang_code == "ID" else "Actual Cash Receipts": cal_df["receipts"].apply(format_rupiah),
                    "Selisih Kas (Net Inflow)" if lang_code == "ID" else "Net Cash Balance": [
                        (f"+Rp {v:,.0f}" if v >= 0 else f"-Rp {abs(v):,.0f}") for v in cal_df["net_cash"]
                    ],
                    "Rasio Arus Kas" if lang_code == "ID" else "Cash Ratio": [f"{v:.1f}%" for v in cal_df["ratio_pct"]],
                    "Status Arus Kas" if lang_code == "ID" else "Cash Status": [
                        ("🟢 Surplus Kas (Receipts > Sales)" if v > 0 else "🔵 Defisit Kalender (Sales > Receipts)")
                        if lang_code == "ID" else
                        ("🟢 Cash Surplus (Receipts > Sales)" if v > 0 else "🔵 Calendar Deficit (Sales > Receipts)")
                        for v in cal_df["net_cash"]
                    ],
                    "Catatan Lapangan & Audit" if lang_code == "ID" else "Field & Audit Notes": [
                        ("Pelunasan piutang tempo bulan-bulan sebelumnya cair masif" if v > 0 else "Faktur penjualan tempo baru belum jatuh tempo")
                        if lang_code == "ID" else
                        ("Heavy collections from backlogged older credit invoices" if v > 0 else "New credit sales have not reached due date")
                        for v in cal_df["net_cash"]
                    ]
                })
                st.dataframe(table_display, use_container_width=True, hide_index=True)

            # Side-by-side methodology guidance matrix
            with st.expander(
                "💡 Panduan Komprehensif: Kapan Menggunakan Metode Kohor vs Arus Kas Kalender?"
                if lang_code == "ID" else
                "💡 Strategic Advisory: When to Use Cohort vs Calendar Cash Flow?"
            ):
                if lang_code == "ID":
                    st.markdown("""
                    | Dimensi Evaluasi | Metode Kohor Faktur (Grafik 1) | Metode Arus Kas Kalender (Grafik 2 - Model Cetakia) |
                    | :--- | :--- | :--- |
                    | **Metodologi Akuntansi** | Pelacakan Kohor Faktur (*Invoice Cohort Tracking*) | Arus Kas Kalender (*Cash Basis Inflow*) |
                    | **Sumbu Waktu (X-Axis)** | Bulan kelahiran invoice (`invoice_month`) | Tanggal transaksi terjadi (`invoice_date` vs `payment_date`) |
                    | **Makna Kas Masuk** | Dari faktur bulan tersebut, berapa yang sudah lunas hingga hari ini | Total uang fisik yang disetor kasir/masuk bank pada bulan tersebut |
                    | **Peluang Receipts > Sales** | **Mustahil secara Matematis** (dibatasi maksimal 100% per invoice) | **Sangat Wajar & Sering Terjadi** bila ada pencairan piutang besar |
                    | **Tujuan Keputusan** | Memantau kesehatan kredit & efektivitas tim penagihan | Memantau likuiditas kas operasional (gaji, bahan baku kertas, modal) |
                    | **Target Pengguna** | Owner, Direktur Keuangan, Manajer Cabang, Credit Controller | Kasir cabang, staf pembukuan harian, treasury kas kecil |
                    """)
                else:
                    st.markdown("""
                    | Evaluation Dimension | Invoice Cohort Tracking (Chart 1) | Calendar Cash Flow (Chart 2 - Cetakia Model) |
                    | :--- | :--- | :--- |
                    | **Accounting Methodology** | Invoice Cohort Tracking | Calendar Cash Basis Inflow |
                    | **Time Horizon (X-Axis)** | Invoice birth month (`invoice_month`) | Transaction dates (`invoice_date` vs `payment_date`) |
                    | **Meaning of Cash** | How much of that month's invoices has been settled to date | Total physical cash/transfer received during that calendar month |
                    | **Receipts > Sales?** | **Mathematically Impossible** (capped at 100% per invoice) | **Very Common & Expected** during heavy backlogged collections |
                    | **Decision Objective** | Measure credit health, collection speed, and default risk | Monitor liquidity & working capital buffer (payroll, paper procurement) |
                    | **Primary Audience** | Business Owner, Finance Director, Branch Managers, Credit Team | Branch cashier, daily bookkeeper, cash management treasury |
                    """)
        else:
            st.info(
                "Tidak ada data transaksi arus kas kalender untuk kombinasi filter yang dipilih."
                if lang_code == "ID" else
                "No calendar cash flow transactions available for the selected filters."
            )

    # =========================================================
    # METHOD 3: CROSS-MONTH TIMESTAMPS & PAYMENT METHOD TRACKING
    # =========================================================
    st.markdown("---")
    st.subheader("🕵️ " + (
        "Tracking Pelunasan Lintas Bulan & Analisis Metode Pembayaran"
        if lang_code == "ID" else
        "Cross-Month Payment Tracking & Payment Channel Analysis"
    ))
    
    st.caption(
        "💡 **Penjelasan Sederhana untuk Manajemen & Auditor**: Melacak faktur-faktur yang tanggal pembayarannya (`payment_date`) terjadi di bulan berbeda dengan tanggal terbit fakturnya (`invoice_date`). Sebagai contoh nyata: faktur yang terbit di akhir bulan (misalnya tanggal **25–30 September**) namun baru disetor kasir pada awal bulan berikutnya (misalnya **1–3 Oktober**) via **Cash/Tunai** atau **Transfer Bank**. Fenomena inilah yang menjelaskan mengapa penerimaan kas kalender (*Receipts*) melonjak di bulan baru melampaui penjualan baru (*Sales*)."
        if lang_code == "ID" else
        "💡 **Management & Audit Context**: Tracks invoices settled in a different calendar month from their issuance date. For example: invoices issued late in the month (**September 25–30**) but deposited at cashier early next month (**October 1–3**) via **Cash** or **Bank Transfer**. This timing lag explains why cash receipts surge in new months, surpassing newly billed sales."
    )

    if "invoice_date" in df_finance.columns and "last_payment_date" in df_finance.columns:
        df_paid_scope = df_finance[df_finance["last_payment_date"].notnull()].copy()
        df_paid_scope["inv_month_str"] = df_paid_scope["invoice_date"].dt.strftime("%Y-%m")
        df_paid_scope["pay_month_str"] = df_paid_scope["last_payment_date"].dt.strftime("%Y-%m")
        df_paid_scope["days_lag"] = (df_paid_scope["last_payment_date"] - df_paid_scope["invoice_date"]).dt.total_seconds() / 86400.0
        df_paid_scope["is_cross"] = df_paid_scope["inv_month_str"] != df_paid_scope["pay_month_str"]

        # Helper to categorize lag duration into everyday human terms
        def get_lag_category(days):
            if days <= 7:
                return "1 - 7 Hari (Akhir ➔ Awal Bulan)" if lang_code == "ID" else "1 - 7 Days (Month-End Crossing)"
            elif days <= 14:
                return "8 - 14 Hari (Jeda 1-2 Minggu)" if lang_code == "ID" else "8 - 14 Days (1-2 Weeks Lag)"
            elif days <= 30:
                return "15 - 30 Hari (Jeda 2-4 Minggu)" if lang_code == "ID" else "15 - 30 Days (2-4 Weeks Lag)"
            else:
                return "> 30 Hari (Jeda Lebih 1 Bulan)" if lang_code == "ID" else "> 30 Days (> 1 Month Lag)"

        df_paid_scope["lag_category"] = df_paid_scope["days_lag"].apply(get_lag_category)

        # Cross-month dataset
        df_cross = df_paid_scope[df_paid_scope["is_cross"]].copy()

        if not df_cross.empty:
            total_cross_invoices = len(df_cross)
            pct_cross = (total_cross_invoices / len(df_paid_scope) * 100) if len(df_paid_scope) > 0 else 0.0
            total_cross_paid = float(df_cross["paid_raw_clean"].sum())
            avg_days_lag = float(df_cross["days_lag"].mean()) if total_cross_invoices > 0 else 0.0
            
            top_pm_series = df_cross.groupby("payment_methods", observed=False)["paid_raw_clean"].sum().sort_values(ascending=False)
            top_pm_name = str(top_pm_series.index[0]) if len(top_pm_series) > 0 else "N/A"
            top_pm_val = float(top_pm_series.iloc[0]) if len(top_pm_series) > 0 else 0.0

            # 4 Summary Strip KPI Cards
            strip_cross = [
                {
                    "label": "Faktur Bayar Lintas Bulan" if lang_code == "ID" else "Cross-Month Invoices",
                    "value": f"{total_cross_invoices:,} faktur",
                    "desc": f"{pct_cross:.1f}% dari {len(df_paid_scope):,} faktur lunas" if lang_code == "ID" else f"{pct_cross:.1f}% of {len(df_paid_scope):,} settled invoices",
                    "color": "#F59E0B"
                },
                {
                    "label": "Total Kas Masuk Lintas Bulan" if lang_code == "ID" else "Cross-Month Cash Inflow",
                    "value": format_rupiah(total_cross_paid),
                    "desc": "Kas masuk dari faktur bulan lalu" if lang_code == "ID" else "Cash from prior month invoices",
                    "color": "#10B981"
                },
                {
                    "label": "Rata-rata Jeda Pelunasan" if lang_code == "ID" else "Average Payment Lag",
                    "value": f"{avg_days_lag:.1f} Hari" if lang_code == "ID" else f"{avg_days_lag:.1f} Days",
                    "desc": "Selisih tanggal invoice & bayar" if lang_code == "ID" else "Lag between billing and payment",
                    "color": "#3B82F6"
                },
                {
                    "label": "Metode Pembayaran Terbesar" if lang_code == "ID" else "Top Cross-Month Method",
                    "value": f"{top_pm_name}",
                    "desc": f"{format_rupiah(top_pm_val)} kas tertagih" if lang_code == "ID" else f"{format_rupiah(top_pm_val)} cross-month cash",
                    "color": "#8B5CF6"
                }
            ]
            render_summary_strip(strip_cross)

            # -------------------------------------------------------------
            # GRAFIK 1: KOMPOSISI KAS MASUK PER BULAN (STACKED BAR CHART)
            # -------------------------------------------------------------
            st.subheader("📊 " + (
                "Komposisi Kas Masuk per Bulan: Faktur Bulan Berjalan vs. Pelunasan Faktur Bulan Lalu"
                if lang_code == "ID" else
                "Monthly Cash Inflow Composition: Same-Month Invoices vs. Prior-Month Collections"
            ))
            st.caption(
                "💡 **Mudah Dipahami**: Batang biru adalah uang yang masuk dari faktur yang terbit di bulan yang sama. Batang oranye adalah uang pelunasan dari faktur bulan-bulan sebelumnya. Lonjakan batang oranye menjelaskan mengapa uang masuk kasir bisa melampaui penjualan baru pada bulan tersebut."
                if lang_code == "ID" else
                "💡 **Easy to Read**: Blue segments represent cash from invoices issued in the same month. Amber segments represent settlements of invoices from prior months. Spikes in amber explain why monthly cash receipts exceed new sales."
            )

            stack_df = df_paid_scope.groupby(["pay_month_str", "is_cross"])["paid_raw_clean"].sum().unstack(fill_value=0.0).reset_index()
            stack_df.columns.name = None
            if False not in stack_df.columns:
                stack_df[False] = 0.0
            if True not in stack_df.columns:
                stack_df[True] = 0.0

            fig_stack = go.Figure()
            fig_stack.add_trace(go.Bar(
                x=stack_df["pay_month_str"],
                y=stack_df[False],
                name="Faktur Bulan Berjalan (Same-Month)" if lang_code == "ID" else "Same-Month Invoices",
                marker_color="#3B82F6",
                hovertemplate=(
                    "<b>Bulan Kas Masuk: %{x}</b><br>" +
                    ("Kas Faktur Bulan Berjalan: Rp %{y:,.0f}<extra></extra>" if lang_code == "ID" else "Same-Month Cash: Rp %{y:,.0f}<extra></extra>")
                )
            ))
            fig_stack.add_trace(go.Bar(
                x=stack_df["pay_month_str"],
                y=stack_df[True],
                name="Pelunasan Faktur Bulan Lalu (Cross-Month)" if lang_code == "ID" else "Prior-Month Invoices Settled",
                marker_color="#F59E0B",
                hovertemplate=(
                    "<b>Bulan Kas Masuk: %{x}</b><br>" +
                    ("Kas Pelunasan Bulan Lalu: Rp %{y:,.0f}<br>" if lang_code == "ID" else "Prior-Month Cash: Rp %{y:,.0f}<br>") +
                    ("<i>(Pemicu utama Receipts > Sales)</i><extra></extra>" if lang_code == "ID" else "<i>(Main driver of Receipts > Sales)</i><extra></extra>")
                )
            ))
            fig_stack.update_layout(
                barmode="stack",
                xaxis_title="Bulan Kasir Menerima Uang (payment_date)" if lang_code == "ID" else "Month Cash Deposited (payment_date)",
                yaxis_title="Total Kas Masuk (Rupiah)" if lang_code == "ID" else "Cash Received (IDR)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            apply_plotly_theme(fig_stack, height=370)
            st.plotly_chart(fig_stack, use_container_width=True)

            # -------------------------------------------------------------
            # DUA KOLOM: BAR CHART METODE BAYAR + DONUT CHART JEDA WAKTU
            # -------------------------------------------------------------
            c_lay1, c_lay2 = st.columns([1.2, 1])

            with c_lay1:
                st.subheader("💳 " + (
                    "Peringkat Metode Pembayaran (Kas Lintas Bulan)"
                    if lang_code == "ID" else
                    "Payment Channels Ranking (Cross-Month Cash)"
                ))
                pm_cross_agg = df_cross.groupby("payment_methods", observed=False).agg(
                    invoices=("invoice_id", "nunique"),
                    total_nominal=("paid_raw_clean", "sum"),
                    avg_lag=("days_lag", "mean")
                ).reset_index().sort_values("total_nominal", ascending=True)

                fig_pm_simple = px.bar(
                    pm_cross_agg,
                    x="total_nominal",
                    y="payment_methods",
                    orientation="h",
                    color="total_nominal",
                    color_continuous_scale=["#93C5FD", "#1D4ED8"],
                    text=pm_cross_agg["total_nominal"].apply(format_rupiah),
                    labels={
                        "total_nominal": "Total Kas Masuk (Rupiah)" if lang_code == "ID" else "Total Cash Realized (IDR)",
                        "payment_methods": "Metode Pembayaran" if lang_code == "ID" else "Payment Method"
                    },
                    custom_data=["invoices", "avg_lag"]
                )
                fig_pm_simple.update_traces(
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{y}</b><br>" +
                        ("Total Kas Lintas Bulan: Rp %{x:,.0f}<br>" if lang_code == "ID" else "Total Cross-Month Cash: Rp %{x:,.0f}<br>") +
                        ("Jumlah Faktur: %{customdata[0]:,} faktur<br>" if lang_code == "ID" else "Invoice Count: %{customdata[0]:,} invoices<br>") +
                        ("Rata-rata Jeda: %{customdata[1]:.1f} Hari<extra></extra>" if lang_code == "ID" else "Average Delay: %{customdata[1]:.1f} Days<extra></extra>")
                    )
                )
                fig_pm_simple.update_layout(
                    xaxis_title="Total Kas Lintas Bulan (Rupiah)" if lang_code == "ID" else "Cross-Month Cash (IDR)",
                    yaxis_title="",
                    coloraxis_showscale=False
                )
                apply_plotly_theme(fig_pm_simple, height=350)
                st.plotly_chart(fig_pm_simple, use_container_width=True)

            with c_lay2:
                st.subheader("🍩 " + (
                    "Kategori Jeda Waktu Pembayaran"
                    if lang_code == "ID" else
                    "Payment Lag Duration Breakdown"
                ))
                b_counts = df_cross["lag_category"].value_counts().reset_index()
                b_counts.columns = ["kategori", "jumlah"]

                color_cat_map = {
                    "1 - 7 Hari (Akhir ➔ Awal Bulan)": "#3B82F6",
                    "8 - 14 Hari (Jeda 1-2 Minggu)": "#10B981",
                    "15 - 30 Hari (Jeda 2-4 Minggu)": "#F59E0B",
                    "> 30 Hari (Jeda Lebih 1 Bulan)": "#EF4444",
                    "1 - 7 Days (Month-End Crossing)": "#3B82F6",
                    "8 - 14 Days (1-2 Weeks Lag)": "#10B981",
                    "15 - 30 Days (2-4 Weeks Lag)": "#F59E0B",
                    "> 30 Days (> 1 Month Lag)": "#EF4444"
                }

                fig_donut_lag = px.pie(
                    b_counts,
                    names="kategori",
                    values="jumlah",
                    hole=0.55,
                    color="kategori",
                    color_discrete_map=color_cat_map
                )
                fig_donut_lag.update_traces(
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>Jumlah Faktur: %{value:,}<br>Porsi: %{percent}<extra></extra>"
                )
                fig_donut_lag.update_layout(
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=20)
                )
                apply_plotly_theme(fig_donut_lag, height=350)
                st.plotly_chart(fig_donut_lag, use_container_width=True)

            # -------------------------------------------------------------
            # TABEL AUDIT INTERAKTIF: RINCIAN FAKTUR LINTAS BULAN
            # -------------------------------------------------------------
            st.markdown("#### " + (
                "📋 Lembar Kerja Audit: Rincian Faktur yang Dibayar Beda Bulan"
                if lang_code == "ID" else
                "📋 Audit Ledger: Individual Cross-Month Settled Invoices"
            ))

            st.info(
                "💡 **Contoh Kasus Nyata di Lapangan**: Faktur yang terbit di akhir bulan (misal tanggal **25–30 September**) dan baru dibayar kasir pada awal bulan berikutnya (**1–3 Oktober**) via **Cash/Tunai** tercatat di tabel bawah ini. Gunakan filter di bawah untuk menelusuri transaksi tersebut secara presisi."
                if lang_code == "ID" else
                "💡 **Real-world Example**: Invoices issued late in the month (**September 25–30**) and paid early next month (**October 1–3**) via **Cash** appear in this ledger. Use the filters below to investigate specific transactions."
            )

            # List customer khusus transaksi faktur beda bulan
            cross_customers = sorted([str(c).strip() for c in df_cross["customer_name"].dropna().unique() if str(c).strip()])
            opt_cust_cross = ["Semua Pelanggan" if lang_code == "ID" else "All Customers"] + cross_customers
            if "cross_wl_cust_select" in st.session_state and st.session_state["cross_wl_cust_select"] not in opt_cust_cross:
                st.session_state["cross_wl_cust_select"] = opt_cust_cross[0]

            # Filter Controls
            wl_c1, wl_c2, wl_c3, wl_c4, wl_c5 = st.columns([1.6, 1, 1, 1, 1])
            with wl_c1:
                sel_cust_cross = st.selectbox(
                    "🔍 " + ("Pilih / Cari Pelanggan:" if lang_code == "ID" else "Select / Search Customer:"),
                    options=opt_cust_cross,
                    index=0,
                    key="cross_wl_cust_select",
                    help="Ketik untuk mencari atau scroll untuk memilih nama pelanggan (khusus data beda bulan)" if lang_code == "ID" else "Type to search or scroll to select customer (cross-month invoices only)"
                )
            with wl_c2:
                opt_pm_wl = ["Semua Metode" if lang_code == "ID" else "All Methods"] + sorted(df_cross["payment_methods"].dropna().unique().tolist())
                if "cross_wl_pm" in st.session_state and st.session_state["cross_wl_pm"] not in opt_pm_wl:
                    st.session_state["cross_wl_pm"] = opt_pm_wl[0]
                sel_pm_wl = st.selectbox(
                    "Metode Pembayaran:" if lang_code == "ID" else "Payment Method:",
                    options=opt_pm_wl,
                    index=0,
                    key="cross_wl_pm"
                )
            with wl_c3:
                opt_lag_wl = ["Semua Jeda" if lang_code == "ID" else "All Lags"] + sorted(df_cross["lag_category"].dropna().unique().tolist())
                if "cross_wl_lag_cat" in st.session_state and st.session_state["cross_wl_lag_cat"] not in opt_lag_wl:
                    st.session_state["cross_wl_lag_cat"] = opt_lag_wl[0]
                sel_lag_wl = st.selectbox(
                    "Kategori Jeda Waktu:" if lang_code == "ID" else "Lag Category:",
                    options=opt_lag_wl,
                    index=0,
                    key="cross_wl_lag_cat"
                )
            with wl_c4:
                opt_inv_m = ["Semua Bulan Terbit" if lang_code == "ID" else "All Billing Months"] + sorted(df_cross["inv_month_str"].dropna().unique().tolist())
                if "cross_wl_inv_m" in st.session_state and st.session_state["cross_wl_inv_m"] not in opt_inv_m:
                    st.session_state["cross_wl_inv_m"] = opt_inv_m[0]
                sel_inv_m = st.selectbox(
                    "Bulan Terbit (Invoice):" if lang_code == "ID" else "Billed Month:",
                    options=opt_inv_m,
                    index=0,
                    key="cross_wl_inv_m"
                )
            with wl_c5:
                opt_pay_m = ["Semua Bulan Bayar" if lang_code == "ID" else "All Payment Months"] + sorted(df_cross["pay_month_str"].dropna().unique().tolist())
                if "cross_wl_pay_m" in st.session_state and st.session_state["cross_wl_pay_m"] not in opt_pay_m:
                    st.session_state["cross_wl_pay_m"] = opt_pay_m[0]
                sel_pay_m = st.selectbox(
                    "Bulan Bayar (Receipt):" if lang_code == "ID" else "Paid Month:",
                    options=opt_pay_m,
                    index=0,
                    key="cross_wl_pay_m"
                )

            with st.expander("🔎 " + ("Pencarian Lanjutan: Filter Berdasarkan No. Faktur Spesifik" if lang_code == "ID" else "Advanced Search: Filter by Specific Invoice Code"), expanded=False):
                q_inv_search = st.text_input(
                    "No. Faktur:" if lang_code == "ID" else "Invoice Code:",
                    placeholder="Contoh: PKDR2602020002, CJFA2602200016...",
                    key="cross_wl_inv_search"
                )

            df_audit_view = df_cross.copy()
            if sel_cust_cross not in ["Semua Pelanggan", "All Customers"]:
                df_audit_view = df_audit_view[df_audit_view["customer_name"] == sel_cust_cross]
            if sel_pm_wl not in ["Semua Metode", "All Methods"]:
                df_audit_view = df_audit_view[df_audit_view["payment_methods"] == sel_pm_wl]
            if sel_lag_wl not in ["Semua Jeda", "All Lags"]:
                df_audit_view = df_audit_view[df_audit_view["lag_category"] == sel_lag_wl]
            if sel_inv_m not in ["Semua Bulan Terbit", "All Billing Months"]:
                df_audit_view = df_audit_view[df_audit_view["inv_month_str"] == sel_inv_m]
            if sel_pay_m not in ["Semua Bulan Bayar", "All Payment Months"]:
                df_audit_view = df_audit_view[df_audit_view["pay_month_str"] == sel_pay_m]
            if q_inv_search and q_inv_search.strip():
                df_audit_view = df_audit_view[df_audit_view["invoice_code"].astype(str).str.lower().str.contains(q_inv_search.strip().lower(), na=False)]

            df_audit_view = df_audit_view.sort_values("days_lag", ascending=False)

            st.caption(
                f"Menampilkan **{len(df_audit_view):,}** faktur beda bulan senilai **{format_rupiah(float(df_audit_view['paid_raw_clean'].sum()))}**."
                if lang_code == "ID" else
                f"Displaying **{len(df_audit_view):,}** cross-month invoices totaling **{format_rupiah(float(df_audit_view['paid_raw_clean'].sum()))}**."
            )

            audit_display = pd.DataFrame({
                "No. Faktur" if lang_code == "ID" else "Invoice Code": df_audit_view["invoice_code"],
                "Nama Pelanggan" if lang_code == "ID" else "Customer Name": df_audit_view["customer_name"],
                "Cabang" if lang_code == "ID" else "Branch": df_audit_view["division_name"],
                "Tgl Terbit Faktur" if lang_code == "ID" else "Invoice Date": df_audit_view["invoice_date"].dt.strftime("%Y-%m-%d %H:%M"),
                "Tgl Bayar Kasir" if lang_code == "ID" else "Payment Date": df_audit_view["last_payment_date"].dt.strftime("%Y-%m-%d %H:%M"),
                "Jeda Pelunasan" if lang_code == "ID" else "Payment Lag": [
                    f"{int(round(float(d)))} Hari ({im} ➔ {pm})"
                    for d, im, pm in zip(df_audit_view["days_lag"], df_audit_view["inv_month_str"], df_audit_view["pay_month_str"])
                ],
                "Kategori Waktu" if lang_code == "ID" else "Lag Bucket": df_audit_view["lag_category"],
                "Metode Pembayaran" if lang_code == "ID" else "Payment Method": df_audit_view["payment_methods"],
                "Nominal Dibayar" if lang_code == "ID" else "Paid Amount": df_audit_view["paid_raw_clean"].apply(format_rupiah),
                "Status" if lang_code == "ID" else "Status": [
                    "🚨 Beda Bulan" if lang_code == "ID" else "🚨 Cross-Month" for _ in range(len(df_audit_view))
                ]
            })

            st.dataframe(audit_display, use_container_width=True, hide_index=True)

            # Export CSV
            csv_cross_data = df_audit_view[[
                "invoice_code", "customer_name", "division_name", "invoice_date",
                "last_payment_date", "days_lag", "lag_category", "inv_month_str", "pay_month_str",
                "payment_methods", "paid_raw_clean"
            ]].to_csv(index=False).encode('utf-8')

            st.download_button(
                label="📥 " + ("Unduh Rekap Faktur Lintas Bulan (.CSV)" if lang_code == "ID" else "Download Cross-Month Invoices (.CSV)"),
                data=csv_cross_data,
                file_name="cetakia_faktur_lintas_bulan.csv",
                mime="text/csv",
                key="download_cross_month_csv"
            )
        else:
            st.info(
                "Tidak ditemukan faktur yang pembayarannya terjadi di beda bulan untuk filter saat ini."
                if lang_code == "ID" else
                "No cross-month payment transactions identified under the current filter scope."
            )

# =============================================================
# TAB 2: SEGMENT & BRANCH RISK EXPOSURE
# =============================================================
with tab2:
    # Compute dynamic segment breakdown
    ind_out = float(df_finance[df_finance["customer_category"] == "INDUSTRI"]["outstanding_eda"].sum()) if "customer_category" in df_finance.columns else 0.0
    div_out = float(df_finance[df_finance["customer_category"] == "DIVISI"]["outstanding_eda"].sum()) if "customer_category" in df_finance.columns else 0.0
    top2_tot = ind_out + div_out
    top2_pct = (top2_tot / total_outstanding * 100) if total_outstanding > 0 else 0.0
    ind_pct = (ind_out / total_outstanding * 100) if total_outstanding > 0 else 0.0
    div_pct = (div_out / total_outstanding * 100) if total_outstanding > 0 else 0.0

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
            f"Segmen INDUSTRI menyumbang {format_rupiah(ind_out)} ({ind_pct:.1f}%) dari seluruh piutang Cetakia, disusul akun internal DIVISI sebesar {format_rupiah(div_out)} ({div_pct:.1f}%). Kedua segmen ini mencakup {top2_pct:.1f}% risiko piutang perusahaan."
            if lang_code == "ID" else
            f"INDUSTRI accounts for {format_rupiah(ind_out)} ({ind_pct:.1f}%) of outstanding receivables, followed by internal DIVISI transfers of {format_rupiah(div_out)} ({div_pct:.1f}%). Together they represent {top2_pct:.1f}% of exposure."
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
    df_wl_base = df_cust[df_cust["outstanding_amount"] > 0].copy()

    # Pre-calculate set of customers who have cross-month invoices
    cross_cust_names = set(
        df_finance_raw[
            (df_finance_raw["paid_raw_clean"] > 0) &
            (df_finance_raw["invoice_date"].dt.to_period("M") != df_finance_raw["last_payment_date"].dt.to_period("M"))
        ]["customer_name"].dropna().unique()
    )

    is_cross_only = st.session_state.get("worklist_cross_only_chk", False)
    if is_cross_only:
        wl_cust_pool = df_wl_base[df_wl_base["customer_name"].isin(cross_cust_names)]
    else:
        wl_cust_pool = df_wl_base

    wl_cust_list = sorted([str(c).strip() for c in wl_cust_pool["customer_name"].dropna().unique() if str(c).strip()])
    wl_cust_options = ["Semua Pelanggan" if lang_code == "ID" else "All Customers"] + wl_cust_list

    if "worklist_cust_select" in st.session_state and st.session_state["worklist_cust_select"] not in wl_cust_options:
        st.session_state["worklist_cust_select"] = wl_cust_options[0]

    wl_col1, wl_col2, wl_col3 = st.columns([1.5, 1, 1])

    with wl_col1:
        sel_wl_cust = st.selectbox(
            "🔍 " + ("Pilih / Cari Nama Pelanggan:" if lang_code == "ID" else "Select / Search Customer Name:"),
            options=wl_cust_options,
            index=0,
            key="worklist_cust_select",
            help="Ketik untuk mencari atau scroll untuk memilih nama pelanggan" if lang_code == "ID" else "Type to search or scroll to select customer name"
        )
        filter_cross_only = st.checkbox(
            "⚡ " + ("Hanya Pelanggan di Rekap Faktur Beda Bulan" if lang_code == "ID" else "Cross-Month Invoiced Customers Only"),
            value=is_cross_only,
            key="worklist_cross_only_chk",
            help="Filter daftar kerja hanya untuk pelanggan yang memiliki riwayat pembayaran faktur lintas bulan" if lang_code == "ID" else "Filter worklist to only debtors who have cross-month settled invoices"
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
    df_wl = df_wl_base.copy()

    if filter_cross_only:
        df_wl = df_wl[df_wl["customer_name"].isin(cross_cust_names)]

    if sel_wl_cust not in ["Semua Pelanggan", "All Customers"]:
        df_wl = df_wl[df_wl["customer_name"] == sel_wl_cust]

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
