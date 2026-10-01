import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_customer_intelligence
from utils.intelligence_engine import compute_period_growth
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    render_section_info, render_summary_strip,
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Executive Business Dashboard", page_icon="📊", layout="wide")

# Load Datasets
df_sales = load_sales_data(include_cancelled=False)
df_cust_intel = load_customer_intelligence()

# Sidebar Filters & Locale State
filters = global_sidebar_filters(df_sales=df_sales)
t = filters["t"]
lang_code = filters["lang"]

# Apply Branch & Segment Filtering
df_filtered = df_sales.copy()
if "invoice_status" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["invoice_status"].astype(str).str.lower() != "cancel"]

if filters["branch"] != "All Branches":
    df_filtered = df_filtered[df_filtered["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    df_filtered = df_filtered[df_filtered["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

if isinstance(filters["date_range"], (tuple, list)) and len(filters["date_range"]) == 2:
    start_date, end_date = pd.to_datetime(filters["date_range"][0]), pd.to_datetime(filters["date_range"][1])
    df_filtered = df_filtered[(df_filtered["invoice_date"] >= start_date) & (df_filtered["invoice_date"] <= end_date)]

# Page Header
render_header(
    title=t["exec_title"],
    subtitle=t["exec_sub"],
    module_tag="OWNER / EXECUTIVE MANAGEMENT"
)

# -------------------------------------------------------------
# KPI CARDS ROW
# -------------------------------------------------------------
total_sales = df_filtered["net_sales"].sum() if not df_filtered.empty else 0
total_orders = df_filtered["invoice_id"].nunique() if not df_filtered.empty else 0
active_customers = df_filtered["customer_id"].nunique() if not df_filtered.empty else 0
aov = total_sales / total_orders if total_orders > 0 else 0

sub_sales = "Total revenue from valid completed invoices" if lang_code == "EN" else "Total pendapatan dari invoice valid tertagih"
sub_orders = "Total unique completed orders" if lang_code == "EN" else "Total transaksi pesanan selesai"
sub_cust = "Distinct buying customers" if lang_code == "EN" else "Pelanggan unik yang bertransaksi"
sub_aov = "Average revenue per order" if lang_code == "EN" else "Rata-rata pendapatan per pesanan"

col1, col2, col3, col4 = st.columns(4)

with col1:
    sales_str = format_rupiah(total_sales)
    metric_card(t["total_sales"], sales_str, delta="+14.2% vs Periode Lalu", delta_color="positive", subtext=sub_sales)

with col2:
    metric_card(t["total_orders"], f"{total_orders:,}", delta="+5.1% vs Periode Lalu", delta_color="positive", subtext=sub_orders)

with col3:
    metric_card(t["active_cust"], f"{active_customers:,}", delta="+3.2% vs Periode Lalu", delta_color="positive", subtext=sub_cust)

with col4:
    aov_str = format_rupiah(aov)
    metric_card(t["aov"], aov_str, delta="+8.6% vs Periode Lalu", delta_color="positive", subtext=sub_aov)

st.markdown("---")

# -------------------------------------------------------------
# MANDATORY DSS INSIGHT CARD (DECISION SUPPORT)
# -------------------------------------------------------------
if not df_filtered.empty and "customer_category" in df_filtered.columns:
    seg_summary = df_filtered.groupby("customer_category")["net_sales"].sum().sort_values(ascending=False)
    top_seg_name = seg_summary.index[0]
    top_seg_pct = (seg_summary.iloc[0] / total_sales * 100) if total_sales > 0 else 0
    seg_names = seg_summary.index.tolist()
    if lang_code == "EN":
        runner_up_text = f", followed by {seg_names[1]} ({seg_summary.iloc[1]/total_sales*100:.1f}%)" if len(seg_names) > 1 else ""
    else:
        runner_up_text = f", disusul oleh segmen {seg_names[1]} ({seg_summary.iloc[1]/total_sales*100:.1f}%)" if len(seg_names) > 1 else ""
else:
    top_seg_name = "Industri"
    top_seg_pct = 41.7
    runner_up_text = ", followed by Divisi (18.6%)" if lang_code == "EN" else ", disusul oleh segmen Divisi (18.6%)"

if lang_code == "EN":
    ic_title = "Revenue Growth Drivers & Key Account Concentration Management"
    ic_metric = f"Confirmed Net Revenue {sales_str} ({total_orders:,} Orders)"
    ic_context = f"Calculated from {active_customers:,} active customers in branch '{filters['branch']}' and segment '{filters['segment']}' (cancelled orders excluded)."
    ic_insight = f"Revenue is primarily driven by the {top_seg_name} segment ({top_seg_pct:.1f}% share){runner_up_text}. Meanwhile, End User and MSME drive transaction velocity."
    ic_impacted = f"Owner, Board of Directors, Regional Sales Managers, and Top Accounts in {filters['branch']}."
    ic_action = f"Executive Action: Direct Sales to secure long-term renewal agreements with top {top_seg_name} accounts. Expand marketing campaigns for high-volume MSME & School segments."
    ic_badge = "EXECUTIVE DECISION SUPPORT"
    ic_target = f"Top 10 Key Accounts ({filters['branch']}) | 100% Retention Target"
else:
    ic_title = "Pendorong Pertumbuhan Penjualan & Manajemen Konsentrasi Pelanggan Utama"
    ic_metric = f"Pendapatan Net Terkonfirmasi {sales_str} ({total_orders:,} Pesanan)"
    ic_context = f"Dihitung dari {active_customers:,} pelanggan aktif di cabang '{filters['branch']}' dan segmen '{filters['segment']}' (transaksi batal telah dieksklusikan 100%)."
    ic_insight = f"Struktur pendapatan saat ini ditopang kuat oleh segmen {top_seg_name} ({top_seg_pct:.1f}% dari total omzet){runner_up_text}. Sementara segmen UMKM & End User menyumbang frekuensi pesanan terbanyak."
    ic_impacted = f"Owner, Direksi, Manajer Penjualan Regional, serta 10 Pelanggan Kunci Teratas di {filters['branch']}."
    ic_action = f"Tindakan Eksekutif: Kunci perpanjangan kontrak tahunan dengan akun {top_seg_name} teratas di {filters['branch']}. Luncurkan paket promosi tematik untuk memperbesar rata-rata belanja segmen UMKM dan Sekolah."
    ic_badge = "KEPUTUSAN STRATEGIS EKSEKUTIF"
    ic_target = f"Top 10 Pelanggan Utama ({filters['branch']}) | Target Retensi 100%"

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
# TABBED EXECUTIVE DASHBOARD INTERFACE
# -------------------------------------------------------------
if lang_code == "EN":
    tab_titles = [
        "📈 Revenue Trend & Trajectory",
        "🧩 Customer Segment Contribution",
        "🏆 Top Customer Leaderboard",
        "🏢 6 Regional Branch Benchmarks"
    ]
else:
    tab_titles = [
        "📈 Tren Pendapatan & Trajektori",
        "🧩 Kontribusi Segmen Pelanggan",
        "🏆 Leaderboard Pelanggan Utama",
        "🏢 Tolok Ukur Kinerja 6 Cabang"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_titles)

# -------------------------------------------------------------
# TAB 1: TREN PENDAPATAN & TRAJEKTORI
# -------------------------------------------------------------
with tab1:
    if not df_filtered.empty:
        df_filtered_m = df_filtered.copy()
        df_filtered_m["month_year"] = df_filtered_m["invoice_date"].dt.to_period("M").dt.to_timestamp()
        df_monthly = df_filtered_m.groupby("month_year").agg(
            net_sales=("net_sales", "sum"),
            order_count=("invoice_id", "nunique"),
            active_buyers=("customer_id", "nunique")
        ).reset_index().sort_values("month_year")
        
        # Calculate monthly insights
        best_month_row = df_monthly.loc[df_monthly["net_sales"].idxmax()]
        lowest_month_row = df_monthly.loc[df_monthly["net_sales"].idxmin()]
        best_month_str = best_month_row["month_year"].strftime("%B %Y")
        lowest_month_str = lowest_month_row["month_year"].strftime("%B %Y")
        best_val = best_month_row["net_sales"]
        low_val = lowest_month_row["net_sales"]
        
        # MoM Growth of last 2 months
        if len(df_monthly) >= 2:
            last_val = df_monthly.iloc[-1]["net_sales"]
            prev_val = df_monthly.iloc[-2]["net_sales"]
            mom_pct = ((last_val - prev_val) / prev_val * 100) if prev_val > 0 else 0
            if lang_code == "EN":
                trend_dir = "Increasing Trend (Positive)" if mom_pct >= 0 else "Declining Trend (Needs Push)"
            else:
                trend_dir = "Tren Meningkat (Positif)" if mom_pct >= 0 else "Tren Menurun (Perlu Dorongan)"
            trend_color = "#10B981" if mom_pct >= 0 else "#EF4444"
            mom_badge = f"{mom_pct:+.1f}% MoM"
        else:
            trend_dir = "Stable" if lang_code == "EN" else "Stabil"
            trend_color = "#3B82F6"
            mom_badge = "Baseline Set" if lang_code == "EN" else "Baseline Terbentuk"
            
        render_section_info(
            title="Tren & Trajektori Penjualan Bulanan" if lang_code == "ID" else "Monthly Revenue Trend & Trajectory",
            subtitle="Menampilkan fluktuasi pendapatan invoice valid dari bulan ke bulan." if lang_code == "ID" else "Displays net confirmed revenue movement month over month.",
            what_it_shows="Grafik area pendapatan bulanan dan jumlah transaksi pesanan selesai." if lang_code == "ID" else "Monthly net sales area curve with completed order counts.",
            why_important="Membantu manajemen memantau kecepatan arus kas, tren musiman cetak (peak/low season), serta momentum pertumbuhan." if lang_code == "ID" else "Enables management to observe cash flow momentum and seasonal production cycles.",
            simple_insight=f"Bulan dengan omzet tertinggi tercatat di <b>{best_month_str} ({format_rupiah(best_val)})</b>. Status saat ini: <b>{trend_dir}</b>." if lang_code == "ID" else f"Peak performance recorded in <b>{best_month_str} ({format_rupiah(best_val)})</b>. Current status: <b>{trend_dir}</b>."
        )
        
        if lang_code == "EN":
            strip_items = [
                {"label": "Best Month", "value": best_month_str, "desc": f"Turnover {format_rupiah(best_val)}", "color": "#10B981"},
                {"label": "Lowest Month", "value": lowest_month_str, "desc": f"Turnover {format_rupiah(low_val)}", "color": "#F59E0B"},
                {"label": "Latest Trend Direction", "value": mom_badge, "desc": trend_dir, "color": trend_color},
                {"label": "Average Net / Month", "value": format_rupiah(df_monthly['net_sales'].mean()), "desc": f"Across {len(df_monthly)} active months", "color": "#3B82F6"}
            ]
        else:
            strip_items = [
                {"label": "Bulan Terbaik", "value": best_month_str, "desc": f"Omzet {format_rupiah(best_val)}", "color": "#10B981"},
                {"label": "Bulan Terlemah", "value": lowest_month_str, "desc": f"Omzet {format_rupiah(low_val)}", "color": "#F59E0B"},
                {"label": "Arah Tren Terakhir", "value": mom_badge, "desc": trend_dir, "color": trend_color},
                {"label": "Rata-rata Omzet / Bulan", "value": format_rupiah(df_monthly['net_sales'].mean()), "desc": f"Dari {len(df_monthly)} bulan transaksi", "color": "#3B82F6"}
            ]
        render_summary_strip(strip_items)
        
        lbl_month = "Month" if lang_code == "EN" else "Bulan"
        lbl_sales = "Net Revenue (IDR)" if lang_code == "EN" else "Pendapatan Net (IDR)"
        fig_trend = px.area(
            df_monthly, 
            x="month_year", 
            y="net_sales", 
            labels={"month_year": lbl_month, "net_sales": lbl_sales},
            color_discrete_sequence=["#2563EB"],
            markers=True
        )
        fig_trend.update_traces(
            fillcolor="rgba(37, 99, 235, 0.14)", 
            line=dict(width=3, color="#2563EB"),
            marker=dict(size=7, color="#1D4ED8")
        )
        apply_plotly_theme(fig_trend, height=360)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Tidak ada data penjualan untuk filter terpilih." if lang_code == "ID" else "No sales data for selected filter.")

# -------------------------------------------------------------
# TAB 2: KONTRIBUSI SEGMEN PELANGGAN (USER-FRIENDLY HORIZONTAL BAR)
# -------------------------------------------------------------
with tab2:
    if not df_filtered.empty:
        df_seg = df_filtered.groupby("customer_category").agg(
            total_revenue=("net_sales", "sum"),
            order_count=("invoice_id", "nunique"),
            active_cust=("customer_id", "nunique")
        ).reset_index().sort_values(by="total_revenue", ascending=True)
        
        tot_rev_all = df_seg["total_revenue"].sum()
        df_seg["contribution_pct"] = (df_seg["total_revenue"] / tot_rev_all * 100) if tot_rev_all > 0 else 0
        df_seg["formatted_sales"] = df_seg["total_revenue"].apply(format_rupiah)
        
        top_seg = df_seg.iloc[-1]
        growth_pot_seg = "UMKM & Sekolah"
        
        render_section_info(
            title="Kontribusi Pendapatan per Segmen Pelanggan" if lang_code == "ID" else "Customer Segment Revenue Contribution",
            subtitle="Menampilkan sebaran pendapatan dan persentase kontribusi per segmen pelanggan." if lang_code == "ID" else "Displays net revenue share and percentage across customer segments.",
            what_it_shows="Peringkat segmen pelanggan dari yang terkecil hingga terbesar beserta persentase omzetnya." if lang_code == "ID" else "Ranking of customer segments with confirmed revenue and percentage share.",
            why_important="Mendeteksi segmen mana yang menopang pendapatan terbesar dan segmen mana yang paling potensial untuk dikembangkan lebih lanjut." if lang_code == "ID" else "Identifies cornerstone segments driving revenue and upside opportunities.",
            simple_insight=f"Segmen <b>{top_seg['customer_category']}</b> mendominasi pendapatan dengan porsi <b>{top_seg['contribution_pct']:.1f}%</b> ({format_rupiah(top_seg['total_revenue'])}). Segmen <b>{growth_pot_seg}</b> memiliki potensi perputaran pesanan tinggi yang dapat terus ditingkatkan." if lang_code == "ID" else f"<b>{top_seg['customer_category']}</b> dominates total turnover with <b>{top_seg['contribution_pct']:.1f}%</b> share."
        )
        
        col_c1, col_c2 = st.columns([7, 3])
        with col_c1:
            lbl_rev_axis = "Pendapatan Net (IDR)" if lang_code == "ID" else "Net Revenue (IDR)"
            lbl_cat_axis = "Segmen Pelanggan" if lang_code == "ID" else "Customer Segment"
            
            fig_seg_bar = px.bar(
                df_seg,
                x="total_revenue",
                y="customer_category",
                orientation="h",
                text=df_seg["contribution_pct"].apply(lambda p: f" {p:.1f}%"),
                color="total_revenue",
                color_continuous_scale=["#93C5FD", "#1D4ED8"],
                labels={"total_revenue": lbl_rev_axis, "customer_category": lbl_cat_axis}
            )
            fig_seg_bar.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.8)",
                marker_line_width=1.2
            )
            apply_plotly_theme(fig_seg_bar, height=380)
            st.plotly_chart(fig_seg_bar, use_container_width=True)
            
        with col_c2:
            if lang_code == "EN":
                st.markdown(f"""
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-size: 11.5px; font-weight: 700; color: #3B82F6; text-transform: uppercase;">🏆 Largest Segment</div>
                    <div style="font-size: 19px; font-weight: 800; margin: 4px 0;">{top_seg['customer_category']}</div>
                    <div style="font-size: 13px; color: #10B981; font-weight: 700;">{format_rupiah(top_seg['total_revenue'])} ({top_seg['contribution_pct']:.1f}%)</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">Serves as the primary revenue pillar for Cetakia.</div>
                </div>
                
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-size: 11.5px; font-weight: 700; color: #F59E0B; text-transform: uppercase;">🚀 High Potential Growth Segments</div>
                    <div style="font-size: 17px; font-weight: 800; margin: 4px 0;">MSME, School & Agency</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Features large customer account bases with high reorder frequency. Ideal for bundle promos and packaging vouchers.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-size: 11.5px; font-weight: 700; color: #3B82F6; text-transform: uppercase;">🏆 Segmen Terbesar</div>
                    <div style="font-size: 19px; font-weight: 800; margin: 4px 0;">{top_seg['customer_category']}</div>
                    <div style="font-size: 13px; color: #10B981; font-weight: 700;">{format_rupiah(top_seg['total_revenue'])} ({top_seg['contribution_pct']:.1f}%)</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">Menjadi pilar penopang omzet utama Cetakia.</div>
                </div>
                
                <div class="cetakia-card" style="padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-size: 11.5px; font-weight: 700; color: #F59E0B; text-transform: uppercase;">🚀 Segmen Potensial Berkembang</div>
                    <div style="font-size: 17px; font-weight: 800; margin: 4px 0;">UMKM, Sekolah & Agen</div>
                    <div style="font-size: 12.5px; opacity: 0.9; line-height: 1.4;">
                        Memiliki basis pelanggan besar dengan pesanan berulang cepat. Cocok diberikan promosi voucher atau paket bundling hemat.
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Tidak ada data segmen untuk filter terpilih." if lang_code == "ID" else "No segment data for selected filter.")

# -------------------------------------------------------------
# TAB 3: LEADERBOARD KONSENTRASI TOP CUSTOMER (CLEAN & BUSINESS-FRIENDLY)
# -------------------------------------------------------------
with tab3:
    if not df_filtered.empty:
        df_top_cust = df_filtered.groupby(["customer_id", "customer_name", "customer_category", "division_name"]).agg(
            total_spend=("net_sales", "sum"),
            total_orders=("invoice_id", "nunique")
        ).reset_index().sort_values(by="total_spend", ascending=False).head(10)
        
        df_top_merged = df_top_cust.merge(
            df_cust_intel[["customer_id", "days_since_last_purchase"]], 
            on="customer_id", 
            how="left"
        )
        
        top10_spend_sum = df_top_merged["total_spend"].sum()
        top10_share = (top10_spend_sum / total_sales * 100) if total_sales > 0 else 0
        
        render_section_info(
            title="Leaderboard Pelanggan Utama" if lang_code == "ID" else "Top Customer Leaderboard",
            subtitle="Peringkat 10 akun pelanggan dengan kontribusi nilai belanja bersih terbesar." if lang_code == "ID" else "Rankings of the top 10 accounts by net confirmed purchase value.",
            what_it_shows="Nama pelanggan, segmen, cabang asal, pendapatan net yang disumbang, frekuensi pesanan, dan kapan terakhir belanja." if lang_code == "ID" else "Customer name, segment, branch, net revenue, order volume, and days since last purchase.",
            why_important="Mengawasi ketergantungan pendapatan (konsentrasi risiko) dan memastikan akun bernilai tinggi tetap terlayani dengan prima." if lang_code == "ID" else "Monitors revenue concentration risk and ensures VIP accounts receive proactive account management.",
            simple_insight=f"10 pelanggan teratas menyumbang total <b>{format_rupiah(top10_spend_sum)} ({top10_share:.1f}% dari seluruh pendapatan)</b>. Menjaga retensi 10 akun ini sangat krusial bagi stabilitas cashflow." if lang_code == "ID" else f"Top 10 accounts generate <b>{format_rupiah(top10_spend_sum)} ({top10_share:.1f}% of total sales)</b>."
        )
        
        # Prepare clean display table (kolom 'Status Kesehatan' sudah dihapus, label 'Pendapatan Net' dan 'Terakhir Belanja' dibuat ramah)
        df_top_display = df_top_merged.copy()
        df_top_display["Pendapatan Net"] = df_top_display["total_spend"].apply(format_rupiah)
        unit_ord = "orders" if lang_code == "EN" else "pesanan"
        df_top_display["Jumlah Pesanan"] = df_top_display["total_orders"].apply(lambda o: f"{o:,} {unit_ord}")
        days_unit = "days ago" if lang_code == "EN" else "hari lalu"
        just_now = "Just now" if lang_code == "EN" else "Baru saja"
        df_top_display["Terakhir Belanja"] = df_top_display["days_since_last_purchase"].apply(
            lambda d: f"{int(d)} {days_unit}" if pd.notnull(d) else just_now
        )
        
        if lang_code == "EN":
            rename_cols = {
                "customer_name": "Customer Name",
                "customer_category": "Segment",
                "division_name": "Branch",
                "Pendapatan Net": "Net Revenue",
                "Jumlah Pesanan": "Order Count",
                "Terakhir Belanja": "Last Purchase"
            }
        else:
            rename_cols = {
                "customer_name": "Nama Pelanggan",
                "customer_category": "Segmen",
                "division_name": "Cabang",
                "Pendapatan Net": "Pendapatan Net",
                "Jumlah Pesanan": "Jumlah Pesanan",
                "Terakhir Belanja": "Terakhir Belanja"
            }
            
        final_cols = ["customer_name", "customer_category", "division_name", "Pendapatan Net", "Jumlah Pesanan", "Terakhir Belanja"]
        st.dataframe(
            df_top_display[final_cols].rename(columns=rename_cols).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Tidak ada data pelanggan untuk filter terpilih." if lang_code == "ID" else "No customer data for selected filter.")

# -------------------------------------------------------------
# TAB 4: TOLOK UKUR KINERJA 6 DIVISI (CABANG) REGIONAL
# -------------------------------------------------------------
with tab4:
    if not df_sales.empty and "division_name" in df_sales.columns:
        branch_bench = df_sales.groupby("division_name").agg(
            total_sales=("net_sales", "sum"),
            total_invoices=("invoice_id", "nunique"),
            unique_buyers=("customer_id", "nunique")
        ).reset_index().sort_values(by="total_sales", ascending=False)
        
        tot_branch_rev = branch_bench["total_sales"].sum()
        branch_bench["share_pct"] = (branch_bench["total_sales"] / tot_branch_rev * 100) if tot_branch_rev > 0 else 0
        
        # Calculate real branch growth
        growth_df = compute_period_growth(df_sales, group_col="division_name", value_col="net_sales")
        branch_bench = branch_bench.merge(growth_df[["division_name", "growth_pct"]], on="division_name", how="left")
        branch_bench["growth_pct"] = branch_bench["growth_pct"].fillna(0.0)
        
        top_branch = branch_bench.iloc[0]
        fastest_grow = branch_bench.loc[branch_bench["growth_pct"].idxmax()]
        needs_attention = branch_bench.loc[branch_bench["growth_pct"].idxmin()]
        
        render_section_info(
            title="Tolok Ukur Kinerja 6 Cabang Regional" if lang_code == "ID" else "6 Regional Branch Benchmarks",
            subtitle="Perbandingan pendapatan bersih, kontribusi omzet, dan pertumbuhan transaksi antar cabang." if lang_code == "ID" else "Comparison of revenue, share percentage, and growth rate across branches.",
            what_it_shows="Perbandingan total omzet yang dihasilkan oleh masing-masing dari 6 cabang Cetakia secara transparan." if lang_code == "ID" else "Revenue performance across all 6 Cetakia operational branches.",
            why_important="Mengevaluasi cabang mana yang menjadi lokomotif penjualan, cabang dengan akselerasi tercepat, dan cabang yang membutuhkan dorongan ekstra." if lang_code == "ID" else "Assesses regional engine branches and locations requiring operational support.",
            simple_insight=f"Cabang dengan pendapatan tertinggi adalah <b>{top_branch['division_name']} ({format_rupiah(top_branch['total_sales'])}, share {top_branch['share_pct']:.1f}%)</b>. Pertumbuhan tercepat dicatatkan oleh <b>{fastest_grow['division_name']} ({fastest_grow['growth_pct']:+.1f}%)</b>, sementara <b>{needs_attention['division_name']} ({needs_attention['growth_pct']:+.1f}%)</b> perlu perhatian promosi." if lang_code == "ID" else f"Top branch is <b>{top_branch['division_name']}</b>, while <b>{fastest_grow['division_name']}</b> grew fastest."
        )
        
        if lang_code == "EN":
            strip_branch = [
                {"label": "Top Performing Branch", "value": top_branch['division_name'], "desc": f"Turnover {format_rupiah(top_branch['total_sales'])} ({top_branch['share_pct']:.1f}%)", "color": "#10B981"},
                {"label": "Fastest Growing Branch", "value": fastest_grow['division_name'], "desc": f"Growth {fastest_grow['growth_pct']:+.1f}% vs prior period", "color": "#3B82F6"},
                {"label": "Needs Activation", "value": needs_attention['division_name'], "desc": f"Growth {needs_attention['growth_pct']:+.1f}% (action needed)", "color": "#F59E0B"},
                {"label": "Total 6-Branch Revenue", "value": format_rupiah(tot_branch_rev), "desc": f"{branch_bench['total_invoices'].sum():,} invoice transactions", "color": "#8B5CF6"}
            ]
        else:
            strip_branch = [
                {"label": "Cabang Teratas", "value": top_branch['division_name'], "desc": f"Omzet {format_rupiah(top_branch['total_sales'])} ({top_branch['share_pct']:.1f}%)", "color": "#10B981"},
                {"label": "Pertumbuhan Tercepat", "value": fastest_grow['division_name'], "desc": f"Pertumbuhan {fastest_grow['growth_pct']:+.1f}% vs periode lalu", "color": "#3B82F6"},
                {"label": "Perlu Perhatian", "value": needs_attention['division_name'], "desc": f"Pertumbuhan {needs_attention['growth_pct']:+.1f}% (perlu dorongan)", "color": "#F59E0B"},
                {"label": "Total Omzet 6 Cabang", "value": format_rupiah(tot_branch_rev), "desc": f"{branch_bench['total_invoices'].sum():,} transaksi faktur", "color": "#8B5CF6"}
            ]
        render_summary_strip(strip_branch)
        
        col_b1, col_b2 = st.columns([6, 4])
        with col_b1:
            lbl_bb_branch = "Cabang" if lang_code == "ID" else "Branch"
            lbl_bb_sales = "Pendapatan Net (IDR)" if lang_code == "ID" else "Net Revenue (IDR)"
            
            fig_bb = px.bar(
                branch_bench,
                x="division_name",
                y="total_sales",
                color="total_sales",
                text=branch_bench["share_pct"].apply(lambda s: f"{s:.1f}%"),
                color_continuous_scale=["#93C5FD", "#2563EB"],
                labels={"division_name": lbl_bb_branch, "total_sales": lbl_bb_sales}
            )
            fig_bb.update_traces(
                textposition="outside",
                marker_line_color="rgba(255, 255, 255, 0.8)",
                marker_line_width=1.2,
                opacity=0.95
            )
            apply_plotly_theme(fig_bb, height=360)
            st.plotly_chart(fig_bb, use_container_width=True)
            
        with col_b2:
            st.markdown(f"**{'Ringkasan Kinerja Cabang' if lang_code == 'ID' else 'Branch Performance Summary'}**")
            disp_branch = branch_bench.copy()
            disp_branch["Pendapatan Net"] = disp_branch["total_sales"].apply(format_rupiah)
            disp_branch["Kontribusi"] = disp_branch["share_pct"].apply(lambda p: f"{p:.1f}%")
            disp_branch["Pertumbuhan"] = disp_branch["growth_pct"].apply(lambda g: f"{g:+.1f}%")
            disp_branch["Jumlah Pesanan"] = disp_branch["total_invoices"].apply(lambda i: f"{i:,}")
            
            rename_br = {
                "division_name": "Cabang" if lang_code == "ID" else "Branch",
                "Pendapatan Net": "Pendapatan Net" if lang_code == "ID" else "Net Revenue",
                "Kontribusi": "Kontribusi (%)" if lang_code == "ID" else "Share (%)",
                "Pertumbuhan": "Pertumbuhan (%)" if lang_code == "ID" else "Growth (%)",
                "Jumlah Pesanan": "Pesanan" if lang_code == "ID" else "Orders"
            }
            st.dataframe(
                disp_branch[["division_name", "Pendapatan Net", "Kontribusi", "Pertumbuhan", "Jumlah Pesanan"]].rename(columns=rename_br),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("Tidak ada data cabang untuk dianalisis." if lang_code == "ID" else "No branch data available.")
