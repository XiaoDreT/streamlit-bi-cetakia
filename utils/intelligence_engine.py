import pandas as pd
import numpy as np
from typing import Union, Dict, Any, List

def classify_customer_health(data: Union[pd.Series, pd.DataFrame]) -> Union[str, pd.Series]:
    """Classifies customer into 4 discrete health states:
    1. Never Purchased: No valid transaction history
    2. Active Customer: Recent transaction within normal cycle (<= 45 days)
    3. At Risk: Exceeded reorder cycle (> 45 days and <= 90 days, or > 1.5x cycle)
    4. Dormant: Long inactivity after previous purchase (> 90 days)
    """
    def _row_health(row: pd.Series) -> str:
        total_orders = row.get("total_orders", 0)
        ltv = row.get("lifetime_sales", 0)
        recency = row.get("days_since_last_purchase")
        
        if pd.isna(total_orders) or total_orders == 0 or pd.isna(ltv) or ltv <= 0:
            return "Never Purchased"
        
        if pd.isna(recency):
            return "Never Purchased"
        
        recency_val = float(recency)
        if recency_val <= 45:
            return "Active Customer"
        elif recency_val <= 90:
            return "At Risk"
        else:
            return "Dormant"

    if isinstance(data, pd.DataFrame):
        return data.apply(_row_health, axis=1)
    return _row_health(data)

def assign_customer_value_tier(data: Union[pd.Series, pd.DataFrame]) -> Union[str, pd.Series]:
    """Classifies customer into Tier A (High Value), Tier B (Medium Value), or Tier C (Low Value)
    based on Lifetime Sales, Total Orders, and Average Order Value.
    """
    def _row_tier(row: pd.Series) -> str:
        ltv = row.get("lifetime_sales", 0) or 0
        orders = row.get("total_orders", 0) or 0
        aov = row.get("average_order_value", 0) or 0
        
        if pd.isna(ltv): ltv = 0
        if pd.isna(orders): orders = 0
        if pd.isna(aov): aov = 0
        
        if ltv >= 1000000 or orders >= 5 or aov >= 500000:
            return "Tier A (High Value)"
        elif ltv >= 250000 or orders >= 2:
            return "Tier B (Medium Value)"
        else:
            return "Tier C (Low Value)"

    if isinstance(data, pd.DataFrame):
        return data.apply(_row_tier, axis=1)
    return _row_tier(data)

def compute_priority_score(data: Union[pd.Series, pd.DataFrame]) -> Union[int, pd.Series]:
    """Computes Customer Priority Score (0-100) to answer 'Who should CS contact first?'.
    Priority Score = Value Component (40 pts) + Recency Risk Component (35 pts) + Frequency Component (25 pts)
    """
    def _row_priority(row: pd.Series) -> int:
        ltv = row.get("lifetime_sales", 0) or 0
        orders = row.get("total_orders", 0) or 0
        health = str(row.get("customer_health", "")).strip()
        
        if pd.isna(ltv): ltv = 0
        if pd.isna(orders): orders = 0
        
        # 1. Value Component (0 - 40 pts)
        if ltv >= 10000000: v_pts = 40
        elif ltv >= 5000000: v_pts = 35
        elif ltv >= 2000000: v_pts = 30
        elif ltv >= 1000000: v_pts = 25
        elif ltv >= 500000: v_pts = 20
        elif ltv >= 200000: v_pts = 15
        elif ltv >= 100000: v_pts = 10
        elif ltv > 0: v_pts = 5
        else: v_pts = 0
        
        # 2. Recency Risk Component (0 - 35 pts)
        if "At Risk" in health:
            r_pts = 35
        elif "Dormant" in health:
            r_pts = 20
        elif "Active" in health:
            r_pts = 10
        else:
            r_pts = 5
            
        # 3. Frequency Component (0 - 25 pts)
        if orders >= 20: f_pts = 25
        elif orders >= 10: f_pts = 20
        elif orders >= 5: f_pts = 15
        elif orders >= 2: f_pts = 10
        elif orders >= 1: f_pts = 5
        else: f_pts = 0
        
        return int(min(100, v_pts + r_pts + f_pts))

    if isinstance(data, pd.DataFrame):
        return data.apply(_row_priority, axis=1)
    return _row_priority(data)

def assign_customer_journey(data: Union[pd.Series, pd.DataFrame]) -> Union[str, pd.Series]:
    """Classifies customer into Customer Journey Status:
    - Never Purchased: 0 orders
    - New Customer: 1 order
    - Growing Customer: 2 - 4 orders, actively ordering
    - Loyal Customer: 5+ orders, high engagement
    - At Risk Customer: Order history, recency 46-90 days
    - Dormant Customer: Order history, recency > 90 days
    """
    def _row_journey(row: pd.Series) -> str:
        orders = row.get("total_orders", 0) or 0
        recency = row.get("days_since_last_purchase")
        
        if pd.isna(orders) or orders == 0:
            return "Never Purchased"
        
        recency_val = float(recency) if pd.notnull(recency) else 999
        
        if recency_val > 90:
            return "Dormant Customer"
        elif recency_val > 45:
            return "At Risk Customer"
        else:
            if orders >= 5:
                return "Loyal Customer"
            elif orders >= 2:
                return "Growing Customer"
            else:
                return "New Customer"

    if isinstance(data, pd.DataFrame):
        return data.apply(_row_journey, axis=1)
    return _row_journey(data)

def next_best_action_engine(customer_row: pd.Series, bought_categories: list = None, lang: str = "ID") -> dict:
    """Evaluates customer behavioral profile and outputs a precise operational action."""
    if bought_categories is None:
        bought_categories = []
        
    health = str(customer_row.get("customer_health", "")).strip()
    tier = str(customer_row.get("value_tier", "")).strip()
    orders = customer_row.get("total_orders", 0) or 0
    cust_name = customer_row.get("customer_name", "Pelanggan")
    
    has_packaging = any("Packaging" in c for c in bought_categories)
    has_sticker = any("Sticker" in c for c in bought_categories)
    
    if orders == 0 or "Never" in health:
        if lang == "ID":
            return {
                "rule_name": "ATURAN AKUISISI PERDANA",
                "action": f"Tim Sales Outbound: Jangkau {cust_name} via telepon/WhatsApp dalam 48 jam untuk asesmen kebutuhan cetak dan tawarkan voucher selamat datang 10% untuk pesanan perdana.",
                "sla": "SLA 48 Jam",
                "badge_color": "#8B5CF6"
            }
        else:
            return {
                "rule_name": "FIRST PURCHASE ACQUISITION",
                "action": f"Outbound Sales: Outreach {cust_name} via Phone/WhatsApp within 48h to assess printing needs and offer a 10% welcome voucher on their initial purchase.",
                "sla": "48h Target SLA",
                "badge_color": "#8B5CF6"
            }
            
    if "At Risk" in health and "Tier A" in tier:
        if lang == "ID":
            return {
                "rule_name": "ATURAN RETENSI TIER A (PRIORITAS UTAMA)",
                "action": f"Customer Service & Key Account Lead: Segera lakukan panggilan personal dalam 24 jam ke {cust_name}. Tawarkan diskon loyalitas 5% dan jadwalkan pertemuan review kontrak untuk mencegah churn.",
                "sla": "SLA 24 Jam (Mendesak)",
                "badge_color": "#EF4444"
            }
        else:
            return {
                "rule_name": "TIER A RETENTION (TOP PRIORITY)",
                "action": f"CS & Key Account Lead: Conduct executive outreach within 24h to {cust_name}. Present 5% loyalty incentive and arrange an account review to prevent competitor deflection.",
                "sla": "24h Urgent SLA",
                "badge_color": "#EF4444"
            }
            
    if "At Risk" in health:
        if lang == "ID":
            return {
                "rule_name": "ATURAN RE-ENGAGEMENT RISIKO TINGGI",
                "action": f"Tim CS: Kirim pesan re-engagement WhatsApp resmi yang menanyakan kepuasan cetak terakhir dan berikan voucher free delivery untuk pesanan berikutnya.",
                "sla": "SLA 48 Jam",
                "badge_color": "#F59E0B"
            }
        else:
            return {
                "rule_name": "AT RISK RE-ENGAGEMENT",
                "action": f"CS Representative: Dispatch automated WhatsApp check-in and free delivery voucher for the next order.",
                "sla": "48h Target SLA",
                "badge_color": "#F59E0B"
            }
            
    if has_packaging and not has_sticker:
        if lang == "ID":
            return {
                "rule_name": "ATURAN CROSS-SELL KEMASAN & STIKER",
                "action": f"Sales AE: Klien membeli Box Kemasan tetapi belum memesan Stiker Label Roll (Korelasi Lift 3.42). Kirimkan sampel fisik stiker & tawarkan Paket Bundling Kemasan 5%.",
                "sla": "SLA 7 Hari",
                "badge_color": "#3B82F6"
            }
        else:
            return {
                "rule_name": "PACKAGING & STICKER CROSS-SELL",
                "action": f"Sales AE: Customer purchases Packaging Box but has not ordered Roll Stickers (Lift 3.42). Send physical label sample kit and propose 5% bundle discount.",
                "sla": "7-Day Target SLA",
                "badge_color": "#3B82F6"
            }
            
    if "Loyal" in assign_customer_journey(customer_row) or "Tier A" in tier:
        if lang == "ID":
            return {
                "rule_name": "ATURAN PERAWATAN KEY ACCOUNT",
                "action": f"Commercial Lead: Akun bernilai tinggi dengan repeat order teratur. Usulkan kontrak pasokan tahunan (SLA cetak prioritas & tempo pembayaran) untuk mengunci pangsa pasar.",
                "sla": "SLA 14 Hari",
                "badge_color": "#10B981"
            }
        else:
            return {
                "rule_name": "KEY ACCOUNT NURTURING",
                "action": f"Commercial Lead: High-value account with consistent cadence. Propose annual supply contract with priority printing turnaround to lock in wallet share.",
                "sla": "14-Day Target SLA",
                "badge_color": "#10B981"
            }
            
    if lang == "ID":
        return {
            "rule_name": "ATURAN MANAJEMEN AKUN RUTIN",
            "action": f"Sales AE: Pertahankan komunikasi reguler, pantau permintaan penawaran baru, dan bagikan info katalog promosi cetak terbaru.",
            "sla": "SLA Bulanan",
            "badge_color": "#3B82F6"
        }
    else:
        return {
            "rule_name": "STANDARD ACCOUNT MANAGEMENT",
            "action": f"Sales AE: Maintain periodic check-ins, monitor incoming quote requests, and circulate new promotional catalogs.",
            "sla": "Monthly Cadence",
            "badge_color": "#3B82F6"
        }

def rebuild_quotation_opportunity_metrics(df_quotes: pd.DataFrame) -> dict:
    """Strictly computes quotation funnel and opportunity values matching business logic:
    1. Total Pipeline Value: SUM(net_quotation_value)
    2. Converted Value: converted_flag == 1 or conversion_status in ['Converted to Invoice', 'Converted to Sales Order']
    3. Open Opportunity Value: converted_flag == 0 and quotation_status in ['draft', 'sent', 'accepted']
    4. Lost Opportunity Value: converted_flag == 0 and quotation_status in ['expired', 'rejected']
    """
    if df_quotes.empty:
        return {
            "total_pipeline": 0, "total_count": 0,
            "converted_val": 0, "converted_count": 0, "win_rate": 0.0,
            "open_opp_val": 0, "open_opp_count": 0, "open_opp_pct": 0.0,
            "lost_opp_val": 0, "lost_opp_count": 0, "lost_opp_pct": 0.0,
            "urgent_count": 0, "urgent_val": 0
        }
        
    total_pipeline = df_quotes["net_quotation_value"].sum()
    total_count = len(df_quotes)
    
    # Converted
    converted_df = df_quotes[df_quotes["converted_flag"] == 1]
    converted_val = converted_df["net_quotation_value"].sum()
    converted_count = len(converted_df)
    win_rate = (converted_count / total_count * 100) if total_count > 0 else 0.0
    
    # Open Opportunity (Active, not yet expired/rejected, not converted)
    open_df = df_quotes[(df_quotes["converted_flag"] == 0) & (df_quotes["quotation_status"].isin(["draft", "sent", "accepted"]))]
    open_opp_val = open_df["net_quotation_value"].sum()
    open_opp_count = len(open_df)
    open_opp_pct = (open_opp_val / total_pipeline * 100) if total_pipeline > 0 else 0.0
    
    # Lost Opportunity (Expired, Rejected without conversion)
    lost_df = df_quotes[(df_quotes["converted_flag"] == 0) & (df_quotes["quotation_status"].isin(["expired", "rejected"]))]
    lost_opp_val = lost_df["net_quotation_value"].sum()
    lost_opp_count = len(lost_df)
    lost_opp_pct = (lost_opp_val / total_pipeline * 100) if total_pipeline > 0 else 0.0
    
    # Urgent Near-Expiry (<= 3 days remaining among Open opportunities)
    urgent_df = open_df[open_df["days_from_expiry"] <= 3]
    urgent_count = len(urgent_df)
    urgent_val = urgent_df["net_quotation_value"].sum()
    
    return {
        "total_pipeline": total_pipeline,
        "total_count": total_count,
        "converted_val": converted_val,
        "converted_count": converted_count,
        "win_rate": win_rate,
        "open_opp_val": open_opp_val,
        "open_opp_count": open_opp_count,
        "open_opp_pct": open_opp_pct,
        "lost_opp_val": lost_opp_val,
        "lost_opp_count": lost_opp_count,
        "lost_opp_pct": lost_opp_pct,
        "urgent_count": urgent_count,
        "urgent_val": urgent_val
    }

def generate_cross_sell_target_list(df_items: pd.DataFrame, df_sales: pd.DataFrame = None) -> pd.DataFrame:
    """Builds an actionable customer target list for product cross-selling.
    Identifies Packaging Box buyers who have not yet purchased Roll Stickers (Affinity Lift: 3.42).
    """
    if df_items.empty:
        return pd.DataFrame()
        
    pkg_items = df_items[df_items["product_category"] == "Sales Packaging"]
    stk_items = df_items[df_items["product_category"] == "Sales Sticker"]
    
    pkg_cust_ids = set(pkg_items["customer_id"].dropna().unique())
    stk_cust_ids = set(stk_items["customer_id"].dropna().unique())
    
    target_cust_ids = list(pkg_cust_ids - stk_cust_ids)
    
    if not target_cust_ids:
        return pd.DataFrame()
        
    target_df = pkg_items[pkg_items["customer_id"].isin(target_cust_ids)].groupby(
        ["customer_id", "customer_name", "customer_category"]
    ).agg(
        pkg_spend=("sales_amount", "sum"),
        pkg_units=("qty", "sum")
    ).reset_index()
    
    # Calculate potential cross-sell value as 20% of packaging spend or minimum Rp 150k
    target_df["potential_value"] = target_df["pkg_spend"].apply(lambda s: max(150000, s * 0.20))
    target_df["current_product"] = "Box Kemasan (Packaging)"
    target_df["recommended_product"] = "Stiker Label Roll Custom"
    target_df["historical_affinity"] = "Lift 3.42 (Confidence 78%)"
    
    return target_df.sort_values(by="potential_value", ascending=False)

def calculate_market_opportunity_matrix(df_intel: pd.DataFrame) -> pd.DataFrame:
    """Calculates Market Opportunity Matrix across customer segments:
    - Strategic Market: High Revenue, High Value (Industri, Divisi)
    - Growth Market: Large Customer Base, Scalable Volume (End User, UMKM)
    - Retention Market: High Existing Value, Key Accounts (Instansi)
    - Development Market: High Potential, Niche Expansion (Sekolah, Agen, Employee)
    """
    buyers = df_intel[df_intel["total_orders"] > 0].copy()
    if buyers.empty:
        return pd.DataFrame()
        
    seg_summary = buyers.groupby("customer_category").agg(
        customer_count=("customer_id", "nunique"),
        total_revenue=("lifetime_sales", "sum"),
        avg_aov=("average_order_value", "mean"),
        repeat_customers=("total_orders", lambda s: (s >= 2).sum())
    ).reset_index()
    
    total_rev = seg_summary["total_revenue"].sum()
    seg_summary["revenue_pct"] = (seg_summary["total_revenue"] / total_rev) * 100
    seg_summary["repeat_rate"] = (seg_summary["repeat_customers"] / seg_summary["customer_count"]) * 100
    
    def classify_market(row):
        rev_pct = row["revenue_pct"]
        cust_cnt = row["customer_count"]
        aov = row["avg_aov"]
        
        if rev_pct >= 25 or aov >= 1500000:
            return "Strategic Market (High Revenue, High Value)"
        elif cust_cnt >= 1500:
            return "Growth Market (Large Customer Base, Scalable Volume)"
        elif rev_pct >= 5 or aov >= 500000:
            return "Retention Market (High Value, Key Accounts)"
        else:
            return "Development Market (High Potential, Niche Expansion)"
            
    seg_summary["opportunity_level"] = seg_summary.apply(classify_market, axis=1)
    return seg_summary.sort_values(by="total_revenue", ascending=False)
