import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_data, load_customer_intelligence
from utils.intelligence_engine import calculate_market_opportunity_matrix
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Market Intelligence Dashboard", page_icon="🌐", layout="wide")

# Load Datasets
df_cust = load_customer_data()
df_intel = load_customer_intelligence()

# Merge Datasets
df_market_full = df_cust.merge(
    df_intel[['customer_id', 'lifetime_sales', 'total_orders', 'average_order_value', 'days_since_last_purchase', 'customer_health']],
    on='customer_id',
    how='left'
)

# Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

df_filtered = df_market_full.copy()
if filters["branch"] != "All Branches":
    if "division_name" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["mkt_intel_title"],
    subtitle="4-Quadrant Market Opportunity Matrix, 6 Regional Branch Benchmarks & Portfolio Strategy Guide" if lang_code == "EN" else "Matriks Peluang Pasar 4-Kuadran, Tolok Ukur Wilayah 6 Cabang & Panduan Alokasi Portofolio",
    module_tag="EXECUTIVE / STRATEGY"
)

# Metrics Summary
total_market_cust = len(df_filtered)
total_market_revenue = df_filtered["lifetime_sales"].sum() if "lifetime_sales" in df_filtered.columns else 0
prospect_count = len(df_filtered[df_filtered["total_orders"] == 0])
avg_market_aov = df_filtered[df_filtered["total_orders"] > 0]["average_order_value"].mean() if "average_order_value" in df_filtered.columns else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    kpi1_title = "Total Registered Base" if lang_code == "EN" else "Total Basis Terdaftar"
    kpi1_sub = "Documented master account population" if lang_code == "EN" else "Populasi master akun terdata"
    acct_unit = "Accounts" if lang_code == "EN" else "Akun"
    metric_card(kpi1_title, f"{total_market_cust:,} {acct_unit}", subtext=kpi1_sub)
with m2:
    kpi2_title = "Total Confirmed Revenue" if lang_code == "EN" else "Total Pendapatan Terkonfirmasi"
    kpi2_sub = "Accumulated billed invoice sales" if lang_code == "EN" else "Akumulasi penjualan invoice tertagih"
    metric_card(kpi2_title, format_rupiah(total_market_revenue), subtext=kpi2_sub)
with m3:
    kpi3_title = "Unconverted Accounts" if lang_code == "EN" else "Akun Belum Bertransaksi"
    kpi3_sub = "First-order acquisition opportunities" if lang_code == "EN" else "Peluang akuisisi pesanan perdana"
    metric_card(kpi3_title, f"{prospect_count:,} Leads", subtext=kpi3_sub)
with m4:
    kpi4_title = "Market Average AOV" if lang_code == "EN" else "Rata-rata AOV Pasar"
    kpi4_sub = "Transaction value per order" if lang_code == "EN" else "Nilai transaksi per pesanan"
    metric_card(kpi4_title, format_rupiah(avg_market_aov), subtext=kpi4_sub)

st.markdown("---")

# -------------------------------------------------------------
# CALCULATE MARKET OPPORTUNITY MATRIX
# -------------------------------------------------------------
market_matrix = calculate_market_opportunity_matrix(df_filtered)

# -------------------------------------------------------------
# STRICT V1.1 MANDATORY DSS INSIGHT CARD (5-PART STRUCTURE)
# -------------------------------------------------------------
ind_df = df_filtered[df_filtered['customer_category'].astype(str).str.upper() == 'INDUSTRI']
ind_count = len(ind_df)
ind_sales = ind_df['lifetime_sales'].sum() if 'lifetime_sales' in ind_df.columns else 0
ind_pct = (ind_sales / total_market_revenue * 100) if total_market_revenue > 0 else 0

if lang_code == "EN":
    ic_title = "Strategic Market Quadrant Concentration & 6-Branch Catchment Strategy"
    ic_metric = f"Industrial Segment: {ind_pct:.1f}% Revenue Share ({format_rupiah(ind_sales)})"
    ic_context = f"Analyzed across 8 registered customer segments within branch {filters['branch']} scope."
    ic_insight = "The Industrial and Division segments serve as the Strategic Market, contributing over 60% of enterprise revenue with the highest AOV. Meanwhile, End User and MSME segments function as the Growth Market with the largest customer count."
    ic_impacted = f"Commercial Director, Key Account Management (KAM) Team, and Branch Managers across {filters['branch']}."
    ic_action = "Board Strategy: Establish a dedicated Key Account Management (KAM) team to secure annual supply contracts with Industrial clients in Cipta Galuh & Cipta Graha. For MSME & End User markets, deploy self-service online ordering campaigns."
    ic_badge = "MARKET PORTFOLIO STRATEGY RULE"
    ic_target = f"Top Industrial Accounts & 6 Operational Branches of Cetakia"
else:
    ic_title = "Konsentrasi Kuadran Pasar Strategis & Strategi Tangkapan Wilayah 6 Cabang"
    ic_metric = f"Segmen Industri: {ind_pct:.1f}% Pangsa Pendapatan ({format_rupiah(ind_sales)})"
    ic_context = f"Dianalisis dari 8 segmen pelanggan terdaftar pada cakupan cabang {filters['branch']}."
    ic_insight = "Segmen Industri dan Divisi terbukti merupakan Pasar Strategis (Strategic Market) yang menyumbang lebih dari 60% total pendapatan perusahaan dengan AOV tertinggi. Sementara itu, segmen End User dan UMKM berfungsi sebagai Pasar Pertumbuhan (Growth Market) dengan basis pelanggan terbesar."
    ic_impacted = f"Direktur Komersial, Tim Key Account Management (KAM), serta Manajer Cabang di wilayah {filters['branch']}."
    ic_action = "Strategi Direksi: Bentuk tim Key Account Management (KAM) khusus untuk mengunci kontrak tahunan dengan klien Industri di Cipta Galuh & Cipta Graha. Untuk pasar UMKM & End User, dorong kampanye otomatisasi pemesanan online."
    ic_badge = "ATURAN STRATEGI PORTOFOLIO PASAR"
    ic_target = f"Akun Industri Teratas & 6 Cabang Operasional Cetakia"

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
# TABBED MARKET INTELLIGENCE INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_labels = [
        "🌐 4-Quadrant Market Opportunity Matrix",
        "📊 Segment Value Distribution & Bubble Matrix",
        "🏢 6 Regional Branch Catchment Benchmark",
        "🧭 Executive Portfolio Strategy Playbook"
    ]
else:
    tab_labels = [
        "🌐 Matriks Peluang Pasar 4-Kuadran",
        "📊 Sebaran Nilai Segmen & Bubble Matrix",
        "🏢 Tolok Ukur Tangkapan 6 Wilayah Cabang",
        "🧭 Panduan Strategi Portofolio Eksekutif"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

with tab1:
    st.subheader("🌐 Comprehensive Market Opportunity Matrix by Segment" if lang_code == "EN" else "🌐 Matriks Peluang Pasar Komprehensif per Segmen")
    st.caption("Strategic 4-Quadrant Classification: Strategic Market (High Value), Growth Market (High Volume), Retention Market (Account Lock-in), and Development Market (New Potential)." if lang_code == "EN" else "Klasifikasi 4-Kuadran Strategis: Strategic Market (Nilai Tinggi), Growth Market (Volume Tinggi), Retention Market (Kunci Akun), dan Development Market (Potensi Baru).")
    
    if not market_matrix.empty:
        disp_matrix = market_matrix.copy()
        disp_matrix["Pendapatan (IDR)"] = disp_matrix["total_revenue"].apply(format_rupiah)
        disp_matrix["Pangsa Pendapatan (%)"] = disp_matrix["revenue_pct"].apply(lambda p: f"{p:.1f}%")
        disp_matrix["Rata-rata AOV"] = disp_matrix["avg_aov"].apply(format_rupiah)
        disp_matrix["Repeat Rate (%)"] = disp_matrix["repeat_rate"].apply(lambda r: f"{r:.1f}%")
        
        if lang_code == "EN":
            matrix_rename = {
                "customer_category": "Market Segment",
                "customer_count": "Active Buyer Accounts",
                "opportunity_level": "Opportunity Quadrant",
                "Pendapatan (IDR)": "Revenue (IDR)",
                "Pangsa Pendapatan (%)": "Revenue Share (%)",
                "Rata-rata AOV": "Average AOV",
                "Repeat Rate (%)": "Repeat Rate (%)"
            }
        else:
            matrix_rename = {
                "customer_category": "Segmen Pasar",
                "customer_count": "Jumlah Akun Pembeli",
                "opportunity_level": "Klasifikasi Kuadran Peluang"
            }
        st.dataframe(
            disp_matrix[[
                "customer_category", "customer_count", "Pendapatan (IDR)", 
                "Pangsa Pendapatan (%)", "Rata-rata AOV", "Repeat Rate (%)", "opportunity_level"
            ]].rename(columns=matrix_rename),
            use_container_width=True
        )
    else:
        empty_matrix_msg = "No segment data for the selected filters." if lang_code == "EN" else "Tidak ada data segmen pada filter terpilih."
        st.info(empty_matrix_msg)

with tab2:
    st.subheader("Segment Value Distribution Matrix (Bubble Matrix)" if lang_code == "EN" else "Matriks Sebaran Nilai Segmen (Bubble Matrix)")
    st.caption("X-Axis: Transacting Customer Accounts | Y-Axis: Total Revenue | Bubble Size: Average AOV" if lang_code == "EN" else "Sumbu X: Jumlah Akun Pelanggan | Sumbu Y: Total Pendapatan | Ukuran Bubble: Rata-rata AOV")
    if not df_filtered.empty:
        df_seg_summary = df_filtered[df_filtered["total_orders"] > 0].groupby("customer_category").agg(
            cust_count=("customer_id", "nunique"),
            total_sales=("lifetime_sales", "sum"),
            avg_aov=("average_order_value", "mean")
        ).reset_index()
        
        bubble_labels = {
            "cust_count": "Transacting Accounts Count" if lang_code == "EN" else "Jumlah Akun Pelanggan Bertransaksi",
            "total_sales": "Total Revenue Contribution (IDR)" if lang_code == "EN" else "Total Kontribusi Pendapatan (IDR)",
            "customer_category": "Segment" if lang_code == "EN" else "Segmen"
        }
        fig_bubble = px.scatter(
            df_seg_summary,
            x="cust_count",
            y="total_sales",
            size="avg_aov",
            color="customer_category",
            hover_name="customer_category",
            labels=bubble_labels
        )
        apply_plotly_theme(fig_bubble, height=360)
        st.plotly_chart(fig_bubble, use_container_width=True)

with tab3:
    st.subheader("Revenue Benchmarking across 6 Regional Branches" if lang_code == "EN" else "Tolok Ukur Pendapatan 6 Wilayah Cabang")
    st.caption("Comparison of confirmed revenue contributions across Cipta Grafika regional branches." if lang_code == "EN" else "Perbandingan kontribusi pendapatan terkonfirmasi antar cabang regional Cipta Grafika.")
    if not df_filtered.empty and "division_name" in df_filtered.columns:
        df_branch = df_filtered[df_filtered["total_orders"] > 0].groupby("division_name").agg(
            active_buyers=("customer_id", "nunique"),
            total_revenue=("lifetime_sales", "sum")
        ).reset_index().sort_values(by="total_revenue", ascending=False)
        
        branch_labels = {
            "division_name": "Branch" if lang_code == "EN" else "Cabang",
            "total_revenue": "Total Confirmed Revenue (IDR)" if lang_code == "EN" else "Total Pendapatan Terkonfirmasi (IDR)"
        }
        fig_branch = px.bar(
            df_branch,
            x="division_name",
            y="total_revenue",
            color="total_revenue",
            color_continuous_scale=["#93C5FD", "#1D4ED8"],
            labels=branch_labels
        )
        fig_branch.update_traces(
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.5,
            opacity=0.92
        )
        apply_plotly_theme(fig_branch, height=360)
        st.plotly_chart(fig_branch, use_container_width=True)

with tab4:
    st.subheader("🧭 Executive Strategic Portfolio Playbook" if lang_code == "EN" else "🧭 Panduan Alokasi Portofolio Strategis")
    if lang_code == "EN":
        st.markdown("""
        <div class="cetakia-card">
            <h4 style="color: #3B82F6; margin-top: 0;">Executive Business Policy Recommendations</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 14px;">
                <div style="background-color: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 14px; border-radius: 6px;">
                    <b style="color: #10B981;">1. Strategic Market Quadrant (Industrial & Division)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Characteristics: Revenue contribution > 60%, highest AOV (> IDR 1.5M). Priority: Lock in long-term relationships through guaranteed production SLAs and multi-year supply contracts.
                    </p>
                </div>
                <div style="background-color: rgba(59, 130, 246, 0.08); border-left: 4px solid #3B82F6; padding: 14px; border-radius: 6px;">
                    <b style="color: #3B82F6;">2. Growth Market Quadrant (End User & MSME)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Characteristics: Largest customer volume (> 8,500 accounts). Priority: Streamline repeat orders via digital self-service portals and promotional bundles to lift AOV.
                    </p>
                </div>
                <div style="background-color: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 14px; border-radius: 6px;">
                    <b style="color: #F59E0B;">3. Retention Market Quadrant (Institutional)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Characteristics: High basket value but seasonal / tender procurement cycles. Priority: Establish scheduled quarterly reviews prior to fiscal tender windows.
                    </p>
                </div>
                <div style="background-color: rgba(139, 92, 246, 0.08); border-left: 4px solid #8B5CF6; padding: 14px; border-radius: 6px;">
                    <b style="color: #8B5CF6;">4. Development Market Quadrant (Schools & Agents)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Characteristics: Lower current revenue share but high upside expansion. Priority: Partner with local printing agents as reseller networks and pitch dedicated graduation/yearbook kits.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="cetakia-card">
            <h4 style="color: #3B82F6; margin-top: 0;">Rekomendasi Kebijakan Bisnis Eksekutif</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 14px;">
                <div style="background-color: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 14px; border-radius: 6px;">
                    <b style="color: #10B981;">1. Kuadran Pasar Strategis (Industri & Divisi)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Karakteristik: Kontribusi pendapatan > 60%, AOV tertinggi (> Rp 1.5 Juta). Prioritas: Pertahankan hubungan jangka panjang melalui SLA produksi terjamin dan perjanjian kontrak pasokan tahunan.
                    </p>
                </div>
                <div style="background-color: rgba(59, 130, 246, 0.08); border-left: 4px solid #3B82F6; padding: 14px; border-radius: 6px;">
                    <b style="color: #3B82F6;">2. Kuadran Pasar Pertumbuhan (End User & UMKM)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Karakteristik: Basis pelanggan terbesar (> 8.500 akun). Prioritas: Percepat proses pemesanan dengan portal online mandiri dan paket bundling untuk menaikkan nilai rata-rata pesanan (AOV).
                    </p>
                </div>
                <div style="background-color: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 14px; border-radius: 6px;">
                    <b style="color: #F59E0B;">3. Kuadran Pasar Retensi (Instansi)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Karakteristik: Nilai per transaksi tinggi namun siklus belanja musiman / tender. Prioritas: Lakukan penjangkauan rutin terjadwal setiap kuartal anggaran sebelum masa tender pengadaan cetak dimulai.
                    </p>
                </div>
                <div style="background-color: rgba(139, 92, 246, 0.08); border-left: 4px solid #8B5CF6; padding: 14px; border-radius: 6px;">
                    <b style="color: #8B5CF6;">4. Kuadran Pasar Pengembangan (Sekolah & Agen)</b>
                    <p style="font-size: 13.5px; margin: 6px 0 0 0; line-height: 1.5;">
                        Karakteristik: Kontribusi saat ini kecil namun memiliki potensi ekspansi tinggi. Prioritas: Gandeng agen percetakan lokal sebagai mitra reseller dan tawarkan paket buku tahunan/kelulusan bagi sekolah.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
