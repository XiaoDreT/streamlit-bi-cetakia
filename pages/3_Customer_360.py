import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_data, load_sales_data, load_product_data, load_customer_intelligence
from components.ui_components import (
    render_header, metric_card, render_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah
)

st.set_page_config(page_title="Customer 360 Profile", page_icon="👤", layout="wide")

# Load Datasets
df_cust = load_customer_data()
df_sales = load_sales_data(include_cancelled=True)
df_items = load_product_data(include_cancelled=False)
df_intel = load_customer_intelligence()

# Global Sidebar Filters & Locale State
filters = global_sidebar_filters()
t = filters["t"]
lang_code = filters["lang"]

# Merge customer master with intelligence summary for clean selection
df_merged_cust = df_cust.merge(
    df_intel[['customer_id', 'lifetime_sales', 'total_orders', 'average_order_value', 'days_since_last_purchase', 'customer_health', 'RFM_score', 'rfm_segment']],
    on='customer_id',
    how='left'
)

if filters["branch"] != "All Branches":
    if "division_name" in df_merged_cust.columns:
        df_merged_cust = df_merged_cust[df_merged_cust["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_merged_cust.columns:
        df_merged_cust = df_merged_cust[df_merged_cust["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["cust_360_title"],
    subtitle=t["cust_360_sub"],
    module_tag="ACCOUNT MANAGEMENT / CS / SALES"
)

# Customer Selector Box
customer_list = df_merged_cust["customer_name"].dropna().unique().tolist()
customer_list.sort()

if not customer_list:
    st.warning("Tidak ada pelanggan yang ditemukan untuk filter terpilih." if lang_code == "ID" else "No customers found for selected filter.")
    st.stop()

col_sel1, col_sel2 = st.columns([7, 3])
with col_sel1:
    selected_cust_name = st.selectbox(t["select_cust_prompt"], options=customer_list, index=0)

target_cust = df_merged_cust[df_merged_cust["customer_name"] == selected_cust_name].iloc[0]
cust_id = target_cust["customer_id"]

with col_sel2:
    st.markdown("<br>", unsafe_allow_html=True)
    health_raw = target_cust.get("customer_health")
    if pd.isna(health_raw) or str(health_raw).lower() in ["nan", "none", ""]:
        health_status = "Baru / Prospek" if lang_code == "ID" else "New / Prospect"
        badge_color = "#8B5CF6"
    else:
        health_status = str(health_raw)
        badge_color = "#10B981" if health_status == "Healthy" else ("#2563EB" if health_status == "Active" else ("#F59E0B" if health_status == "At Risk" else "#EF4444"))
    st.markdown(f"""
        <div class="cetakia-card" style="padding: 12px 18px; margin-bottom: 0; text-align: center;">
            <span style="font-size: 12px; font-weight: 700; opacity: 0.8;">{"KESEHATAN AKUN:" if lang_code == "ID" else "ACCOUNT HEALTH:"}</span> 
            <span style="color: {badge_color}; font-size: 16px; font-weight: 800; margin-left: 8px;">● {health_status.upper()}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# SECTION 1: CUSTOMER PROFILE & BUSINESS VALUE
# -------------------------------------------------------------
st.subheader(f"{t['profile_val_title']} {target_cust['customer_name']}")

p1, p2, p3, p4 = st.columns(4)
with p1:
    category = target_cust.get("customer_category", "N/A")
    division = target_cust.get("division_name", "N/A")
    st.markdown(f"""
        <div class="cetakia-metric-card">
            <div class="metric-title">{"Metadata Pelanggan" if lang_code == "ID" else "Customer Metadata"}</div>
            <div style="font-size: 16px; font-weight: 700;">{target_cust.get('customer_code', 'CUST-001')}</div>
            <div class="metric-subtext">{"Kategori:" if lang_code == "ID" else "Category:"} <b>{category}</b></div>
            <div class="metric-subtext">{"Cabang:" if lang_code == "ID" else "Branch:"} <b>{division}</b></div>
        </div>
    """, unsafe_allow_html=True)

with p2:
    ltv_raw = target_cust.get("lifetime_sales")
    ltv = float(ltv_raw) if pd.notnull(ltv_raw) else 0.0
    ltv_str = format_rupiah(ltv)
    metric_card("Total Belanja Seumur Hidup" if lang_code == "ID" else "Observed Lifetime Spend", ltv_str, subtext="Total pendapatan invoice tertagih" if lang_code == "ID" else "Total billed sales revenue")

with p3:
    orders_raw = target_cust.get("total_orders")
    orders = int(orders_raw) if pd.notnull(orders_raw) else 0
    order_unit = "Pesanan" if lang_code == "ID" else "Orders"
    metric_card("Total Pesanan Selesai" if lang_code == "ID" else "Total Orders Completed", f"{orders:,} {order_unit}", subtext="Jumlah pesanan historis" if lang_code == "ID" else "Historical order count")

with p4:
    aov_raw = target_cust.get("average_order_value")
    aov = float(aov_raw) if pd.notnull(aov_raw) else 0.0
    aov_str = format_rupiah(aov)
    metric_card("Rata-rata Nilai Pesanan" if lang_code == "ID" else "Average Order Value", aov_str, subtext="Nilai rata-rata per pesanan" if lang_code == "ID" else "Average spend per order")

st.markdown("---")

# -------------------------------------------------------------
# SECTION 2: DYNAMIC BUSINESS RECOMMENDATION (DSS ENGINE) - INDONESIAN
# -------------------------------------------------------------
recency_days = target_cust.get("days_since_last_purchase")
recency_val = int(recency_days) if pd.notnull(recency_days) else 0
rfm_raw = target_cust.get("rfm_segment")
rfm_seg = str(rfm_raw) if pd.notnull(rfm_raw) and str(rfm_raw).lower() not in ["nan", "none", ""] else ("Baru / Belum Ada" if lang_code == "ID" else "New / Unsegmented")

if lang_code == "ID":
    if health_status in ["At Risk", "Dormant"]:
        action_text = f"🚨 TINDAKAN MENDESAK: Pelanggan '{selected_cust_name}' belum melakukan pemesanan selama {recency_val} hari (melebihi siklus pemesanan historis). Tim CS harus segera melakukan panggilan re-engagement dan menawarkan diskon loyalitas 5%."
        badge_label = "ATURAN PENCEGAHAN CHURN"
    elif health_status == "Healthy":
        action_text = f"💡 PELUANG EKSPANSI: Pelanggan '{selected_cust_name}' dalam status Sehat (Healthy) dengan pembelian berulang aktif. Sales AE harus mengenalkan kategori produk cross-sell teratas untuk memperluas pangsa pasar."
        badge_label = "ATURAN CROSS-SELL"
    elif orders == 0 or "Baru" in health_status or "New" in health_status or "Prospek" in health_status:
        action_text = f"🎯 AKUISISI TRANSAKSI PERDANA: Pelanggan '{selected_cust_name}' adalah akun terdaftar yang belum memiliki riwayat invoice tertagih. Tim Sales AE direkomendasikan untuk menjangkau klien, memahami kebutuhan cetak, dan menawarkan voucher selamat datang pada pesanan pertama."
        badge_label = "ATURAN AKUISISI PERDANA"
    else:
        action_text = f"📌 PEMELIHARAAN RUTIN: Pelanggan '{selected_cust_name}' memesan secara aktif dalam batas normal. Pertahankan komunikasi standar dan pantau permintaan penawaran (quotation)."
        badge_label = "ATURAN MANAJEMEN AKUN"
    
    ic_title = f"Rekomendasi Keputusan Otomatis untuk {selected_cust_name}"
    ic_metric = f"Kesehatan: {health_status} | Recency: {recency_val} Hari | RFM: {rfm_seg}"
    ic_context = f"Akun terdaftar di cabang {division}, segmen {category}. Total belanja seumur hidup: {ltv_str} dari {orders} pesanan."
    ic_insight = f"Kecepatan pembelian menunjukkan jarak waktu {recency_val} hari sejak transaksi terakhir yang teramati." if orders > 0 else "Akun ini belum memiliki catatan transaksi pembelian sebelumnya dalam database analitis."
else:
    if health_status in ["At Risk", "Dormant"]:
        action_text = f"🚨 URGENT ACTION: Customer '{selected_cust_name}' has not placed an order in {recency_val} days (exceeding historical reorder cycle). CS should execute outbound re-engagement call immediately and offer a 5% loyalty discount."
        badge_label = "CHURN PREVENTION RULE"
    elif health_status == "Healthy":
        action_text = f"💡 EXPANSION OPPORTUNITY: Customer '{selected_cust_name}' is in Healthy state with active repeat orders. Sales AE should introduce top cross-sell product categories to expand wallet share."
        badge_label = "CROSS-SELL RULE"
    elif orders == 0 or "New" in health_status or "Prospect" in health_status:
        action_text = f"🎯 FIRST ORDER ONBOARDING: Customer '{selected_cust_name}' is a registered account without billed invoice history. Sales AE is advised to outreach, assess print requirements, and provide a welcome offer on first purchase."
        badge_label = "FIRST PURCHASE ONBOARDING"
    else:
        action_text = f"📌 REGULAR MAINTENANCE: Customer '{selected_cust_name}' is actively ordering within normal parameters. Maintain standard account touchpoints and track quote requests."
        badge_label = "ACCOUNT MANAGEMENT RULE"
    
    ic_title = f"Automated Decision Recommendation for {selected_cust_name}"
    ic_metric = f"Health: {health_status} | Recency: {recency_val} Days | RFM: {rfm_seg}"
    ic_context = f"Account registered in branch {division}, segment {category}. Total lifetime spend: {ltv_str} across {orders} orders."
    ic_insight = f"Purchasing velocity shows current recency of {recency_val} days since last observed transaction." if orders > 0 else "This account has no prior transaction records in the analytical database."

render_insight_card(
    title=ic_title,
    metric=ic_metric,
    context=ic_context,
    insight=ic_insight,
    action=action_text,
    badge=badge_label
)

st.markdown("---")

# -------------------------------------------------------------
# SECTION 3: TRANSACTION LEDGER & PRODUCT PREFERENCE
# -------------------------------------------------------------
c_left, c_right = st.columns([5, 5])

with c_left:
    st.subheader(t["product_pref"])
    df_cust_items = df_items[df_items["customer_id"] == cust_id]
    if "invoice_status" in df_cust_items.columns:
        df_cust_items = df_cust_items[df_cust_items["invoice_status"].astype(str).str.lower() != "cancel"]
    
    if not df_cust_items.empty:
        df_prod_pref = df_cust_items.groupby("product_category")["sales_amount"].sum().reset_index()
        fig_prod = px.bar(
            df_prod_pref,
            x="sales_amount",
            y="product_category",
            orientation="h",
            color="sales_amount",
            color_continuous_scale="Blues",
            labels={"sales_amount": "Total Penjualan (IDR)" if lang_code == "ID" else "Total Net Sales (IDR)", "product_category": "Kategori Produk" if lang_code == "ID" else "Product Category"}
        )
        apply_plotly_theme(fig_prod, height=320)
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.info("Tidak ada riwayat pembelian detail item untuk pelanggan ini." if lang_code == "ID" else "No detailed line-item purchase history found for this customer.")

with c_right:
    st.subheader(t["recent_invoices"])
    df_cust_sales = df_sales[df_sales["customer_id"] == cust_id].sort_values(by="invoice_date", ascending=False).head(5)
    
    if not df_cust_sales.empty:
        df_sales_disp = df_cust_sales[["invoice_code", "invoice_date", "net_sales", "invoice_status"]].copy()
        df_sales_disp["Invoice Date"] = df_sales_disp["invoice_date"].dt.strftime("%Y-%m-%d")
        df_sales_disp["Amount"] = df_sales_disp["net_sales"].apply(lambda x: format_rupiah(x))
        
        st.dataframe(
            df_sales_disp[["invoice_code", "Invoice Date", "Amount", "invoice_status"]].rename(columns={
                "invoice_code": "Kode Invoice" if lang_code == "ID" else "Invoice Code",
                "Invoice Date": "Tanggal Invoice" if lang_code == "ID" else "Invoice Date",
                "Amount": "Jumlah" if lang_code == "ID" else "Amount",
                "invoice_status": "Status"
            }),
            use_container_width=True
        )
    else:
        st.info("Tidak ada transaksi invoice ditemukan untuk pelanggan ini." if lang_code == "ID" else "No invoice transactions found for this customer.")
