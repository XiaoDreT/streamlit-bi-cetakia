import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_customer_data, load_sales_data, load_product_data, load_customer_intelligence
from utils.intelligence_engine import (
    classify_customer_health, assign_customer_value_tier, 
    assign_customer_journey, next_best_action_engine
)
from components.ui_components import (
    render_header, metric_card, render_business_insight_card, 
    global_sidebar_filters, apply_plotly_theme, format_rupiah, format_data_value
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

# Apply Business Intelligence Engine Rules
df_merged_cust["customer_health"] = df_merged_cust.apply(classify_customer_health, axis=1)
df_merged_cust["value_tier"] = df_merged_cust.apply(assign_customer_value_tier, axis=1)
df_merged_cust["journey_status"] = df_merged_cust.apply(assign_customer_journey, axis=1)

if filters["branch"] != "All Branches":
    if "division_name" in df_merged_cust.columns:
        df_merged_cust = df_merged_cust[df_merged_cust["division_name"] == filters["branch"]]

if filters["segment"] != "All Segments":
    if "customer_category" in df_merged_cust.columns:
        df_merged_cust = df_merged_cust[df_merged_cust["customer_category"].astype(str).str.upper() == filters["segment"].upper()]

# Page Header
render_header(
    title=t["cust_360_title"],
    subtitle="Single-Account 360° Profile, Tier A/B/C Value Tier, Journey Stage & Next Best Action Engine" if lang_code == "EN" else "Profil Akun Tunggal, Tingkat Nilai Tier A/B/C, Status Journey & Next Best Action Engine",
    module_tag="ACCOUNT MANAGEMENT / CS / SALES"
)

# Customer Selector Box
customer_list = df_merged_cust["customer_name"].dropna().unique().tolist()
customer_list.sort()

if not customer_list:
    st.warning("No customers found for the selected filters." if lang_code == "EN" else "Tidak ada pelanggan yang ditemukan untuk filter terpilih.")
    st.stop()

col_sel1, col_sel2 = st.columns([6, 4])
with col_sel1:
    selected_cust_name = st.selectbox(t["select_cust_prompt"], options=customer_list, index=0)

target_cust = df_merged_cust[df_merged_cust["customer_name"] == selected_cust_name].iloc[0]
cust_id = target_cust["customer_id"]

health_status = target_cust.get("customer_health", "Never Purchased")
value_tier = target_cust.get("value_tier", "Tier C (Low Value)")
journey_status = target_cust.get("journey_status", "Never Purchased")

health_colors = {
    "Active Customer": "#3B82F6",
    "At Risk": "#F59E0B",
    "Dormant": "#EF4444",
    "Never Purchased": "#8B5CF6"
}
badge_color = health_colors.get(health_status, "#8B5CF6")

badge_health_label = "HEALTH" if lang_code == "EN" else "KESEHATAN"
badge_tier_label = "VALUE TIER"
badge_journey_label = "JOURNEY"

with col_sel2:
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 24px; justify-content: flex-end;">
        <div class="cetakia-card" style="padding: 10px 14px; margin-bottom: 0; text-align: center; flex: 1;">
            <div style="font-size: 11px; font-weight: 700; opacity: 0.8;">{badge_health_label}</div>
            <div style="color: {badge_color}; font-size: 13px; font-weight: 800; margin-top: 2px;">● {health_status.upper()}</div>
        </div>
        <div class="cetakia-card" style="padding: 10px 14px; margin-bottom: 0; text-align: center; flex: 1;">
            <div style="font-size: 11px; font-weight: 700; opacity: 0.8;">{badge_tier_label}</div>
            <div style="color: #10B981; font-size: 13px; font-weight: 800; margin-top: 2px;">{value_tier.split()[0]}</div>
        </div>
        <div class="cetakia-card" style="padding: 10px 14px; margin-bottom: 0; text-align: center; flex: 1;">
            <div style="font-size: 11px; font-weight: 700; opacity: 0.8;">{badge_journey_label}</div>
            <div style="color: #3B82F6; font-size: 13px; font-weight: 800; margin-top: 2px;">{journey_status.replace(' Customer', '')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# FETCH PURCHASED ITEMS & EVALUATE NEXT BEST ACTION ENGINE
# -------------------------------------------------------------
df_cust_items = df_items[df_items["customer_id"] == cust_id]
if "invoice_status" in df_cust_items.columns:
    df_cust_items = df_cust_items[df_cust_items["invoice_status"].astype(str).str.lower() != "cancel"]

bought_categories = df_cust_items["product_category"].dropna().unique().tolist() if not df_cust_items.empty else []
nba = next_best_action_engine(target_cust, bought_categories=bought_categories, lang=lang_code)

# -------------------------------------------------------------
# STRICT V1.1 MANDATORY DSS INSIGHT CARD (NEXT BEST ACTION)
# -------------------------------------------------------------
ltv_raw = target_cust.get("lifetime_sales")
ltv = float(ltv_raw) if pd.notnull(ltv_raw) else 0.0
ltv_str = format_rupiah(ltv)

orders_raw = target_cust.get("total_orders")
orders = int(orders_raw) if pd.notnull(orders_raw) else 0

recency_days = target_cust.get("days_since_last_purchase")
recency_val = int(recency_days) if pd.notnull(recency_days) else 0

category = target_cust.get("customer_category", "N/A")
division = target_cust.get("division_name", "N/A")

if lang_code == "EN":
    ic_title = f"Automated Decision Support Recommendation for {selected_cust_name}"
    ic_metric = f"Health: {health_status} | {value_tier} | {journey_status}"
    ic_context = f"Account registered at branch {division}, segment {category}. Total confirmed spending: {ltv_str} across {orders} valid orders."
    ic_insight = f"Observed purchase recency: {recency_val} days since last transaction. " + (
        f"Observed product categories include {len(bought_categories)} types." if bought_categories else "No purchase history observed yet."
    )
    ic_impacted = f"Branch {division} Account Executive / CS Representative managing {selected_cust_name}."
    ic_action = nba["action"]
    ic_target = f"{selected_cust_name} ({target_cust.get('customer_code', 'CUST')}) | {nba['sla']}"
    ic_badge = nba["rule_name"]
else:
    ic_title = f"Rekomendasi Keputusan Otomatis untuk {selected_cust_name}"
    ic_metric = f"Kesehatan: {health_status} | {value_tier} | {journey_status}"
    ic_context = f"Akun terdaftar di cabang {division}, segmen {category}. Total belanja terkonfirmasi: {ltv_str} dari {orders} pesanan valid."
    ic_insight = f"Interval pemesanan teramati: {recency_val} hari sejak transaksi terakhir. " + (
        f"Kategori produk teramati mencakup {len(bought_categories)} jenis." if bought_categories else "Belum memiliki riwayat produk yang terbeli."
    )
    ic_impacted = f"Account Executive / CS Representative Cabang {division} yang bertanggung jawab mengelola {selected_cust_name}."
    ic_action = nba["action"]
    ic_target = f"{selected_cust_name} ({target_cust.get('customer_code', 'CUST')}) | {nba['sla']}"
    ic_badge = nba["rule_name"]

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
# TABBED 360 ACCOUNT DRILL-DOWN
# -------------------------------------------------------------
if lang_code == "EN":
    tab_labels = [
        "👤 Account Value Summary & Metadata",
        "⚡ Next Best Action Engine",
        "📦 Basket & Product Preferences",
        "🧾 Invoice Transaction History (Ledger)"
    ]
else:
    tab_labels = [
        "👤 Ringkasan Nilai & Metadata Akun",
        "⚡ Next Best Action Engine",
        "📦 Keranjang & Preferensi Produk",
        "🧾 Riwayat Transaksi Invoice (Ledger)"
    ]

tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

with tab1:
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        card_meta_title = "Customer Metadata" if lang_code == "EN" else "Metadata Pelanggan"
        card_cat_label = "Category" if lang_code == "EN" else "Kategori"
        card_branch_label = "Branch" if lang_code == "EN" else "Cabang"
        card_contact_label = "Contact" if lang_code == "EN" else "Kontak"
        st.markdown(f"""
            <div class="cetakia-metric-card">
                <div class="metric-title">{card_meta_title}</div>
                <div style="font-size: 16px; font-weight: 700;">{target_cust.get('customer_code', 'CUST-001')}</div>
                <div class="metric-subtext">{card_cat_label}: <b>{category}</b></div>
                <div class="metric-subtext">{card_branch_label}: <b>{division}</b></div>
                <div class="metric-subtext">{card_contact_label}: <b>{format_data_value(target_cust.get('phone'), fallback='-')}</b></div>
            </div>
        """, unsafe_allow_html=True)
    with p2:
        ltv_title = "Customer Lifetime Value (LTV)" if lang_code == "EN" else "Total Belanja Seumur Hidup (LTV)"
        ltv_sub = "Total confirmed invoiced revenue" if lang_code == "EN" else "Total pendapatan invoice tertagih valid"
        metric_card(ltv_title, ltv_str, subtext=ltv_sub)
    with p3:
        order_unit = "Orders" if lang_code == "EN" else "Pesanan"
        order_title = "Total Completed Orders" if lang_code == "EN" else "Total Pesanan Selesai"
        if lang_code == "EN":
            order_sub = f"Recency: {recency_val} days ago" if orders > 0 else "No completed orders yet"
        else:
            order_sub = f"Recency: {recency_val} hari yang lalu" if orders > 0 else "Belum ada pesanan selesai"
        metric_card(order_title, f"{orders:,} {order_unit}", subtext=order_sub)
    with p4:
        aov_raw = target_cust.get("average_order_value")
        aov = float(aov_raw) if pd.notnull(aov_raw) else 0.0
        aov_title = "Average Order Value (AOV)" if lang_code == "EN" else "Rata-rata Nilai Pesanan (AOV)"
        aov_sub = f"Classification: {value_tier}" if lang_code == "EN" else f"Klasifikasi: {value_tier}"
        metric_card(aov_title, format_rupiah(aov), subtext=aov_sub)

with tab2:
    st.subheader(f"⚡ Next Best Action Engine: {selected_cust_name}")
    sla_label = "Target SLA:"
    health_label = "Health Status:" if lang_code == "EN" else "Status Kesehatan:"
    tier_label = "Value Tier:"
    st.markdown(f"""
    <div class="cetakia-card" style="border-left: 5px solid {nba['badge_color']};">
        <h4 style="color: {nba['badge_color']}; margin-top: 0;">🎯 {nba['rule_name']}</h4>
        <p style="font-size: 15px; font-weight: 600; line-height: 1.6;">
            {nba['action']}
        </p>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; font-size: 13px;">
            <div style="background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
                <b>{sla_label}</b> {nba['sla']}
            </div>
            <div style="background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
                <b>{health_label}</b> {health_status}
            </div>
            <div style="background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
                <b>{tier_label}</b> {value_tier}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.subheader(t["product_pref"])
    if not df_cust_items.empty:
        df_prod_pref = df_cust_items.groupby("product_category")["sales_amount"].sum().reset_index()
        sales_axis = "Total Sales (IDR)" if lang_code == "EN" else "Total Penjualan (IDR)"
        cat_axis = "Product Category" if lang_code == "EN" else "Kategori Produk"
        fig_prod = px.bar(
            df_prod_pref,
            x="sales_amount",
            y="product_category",
            orientation="h",
            color="sales_amount",
            color_continuous_scale=["#93C5FD", "#1D4ED8"],
            labels={"sales_amount": sales_axis, "product_category": cat_axis}
        )
        fig_prod.update_traces(
            marker_line_color="rgba(255, 255, 255, 0.7)",
            marker_line_width=1.5,
            opacity=0.92
        )
        apply_plotly_theme(fig_prod, height=320)
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        no_items_msg = "ℹ️ No item purchase history found for this customer." if lang_code == "EN" else "ℹ️ Tidak ada riwayat pembelian detail item untuk pelanggan ini."
        st.info(no_items_msg)

with tab4:
    st.subheader(t["recent_invoices"])
    caption_txt = "Showing the last 10 invoice transactions including invoice status." if lang_code == "EN" else "Menampilkan 10 transaksi invoice terakhir termasuk status faktur."
    st.caption(caption_txt)
    
    df_cust_sales = df_sales[df_sales["customer_id"] == cust_id].sort_values(by="invoice_date", ascending=False).head(10)
    
    if not df_cust_sales.empty:
        df_sales_disp = df_cust_sales[["invoice_code", "invoice_date", "net_sales", "invoice_status"]].copy()
        df_sales_disp["Invoice Date"] = df_sales_disp["invoice_date"].dt.strftime("%Y-%m-%d")
        df_sales_disp["Amount"] = df_sales_disp["net_sales"].apply(lambda x: format_rupiah(x))
        
        col_rename = {
            "invoice_code": "Invoice Code" if lang_code == "EN" else "Kode Invoice",
            "Invoice Date": "Invoice Date" if lang_code == "EN" else "Tanggal Invoice",
            "Amount": "Amount (IDR)" if lang_code == "EN" else "Jumlah (IDR)",
            "invoice_status": "Invoice Status" if lang_code == "EN" else "Status Faktur"
        }
        st.dataframe(
            df_sales_disp[["invoice_code", "Invoice Date", "Amount", "invoice_status"]].rename(columns=col_rename),
            use_container_width=True
        )
    else:
        no_inv_msg = "ℹ️ No invoice transactions found for this customer." if lang_code == "EN" else "ℹ️ Tidak ada transaksi invoice ditemukan untuk pelanggan ini."
        st.info(no_inv_msg)
