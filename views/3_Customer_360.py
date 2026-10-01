import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_customer_data, load_sales_data, load_product_data, load_customer_intelligence
from utils.intelligence_engine import assign_customer_value_category, classify_customer_health_8
from components.ui_components import (
    render_header, metric_card, render_section_info, render_summary_strip,
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
)

st.set_page_config(page_title="Customer 360 Behavior Profile", page_icon="👤", layout="wide")

# Load Datasets
df_cust = load_customer_data()
df_sales = load_sales_data(include_cancelled=False)
df_items = load_product_data(include_cancelled=False)
df_intel = load_customer_intelligence()

# Global Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

# Merge customer master with intelligence summary
df_merged_cust = df_cust.merge(
    df_intel[['customer_id', 'lifetime_sales', 'total_orders', 'average_order_value', 'days_since_last_purchase', 'rfm_segment']],
    on='customer_id',
    how='left'
)

# Apply Customer Value Classification & 8-segment behavior
df_merged_cust["customer_value_cat"] = assign_customer_value_category(df_merged_cust, lang="ID")
df_merged_cust["customer_segment_8"] = classify_customer_health_8(df_merged_cust)

if filters["branch"] != "All Branches":
    if "division_name" in df_merged_cust.columns:
        df_merged_cust = df_merged_cust[df_merged_cust["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_merged_cust.columns:
        df_merged_cust = df_merged_cust[df_merged_cust["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title="Profil Perilaku & Preferensi Pelanggan (Customer 360)" if lang_code == "ID" else "Customer 360 Behavioral & Preference Profile",
    subtitle="Eksplorasi mendalam pola pembelian, frekuensi transaksi, tren belanja, dan preferensi produk per akun." if lang_code == "ID" else "Deep exploration of purchase patterns, frequency, activity trends, and product preferences.",
    module_tag="CUSTOMER 360 / ACCOUNT MANAGEMENT"
)

# Customer Selector Box
customer_list = df_merged_cust["customer_name"].dropna().unique().tolist()
customer_list.sort()

if not customer_list:
    st.warning("Tidak ada pelanggan yang ditemukan untuk filter terpilih." if lang_code == "ID" else "No customers found for the selected filters.")
    st.stop()

col_sel1, col_sel2 = st.columns([7, 3])
with col_sel1:
    prompt_txt = "🔎 Cari atau Pilih Akun Pelanggan untuk Menganalisis Perilakunya:" if lang_code == "ID" else "🔎 Search or Select Customer Account to Inspect Behavior:"
    selected_cust_name = st.selectbox(prompt_txt, options=customer_list, index=0)

target_cust = df_merged_cust[df_merged_cust["customer_name"] == selected_cust_name].iloc[0]
cust_id = target_cust["customer_id"]

val_cat = target_cust.get("customer_value_cat", "Customer Bernilai Rendah")
seg8_status = target_cust.get("customer_segment_8", "Dormant / Low Value")
category = target_cust.get("customer_category", "Umum")
division = target_cust.get("division_name", "Pusat")

# Determine activity status
recency_days = target_cust.get("days_since_last_purchase")
recency_val = int(recency_days) if pd.notnull(recency_days) else None
if recency_val is not None:
    if recency_val <= 45:
        activity_label = "● ACTIVE BUYER" if lang_code == "EN" else "● AKTIF BERBELANJA"
        activity_color = "#10B981"
        activity_desc = f"Last order {recency_val} days ago (normal cycle)" if lang_code == "EN" else f"Terakhir belanja {recency_val} hari lalu (siklus normal)"
    elif recency_val <= 90:
        activity_label = "● DECLINING FREQUENCY" if lang_code == "EN" else "● MULAI JARANG BELANJA"
        activity_color = "#F59E0B"
        activity_desc = f"Last order {recency_val} days ago (needs contact)" if lang_code == "EN" else f"Terakhir belanja {recency_val} hari lalu (perlu dihubungi)"
    else:
        activity_label = "● INACTIVE / REACTIVATE" if lang_code == "EN" else "● PASIF / PERLU DIAKTIVASI"
        activity_color = "#EF4444"
        activity_desc = f"Last order {recency_val} days ago (> 90 days)" if lang_code == "EN" else f"Terakhir belanja {recency_val} hari lalu (> 90 hari)"
else:
    activity_label = "● NO TRANSACTION" if lang_code == "EN" else "● BELUM TRANSAKSI"
    activity_color = "#94A3B8"
    activity_desc = "No recorded invoice order history" if lang_code == "EN" else "Belum ada riwayat pesanan invoice"

lbl_status_card = "ACTIVITY STATUS" if lang_code == "EN" else "STATUS KEAKTIFAN"

with col_sel2:
    st.markdown(f"""
    <div style="background-color: var(--secondary-background-color, rgba(128,128,128,0.06)); border: 1px solid rgba(156,163,175,0.25); border-radius: 10px; padding: 12px 16px; margin-top: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 11px; font-weight: 700; opacity: 0.8;">{lbl_status_card}</span>
            <span style="color: {activity_color}; font-size: 12px; font-weight: 800;">{activity_label}</span>
        </div>
        <div style="font-size: 12.5px; opacity: 0.9;">{activity_desc}</div>
        <div style="margin-top: 6px; font-size: 12px; color: #3B82F6; font-weight: 600;">{val_cat} | {seg8_status}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# FETCH CUSTOMER TRANSACTION HISTORY & ITEMS
# -------------------------------------------------------------
cust_sales = df_sales[df_sales["customer_id"] == cust_id].sort_values(by="invoice_date")
cust_items = df_items[df_items["customer_id"] == cust_id]

ltv = float(target_cust.get("lifetime_sales", 0.0) or 0.0)
total_orders = int(target_cust.get("total_orders", 0) or 0)
aov = float(target_cust.get("average_order_value", 0.0) or (ltv / total_orders if total_orders > 0 else 0.0))

# -------------------------------------------------------------
# BAGIAN 1: POLA & FREKUENSI BELANJA PELANGGAN
# -------------------------------------------------------------
if lang_code == "EN":
    render_section_info(
        title=f"1. Purchase Pattern & Order Frequency: {selected_cust_name}",
        subtitle="Evaluating activity, reorder frequency, and average order basket for this account.",
        what_it_shows="Customer lifetime spend (LTV), completed order count, average order value (AOV), ordering recency, and favorite product categories.",
        why_important="Enables account executives and CS to understand customer ordering behavior: large cyclical volume vs routine small retail reorders.",
        simple_insight=f"This account has recorded <b>{total_orders:,} transactions</b> totaling <b>{format_rupiah(ltv)}</b> in lifetime spend. Average order value is <b>{format_rupiah(aov)}</b>."
    )
else:
    render_section_info(
        title=f"1. Pola & Frekuensi Belanja: {selected_cust_name}",
        subtitle="Menilai seberapa aktif, seberapa sering, dan berapa nilai rata-rata pesanan pelanggan ini.",
        what_it_shows="Metrik total belanja seumur hidup (LTV), jumlah pesanan selesai, rata-rata nilai transaksi (AOV), interval waktu belanja, dan kategori produk yang paling sering dipesan.",
        why_important="Membantu tim account executive dan CS memahami kebiasaan belanja pelanggan: apakah pelanggan bertipe pesanan besar musiman, atau pembeli ritel rutin mingguan.",
        simple_insight=f"Pelanggan ini mencatatkan total <b>{total_orders:,} transaksi</b> dengan akumulasi belanja <b>{format_rupiah(ltv)}</b>. Rata-rata per transaksi adalah <b>{format_rupiah(aov)}</b>."
    )

first_tx_str = cust_sales["invoice_date"].min().strftime("%d %b %Y") if not cust_sales.empty else "-"
last_tx_str = cust_sales["invoice_date"].max().strftime("%d %b %Y") if not cust_sales.empty else "-"

fav_cat = "-"
if not cust_items.empty:
    fav_cat = cust_items["product_category"].value_counts().index[0].replace("Sales ", "")

if lang_code == "EN":
    stat_behavior = [
        {"label": "Lifetime Spend (LTV)", "value": format_rupiah(ltv), "desc": f"Segment: {category} ({division})", "color": "#10B981"},
        {"label": "Order Frequency", "value": f"{total_orders:,} Orders", "desc": f"First purchase: {first_tx_str}", "color": "#3B82F6"},
        {"label": "Average Order Value", "value": format_rupiah(aov), "desc": "Net average per invoice", "color": "#8B5CF6"},
        {"label": "Top Category", "value": fav_cat, "desc": f"Last purchase: {last_tx_str}", "color": "#F59E0B"}
    ]
else:
    stat_behavior = [
        {"label": "Total Nilai Belanja (LTV)", "value": format_rupiah(ltv), "desc": f"Segmen: {category} ({division})", "color": "#10B981"},
        {"label": "Frekuensi Pesanan", "value": f"{total_orders:,} Pesanan", "desc": f"Transaksi pertama: {first_tx_str}", "color": "#3B82F6"},
        {"label": "Rata-rata Nilai Pesanan", "value": format_rupiah(aov), "desc": "Rata-rata omzet per faktur", "color": "#8B5CF6"},
        {"label": "Kategori Favorit", "value": fav_cat, "desc": f"Terakhir belanja: {last_tx_str}", "color": "#F59E0B"}
    ]
render_summary_strip(stat_behavior)

# -------------------------------------------------------------
# BAGIAN 2: TREN AKTIVITAS BELANJA DARI WAKTU KE WAKTU
# -------------------------------------------------------------
st.markdown(f"### {'📈 Tren Aktivitas Belanja Bulanan' if lang_code == 'ID' else '📈 Monthly Spend & Activity Trend'}")
if not cust_sales.empty:
    cust_sales_m = cust_sales.copy()
    cust_sales_m["month_year"] = cust_sales_m["invoice_date"].dt.to_period("M").dt.to_timestamp()
    monthly_cust = cust_sales_m.groupby("month_year").agg(
        total_spent=("net_sales", "sum"),
        order_count=("invoice_id", "nunique")
    ).reset_index().sort_values("month_year")
    
    col_t1, col_t2 = st.columns([7, 3])
    with col_t1:
        lbl_my = "Bulan Transaksi" if lang_code == "ID" else "Transaction Month"
        lbl_sp = "Nilai Belanja (IDR)" if lang_code == "ID" else "Spend Amount (IDR)"
        fig_cust_trend = px.area(
            monthly_cust,
            x="month_year",
            y="total_spent",
            markers=True,
            color_discrete_sequence=["#3B82F6"],
            labels={"month_year": lbl_my, "total_spent": lbl_sp}
        )
        fig_cust_trend.update_traces(
            fillcolor="rgba(59, 130, 246, 0.15)",
            line=dict(width=3, color="#2563EB"),
            marker=dict(size=7, color="#1D4ED8")
        )
        apply_plotly_theme(fig_cust_trend, height=300)
        st.plotly_chart(fig_cust_trend, use_container_width=True)
        
    with col_t2:
        highest_month = monthly_cust.loc[monthly_cust["total_spent"].idxmax()]
        recent_month = monthly_cust.iloc[-1]
        ord_u = "pesanan" if lang_code == "ID" else "orders"
        if lang_code == "EN":
            card_t2 = f"""
            <div class="cetakia-card" style="padding: 16px 18px; margin-top: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #10B981; text-transform: uppercase;">🏆 All-Time Spend Peak</div>
                <div style="font-size: 18px; font-weight: 800; margin: 3px 0;">{highest_month['month_year'].strftime('%B %Y')}</div>
                <div style="font-size: 13px; color: #10B981; font-weight: 700;">{format_rupiah(highest_month['total_spent'])} ({highest_month['order_count']} {ord_u})</div>
                <hr style="margin: 10px 0; border: 0; border-top: 1px dashed rgba(156,163,175,0.3);">
                <div style="font-size: 11px; font-weight: 700; color: #3B82F6; text-transform: uppercase;">🕒 Most Recent Month</div>
                <div style="font-size: 16px; font-weight: 800; margin: 3px 0;">{recent_month['month_year'].strftime('%B %Y')}</div>
                <div style="font-size: 12.5px; opacity: 0.9;">Spend this month: {format_rupiah(recent_month['total_spent'])}</div>
            </div>
            """
        else:
            card_t2 = f"""
            <div class="cetakia-card" style="padding: 16px 18px; margin-top: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #10B981; text-transform: uppercase;">🏆 Puncak Belanja Tertinggi</div>
                <div style="font-size: 18px; font-weight: 800; margin: 3px 0;">{highest_month['month_year'].strftime('%B %Y')}</div>
                <div style="font-size: 13px; color: #10B981; font-weight: 700;">{format_rupiah(highest_month['total_spent'])} ({highest_month['order_count']} {ord_u})</div>
                <hr style="margin: 10px 0; border: 0; border-top: 1px dashed rgba(156,163,175,0.3);">
                <div style="font-size: 11px; font-weight: 700; color: #3B82F6; text-transform: uppercase;">🕒 Transaksi Terakhir</div>
                <div style="font-size: 16px; font-weight: 800; margin: 3px 0;">{recent_month['month_year'].strftime('%B %Y')}</div>
                <div style="font-size: 12.5px; opacity: 0.9;">Total belanja bulan ini: {format_rupiah(recent_month['total_spent'])}</div>
            </div>
            """
        st.markdown(card_t2, unsafe_allow_html=True)
else:
    st.info("Belum ada riwayat transaksi bulanan untuk akun ini." if lang_code == "ID" else "No monthly transaction history recorded for this customer account.")

st.markdown("---")

# -------------------------------------------------------------
# BAGIAN 3: PREFERENSI KATEGORI PRODUK & POTENSI KEBUTUHAN
# -------------------------------------------------------------
if lang_code == "EN":
    render_section_info(
        title="2. Product Category Preferences & Unmet Need Opportunities",
        subtitle="Analyzing core printing product categories and discovering high-potential complementary products.",
        what_it_shows="Most frequent product categories, largest spend absorbing categories, basket mix, and complementary cross-sell recommendations.",
        why_important="Enables sales teams to propose highly tailored complementary bundles relevant to customer business models rather than generic catalog spam.",
        simple_insight="Identifying dominant purchase categories unlocks bundle cross-sell opportunities to increase average order basket size (AOV)."
    )
else:
    render_section_info(
        title="2. Preferensi Kategori Produk & Potensi Kebutuhan Pelanggan",
        subtitle="Menganalisis jenis produk cetak yang menjadi andalan pelanggan dan peluang penawaran produk pelengkap.",
        what_it_shows="Kategori produk yang paling sering dipesan, kategori yang menyerap dana terbesar, bauran preferensi, serta rekomendasi kategori pelengkap yang belum pernah dipesan.",
        why_important="Membantu tim penjualan menawarkan produk komplementer (cross-sell) yang relevan dengan bisnis pelanggan, bukan menawarkan produk secara acak.",
        simple_insight="Mengetahui kategori yang paling sering dibeli membuka peluang penawaran paket bundling untuk memperbesar ukuran keranjang belanja."
    )

if not cust_items.empty:
    cust_cat_summary = cust_items.groupby("product_category").agg(
        total_spend=("sales_amount", "sum"),
        units_sold=("qty", "sum"),
        order_count=("invoice_id", "nunique")
    ).reset_index().sort_values(by="total_spend", ascending=False)
    
    tot_item_spend = cust_cat_summary["total_spend"].sum()
    cust_cat_summary["spend_pct"] = (cust_cat_summary["total_spend"] / tot_item_spend * 100) if tot_item_spend > 0 else 0
    cust_cat_summary["clean_cat"] = cust_cat_summary["product_category"].str.replace("Sales ", "")
    
    col_p1, col_p2 = st.columns([6, 4])
    
    with col_p1:
        st.markdown(f"**{'Bauran Nilai Belanja per Kategori Produk' if lang_code == 'ID' else 'Spend Mix Across Product Categories'}**")
        lbl_p_spend = "Total Belanja (IDR)" if lang_code == "ID" else "Total Spend (IDR)"
        lbl_p_cat = "Kategori Produk" if lang_code == "ID" else "Product Category"
        fig_cat_bar = px.bar(
            cust_cat_summary.sort_values(by="total_spend", ascending=True),
            x="total_spend",
            y="clean_cat",
            orientation="h",
            color="total_spend",
            text=cust_cat_summary.sort_values(by="total_spend", ascending=True)["spend_pct"].apply(lambda p: f" {p:.1f}%"),
            color_continuous_scale=["#93C5FD", "#1D4ED8"],
            labels={"total_spend": lbl_p_spend, "clean_cat": lbl_p_cat}
        )
        fig_cat_bar.update_traces(
            textposition="outside",
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.2
        )
        apply_plotly_theme(fig_cat_bar, height=340)
        st.plotly_chart(fig_cat_bar, use_container_width=True)
        
    with col_p2:
        st.markdown(f"**{'Proporsi Volume & Frekuensi Pesanan' if lang_code == 'ID' else 'Order Frequency & Volume Mix'}**")
        fig_donut_cat = px.pie(
            cust_cat_summary,
            names="clean_cat",
            values="order_count",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_donut_cat.update_traces(textposition="inside", textinfo="percent+label")
        apply_plotly_theme(fig_donut_cat, height=340)
        st.plotly_chart(fig_donut_cat, use_container_width=True)
        
    # Identification of complementary opportunities (Potensi Kebutuhan)
    bought_cats = set(cust_cat_summary["clean_cat"].tolist())
    
    complementary_opps = []
    if any("Packaging" in c for c in bought_cats) and not any("Sticker" in c for c in bought_cats):
        if lang_code == "EN":
            complementary_opps.append({
                "target": "Custom Roll / Die-cut Product Labels",
                "alasan": "Customer already purchases Box Packaging but has not ordered branded labels/stickers.",
                "ide_aksi": "Offer a 5% combo packaging + label bundle with roll sticker samples on next visit."
            })
        else:
            complementary_opps.append({
                "target": "Stiker Label Roll / Cutting",
                "alasan": "Pelanggan sudah membeli Kemasan (Packaging) namun belum memesan Stiker Label untuk merek/kemasan.",
                "ide_aksi": "Tawarkan paket bundling kemasan + label hemat 5% dengan membawa sampel stiker roll."
            })
    if any("Large Format" in c or "Banner" in c for c in bought_cats) and not any("Stand" in c or "Finishing" in c for c in bought_cats):
        if lang_code == "EN":
            complementary_opps.append({
                "target": "Display Standee (X-Banner / Roll Up Display)",
                "alasan": "Customer frequently orders promotional banners but has not ordered portable display hardware.",
                "ide_aksi": "Pitch event-ready display kits including standee hardware and carrying case."
            })
        else:
            complementary_opps.append({
                "target": "Display Standee (X-Banner / Roll Up)",
                "alasan": "Pelanggan sering memesan spanduk/banner promosi namun belum melengkapi dengan stand display portable.",
                "ide_aksi": "Tawarkan paket display event siap pasang."
            })
    if any("A3" in c or "Brochure" in c or "Book" in c for c in bought_cats) and not any("Corporate ID" in c or "Stationery" in c for c in bought_cats):
        if lang_code == "EN":
            complementary_opps.append({
                "target": "Business Cards & Corporate Identity Starter Kit",
                "alasan": "Customer prints marketing collateral but has not ordered standard corporate stationery/identity.",
                "ide_aksi": "Pitch matte-laminated corporate business card bundles for the client's sales team."
            })
        else:
            complementary_opps.append({
                "target": "Kartu Nama & Starter Branding Korporat",
                "alasan": "Pelanggan mencetak dokumen pemasaran namun belum memesan identitas korporat standar.",
                "ide_aksi": "Tawarkan bundling kartu nama matte finishing untuk kebutuhan tim representatif."
            })
        
    if not complementary_opps:
        if lang_code == "EN":
            complementary_opps.append({
                "target": "Promotional Souvenirs & Corporate Merchandise",
                "alasan": "Customer demonstrates a solid repeat order history across primary printing categories.",
                "ide_aksi": "Introduce Cetakia's custom corporate merchandise catalog for corporate year-end gifts or events."
            })
        else:
            complementary_opps.append({
                "target": "Souvenir & Merchandise Promosi (Tumbler/Tote Bag)",
                "alasan": "Pelanggan telah memiliki riwayat repeat order yang solid pada kategori cetak utama.",
                "ide_aksi": "Kenalkan katalog merchandise custom Cetakia untuk keperluan gift akhir tahun atau event perusahaan."
            })
        
    lbl_rec_opp = "🎯 Rekomendasi Kebutuhan Pelengkap (Peluang Penjualan)" if lang_code == "ID" else "🎯 Recommended Complementary Opportunities (Cross-Sell)"
    lbl_opp_prod = "Peluang Produk" if lang_code == "ID" else "Opportunity Product"
    lbl_opp_why = "Analisis Perilaku" if lang_code == "ID" else "Behavioral Rationale"
    lbl_opp_act = "Ide Tindakan Sales" if lang_code == "ID" else "Sales Action Idea"
    
    st.markdown(f"### {lbl_rec_opp}")
    for opp in complementary_opps:
        st.markdown(f"""
        <div class="cetakia-card" style="border-left: 4px solid #10B981; padding: 14px 18px; margin-bottom: 10px;">
            <div style="font-weight: 700; color: #10B981; font-size: 14px;">{lbl_opp_prod}: {opp['target']}</div>
            <div style="font-size: 13px; margin: 4px 0; opacity: 0.9;"><b>{lbl_opp_why}:</b> {opp['alasan']}</div>
            <div style="font-size: 13px; color: #3B82F6; font-weight: 600;"><b>{lbl_opp_act}:</b> {opp['ide_aksi']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Belum ada riwayat detail item produk yang dibeli untuk pelanggan ini." if lang_code == "ID" else "No detailed purchased item history available for this customer.")
