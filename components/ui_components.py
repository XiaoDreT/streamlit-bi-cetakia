import base64
import os
import streamlit as st
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime

# Set global Plotly template to adapt to Streamlit
pio.templates.default = "plotly_white"

def _get_logo_b64(filename: str) -> str:
    """Encodes WebP logo files to base64 dynamically for theme-adaptive sidebar rendering."""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename),
        os.path.abspath(filename),
        os.path.join(os.getcwd(), filename)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return ""

def format_rupiah(val, include_decimal: bool = False) -> str:
    """Formats numeric amount into full unabbreviated Indonesian Rupiah format (e.g. Rp 20.612.345.678)."""
    if pd.isnull(val) or val == 0:
        return "Rp 0"
    try:
        val = float(val)
        if include_decimal:
            formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            formatted = f"{int(round(val)):,}".replace(",", ".")
        return f"Rp {formatted}"
    except Exception:
        return f"Rp {val}"

def format_data_value(val, fmt: str = "str", fallback: str = "Belum Ada Data") -> str:
    """Safely formats data values, replacing NaN, null, or empty values with fallback string."""
    if pd.isna(val) or val is None or str(val).strip().lower() in ["nan", "none", "", "nat", "inf", "-inf"]:
        return fallback
    if fmt == "currency":
        return format_rupiah(val)
    elif fmt == "int":
        try:
            return f"{int(round(float(val))):,}".replace(",", ".")
        except Exception:
            return fallback
    elif fmt == "pct":
        try:
            return f"{float(val):.1f}%"
        except Exception:
            return fallback
    return str(val)

# Complete Translation Dictionary
TRANSLATIONS = {
    "ID": {
        "app_title": "Cetakia BI — Decision Support System",
        "app_subtitle": "Sistem Pendukung Keputusan Bisnis Percetakan Cipta Grafika",
        "select_branch": "Pilih Cabang",
        "all_branches": "Semua Cabang",
        "select_segment": "Segmen Pelanggan",
        "all_segments": "Semua Segmen",
        "date_interval": "Rentang Tanggal Scope",
        "select_lang": "Bahasa (Language)",
        "snapshot_cutoff": "Cutoff Snapshot Data",
        "data_mode": "Mode Data Analitis Master",
        "what_happened": "1. APA YANG TERJADI? (METRIK)",
        "context_baseline": "2. KONTEKS & BASELINE",
        "why_who": "3. MENGAPA & SIAPA YANG TERDAMPAK? (INSIGHT)",
        "recommended_action": "🚀 4. REKOMENDASI TINDAKAN BISNIS",
        "total_sales": "Total Penjualan Net",
        "total_orders": "Total Pesanan / Transaksi",
        "active_cust": "Pelanggan Aktif",
        "aov": "Rata-rata Nilai Pesanan (AOV)",
        "billed_rev_sub": "Pendapatan invoice tertagih",
        "distinct_trans_sub": "Transaksi invoice unik",
        "buying_base_sub": "Basis pelanggan yang membeli",
        "revenue_per_order_sub": "Pendapatan per transaksi pesanan",
        "exec_title": "Dashboard Bisnis Eksekutif",
        "exec_sub": "Kesehatan Bisnis Makro, Driver Penjualan, Kinerja Cabang & Konsentrasi Pelanggan",
        "revenue_trend": "📈 Tren & Trajektori Penjualan Bulanan",
        "segment_contrib": "🧩 Kontribusi Segmen Pelanggan",
        "top_cust_leaderboard": "🏆 Leaderboard Konsentrasi Pelanggan Teratas",
        "cust_intel_title": "Dashboard Intelijen Pelanggan",
        "cust_intel_sub": "Distribusi Kesehatan Portofolio, Segmen RFM, Peringatan Risiko Churn & Retensi",
        "cust_health_donut": "🍩 Distribusi Kesehatan Pelanggan",
        "rfm_bar": "📊 Komposisi Segmen Loyalitas RFM",
        "market_map_scatter": "🌐 Peta Peluang Pasar Segmen",
        "at_risk_worklist": "📋 Daftar Kerja Pelanggan Berisiko Tinggi",
        "cust_360_title": "Profil Pelanggan 360°",
        "cust_360_sub": "Profil 360°, Nilai Seumur Hidup, Kecepatan Pembelian, Mix Produk & Rekomendasi Bisnis",
        "select_cust_prompt": "🔎 Pilih Akun Pelanggan untuk Diinspeksi:",
        "profile_val_title": "📋 Profil & Nilai Bisnis:",
        "product_pref": "📦 Preferensi Kategori Produk",
        "recent_invoices": "📜 Invoice Transaksi Terakhir",
        "sales_intel_title": "Dashboard Intelijen Penjualan",
        "sales_intel_sub": "Funnel Konversi Quotation Multi-Tahap, Pemulihan Expired Quote & Performa Sales",
        "quotation_funnel": "🔻 Funnel Konversi Quotation Multi-Tahap",
        "rep_leaderboard": "🏆 Leaderboard Unconverted Salesperson",
        "urgent_worklist": "⚠️ Daftar Kerja Quotation Mendesak (Mendekati Expired <= 72 Jam)",
        "prod_intel_title": "Dashboard Intelijen Produk",
        "prod_intel_sub": "Kontribusi Kategori, Matriks Penetrasi vs Revenue, Pasangan Co-Purchase & Bundle",
        "cat_mix": "🧩 Mix Pendapatan & Volume Kategori",
        "top_prod_leaders": "🏆 10 Produk Pemimpin Pendapatan",
        "opp_matrix": "🎯 Matriks Peluang Penetrasi Pelanggan vs Revenue",
        "copurchase_pairs": "🔗 Pasangan Produk Co-Purchase Direkomendasikan",
        "mkt_intel_title": "Dashboard Intelijen Pasar",
        "mkt_intel_sub": "Kontribusi Segmen Pasar, Benchmark Tangkapan Cabang Regional & Kerapatan Peluang",
        "mkt_matrix": "🌐 Matriks Kerapatan Segmen Pasar",
        "branch_benchmark": "🏢 Benchmark Tangkapan Pasar Cabang Regional",
        "strat_guidance": "📌 Panduan Strategi & Interpretasi Bisnis"
    },
    "EN": {
        "app_title": "Cetakia BI — Decision Support System",
        "app_subtitle": "Printing Business Management Decision Support System",
        "select_branch": "Select Branch",
        "all_branches": "All Branches",
        "select_segment": "Customer Segment",
        "all_segments": "All Segments",
        "date_interval": "Date Scope Interval",
        "select_lang": "Language / Bahasa",
        "snapshot_cutoff": "Data Snapshot Cutoff",
        "data_mode": "Master Analytical Data Mode",
        "what_happened": "1. WHAT HAPPENED? (METRIC)",
        "context_baseline": "2. CONTEXT & BASELINE",
        "why_who": "3. WHY & WHO IS AFFECTED? (INSIGHT)",
        "recommended_action": "🚀 4. RECOMMENDED BUSINESS ACTION",
        "total_sales": "Total Net Sales",
        "total_orders": "Total Orders / Transactions",
        "active_cust": "Active Customers",
        "aov": "Average Order Value (AOV)",
        "billed_rev_sub": "Billed invoice revenue",
        "distinct_trans_sub": "Distinct invoice transactions",
        "buying_base_sub": "Unique buying customer base",
        "revenue_per_order_sub": "Revenue per order transaction",
        "exec_title": "Executive Business Dashboard",
        "exec_sub": "Macro Business Health, Revenue Drivers, Branch Performance & Customer Concentration",
        "revenue_trend": "📈 Monthly Revenue Trend & Trajectory",
        "segment_contrib": "🧩 Customer Segment Contribution",
        "top_cust_leaderboard": "🏆 Top Customer Concentration Leaderboard",
        "cust_intel_title": "Customer Intelligence Dashboard",
        "cust_intel_sub": "Portfolio Health Distribution, RFM Loyalty Segments, Churn Risk Alerts & Retention",
        "cust_health_donut": "🍩 Customer Health Distribution",
        "rfm_bar": "📊 RFM Loyalty Segment Composition",
        "market_map_scatter": "🌐 Segment Market Opportunity Map",
        "at_risk_worklist": "📋 High-Value At-Risk Customer Worklist",
        "cust_360_title": "Customer 360 Single-Account View",
        "cust_360_sub": "360° Profile, Lifetime Value, Purchase Velocity, Product Mix & Targeted Recommendation",
        "select_cust_prompt": "🔎 Select Customer Account to Inspect:",
        "profile_val_title": "📋 Profile & Business Value:",
        "product_pref": "📦 Product Category Purchase Preference",
        "recent_invoices": "📜 Recent Invoice Transactions",
        "sales_intel_title": "Sales Intelligence Dashboard",
        "sales_intel_sub": "Multi-Stage Quotation Conversion Funnel, Expired Opportunity Recovery & Sales Performance",
        "quotation_funnel": "🔻 Multi-Stage Quotation Conversion Funnel",
        "rep_leaderboard": "🏆 Sales Rep Unconverted Value Leaderboard",
        "urgent_worklist": "⚠️ Urgent Quotation Action Worklist (Expiring within 72 Hours)",
        "prod_intel_title": "Product Intelligence Dashboard",
        "prod_intel_sub": "Category Contribution, Revenue vs Penetration Matrix, Co-Purchase Affinity & Bundles",
        "cat_mix": "🧩 Category Revenue & Volume Mix",
        "top_prod_leaders": "🏆 Top 10 Product Revenue Leaders",
        "opp_matrix": "🎯 Revenue vs. Customer Penetration Opportunity Matrix",
        "copurchase_pairs": "🔗 Recommended Product Co-Purchase Pairs",
        "mkt_intel_title": "Market Intelligence Dashboard",
        "mkt_intel_sub": "Segment Contribution Share, Regional Branch Market Catchment & Opportunity Density",
        "mkt_matrix": "🌐 Market Opportunity Matrix (Segment Density)",
        "branch_benchmark": "🏢 Regional Branch Market Catchment Benchmarking",
        "strat_guidance": "📌 Strategic Business Interpretation"
    }
}

def inject_custom_css():
    """Injects CSS styling using Streamlit's native theme CSS variables for 100% Dark & Light mode adaptivity."""
    css_code = f"""<style>
/* Global Font & App Styling */
.stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* Header Banner */
.cetakia-header {{
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%);
    padding: 22px 26px;
    border-radius: 12px;
    border: 1px solid #3B82F6;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}}
.cetakia-header h1 {{
    color: #FFFFFF !important;
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 6px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.cetakia-header p {{
    color: #DBEAFE !important;
    font-size: 14px;
    margin: 0;
}}

/* Sidebar Theme-Adaptive Logo (Pure CSS & HTML) */
.cetakia-sidebar-logo-box {{
    margin-bottom: 12px;
    padding: 2px 0;
    min-height: 48px;
    display: flex;
    align-items: center;
}}
.cetakia-logo-light, .cetakia-logo-dark {{
    max-width: 160px;
    height: auto;
    object-fit: contain;
    transition: opacity 0.15s ease-in-out;
}}

/* Fallback default display before JavaScript sets data-theme */
html:not([data-theme]) .cetakia-logo-light {{
    display: block;
}}
html:not([data-theme]) .cetakia-logo-dark {{
    display: none;
}}

/* Explicit data-theme rules applied dynamically */
[data-theme="dark"] .cetakia-logo-light,
html[data-theme="dark"] .cetakia-logo-light,
.stApp[data-theme="dark"] .cetakia-logo-light,
.cetakia-sidebar-logo-box[data-theme="dark"] .cetakia-logo-light {{
    display: none !important;
}}

[data-theme="dark"] .cetakia-logo-dark,
html[data-theme="dark"] .cetakia-logo-dark,
.stApp[data-theme="dark"] .cetakia-logo-dark,
.cetakia-sidebar-logo-box[data-theme="dark"] .cetakia-logo-dark {{
    display: block !important;
}}

[data-theme="light"] .cetakia-logo-light,
html[data-theme="light"] .cetakia-logo-light,
.stApp[data-theme="light"] .cetakia-logo-light,
.cetakia-sidebar-logo-box[data-theme="light"] .cetakia-logo-light {{
    display: block !important;
}}

[data-theme="light"] .cetakia-logo-dark,
html[data-theme="light"] .cetakia-logo-dark,
.stApp[data-theme="light"] .cetakia-logo-dark,
.cetakia-sidebar-logo-box[data-theme="light"] .cetakia-logo-dark {{
    display: none !important;
}}

/* Custom Card Container Adapting to Native Theme */
.cetakia-card {{
    background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
    border: 1px solid rgba(156, 163, 175, 0.25);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}}
.cetakia-card h3, .cetakia-card h4 {{
    color: var(--text-color, inherit);
    margin-top: 0;
}}
.cetakia-card p {{
    color: var(--text-color, inherit);
    opacity: 0.9;
}}

/* Custom Metric Cards Adapting to Native Theme */
.cetakia-metric-card {{
    background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
    border: 1px solid rgba(156, 163, 175, 0.25);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.cetakia-metric-card:hover {{
    border-color: #3B82F6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    transform: translateY(-2px);
}}
.metric-title {{
    color: var(--text-color, inherit);
    opacity: 0.8;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}}
.metric-value {{
    color: var(--text-color, inherit);
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 4px;
}}
.metric-delta-positive {{
    color: #10B981;
    font-size: 13px;
    font-weight: 700;
}}
.metric-delta-negative {{
    color: #EF4444;
    font-size: 13px;
    font-weight: 700;
}}
.metric-subtext {{
    color: var(--text-color, inherit);
    opacity: 0.75;
    font-size: 12px;
    margin-top: 4px;
}}

/* DSS Mandatory Insight Card Component Adapting to Native Theme */
.cetakia-insight-card {{
    background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
    border-left: 5px solid #3B82F6;
    border-top: 1px solid rgba(156, 163, 175, 0.25);
    border-right: 1px solid rgba(156, 163, 175, 0.25);
    border-bottom: 1px solid rgba(156, 163, 175, 0.25);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 22px 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}}
.insight-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}}
.insight-title {{
    color: #3B82F6;
    font-size: 17px;
    font-weight: 700;
    margin: 0;
}}
.insight-badge {{
    background-color: rgba(59, 130, 246, 0.15);
    color: #3B82F6;
    border: 1px solid rgba(59, 130, 246, 0.3);
    font-size: 11px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 14px;
    text-transform: uppercase;
}}
.insight-section {{
    margin-bottom: 12px;
}}
.insight-label {{
    font-size: 12px;
    font-weight: 700;
    color: var(--text-color, inherit);
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.insight-content-metric {{
    font-size: 19px;
    font-weight: 800;
    color: #10B981;
}}
.insight-content-text {{
    font-size: 14px;
    color: var(--text-color, inherit);
    line-height: 1.6;
}}
.insight-action-box {{
    background-color: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 14px;
}}
.insight-action-title {{
    color: #10B981;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.insight-action-desc {{
    color: var(--text-color, inherit);
    font-size: 13.5px;
    font-weight: 500;
    margin: 0;
    line-height: 1.5;
}}

/* Data Tables Styling */
div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
    border: 1px solid rgba(156, 163, 175, 0.25);
    border-radius: 8px;
    overflow: hidden;
}}
</style>"""
    st.markdown(css_code, unsafe_allow_html=True)

def render_header(title: str, subtitle: str, module_tag: str = "CETAKIA DSS"):
    """Renders standardized top banner header."""
    inject_custom_css()
    
    header_html = f"""<div class="cetakia-header">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<h1>📊 {title}</h1>
<p>{subtitle}</p>
</div>
<div style="background: rgba(255, 255, 255, 0.2); border: 1px solid #BFDBFE; color: #FFFFFF; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 12px;">
{module_tag}
</div>
</div>
</div>"""
    st.markdown(header_html, unsafe_allow_html=True)

def metric_card(title: str, value: str, delta: str = None, delta_color: str = "positive", subtext: str = None):
    """Renders metric card cleanly without indented HTML string spaces."""
    delta_class = "metric-delta-positive" if delta_color == "positive" else "metric-delta-negative"
    delta_symbol = "▲" if delta_color == "positive" else "▼"
    
    delta_html = f'<div class="{delta_class}">{delta_symbol} {delta}</div>' if delta else ""
    subtext_html = f'<div class="metric-subtext">{subtext}</div>' if subtext else ""
    
    # UNINDENTED raw HTML string prevents markdown code-block parsing!
    card_html = f"""<div class="cetakia-metric-card">
<div class="metric-title">{title}</div>
<div class="metric-value">{value}</div>
{delta_html}
{subtext_html}
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)

def render_insight_card(title: str, metric: str, context: str, insight: str, action: str, badge: str = "DECISION RULE"):
    """Renders mandatory 4-part DSS insight card unindented."""
    lang_code = st.session_state.get("lang_code", "ID")
    t = TRANSLATIONS.get(lang_code, TRANSLATIONS["ID"])
    
    card_html = f"""<div class="cetakia-insight-card">
<div class="insight-header">
<div class="insight-title">💡 {title}</div>
<div class="insight-badge">{badge}</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
<div class="insight-section">
<div class="insight-label">{t['what_happened']}</div>
<div class="insight-content-metric">{metric}</div>
</div>
<div class="insight-section">
<div class="insight-label">{t['context_baseline']}</div>
<div class="insight-content-text">{context}</div>
</div>
</div>
<div class="insight-section" style="margin-bottom: 12px;">
<div class="insight-label">{t['why_who']}</div>
<div class="insight-content-text">{insight}</div>
</div>
<div class="insight-action-box">
<div class="insight-action-title">{t['recommended_action']}</div>
<div class="insight-action-desc">{action}</div>
</div>
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)

def render_business_insight_card(
    title: str,
    metric: str,
    context: str,
    insight: str,
    who_impacted: str,
    action: str,
    badge: str = "DECISION SUPPORT RULE",
    target_entity: str = None
):
    """Renders stricter V1.1 DSS Business Insight Card following:
    Metric + Context + Insight + Who is Impacted + Recommended Action (+ Target Entity)
    """
    lang_code = st.session_state.get("lang_code", "ID")
    if lang_code == "EN":
        lbl_metric = "1. OBSERVED METRIC (WHAT HAPPENED)"
        lbl_context = "2. CONTEXT & BASELINE"
        lbl_insight = "3. ROOT CAUSE INSIGHT (WHY IT HAPPENED)"
        lbl_impacted = "4. IMPACTED ENTITIES (WHO IS IMPACTED)"
        lbl_action = "🚀 5. RECOMMENDED BUSINESS ACTION (ACTIONABLE WORKFLOW)"
        lbl_target = "Target Entity / Operational SLA:"
    else:
        lbl_metric = "1. METRIK TERAMATI (WHAT HAPPENED)"
        lbl_context = "2. KONTEKS & BASELINE"
        lbl_insight = "3. INSIGHT PENYEBAB UTAMA (WHY IT HAPPENED)"
        lbl_impacted = "4. ENTITAS TERDAMPAK (WHO IS IMPACTED)"
        lbl_action = "🚀 5. REKOMENDASI TINDAKAN BISNIS (ACTIONABLE WORKFLOW)"
        lbl_target = "Target Entitas / SLA Operasional:"

    target_html = f'<div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(16, 185, 129, 0.4); font-size: 13px;"><b>🎯 {lbl_target}</b> {target_entity}</div>' if target_entity else ""
    
    card_html = f"""<div class="cetakia-insight-card">
<div class="insight-header">
<div class="insight-title">💡 {title}</div>
<div class="insight-badge">{badge}</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px;">
<div class="insight-section">
<div class="insight-label">{lbl_metric}</div>
<div class="insight-content-metric">{metric}</div>
</div>
<div class="insight-section">
<div class="insight-label">{lbl_context}</div>
<div class="insight-content-text">{context}</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px;">
<div class="insight-section">
<div class="insight-label">{lbl_insight}</div>
<div class="insight-content-text">{insight}</div>
</div>
<div class="insight-section">
<div class="insight-label">{lbl_impacted}</div>
<div class="insight-content-text" style="color: #F59E0B; font-weight: 600;">{who_impacted}</div>
</div>
</div>
<div class="insight-action-box">
<div class="insight-action-title">{lbl_action}</div>
<div class="insight-action-desc">{action}</div>
{target_html}
</div>
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)

def global_sidebar_filters(df_sales=None, df_customers=None):
    """Generates standardized global filter sidebar with Language selector and theme-adaptive logo."""
    inject_custom_css()
    
    # Render theme-adaptive logo (supports both light and dark mode automatically)
    dark_b64 = _get_logo_b64("cetakia_text_dark.webp")
    light_b64 = _get_logo_b64("cetakia_text_light.webp")
    
    # Render theme-adaptive logo using st.sidebar.html
    st.sidebar.html(f'''
    <div class="cetakia-sidebar-logo-box" id="cetakia-sidebar-logo" style="margin-bottom: 12px; display: flex; align-items: center; min-height: 48px;">
        <img src="data:image/webp;base64,{light_b64}" class="cetakia-logo-light" alt="Cetakia Logo Light" style="max-width: 160px; height: auto;" />
        <img src="data:image/webp;base64,{dark_b64}" class="cetakia-logo-dark" alt="Cetakia Logo Dark" style="max-width: 160px; height: auto; display: none;" />
    </div>
    <script>
    (function() {{
        function detectTheme() {{
            try {{
                var sidebar = document.querySelector('[data-testid="stSidebar"]') || document.querySelector('section[data-testid="stSidebar"]');
                var app = document.querySelector('.stApp');
                var el = sidebar || app || document.body;
                if (el) {{
                    var appStyle = window.getComputedStyle(el);
                    var bg = appStyle.backgroundColor;
                    var bgMatch = bg && bg.match(/[0-9]+/g);
                    if (bgMatch && bgMatch.length >= 3) {{
                        var r = Number(bgMatch[0]), g = Number(bgMatch[1]), b = Number(bgMatch[2]);
                        var a = bgMatch[3] !== undefined ? parseFloat(bgMatch[3]) : 1;
                        if (a > 0.05 && (r !== 0 || g !== 0 || b !== 0 || a === 1)) {{
                            var bgBrightness = 0.299 * r + 0.587 * g + 0.114 * b;
                            return bgBrightness < 128 ? 'dark' : 'light';
                        }}
                    }}
                    var col = appStyle.color;
                    var colMatch = col && col.match(/[0-9]+/g);
                    if (colMatch && colMatch.length >= 3) {{
                        var cr = Number(colMatch[0]), cg = Number(colMatch[1]), cb = Number(colMatch[2]);
                        var cBrightness = 0.299 * cr + 0.587 * cg + 0.114 * cb;
                        return cBrightness > 128 ? 'dark' : 'light';
                    }}
                }}
            }} catch(e) {{}}

            return 'light';
        }}

        function syncTheme() {{
            var theme = detectTheme();
            var isDark = (theme === 'dark');

            if (document.documentElement.getAttribute('data-theme') !== theme) {{
                document.documentElement.setAttribute('data-theme', theme);
            }}

            var boxes = document.querySelectorAll('.cetakia-sidebar-logo-box');
            boxes.forEach(function(box) {{
                if (box.getAttribute('data-theme') !== theme) {{
                    box.setAttribute('data-theme', theme);
                }}
                var lightImg = box.querySelector('.cetakia-logo-light');
                var darkImg = box.querySelector('.cetakia-logo-dark');
                var targetLight = isDark ? 'none' : 'block';
                var targetDark = isDark ? 'block' : 'none';
                if (lightImg && lightImg.style.display !== targetLight) {{
                    lightImg.style.setProperty('display', targetLight, 'important');
                }}
                if (darkImg && darkImg.style.display !== targetDark) {{
                    darkImg.style.setProperty('display', targetDark, 'important');
                }}
            }});
        }}

        window.__cetakia_sync_theme = syncTheme;
        syncTheme();

        if (!window.__cetakia_theme_listener_installed) {{
            window.__cetakia_theme_listener_installed = true;
            window.addEventListener('storage', syncTheme);
            if (window.matchMedia) {{
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', syncTheme);
            }}
            window.setInterval(syncTheme, 300);
        }}
    }})();
    </script>
    ''', unsafe_allow_javascript=True)
    
    # Language Selector in Sidebar
    lang_options = ["Bahasa Indonesia", "English"]
    current_lang_idx = 0 if st.session_state.get("lang", "Bahasa Indonesia") == "Bahasa Indonesia" else 1
    selected_lang = st.sidebar.selectbox("Bahasa (Language)", options=lang_options, index=current_lang_idx, key="lang_select")
    
    st.session_state["lang"] = selected_lang
    st.session_state["lang_code"] = "ID" if selected_lang == "Bahasa Indonesia" else "EN"
    lang_code = st.session_state["lang_code"]
    t = TRANSLATIONS[lang_code]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"🎛️ {t['select_branch']}")
    
    # Branch Filter (Persistent across navigation, resets on browser refresh)
    branch_options = [
        t["all_branches"],
        "Cipta Graha",
        "Cipta Digital",
        "Cipta Galuh",
        "Cipta Cianjur",
        "Cipta Purwakarta",
        "Cipta Online"
    ]
    saved_branch = st.session_state.get("global_branch_norm", "All Branches")
    if saved_branch in ["All Branches", "Semua Cabang"]:
        branch_idx = 0
    elif saved_branch in branch_options:
        branch_idx = branch_options.index(saved_branch)
    else:
        branch_idx = 0
        
    selected_branch = st.sidebar.selectbox(
        t["select_branch"],
        options=branch_options,
        index=branch_idx,
        key=f"global_branch_select_{lang_code}"
    )
    norm_branch = "All Branches" if selected_branch == t["all_branches"] else selected_branch
    st.session_state["global_branch_norm"] = norm_branch
    
    # Customer Segment Filter (Persistent across navigation, resets on browser refresh)
    segment_options = [
        t["all_segments"],
        "Instansi",
        "End User",
        "Agen",
        "Sekolah",
        "UMKM",
        "Industri",
        "Employee",
        "Divisi"
    ]
    saved_segment = st.session_state.get("global_segment_norm", "All Segments")
    if saved_segment in ["All Segments", "Semua Segmen"]:
        segment_idx = 0
    elif saved_segment in segment_options:
        segment_idx = segment_options.index(saved_segment)
    else:
        segment_idx = 0
        
    selected_segment = st.sidebar.selectbox(
        t["select_segment"],
        options=segment_options,
        index=segment_idx,
        key=f"global_segment_select_{lang_code}"
    )
    norm_segment = "All Segments" if selected_segment == t["all_segments"] else selected_segment
    st.session_state["global_segment_norm"] = norm_segment
    
    # Date Range Filter (Persistent across navigation, resets on browser refresh)
    min_date = datetime(2025, 10, 1).date()
    max_date = datetime(2026, 9, 19).date()
    default_date_range = (min_date, max_date)
    
    saved_date_range = st.session_state.get("global_date_range_val", default_date_range)
    if not (isinstance(saved_date_range, (tuple, list)) and len(saved_date_range) == 2):
        saved_date_range = default_date_range
        
    date_range = st.sidebar.date_input(
        t["date_interval"],
        value=saved_date_range,
        min_value=min_date,
        max_value=max_date,
        key="global_date_interval_picker"
    )
    
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        st.session_state["global_date_range_val"] = date_range
    else:
        date_range = saved_date_range
    
    st.sidebar.markdown("---")
    cutoff_date_str = "September 19, 2026" if lang_code == "EN" else "19 September 2026"
    data_mode_str = "Master Analytical Data" if lang_code == "EN" else "Master Data Analitis"
    st.sidebar.caption(f"📌 **{t['snapshot_cutoff']}:** {cutoff_date_str}")
    st.sidebar.caption(f"⚡ **{t['data_mode']}:** {data_mode_str}")
    
    # Return filter values normalized
    norm_branch = "All Branches" if selected_branch == t["all_branches"] else selected_branch
    norm_segment = "All Segments" if selected_segment == t["all_segments"] else selected_segment
    
    return {
        "branch": norm_branch,
        "segment": norm_segment,
        "date_range": date_range,
        "lang": lang_code,
        "t": t
    }

def apply_plotly_theme(fig, height=380):
    """Applies clean Plotly theme matching Streamlit native theme (Dark & Light)."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(156, 163, 175, 0.15)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(156, 163, 175, 0.15)", zeroline=False)
    fig.update_traces(
        selector=dict(type="bar"),
        marker_line_color="rgba(255, 255, 255, 0.6)",
        marker_line_width=1.2,
        opacity=0.92
    )
    return fig
