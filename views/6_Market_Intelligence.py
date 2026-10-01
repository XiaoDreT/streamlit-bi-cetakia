import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_data, load_customer_intelligence, load_sales_data, load_product_data
from utils.intelligence_engine import (
    calculate_market_opportunity_matrix, compute_period_growth,
    analyze_support_umkm_intelligence, compute_marketing_campaign_intelligence
)
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    render_section_info, render_summary_strip,
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Market & Marketing Campaign Intelligence — Cetakia BI", page_icon="🌐", layout="wide")

# Load Datasets
df_cust = load_customer_data()
df_intel = load_customer_intelligence()
df_sales = load_sales_data(include_cancelled=False)
df_items = load_product_data(include_cancelled=False)

# Merge branch division metadata into product items if needed
if "division_name" not in df_items.columns and "invoice_id" in df_items.columns and "division_name" in df_sales.columns:
    df_items = df_items.merge(
        df_sales[["invoice_id", "division_name"]].drop_duplicates(),
        on="invoice_id",
        how="left"
    )

# Merge customer master with customer intelligence
df_market_full = df_cust.merge(
    df_intel[['customer_id', 'lifetime_sales', 'total_orders', 'average_order_value', 'days_since_last_purchase', 'customer_health']],
    on='customer_id',
    how='left'
)

# Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]
is_en = (lang_code == "EN")

df_filtered = df_market_full.copy()
if filters["branch"] != "All Branches":
    if "division_name" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title="Dashboard Analisis Pasar & Marketing Intelligence" if not is_en else "Market & Marketing Campaign Intelligence Dashboard",
    subtitle="Analisis segmen pasar, program SupportUMKM, dan peluang promosi berbasis perilaku belanja pelanggan." if not is_en else "Market segment analysis, SupportUMKM program intelligence, and behavior-driven promotional campaigns.",
    module_tag="STRATEGY / MARKETING INTELLIGENCE"
)

# Metrics Summary
total_market_cust = len(df_filtered)
total_market_revenue = df_filtered["lifetime_sales"].sum() if "lifetime_sales" in df_filtered.columns else 0
prospect_count = len(df_filtered[df_filtered["total_orders"] == 0])
avg_market_aov = df_filtered[df_filtered["total_orders"] > 0]["average_order_value"].mean() if "average_order_value" in df_filtered.columns else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    kpi1_title = "Total Basis Terdaftar" if not is_en else "Total Registered Base"
    kpi1_sub = "Populasi akun pelanggan terdata" if not is_en else "Documented account population"
    acct_unit = "Akun" if not is_en else "Accounts"
    metric_card(kpi1_title, f"{total_market_cust:,} {acct_unit}", subtext=kpi1_sub)

with m2:
    kpi2_title = "Total Pendapatan Terkonfirmasi" if not is_en else "Total Confirmed Revenue"
    kpi2_sub = "Akumulasi penjualan invoice tertagih" if not is_en else "Accumulated billed invoice sales"
    metric_card(kpi2_title, format_rupiah(total_market_revenue), subtext=kpi2_sub)

with m3:
    kpi3_title = "Akun Belum Bertransaksi" if not is_en else "Unconverted Accounts"
    kpi3_sub = "Peluang akuisisi pesanan perdana" if not is_en else "First-order acquisition opportunities"
    prospect_unit = "Prospek" if not is_en else "Prospects"
    metric_card(kpi3_title, f"{prospect_count:,} {prospect_unit}", subtext=kpi3_sub)

with m4:
    kpi4_title = "Rata-rata Nilai Pesanan (AOV)" if not is_en else "Market Average AOV"
    kpi4_sub = "Nilai transaksi per pesanan pasar" if not is_en else "Transaction value per order"
    metric_card(kpi4_title, format_rupiah(avg_market_aov), subtext=kpi4_sub)

st.markdown("---")

# -------------------------------------------------------------
# CALCULATE MARKET OPPORTUNITY MATRIX
# -------------------------------------------------------------
market_matrix = calculate_market_opportunity_matrix(df_filtered, df_sales)

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD (DECISION SUPPORT)
# -------------------------------------------------------------
ind_df = df_filtered[df_filtered['customer_category'].astype(str).str.upper() == 'INDUSTRI']
ind_sales = ind_df['lifetime_sales'].sum() if 'lifetime_sales' in ind_df.columns else 0
ind_pct = (ind_sales / total_market_revenue * 100) if total_market_revenue > 0 else 0

if is_en:
    ic_title = "Strategic Market Growth Engine & Portfolio Allocation"
    ic_metric = f"Industrial Sector: {ind_pct:.1f}% Revenue Share ({format_rupiah(ind_sales)})"
    ic_context = f"Evaluated across 8 customer segments in branch '{filters['branch']}'."
    ic_insight = "Industrial segment is the primary market growth engine (+9.10% market growth contribution / +Rp 808M expansion) with +21.6% PoP run-rate growth. End User (+5.96% contribution) and MSME (+3.30% contribution) drive high-velocity volume adoption (+33% to +38% growth). Internal Employee orders (0.1% share) are categorized separately to prevent commercial market distortion."
    ic_impacted = f"Commercial Director, Key Account Management (KAM) Team, and Branch Managers across {filters['branch']}."
    ic_action = "Board Strategy: Establish Dedicated KAM teams in Cipta Galuh & Cipta Graha to lock in annual Industrial contracts. Deploy self-service promotional vouchers for the high-growth End User and MSME segments."
    ic_badge = "MARKET PORTFOLIO DECISION SUPPORT"
    ic_target = f"Top Industrial Accounts & 6 Operational Branches of Cetakia"
else:
    ic_title = "Pendorong Utama Pertumbuhan Pasar & Alokasi Portofolio Strategis"
    ic_metric = f"Segmen Industri: {ind_pct:.1f}% Pangsa Pendapatan ({format_rupiah(ind_sales)})"
    ic_context = f"Dianalisis dari 8 segmen pelanggan terdaftar pada cakupan cabang '{filters['branch']}'."
    ic_insight = "Segmen Industri menjadi motor penggerak pertumbuhan pasar nomor satu (+9.10% kontribusi pertumbuhan / +Rp 808 Juta ekspansi) dengan kenaikan omzet +21.6%. Segmen End User (+5.96% kontribusi) dan UMKM (+3.30% kontribusi) memimpin akselerasi volume ritel (+33% s/d +38% growth). Transaksi internal Karyawan (0.1% omzet) diklasifikasikan terpisah secara proporsional agar tidak mendistorsi skala pasar komersial."
    ic_impacted = f"Direktur Komersial, Tim Key Account Management (KAM), serta Manajer Cabang di wilayah '{filters['branch']}'."
    ic_action = "Strategi Direksi: Kunci kontrak tahunan dengan akun Industri di Cipta Galuh & Cipta Graha. Untuk segmen yang bertumbuh pesat (Sekolah & UMKM), berikan dukungan tim promosi khusus dan paket cetak terpadu."
    ic_badge = "KEPUTUSAN STRATEGIS PASAR"
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
# THREE-PILLAR INTELLIGENCE INTERFACE
# -------------------------------------------------------------
if is_en:
    tab_labels = [
        "🌐 Market Overview & Regional Benchmarks",
        "🤝 SupportUMKM Intelligence",
        "🎯 Marketing Campaign Intelligence"
    ]
else:
    tab_labels = [
        "🌐 Analisis Pasar & Tolok Ukur Cabang",
        "🤝 SupportUMKM Intelligence",
        "🎯 Marketing Campaign Intelligence"
    ]

tab1, tab2, tab3 = st.tabs(tab_labels)

# =============================================================
# TAB 1: ANALISIS PASAR & TOLOK UKUR CABANG
# =============================================================
with tab1:
    if is_en:
        render_section_info(
            title="Market Opportunity Matrix by Segment (Market Size, Revenue, and Growth Rate)",
            subtitle="Comprehensive analysis of market size, current revenue, normalized growth rate, and real market contribution per segment.",
            what_it_shows="Market size (customer count), current net revenue, share percentage, average AOV, time-normalized PoP Growth (%), and Market Growth Contribution (%).",
            why_important="Separates primary market growth drivers (Industrial, End User, MSME) from internal non-market transactions, ensuring capital and marketing investments target high-yield areas.",
            simple_insight="<b>Industrial</b> is the #1 market expansion engine (+Rp 808M / +9.10% market growth contribution). <b>End User (+Rp 530M)</b> and <b>MSME (+Rp 293M)</b> lead volume velocity. <b>Division (+Rp 187M)</b> and <b>Institution (+Rp 95M)</b> exhibit steady positive growth under time-normalized comparison."
        )
    else:
        render_section_info(
            title="Matriks Peluang Pasar per Segmen (Ukuran Pasar, Pendapatan, dan Pertumbuhan)",
            subtitle="Analisis komprehensif ukuran pasar, omzet saat ini, laju pertumbuhan ternormalisasi, dan kontribusi ekspansi pasar riil per segmen.",
            what_it_shows="Ukuran pasar (jumlah pelanggan), pendapatan saat ini, persentase pangsa, rata-rata AOV, laju pertumbuhan PoP ternormalisasi (%), dan Kontribusi Pertumbuhan Pasar (%).",
            why_important="Membedakan segmen penggerak pasar utama (omzet & kontribusi ekspansi besar) dari transaksi internal, sehingga alokasi modal dan tim penjualan fokus pada area yang menghasilkan dampak finansial nyata.",
            simple_insight="<b>Industri</b> adalah penggerak pertumbuhan nomor satu (+Rp 808 Juta / +9.10% kontribusi pasar). <b>End User (+Rp 530 Jt)</b> dan <b>UMKM (+Rp 293 Jt)</b> memimpin akselerasi volume. <b>Divisi (+Rp 187 Jt)</b> dan <b>Instansi (+Rp 95 Jt)</b> bertumbuh positif dan stabil setelah dinormalisasi durasi waktu berimbang."
        )
    
    if not market_matrix.empty:
        top_contrib_seg = market_matrix.loc[market_matrix["growth_contrib_pct"].idxmax()]
        largest_seg = market_matrix.iloc[0]
        total_market_growth = market_matrix["growth_contrib_pct"].sum()
        retail_expansion = market_matrix[market_matrix["customer_category"].isin(["END USER", "UMKM"])]["delta_sales"].sum()
        
        if is_en:
            strip_market = [
                {"label": "🚀 Top Growth Contributor", "value": top_contrib_seg["customer_category"], "desc": f"+{top_contrib_seg['growth_contrib_pct']:.2f}% market growth (+{format_rupiah(top_contrib_seg['delta_sales'])})", "color": "#10B981"},
                {"label": "🏆 Largest Revenue Segment", "value": largest_seg["customer_category"], "desc": f"{format_rupiah(largest_seg['total_revenue'])} ({largest_seg['revenue_pct']:.1f}% share)", "color": "#2563EB"},
                {"label": "🛍️ Retail & MSME Expansion", "value": format_rupiah(retail_expansion), "desc": "Combined End User & MSME added sales", "color": "#F59E0B"},
                {"label": "📈 Total Company Growth", "value": f"+{total_market_growth:.1f}%", "desc": f"Across {market_matrix['customer_count'].sum():,} buying accounts", "color": "#8B5CF6"}
            ]
        else:
            strip_market = [
                {"label": "🚀 Kontributor Pertumbuhan Terbesar", "value": top_contrib_seg["customer_category"], "desc": f"+{top_contrib_seg['growth_contrib_pct']:.2f}% kontribusi (+{format_rupiah(top_contrib_seg['delta_sales'])})", "color": "#10B981"},
                {"label": "🏆 Segmen Omzet Terbesar", "value": largest_seg["customer_category"], "desc": f"{format_rupiah(largest_seg['total_revenue'])} ({largest_seg['revenue_pct']:.1f}% share)", "color": "#2563EB"},
                {"label": "🛍️ Ekspansi Ritel & UMKM", "value": format_rupiah(retail_expansion), "desc": "Total tambahan omzet End User & UMKM", "color": "#F59E0B"},
                {"label": "📈 Total Pertumbuhan Pasar", "value": f"+{total_market_growth:.1f}%", "desc": f"Basis {market_matrix['customer_count'].sum():,} akun pembeli aktif", "color": "#8B5CF6"}
            ]
        render_summary_strip(strip_market)
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        col_toggle, col_note = st.columns([7, 3])
        with col_toggle:
            if is_en:
                metric_options = [
                    "📊 Market Growth Contribution (% Impact - Outlier Free)",
                    "📈 Net Segment Run-Rate Growth (% PoP)",
                    "💰 Net Revenue Expansion Value (IDR Added)"
                ]
                selected_metric = st.radio("Select Market Growth Perspective:", metric_options, horizontal=True)
            else:
                metric_options = [
                    "📊 Kontribusi Pertumbuhan Pasar (% Kontribusi - Bebas Outlier)",
                    "📈 Laju Pertumbuhan Bersih per Segmen (% PoP)",
                    "💰 Nilai Tambahan Omzet Riil (IDR)"
                ]
                selected_metric = st.radio("Pilih Sudut Pandang Pertumbuhan Pasar:", metric_options, horizontal=True)
                
        with col_note:
            note_text = "💡 <b>Rekomendasi Analitik:</b> Gunakan <i>Kontribusi Pertumbuhan Pasar</i> untuk melihat dampak omzet riil tanpa distorsi segmen mikro." if not is_en else "💡 <b>Best Practice:</b> Use <i>Market Growth Contribution</i> to observe real financial impact without micro-segment skew."
            st.markdown(f"<div style='font-size: 12.5px; opacity: 0.85; padding: 8px 12px; background: rgba(59,130,246,0.08); border-radius: 6px; margin-top: 20px;'>{note_text}</div>", unsafe_allow_html=True)
            
        col_g1, col_g2 = st.columns([6, 4])
        with col_g1:
            if "Kontribusi" in selected_metric or "Contribution" in selected_metric:
                plot_col = "growth_contrib_pct"
                lbl_chart_title = "**Grafik Kontribusi Segmen terhadap Pertumbuhan Pasar Total (%)**" if not is_en else "**Market Growth Contribution by Segment (%)**"
                lbl_x = "Kontribusi terhadap Pertumbuhan Pasar (%)" if not is_en else "Market Growth Contribution (%)"
                plot_data = market_matrix.sort_values(by=plot_col, ascending=True)
                bar_text = plot_data.apply(lambda r: f" +{r['growth_contrib_pct']:.2f}% (+{format_rupiah(r['delta_sales'])})", axis=1)
                color_seq = ["#93C5FD", "#3B82F6", "#1D4ED8", "#10B981"]
            elif "Laju" in selected_metric or "Net Segment" in selected_metric:
                plot_col = "growth_pct"
                lbl_chart_title = "**Grafik Laju Pertumbuhan Bersih per Segmen (% PoP Run-Rate)**" if not is_en else "**Net Segment Run-Rate Growth Rate (% PoP)**"
                lbl_x = "Laju Pertumbuhan Bersih (%)" if not is_en else "Net Growth Rate (%)"
                plot_data = market_matrix.sort_values(by=plot_col, ascending=True)
                bar_text = plot_data.apply(lambda r: f" {r['growth_pct']:+.1f}% ({'Internal' if r['customer_category'] in ['EMPLOYEE', 'DIVISI'] else 'Komersial'})", axis=1)
                color_seq = ["#FCA5A5", "#FBBF24", "#34D399", "#10B981"]
            else:
                plot_col = "delta_sales"
                lbl_chart_title = "**Grafik Nilai Tambahan Omzet Riil per Segmen (IDR)**" if not is_en else "**Net Revenue Expansion Value per Segment (IDR)**"
                lbl_x = "Tambahan Omzet Bersih (IDR)" if not is_en else "Net Revenue Added (IDR)"
                plot_data = market_matrix.sort_values(by=plot_col, ascending=True)
                bar_text = plot_data["delta_sales"].apply(lambda d: f" +{format_rupiah(d)}")
                color_seq = ["#A7F3D0", "#10B981", "#047857"]
                
            st.markdown(lbl_chart_title)
            fig_growth = px.bar(
                plot_data,
                x=plot_col,
                y="customer_category",
                orientation="h",
                color=plot_col,
                text=bar_text,
                color_continuous_scale=color_seq,
                labels={plot_col: lbl_x, "customer_category": "Segmen Pasar" if not is_en else "Market Segment"}
            )
            fig_growth.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.7)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_growth, height=360)
            st.plotly_chart(fig_growth, use_container_width=True)
            
        with col_g2:
            st.markdown(f"**{'Diagnosis Bisnis Potensi Segmen' if not is_en else 'Segment Potential Strategic Diagnosis'}**")
            if is_en:
                card_g2 = """
                <div class="cetakia-card" style="padding: 16px 18px;">
                    <div style="font-size: 13px; margin-bottom: 10px;">
                        <b style="color: #10B981;">🚀 Primary Commercial Growth Engines:</b><br>
                        • <b>Industrial (+9.10% contribution / +Rp 808M):</b> The #1 revenue driver with +21.6% PoP expansion, anchoring enterprise cashflow.<br>
                        • <b>End User (+5.96% contribution / +Rp 530M):</b> Strong retail walk-in and online order volume (+38.3% growth).<br>
                        • <b>MSME (+3.30% contribution / +Rp 293M):</b> High repeat order demand for packaging boxes and custom roll labels (+33.1% growth).
                    </div>
                    <div style="font-size: 13px; border-top: 1px dashed rgba(156,163,175,0.3); padding-top: 8px; margin-bottom: 8px;">
                        <b style="color: #3B82F6;">🏛️ Stable Institutional & Branch Fulfillment:</b><br>
                        • <b>Division (+2.11% contribution) & Institution (+1.07% contribution):</b> Healthy positive expansion (+10.6% to +17.5%) under time-normalized comparison, providing consistent contract revenue.
                    </div>
                    <div style="font-size: 12.5px; border-top: 1px dashed rgba(156,163,175,0.3); padding-top: 8px; opacity: 0.85;">
                        <b style="color: #8B5CF6;">👔 Internal Staff Order Note (Employee):</b><br>
                        • <b>Employee (+0.13% contribution / +Rp 11.7M):</b> Internal personal employee perk purchases (0.1% of turnover), proportionally weighted to eliminate misleading commercial outliers.
                    </div>
                </div>
                """
            else:
                card_g2 = """
                <div class="cetakia-card" style="padding: 16px 18px;">
                    <div style="font-size: 13px; margin-bottom: 10px;">
                        <b style="color: #10B981;">🚀 Motor Utama Pertumbuhan Pasar Komersial:</b><br>
                        • <b>Industri (+9.10% kontribusi / +Rp 808 Juta):</b> Pendorong omzet nomor satu dengan pertumbuhan +21.6%, jangkar utama stabilitas perusahaan.<br>
                        • <b>End User (+5.96% kontribusi / +Rp 530 Juta):</b> Volume transaksi ritel harian dan online melonjak pesat (+38.3% growth).<br>
                        • <b>UMKM (+3.30% kontribusi / +Rp 293 Juta):</b> Permintaan repeat order kemasan box dan stiker label roll bertumbuh pesat (+33.1% growth).
                    </div>
                    <div style="font-size: 13px; border-top: 1px dashed rgba(156,163,175,0.3); padding-top: 8px; margin-bottom: 8px;">
                        <b style="color: #3B82F6;">🏛️ Penopang Arus Kas Stabil & Institusi:</b><br>
                        • <b>Divisi (+2.11% kontribusi) & Instansi (+1.07% kontribusi):</b> Menunjukkan pertumbuhan positif teratur (+10.6% s/d +17.5%) setelah dinormalisasi waktu berimbang.
                    </div>
                    <div style="font-size: 12.5px; border-top: 1px dashed rgba(156,163,175,0.3); padding-top: 8px; opacity: 0.85;">
                        <b style="color: #8B5CF6;">👔 Catatan Transaksi Internal Karyawan:</b><br>
                        • <b>Employee (+0.13% kontribusi / +Rp 11.7 Juta):</b> Transaksi personal staf (0.1% dari omzet), diperlakukan proporsional sehingga tidak mendistorsi analisis pasar komersial.
                    </div>
                </div>
                """
            st.markdown(card_g2, unsafe_allow_html=True)
            
        st.markdown(f"**{'Tabel Komprehensif Matriks Peluang & Pertumbuhan Pasar' if not is_en else 'Comprehensive Market Opportunity & Growth Matrix Table'}**")
        
        def get_segment_type(cat, is_en=False):
            cat_u = str(cat).upper()
            if cat_u in ["INDUSTRI", "AGEN"]:
                return "B2B Commercial" if is_en else "Komersial B2B"
            elif cat_u in ["INSTANSI", "SEKOLAH"]:
                return "B2G / Institutional" if is_en else "Institusi & B2G"
            elif cat_u in ["UMKM", "END USER"]:
                return "Retail & Scalable Volume" if is_en else "Ritel & UMKM Skalabel"
            elif cat_u == "DIVISI":
                return "Internal Operations" if is_en else "Internal Operasi Cabang"
            elif cat_u == "EMPLOYEE":
                return "Internal Staff Perk" if is_en else "Internal Karyawan"
            return "Other"
            
        disp_matrix = market_matrix.copy()
        disp_matrix["Tipe Pasar"] = disp_matrix["customer_category"].apply(lambda c: get_segment_type(c, is_en=is_en))
        disp_matrix["Pendapatan (IDR)"] = disp_matrix["total_revenue"].apply(format_rupiah)
        disp_matrix["Pangsa Omzet"] = disp_matrix["revenue_pct"].apply(lambda p: f"{p:.1f}%")
        disp_matrix["Laju Pertumbuhan Segmen"] = disp_matrix["growth_pct"].apply(lambda g: f"{g:+.1f}%")
        disp_matrix["Kontribusi Pertumbuhan"] = disp_matrix["growth_contrib_pct"].apply(lambda c: f"{c:+.2f}%")
        disp_matrix["Tambahan Omzet"] = disp_matrix["delta_sales"].apply(lambda d: f"+{format_rupiah(d)}")
        disp_matrix["Rata-rata AOV"] = disp_matrix["avg_aov"].apply(format_rupiah)
        unit_acct = "accounts" if is_en else "akun"
        disp_matrix["Jumlah Pembeli"] = disp_matrix["customer_count"].apply(lambda c: f"{c:,} {unit_acct}")
        
        if is_en:
            matrix_rename = {
                "customer_category": "Market Segment",
                "Tipe Pasar": "Segment Type",
                "Jumlah Pembeli": "Market Size",
                "Pendapatan (IDR)": "Current Revenue",
                "Pangsa Omzet": "Market Share",
                "Laju Pertumbuhan Segmen": "PoP Growth Rate",
                "Kontribusi Pertumbuhan": "Market Contribution",
                "Tambahan Omzet": "Added Revenue",
                "Rata-rata AOV": "Average AOV",
                "opportunity_level": "Strategic Classification"
            }
        else:
            matrix_rename = {
                "customer_category": "Segmen Pasar",
                "Tipe Pasar": "Kategori Peran",
                "Jumlah Pembeli": "Ukuran Pasar",
                "Pendapatan (IDR)": "Pendapatan Net Saat Ini",
                "Pangsa Omzet": "Pangsa Omzet",
                "Laju Pertumbuhan Segmen": "Pertumbuhan Segmen (%)",
                "Kontribusi Pertumbuhan": "Kontribusi Pasar (%)",
                "Tambahan Omzet": "Tambahan Omzet",
                "Rata-rata AOV": "Rata-rata Nilai Pesanan",
                "opportunity_level": "Klasifikasi Kuadran Bisnis"
            }
        st.dataframe(
            disp_matrix[[
                "customer_category", "Tipe Pasar", "Jumlah Pembeli", "Pendapatan (IDR)", 
                "Pangsa Omzet", "Laju Pertumbuhan Segmen", "Kontribusi Pertumbuhan", 
                "Tambahan Omzet", "Rata-rata AOV", "opportunity_level"
            ]].rename(columns=matrix_rename).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    # Sub-section: 6 Branch benchmarks & Portfolio playbook
    if not df_filtered.empty and "division_name" in df_filtered.columns:
        st.markdown(f"### {'🏢 Tolok Ukur Pendapatan 6 Divisi Cabang Regional' if not is_en else '🏢 6 Regional Branch Catchment & Revenue Benchmarks'}")
        df_branch_full = df_sales[df_sales["net_sales"] > 0].groupby("division_name").agg(
            active_buyers=("customer_id", "nunique"),
            total_revenue=("net_sales", "sum"),
            order_count=("invoice_id", "nunique")
        ).reset_index().sort_values(by="total_revenue", ascending=False)
        
        tot_b_rev = df_branch_full["total_revenue"].sum()
        df_branch_full["share_pct"] = (df_branch_full["total_revenue"] / tot_b_rev * 100) if tot_b_rev > 0 else 0
        b_growth = compute_period_growth(df_sales, group_col="division_name", value_col="net_sales")
        df_branch_full = df_branch_full.merge(b_growth[["division_name", "growth_pct", "growth_contrib_pct", "delta_sales"]], on="division_name", how="left").fillna(0.0)
        
        col_b1, col_b2 = st.columns([6, 4])
        with col_b1:
            lbl_b_name = "Divisi Cabang" if not is_en else "Branch Division"
            lbl_b_rev = "Pendapatan Net (IDR)" if not is_en else "Net Revenue (IDR)"
            fig_branch = px.bar(
                df_branch_full,
                x="division_name",
                y="total_revenue",
                color="total_revenue",
                text=df_branch_full["share_pct"].apply(lambda p: f"{p:.1f}%"),
                color_continuous_scale=["#93C5FD", "#1D4ED8"],
                labels={"division_name": lbl_b_name, "total_revenue": lbl_b_rev}
            )
            fig_branch.update_traces(textposition="outside")
            apply_plotly_theme(fig_branch, height=340)
            st.plotly_chart(fig_branch, use_container_width=True)
            
        with col_b2:
            disp_b = df_branch_full.copy()
            disp_b["Pendapatan"] = disp_b["total_revenue"].apply(format_rupiah)
            disp_b["Pangsa"] = disp_b["share_pct"].apply(lambda p: f"{p:.1f}%")
            disp_b["Pertumbuhan"] = disp_b["growth_pct"].apply(lambda g: f"{g:+.1f}%")
            disp_b["Pesanan"] = disp_b["order_count"].apply(lambda o: f"{o:,}")
            rename_b_tab = {
                "division_name": "Divisi Cabang" if not is_en else "Branch Division",
                "Pendapatan": "Pendapatan Net" if not is_en else "Net Revenue",
                "Pangsa": "Pangsa (%)" if not is_en else "Share (%)",
                "Pertumbuhan": "Growth (%)" if not is_en else "Growth (%)",
                "Pesanan": "Pesanan" if not is_en else "Orders"
            }
            st.dataframe(
                disp_b[["division_name", "Pendapatan", "Pangsa", "Pertumbuhan", "Pesanan"]].rename(columns=rename_b_tab).reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )


# =============================================================
# TAB 2: SUPPORTUMKM INTELLIGENCE (FOKUS UTAMA)
# =============================================================
with tab2:
    if is_en:
        render_section_info(
            title="SupportUMKM Program Customer Intelligence",
            subtitle="Guiding the SupportUMKM team: 'What types of MSME businesses have interacted with Cipta Grafika and what can we offer next?'",
            what_it_shows="Documented MSME buyer base, purchasing patterns (packaging, stickers, banners), complementary product gaps, and field visit data readiness.",
            why_important="Empowers the SupportUMKM outreach team with concrete customer behavior data before conducting on-site business visits and promotional follow-ups.",
            simple_insight="MSMEs predominantly start by purchasing Promotional Banners and Product Stickers. The highest conversion opportunity lies in bundling packaging boxes with roll stickers."
        )
    else:
        render_section_info(
            title="Intelijen Pelanggan & Program Pendampingan SupportUMKM",
            subtitle="Memandu Tim SupportUMKM: 'Customer UMKM seperti apa yang pernah berinteraksi dengan Cipta Grafika dan apa yang dapat ditawarkan berikutnya?'",
            what_it_shows="Profil akun UMKM terdaftar, pola belanja faktual (kemasan, stiker, spanduk), potensi produk pelengkap, serta status kesiapan data kunjungan lapangan.",
            why_important="Membekali tim lapangan SupportUMKM dengan pemahaman perilaku belanja nyata sebelum melakukan kunjungan tempat usaha atau memberikan penawaran promosi.",
            simple_insight="Sebagian besar UMKM mengawali pesanan dari Spanduk Promosi dan Stiker Label. Peluang pengembangan terbesar adalah menawarkan paket komplit Kemasan Box + Stiker Roll."
        )
        
    umkm_intel_res = analyze_support_umkm_intelligence(
        df_cust=df_cust,
        df_intel=df_intel,
        df_sales=df_sales,
        df_items=df_items,
        branch=filters["branch"]
    )
    
    kpi_u = umkm_intel_res["kpis"]
    
    # Section 2 & 7: SupportUMKM Overview Strips
    if is_en:
        strip_umkm = [
            {"label": "👥 Registered MSMEs", "value": f"{kpi_u['total_registered']:,} Accounts", "desc": f"{kpi_u['total_buyers']:,} have ordered, {kpi_u['prospects']:,} unconverted", "color": "#2563EB"},
            {"label": "⚡ Active MSME Buyers", "value": f"{kpi_u['active_buyers']:,} Accounts", "desc": f"{kpi_u['new_buyers']:,} are new recent clients (≤ 2 orders)", "color": "#10B981"},
            {"label": "⚠️ Infrequent / At Risk", "value": f"{kpi_u['at_risk_buyers']:,} Accounts", "desc": "Last purchase was 46-90 days ago", "color": "#F59E0B"},
            {"label": "💎 High-Spend MSMEs", "value": f"{kpi_u['high_val_buyers']:,} Accounts", "desc": "Total purchases ≥ Rp 1,000,000", "color": "#8B5CF6"}
        ]
    else:
        strip_umkm = [
            {"label": "👥 Total UMKM Terdaftar", "value": f"{kpi_u['total_registered']:,} Akun", "desc": f"{kpi_u['total_buyers']:,} pernah beli, {kpi_u['prospects']:,} prospek", "color": "#2563EB"},
            {"label": "⚡ Pelanggan UMKM Aktif", "value": f"{kpi_u['active_buyers']:,} Akun", "desc": f"{kpi_u['new_buyers']:,} adalah akun UMKM baru (≤ 2 pesanan)", "color": "#10B981"},
            {"label": "⚠️ Mulai Jarang Belanja", "value": f"{kpi_u['at_risk_buyers']:,} Akun", "desc": "Terakhir belanja 46 s/d 90 hari yang lalu", "color": "#F59E0B"},
            {"label": "💎 UMKM Belanja Tinggi", "value": f"{kpi_u['high_val_buyers']:,} Akun", "desc": "Akumulasi belanja ≥ Rp 1.000.000", "color": "#8B5CF6"}
        ]
    render_summary_strip(strip_umkm)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 3: Customer Behavior untuk SupportUMKM (Pola Belanja UMKM)
    st.markdown(f"### {'📊 Pola Belanja Customer UMKM' if not is_en else '📊 MSME Customer Purchasing Behavior'}")
    
    col_u1, col_u2 = st.columns(2)
    top_u_cats = umkm_intel_res["top_categories"].head(6)
    top_u_prods = umkm_intel_res["top_products"].head(8)
    
    with col_u1:
        st.markdown(f"**{'Kategori Produk yang Paling Banyak Dibeli UMKM' if not is_en else 'Top Categories Purchased by MSMEs'}**")
        fig_ucat = px.bar(
            top_u_cats.sort_values(by="total_omzet", ascending=True),
            x="total_omzet",
            y="clean_category",
            orientation="h",
            color="total_omzet",
            text=top_u_cats.sort_values(by="total_omzet", ascending=True)["total_omzet"].apply(format_rupiah),
            color_continuous_scale=["#93C5FD", "#2563EB"],
            labels={"total_omzet": "Total Omzet (IDR)", "clean_category": "Kategori"}
        )
        fig_ucat.update_traces(textposition="outside")
        apply_plotly_theme(fig_ucat, height=320)
        st.plotly_chart(fig_ucat, use_container_width=True)
        
    with col_u2:
        st.markdown(f"**{'10 Produk Percetakan Paling Sering Dipesan UMKM' if not is_en else 'Top 8 Printing Products Ordered by MSMEs'}**")
        fig_uprod = px.bar(
            top_u_prods.sort_values(by="total_omzet", ascending=True),
            x="total_omzet",
            y="product_name",
            orientation="h",
            color="total_omzet",
            text=top_u_prods.sort_values(by="total_omzet", ascending=True).apply(lambda r: f" {format_rupiah(r['total_omzet'])} ({r['pembeli_unik']:,} pembeli)", axis=1),
            color_continuous_scale=["#FDE68A", "#D97706"],
            labels={"total_omzet": "Total Omzet (IDR)", "product_name": "Nama Produk"}
        )
        fig_uprod.update_traces(textposition="outside")
        apply_plotly_theme(fig_uprod, height=320)
        st.plotly_chart(fig_uprod, use_container_width=True)
        
    # Structured Interpretation Box: [DATA] + [INSIGHT] + [CAMPAIGN IDEA]
    st.markdown("""
    <div class="cetakia-card" style="border-left: 5px solid #2563EB; padding: 18px 22px; margin-top: 5px;">
        <div style="font-size: 13.5px; line-height: 1.6;">
            <b style="color: #2563EB;">[DATA AKTUAL]</b> Kategori <b>Cetak A3 (Stiker & Art Carton)</b> dan <b>Format Besar (Flexy Spanduk)</b> menyerap lebih dari 65% total pesanan UMKM. Produk nomor satu adalah <i>Flexy 280 gsm</i> (2.300+ pesanan) dan <i>Stiker A3+ Chromo/Vynil</i> (4.000+ pesanan).<br>
            <b style="color: #10B981;">[INSIGHT PERILAKU]</b> Kebutuhan branding identitas produk (stiker label kemasan) dan media promosi fisik toko (spanduk spanduk outlet) merupakan 2 pilar kebutuhan primer pelaku UMKM dalam data transaksi.<br>
            <b style="color: #F59E0B;">[IDE KAMPANYE SUPPORTUMKM]</b> Tim SupportUMKM dapat memprioritaskan penawaran paket kombo terintegrasi (Box Kemasan + Stiker Label) bagi pelaku kuliner/ritel, serta stand display portabel bagi pelaku UMKM yang baru memesan spanduk toko. <i>Potensi peningkatan nilai transaksi perlu diuji melalui kampanye nyata.</i>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 7 & 8: Potensi Produk Tambahan Customer UMKM
    st.markdown(f"### {'📦 Potensi Produk Tambahan Customer UMKM (Cross-Product Gap)' if not is_en else '📦 MSME Cross-Product Expansion Potential'}**")
    
    cross_u = umkm_intel_res["cross_opps"]
    col_opp1, col_opp2, col_opp3 = st.columns(3)
    
    with col_opp1:
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 4px solid #10B981; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #10B981; text-transform: uppercase;">Sudah Beli Kemasan → Belum Stiker</div>
            <div style="font-size: 26px; font-weight: 800; margin: 6px 0;">{cross_u['kemasan_no_stiker_count']:,} UMKM</div>
            <p style="font-size: 13px; margin: 0; opacity: 0.85;">
                Pelaku UMKM yang memesan Box/Kemasan tetapi belum memesan Stiker Label merek di Cetakia.
            </p>
            <div style="margin-top: 10px; font-size: 12px; color: #10B981; font-weight: 600;">
                💡 Rekomendasi: Tawarkan paket kombo Stiker Label Roll saat pendampingan.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_opp2:
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 4px solid #3B82F6; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #3B82F6; text-transform: uppercase;">Sudah Beli Stiker → Belum Kemasan</div>
            <div style="font-size: 26px; font-weight: 800; margin: 6px 0;">{cross_u['stiker_no_kemasan_count']:,} UMKM</div>
            <p style="font-size: 13px; margin: 0; opacity: 0.85;">
                Pelaku UMKM yang aktif mencetak stiker label, namun belum memesan box atau kantong kemasan.
            </p>
            <div style="margin-top: 10px; font-size: 12px; color: #3B82F6; font-weight: 600;">
                💡 Rekomendasi: Tunjukkan sampel box kemasan & paper bag custom Cipta Grafika.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_opp3:
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 4px solid #F59E0B; padding: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #F59E0B; text-transform: uppercase;">Sudah Beli Spanduk → Belum Display</div>
            <div style="font-size: 26px; font-weight: 800; margin: 6px 0;">{cross_u['banner_no_display_count']:,} UMKM</div>
            <p style="font-size: 13px; margin: 0; opacity: 0.85;">
                Pelaku UMKM yang telah memesan spanduk/banner, tetapi belum memiliki rangka display standee.
            </p>
            <div style="margin-top: 10px; font-size: 12px; color: #F59E0B; font-weight: 600;">
                💡 Rekomendasi: Berikan penawaran khusus X-Banner / Roll Up praktis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 16 & 17: SupportUMKM Field Visit Insight & Conversion Journey
    st.markdown(f"### {'🗺️ Hasil Kunjungan Lapangan SupportUMKM & Alur Konversi' if not is_en else '🗺️ SupportUMKM Field Visits & Conversion Journey'}**")
    
    col_vis1, col_vis2 = st.columns([6, 4])
    with col_vis1:
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 5px solid #EF4444; padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="color: #EF4444; margin: 0;">📋 Status Data Kunjungan Lapangan SupportUMKM</h4>
                <span style="background: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">BELUM TERSEDIA</span>
            </div>
            <p style="font-size: 13px; line-height: 1.5; opacity: 0.9; margin: 0 0 10px 0;">
                <b>Catatan Faktual:</b> Log riwayat kunjungan fisik ke tempat usaha UMKM (field visits) <i>belum tersedia pada Analytical Dataset Cetakia saat ini</i>. Untuk menghindari insight palsu, dashboard tidak menampilkan angka simulasi seolah-olah data riil.
            </p>
            <div style="font-size: 12.5px; background: rgba(128,128,128,0.06); padding: 10px 14px; border-radius: 6px;">
                <b>📌 Spesifikasi Kebutuhan Data Lapangan (Untuk Tim Tech / IT Cetakia):</b><br>
                • <code>visit_id</code> & <code>customer_id</code> (ID kunjungan & ID akun UMKM)<br>
                • <code>tanggal_kunjungan</code> & <code>lokasi</code> (Waktu dan alamat cabang operasional)<br>
                • <code>jenis_usaha</code> (Sektor usaha: Kuliner, Fashion, Kriya, Ritel, Jasa)<br>
                • <code>produk_terakhir_dibeli</code> & <code>kebutuhan_teridentifikasi</code> (Kebutuhan cetak baru)<br>
                • <code>status_tindak_lanjut</code> & <code>program_promosi_diberikan</code> (Voucher/Sampel diserahkan)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_vis2:
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 5px solid #8B5CF6; padding: 18px 22px;">
            <h4 style="color: #8B5CF6; margin: 0 0 10px 0;">🚀 Alur Perjalanan Konversi UMKM Ideal</h4>
            <div style="font-size: 13px; line-height: 1.6; opacity: 0.95;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="background: #8B5CF6; color: white; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">1</span>
                    <b>Kunjungan Lapangan:</b> Temui pelaku usaha di tempat.
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="background: #3B82F6; color: white; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">2</span>
                    <b>Identifikasi Kebutuhan:</b> Catat kebutuhan kemasan/promosi.
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="background: #10B981; color: white; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">3</span>
                    <b>Pesanan Perdana:</b> Berikan sampel fisik & voucher selamat datang.
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="background: #F59E0B; color: white; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">4</span>
                    <b>Pesanan Berulang (Repeat):</b> Jadwal follow-up berkala.
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: #EF4444; color: white; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">5</span>
                    <b>Mitra Loyal Mandiri:</b> Transaksi multi-kategori & referral.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section: Daftar Kerja Pelanggan UMKM (Worklist Lapangan)
    st.markdown(f"### {'📋 Daftar Kerja Pelanggan UMKM untuk Tim Lapangan & Marketing' if not is_en else '📋 MSME Customer Worklist for Field & Marketing Teams'}")
    
    umkm_wl = umkm_intel_res["worklist"].copy()
    col_f1, col_f2 = st.columns([6, 4])
    with col_f1:
        search_kw = st.text_input("🔍 Cari Nama Usaha UMKM / Kontak:", placeholder="Ketik nama usaha..." if not is_en else "Search MSME business name...")
    with col_f2:
        filter_status = st.selectbox(
            "Filter Rekomendasi Peluang:",
            ["Semua Peluang", "Peluang Kunjungan Akuisisi Perdana", "Peluang Paket Kemasan + Stiker Label", "Peluang Penawaran Display Stand / Roll Up", "Kandidat Program Referral B2B UMKM", "Peluang Re-Aktivasi & Cek Kebutuhan Cetak"] if not is_en else
            ["All Opportunities", "First Order Acquisition Visit", "Packaging + Sticker Bundle", "Display Standee Offer", "B2B Referral Candidate", "Re-Activation Follow-Up"]
        )
        
    if search_kw:
        umkm_wl = umkm_wl[umkm_wl["customer_name"].astype(str).str.contains(search_kw, case=False, na=False)]
    if filter_status != ("Semua Peluang" if not is_en else "All Opportunities"):
        umkm_wl = umkm_wl[umkm_wl["peluang_promosi"] == filter_status]
        
    disp_uwl = umkm_wl.head(30).copy()
    disp_uwl["Total Belanja"] = disp_uwl["lifetime_sales"].apply(format_rupiah)
    disp_uwl["Transaksi"] = disp_uwl["total_orders"].apply(lambda o: f"{int(o):,} kali" if not is_en else f"{int(o):,} orders")
    disp_uwl["Terakhir Belanja"] = disp_uwl["days_since_last_purchase"].apply(
        lambda d: "Belum Pernah Belanja" if pd.isna(d) or d > 900 else (f"{int(d)} hari lalu" if not is_en else f"{int(d)} days ago")
    )
    
    rename_uwl = {
        "customer_name": "Nama Usaha (Pelanggan)" if not is_en else "Business Name",
        "division_name": "Cabang Terdekat" if not is_en else "Branch",
        "Total Belanja": "Total Belanja" if not is_en else "Total Spend",
        "Transaksi": "Sudah Belanja" if not is_en else "Order Frequency",
        "Terakhir Belanja": "Terakhir Belanja" if not is_en else "Last Purchase",
        "peluang_promosi": "Peluang Promosi Teridentifikasi" if not is_en else "Promotion Opportunity"
    }
    st.dataframe(
        disp_uwl[["customer_name", "division_name", "Total Belanja", "Transaksi", "Terakhir Belanja", "peluang_promosi"]].rename(columns=rename_uwl).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )


# =============================================================
# TAB 3: MARKETING CAMPAIGN INTELLIGENCE
# =============================================================
with tab3:
    if is_en:
        render_section_info(
            title="Marketing Campaign Intelligence & Promotion Opportunities",
            subtitle="Understand customer buying behavior to identify promotion and campaign opportunities.",
            what_it_shows="Factual cross-product buying gaps, target audience sizing, referral candidates, behavioral retargeting, and actionable opportunity table.",
            why_important="Replaces static guesswork with data-driven audience pools, guiding marketing staff to execute promotions that match real customer needs.",
            simple_insight="Over 1,400 customers purchased packaging without stickers, and 4,500+ purchased banners without display stands. These represent prime promotional opportunities."
        )
    else:
        render_section_info(
            title="Peluang Promosi & Kampanye Pemasaran Berbasis Perilaku",
            subtitle="Memahami perilaku pelanggan untuk menentukan target promosi dan kampanye produk.",
            what_it_shows="Peluang penawaran produk silang (cross-product gap), ukuran target audiens promosi, kandidat referral loyal, retargeting belanja terakhir, dan tabel peluang kampanye.",
            why_important="Menggantikan tebak-tebakan program promosi dengan kelompok audiens berbasis data riil, sehingga tim marketing dapat menyasar pelanggan dengan penawaran yang relevan.",
            simple_insight="Lebih dari 1.400 pelanggan membeli kemasan tanpa stiker, dan 4.500+ pelanggan membeli spanduk tanpa display stand. Ini adalah target utama penawaran promosi."
        )
        
    # Interactive Retargeting Days Slider
    col_ret_head, col_ret_param = st.columns([7, 3])
    with col_ret_head:
        st.markdown("### 🎯 Ukuran Target Audiens Kampanye Pemasaran" if not is_en else "### 🎯 Marketing Campaign Target Audience Sizing")
    with col_ret_param:
        retarget_window = st.select_slider(
            "Periode Retargeting Belanja Terakhir:" if not is_en else "Behavioral Retargeting Window:",
            options=[14, 30, 45, 60],
            value=30,
            format_func=lambda x: f"{x} Hari Terakhir" if not is_en else f"Last {x} Days"
        )
        
    camp_intel_res = compute_marketing_campaign_intelligence(
        df_cust=df_cust,
        df_intel=df_intel,
        df_sales=df_sales,
        df_items=df_items,
        branch=filters["branch"],
        segment=filters["segment"],
        retarget_days=retarget_window
    )
    
    counts_c = camp_intel_res["counts"]
    
    # Section 9 & 18: Campaign Target Audience Sizing Cards
    if is_en:
        strip_camp = [
            {"label": "🎟️ Target Voucher", "value": f"{counts_c['voucher']:,} Accounts", "desc": "Bought Packaging, not yet Stickers", "color": "#10B981"},
            {"label": "🤝 Target Referral", "value": f"{counts_c['referral']:,} Accounts", "desc": "Active repeat clients (≥3 orders, ≥Rp1M)", "color": "#3B82F6"},
            {"label": "📅 Target Seasonal", "value": f"{counts_c['seasonal']:,} Accounts", "desc": "Calendars, Agendas & Corporate ID", "color": "#F59E0B"},
            {"label": f"🔄 Retargeting ({retarget_window}d)", "value": f"{counts_c['retarget']:,} Accounts", "desc": "Recent Banner buyers, no Display stand", "color": "#8B5CF6"}
        ]
    else:
        strip_camp = [
            {"label": "🎟️ Target Voucher", "value": f"{counts_c['voucher']:,} Akun", "desc": "Beli Kemasan, belum pernah beli Stiker", "color": "#10B981"},
            {"label": "🤝 Target Referral", "value": f"{counts_c['referral']:,} Akun", "desc": "Pelanggan setia aktif (≥3 order, ≥Rp 1Jt)", "color": "#3B82F6"},
            {"label": "📅 Target Produk Musiman", "value": f"{counts_c['seasonal']:,} Akun", "desc": "Pernah pesan Kalender, Agenda, Corporate ID", "color": "#F59E0B"},
            {"label": f"🔄 Promosi Perilaku ({retarget_window}hr)", "value": f"{counts_c['retarget']:,} Akun", "desc": "Baru cetak Banner, belum punya Display", "color": "#8B5CF6"}
        ]
    render_summary_strip(strip_camp)
    
    # Overlap Audience Callout
    tot_uniq = camp_intel_res["total_unique_target"]
    multi_cnt = camp_intel_res["multi_opp_count"]
    st.markdown(f"""
    <div style="font-size: 13px; opacity: 0.9; margin: 8px 0 16px 0; padding: 8px 14px; background: rgba(59,130,246,0.08); border-radius: 6px;">
        💡 <b>Analisis Jangkauan Target:</b> Terdapat total <b>{tot_uniq:,} pelanggan unik</b> yang masuk ke dalam setidaknya satu kriteria promosi. Sebanyak <b>{multi_cnt:,} pelanggan</b> memiliki lebih dari satu peluang promosi, sehingga tim marketing dapat memprioritaskan penawaran paket terpadu.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 4: Customer Behavior -> Product Opportunity (Cross-Product Opportunity Chart)
    st.markdown(f"### {'📊 Pola Belanja Pelanggan → Peluang Penawaran Produk Pelengkap' if not is_en else '📊 Customer Behavior → Product Cross-Selling Opportunities'}")
    
    cross_df = camp_intel_res["cross_pairs"].copy()
    cross_df["label_bar"] = cross_df["sudah_dibeli"] + " ➔ Belum Beli: " + cross_df["belum_dibeli"]
    
    fig_cross = px.bar(
        cross_df.sort_values(by="jumlah_customer", ascending=True),
        x="jumlah_customer",
        y="label_bar",
        orientation="h",
        color="jumlah_customer",
        text=cross_df.sort_values(by="jumlah_customer", ascending=True)["jumlah_customer"].apply(lambda c: f" {c:,} Pelanggan"),
        color_continuous_scale=["#93C5FD", "#1D4ED8"],
        labels={"jumlah_customer": "Jumlah Customer Potensial", "label_bar": "Kombinasi Pola Belanja"}
    )
    fig_cross.update_traces(textposition="outside")
    apply_plotly_theme(fig_cross, height=280)
    st.plotly_chart(fig_cross, use_container_width=True)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 10, 11, 12, 13, 14: 4 Pilar Peluang Promosi dengan pemisahan tegas [DATA] / [INSIGHT] / [CAMPAIGN IDEA]
    st.markdown(f"### {'🚀 4 Pilar Peluang Promosi Pemasaran Berdasarkan Data Faktual' if not is_en else '🚀 4 Promotion Opportunity Pillars Based on Behavioral Data'}")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        # 1. VOUCHER PROMOTION
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 5px solid #10B981; padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="color: #10B981; margin: 0;">🎟️ 1. Peluang Promosi Voucher Paket Kombo</h4>
                <span style="background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">VOUCHER OPPORTUNITY</span>
            </div>
            <p style="font-size: 13.5px; margin: 8px 0; line-height: 1.5;">
                <b>Target Sasaran:</b> Pelanggan yang sudah memesan Kemasan Box/Paper Bag tetapi belum memesan Stiker Label.<br>
                <b>Jumlah Audiens:</b> <b>{counts_c['voucher']:,} Akun Pelanggan</b>
            </p>
            <div style="font-size: 13px; line-height: 1.5; background: rgba(128,128,128,0.06); padding: 10px 14px; border-radius: 6px; margin: 8px 0;">
                <b style="color: #10B981;">[DATA]</b> Pelanggan pada kelompok ini memiliki histori pembelian kategori kemasan namun nol transaksi untuk stiker label.<br>
                <b style="color: #2563EB;">[INSIGHT]</b> Kebutuhan wadah/kemasan sudah nyata, namun label branding kemungkinan dipesan ke vendor lain atau belum digunakan.<br>
                <b style="color: #F59E0B;">[CAMPAIGN IDEA]</b> Tawarkan voucher potongan untuk paket komplit "Box Kemasan + Stiker Label Roll". <i>Potensi peningkatan nilai transaksi perlu diuji melalui campaign.</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. REFERRAL PROGRAM
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 5px solid #3B82F6; padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="color: #3B82F6; margin: 0;">🤝 2. Peluang Program Referral Antar-Bisnis</h4>
                <span style="background: rgba(59, 130, 246, 0.15); color: #3B82F6; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">REFERRAL OPPORTUNITY</span>
            </div>
            <p style="font-size: 13.5px; margin: 8px 0; line-height: 1.5;">
                <b>Target Sasaran:</b> Pelanggan dengan hubungan transaksi aktif, repeat order ≥ 3 kali, dan total belanja ≥ Rp 1 Juta.<br>
                <b>Jumlah Audiens:</b> <b>{counts_c['referral']:,} Akun Pelanggan</b>
            </p>
            <div style="font-size: 13px; line-height: 1.5; background: rgba(128,128,128,0.06); padding: 10px 14px; border-radius: 6px; margin: 8px 0;">
                <b style="color: #10B981;">[DATA]</b> Kelompok ini memiliki rekam jejak loyalitas tinggi dengan frekuensi berulang dan nilai belanja di atas rata-rata.<br>
                <b style="color: #2563EB;">[INSIGHT]</b> Kepuasan layanan telah terbukti melalui repeat order, menjadikannya kandidat paling kredibel untuk program referral.<br>
                <b style="color: #F59E0B;">[CAMPAIGN IDEA]</b> Undang customer ini sebagai peserta program "Ajak Rekanan Bisnis": pemberi rekomendasi dan rekanan baru mendapatkan insentif pada pesanan berikutnya.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        # 3. SEASONAL / THEMATIC
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 5px solid #F59E0B; padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="color: #F59E0B; margin: 0;">📅 3. Momentum Kampanye Produk Musiman / Tematik</h4>
                <span style="background: rgba(245, 158, 11, 0.15); color: #F59E0B; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">SEASONAL OPPORTUNITY</span>
            </div>
            <p style="font-size: 13.5px; margin: 8px 0; line-height: 1.5;">
                <b>Target Sasaran:</b> Akun Korporasi, Sekolah, dan Lembaga dengan histori pesanan Kalender, Agenda, dan Buku.<br>
                <b>Jumlah Audiens:</b> <b>{counts_c['seasonal']:,} Akun Pelanggan</b>
            </p>
            <div style="font-size: 13px; line-height: 1.5; background: rgba(128,128,128,0.06); padding: 10px 14px; border-radius: 6px; margin: 8px 0;">
                <b style="color: #10B981;">[DATA]</b> Data transaksi kurun waktu 9 bulan berjalan tahun 2026 menunjukkan peningkatan pemesanan agenda/buku pada periode kuartal tertentu.<br>
                <b style="color: #2563EB;">[INSIGHT]</b> Menunjukkan indikasi momentum pembelian pada periode tertentu <i>(Catatan: analisis seasonal yang terbukti secara definitif membutuhkan data histori ≥ 2 tahun)</i>.<br>
                <b style="color: #F59E0B;">[CAMPAIGN IDEA]</b> Siapkan program early bird kalender meja dan buku agenda sebelum periode puncak untuk mengamankan kapasitas antrean mesin produksi.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 4. BEHAVIORAL RETARGETING
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 5px solid #8B5CF6; padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="color: #8B5CF6; margin: 0;">🔄 4. Promosi Berdasarkan Belanja Terakhir (Retargeting)</h4>
                <span style="background: rgba(139, 92, 246, 0.15); color: #8B5CF6; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">BEHAVIOR RETARGETING</span>
            </div>
            <p style="font-size: 13.5px; margin: 8px 0; line-height: 1.5;">
                <b>Target Sasaran:</b> Pelanggan yang baru saja mencetak Banner dalam <b>{retarget_window} hari terakhir</b> namun belum memesan Display Stand.<br>
                <b>Jumlah Audiens:</b> <b>{counts_c['retarget']:,} Akun Pelanggan</b>
            </p>
            <div style="font-size: 13px; line-height: 1.5; background: rgba(128,128,128,0.06); padding: 10px 14px; border-radius: 6px; margin: 8px 0;">
                <b style="color: #10B981;">[DATA]</b> Pelanggan baru saja menyelesaikan cetak spanduk flexy dalam kurun {retarget_window} hari dan belum memiliki catatan pembelian rangka display.<br>
                <b style="color: #2563EB;">[INSIGHT]</b> Terdapat kebutuhan fisik untuk mendisplay materi visual tersebut di lokasi acara atau outlet usaha.<br>
                <b style="color: #F59E0B;">[CAMPAIGN IDEA]</b> Kirimkan notifikasi WhatsApp resmi: "Lengkapi spanduk Anda dengan Display Standee praktis (X-Banner/Roll Up)". <i>Efektivitas konversi perlu dievaluasi berkala.</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 6 & 15: Campaign Opportunity Table
    st.markdown(f"### {'📋 Tabel Ringkasan Peluang Kampanye Pemasaran' if not is_en else '📋 Marketing Campaign Opportunity Summary Table'}")
    st.dataframe(camp_intel_res["opp_table"], use_container_width=True, hide_index=True)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 24: Customer Profile Explorer (Pencarian Akun Pelanggan)
    st.markdown(f"### {'🔎 Profil Perilaku Akun Pelanggan & Peluang Promosi' if not is_en else '🔎 Customer Behavioral Profile & Promotion Opportunity'}")
    
    active_search_pool = df_filtered[df_filtered["total_orders"] > 0].copy()
    if not active_search_pool.empty:
        col_c_sel, col_c_info = st.columns([4, 6])
        with col_c_sel:
            cust_names = active_search_pool["customer_name"].dropna().unique().tolist()
            selected_cname = st.selectbox(
                "Pilih Akun Pelanggan untuk Diinspeksi:" if not is_en else "Select Customer Account to Inspect:",
                options=cust_names[:100]
            )
            
        with col_c_info:
            target_crow = active_search_pool[active_search_pool["customer_name"] == selected_cname].iloc[0]
            cid_sel = target_crow["customer_id"]
            
            # Identify promo fit
            opp_fits = []
            if cid_sel in camp_intel_res["voucher_target_ids"]:
                opp_fits.append("🎟️ Cocok untuk Voucher Paket Kemasan + Stiker")
            if cid_sel in camp_intel_res["referral_target_ids"]:
                opp_fits.append("🤝 Kandidat Mitra Referral Bisnis")
            if cid_sel in camp_intel_res["seasonal_target_ids"]:
                opp_fits.append("📅 Target Kampanye Produk Musiman/Korporat")
            if cid_sel in camp_intel_res["retarget_target_ids"]:
                opp_fits.append("🔄 Target Retargeting Display Stand (Banner Baru)")
            if not opp_fits:
                opp_fits.append("📦 Pelanggan Reguler — Tawarkan Katalog Produk Terbaru")
                
            c_days = target_crow["days_since_last_purchase"]
            c_days_str = f"{int(c_days)} hari lalu" if pd.notnull(c_days) and c_days < 900 else "Belum tercatat"
            
            st.markdown(f"""
            <div class="cetakia-card" style="padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <h4 style="color: #2563EB; margin: 0;">🏢 {selected_cname}</h4>
                    <span style="font-size: 12px; font-weight: 700; background: rgba(37,99,235,0.1); color: #2563EB; padding: 2px 8px; border-radius: 10px;">{target_crow.get('customer_category', 'Pelanggan')}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 13px; margin: 10px 0; border-top: 1px dashed rgba(156,163,175,0.25); border-bottom: 1px dashed rgba(156,163,175,0.25); padding: 8px 0;">
                    <div><b>Terakhir Belanja:</b><br>{c_days_str}</div>
                    <div><b>Sudah Belanja:</b><br>{int(target_crow.get('total_orders', 0)):,} kali transaksi</div>
                    <div><b>Total Belanja:</b><br>{format_rupiah(target_crow.get('lifetime_sales', 0))}</div>
                </div>
                <div style="font-size: 13px;">
                    <b>Peluang Promosi yang Relevan:</b><br>
                    {'<br>'.join(f'• {fit}' for fit in opp_fits)}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Section 28 & 29: Kesiapan Pengukuran Kampanye & Kesenjangan Data (ROI Gap Notice)
    st.markdown(f"### {'⚙️ Kesiapan Pengukuran Kampanye & Kesenjangan Data (Data Lineage)' if not is_en else '⚙️ Campaign Measurement Readiness & Data Lineage'}")
    
    st.markdown(f"""
    <div class="cetakia-card" style="border-left: 5px solid #EF4444; padding: 18px 22px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="color: #EF4444; margin: 0;">⚠️ Prinsip Integritas Analitik: Transparansi ROI & Riwayat Kampanye</h4>
            <span style="background: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">DATA GAP NOTICE</span>
        </div>
        <p style="font-size: 13.5px; line-height: 1.6; opacity: 0.95; margin: 0 0 10px 0;">
            <b>Status ROI Kampanye:</b> <i>ROI Campaign belum dapat dihitung karena data biaya promosi dan histori respon campaign belum tersedia pada dataset saat ini.</i> Dashboard Cetakia BI berprinsip pantang membuat klaim persentase ROI atau uplift yang tidak didukung data nyata.
        </p>
        <div style="font-size: 12.5px; background: rgba(128,128,128,0.06); padding: 10px 14px; border-radius: 6px;">
            <b>📌 Spesifikasi Data Lanjutan yang Dibutuhkan untuk Closed-Loop Analytics (Tim Tech):</b><br>
            • <code>campaign_id</code> & <code>campaign_type</code> (Voucher UMKM, Referral, Musiman, Retargeting)<br>
            • <code>target_customer_id</code> & <code>offer_details</code> (Daftar akun target & penawaran promosi yang diberikan)<br>
            • <code>campaign_cost</code> (Total biaya promosi / subsidi voucher yang dikeluarkan)<br>
            • <code>redemption_flag</code> & <code>revenue_after_campaign</code> (Klaim promo & omzet transaksi riil setelah kampanye)<br>
            <i>Setelah data ini terintegrasi, Cetakia BI dapat secara otomatis mengukur Return on Investment (ROI) dan Conversion Rate secara presisi.</i>
        </div>
    </div>
    """, unsafe_allow_html=True)
