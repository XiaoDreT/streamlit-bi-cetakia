import datetime
import pandas as pd
import numpy as np
from typing import Union, Dict, Any, List

def classify_customer_health_8(data: Union[pd.Series, pd.DataFrame]) -> Union[str, pd.Series]:
    """Classifies customer into 8 business-friendly segments:
    1. Champion / Key Account: High Value, frequent, actively buying
    2. At Risk High Value: High Value, but inactive / overdue cycle
    3. Regular Customer: Consistent repeat buyer with moderate spend
    4. Cross-Sell Potential: Active repeat buyer with potential for catalog expansion
    5. High Value Low Frequency: Large transaction basket, infrequent purchase
    6. Frequent Small Buyer: Transacts often with compact order values
    7. New / Recent Buyer: First/second purchase, recently active
    8. Dormant / Low Value: Low spend and inactive for > 90 days
    """
    def _row_seg8(row: pd.Series) -> str:
        total_orders = row.get("total_orders", 0) or 0
        ltv = row.get("lifetime_sales", 0) or 0
        recency = row.get("days_since_last_purchase", 999)
        if pd.isna(total_orders) or total_orders == 0 or pd.isna(ltv) or ltv <= 0:
            return "Dormant / Low Value"
        if pd.isna(recency): recency = 999
        r = float(recency)
        m = float(ltv)
        f = int(total_orders)
        
        # 1. Champion / Key Account
        if m >= 1000000 and f >= 4 and r <= 60:
            return "Champion / Key Account"
        # 2. At Risk High Value
        elif m >= 1000000 and r > 60:
            return "At Risk High Value"
        # 5. High Value Low Frequency
        elif m >= 1000000 and f < 4 and r <= 60:
            return "High Value Low Frequency"
        # 6. Frequent Small Buyer
        elif f >= 4 and m < 1000000 and r <= 90:
            return "Frequent Small Buyer"
        # 7. New / Recent Buyer
        elif f <= 2 and r <= 45:
            return "New / Recent Buyer"
        # 3. Regular Customer
        elif f >= 2 and r <= 60 and m >= 250000:
            return "Regular Customer"
        # 4. Cross-Sell Potential
        elif f >= 2 and r <= 90:
            return "Cross-Sell Potential"
        # 8. Dormant / Low Value
        else:
            return "Dormant / Low Value"

    if isinstance(data, pd.DataFrame):
        return data.apply(_row_seg8, axis=1)
    return _row_seg8(data)

def assign_customer_value_category(data: Union[pd.Series, pd.DataFrame], lang: str = "ID") -> Union[str, pd.Series]:
    """Classifies customer into 4 simplified, friendly value classifications without technical tier jargon:
    - Customer Bernilai Sangat Tinggi / Very High Value Customer
    - Customer Bernilai Tinggi / High Value Customer
    - Customer Bernilai Menengah / Medium Value Customer
    - Customer Bernilai Rendah / Low Value Customer
    """
    def _row_val(row: pd.Series) -> str:
        ltv = row.get("lifetime_sales", 0) or 0
        orders = row.get("total_orders", 0) or 0
        aov = row.get("average_order_value", 0) or 0
        
        if pd.isna(ltv): ltv = 0
        if pd.isna(orders): orders = 0
        if pd.isna(aov): aov = 0
        
        if lang == "EN":
            if ltv >= 5000000 or (ltv >= 2000000 and orders >= 10):
                return "Very High Value Customer"
            elif ltv >= 1000000 or orders >= 5 or aov >= 500000:
                return "High Value Customer"
            elif ltv >= 250000 or orders >= 2:
                return "Medium Value Customer"
            else:
                return "Low Value Customer"
        else:
            if ltv >= 5000000 or (ltv >= 2000000 and orders >= 10):
                return "Customer Bernilai Sangat Tinggi"
            elif ltv >= 1000000 or orders >= 5 or aov >= 500000:
                return "Customer Bernilai Tinggi"
            elif ltv >= 250000 or orders >= 2:
                return "Customer Bernilai Menengah"
            else:
                return "Customer Bernilai Rendah"

    if isinstance(data, pd.DataFrame):
        return data.apply(_row_val, axis=1)
    return _row_val(data)

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
    """Classifies customer into Tier A / B / C (kept for backwards compatibility)."""
    return assign_customer_value_category(data, lang="ID")

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

def calculate_market_opportunity_matrix(df_intel: pd.DataFrame, df_sales: pd.DataFrame = None) -> pd.DataFrame:
    """Calculates Market Opportunity Matrix across customer segments:
    - Integrates Time-Normalized Growth Rate (PoP Growth %)
    - Market Growth Contribution (%) reflecting real volume/revenue impact
    - Segment Business Role (Commercial B2B, Institutional B2G, Retail/MSME, Internal Operations, Internal Staff)
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
    
    # Calculate Growth Rate (%) and Market Growth Contribution (%) if df_sales is provided
    if df_sales is not None and not df_sales.empty:
        growth_df = compute_period_growth(df_sales, group_col="customer_category", value_col="net_sales")
        if not growth_df.empty:
            cols_to_merge = [c for c in ["customer_category", "growth_pct", "growth_contrib_pct", "delta_sales", "prior_sales", "current_sales"] if c in growth_df.columns]
            seg_summary = seg_summary.merge(growth_df[cols_to_merge], on="customer_category", how="left")
            
    if "growth_pct" not in seg_summary.columns:
        seg_summary["growth_pct"] = 0.0
    if "growth_contrib_pct" not in seg_summary.columns:
        seg_summary["growth_contrib_pct"] = 0.0
    if "delta_sales" not in seg_summary.columns:
        seg_summary["delta_sales"] = 0.0
        
    seg_summary["growth_pct"] = seg_summary["growth_pct"].fillna(0.0)
    seg_summary["growth_contrib_pct"] = seg_summary["growth_contrib_pct"].fillna(0.0)
    seg_summary["delta_sales"] = seg_summary["delta_sales"].fillna(0.0)
    
    # Segment Classification with clear distinction between External Commercial Market vs Internal Operations
    def classify_market(row):
        cat = str(row["customer_category"]).upper()
        rev_pct = row["revenue_pct"]
        contrib = row.get("growth_contrib_pct", 0.0)
        
        # Internal non-market operations
        if cat == "EMPLOYEE":
            return "Internal Transactions (Employee Orders)"
        elif cat == "DIVISI":
            return "Internal Operations (Inter-Branch Fulfillment)"
            
        # Commercial market segments
        if rev_pct >= 25 or contrib >= 5.0:
            return "Strategic Core Market (Primary Revenue Engine)"
        elif rev_pct >= 10 or contrib >= 2.0:
            return "Growth Engine Market (High Volume & Fast Traction)"
        elif rev_pct >= 4:
            return "Institutional Market (Stable B2G & B2B Retention)"
        else:
            return "Niche Expansion Market (Specialized Edu/Promotional)"
            
    seg_summary["opportunity_level"] = seg_summary.apply(classify_market, axis=1)
    return seg_summary.sort_values(by="total_revenue", ascending=False)

def compute_period_growth(df: pd.DataFrame, group_col: str, value_col: str = "net_sales", date_col: str = "invoice_date") -> pd.DataFrame:
    """Computes time-normalized Period-over-Period growth (%) comparing recent period against prior period.
    Uses equal-time duration halves and daily run-rate normalization to prevent uneven duration distortion.
    Also calculates growth contribution (%) and net expansion value to prevent small-base outliers.
    """
    if df.empty or date_col not in df.columns or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "current_sales", "prior_sales", "delta_sales", "growth_pct", "growth_contrib_pct"])
    
    valid_df = df.dropna(subset=[date_col]).copy()
    if valid_df.empty:
        return pd.DataFrame(columns=[group_col, "current_sales", "prior_sales", "delta_sales", "growth_pct", "growth_contrib_pct"])
        
    min_date = valid_df[date_col].min()
    max_date = valid_df[date_col].max()
    
    # Equal-time midpoint: splits date range into two identical-duration halves
    mid_date = min_date + (max_date - min_date) / 2
    d1_days = max(1.0, (mid_date - min_date).total_seconds() / 86400)
    d2_days = max(1.0, (max_date - mid_date).total_seconds() / 86400)
    
    valid_df["_period"] = valid_df[date_col].apply(lambda d: "Current" if d >= mid_date else "Prior")
    piv = valid_df.groupby([group_col, "_period"])[value_col].sum().unstack(fill_value=0.0).reset_index()
    if "Current" not in piv.columns: piv["Current"] = 0.0
    if "Prior" not in piv.columns: piv["Prior"] = 0.0
    
    piv["current_sales"] = piv["Current"]
    piv["prior_sales"] = piv["Prior"]
    piv["delta_sales"] = piv["Current"] - piv["Prior"]
    
    # Run-rate normalized to 30-day equivalent
    piv["prior_runrate"] = piv["Prior"] / d1_days * 30.0
    piv["current_runrate"] = piv["Current"] / d2_days * 30.0
    
    # Segment Growth Rate (%) based on daily/monthly run-rate
    piv["growth_pct"] = piv.apply(
        lambda r: ((r["current_runrate"] - r["prior_runrate"]) / r["prior_runrate"] * 100) if r["prior_runrate"] > 0 else 0.0,
        axis=1
    ).round(1)
    
    # Market Growth Contribution (%) - Segment's contribution to total company market growth
    total_prior = piv["Prior"].sum()
    piv["growth_contrib_pct"] = piv.apply(
        lambda r: (r["delta_sales"] / total_prior * 100) if total_prior > 0 else 0.0,
        axis=1
    ).round(2)
    
    return piv[[group_col, "current_sales", "prior_sales", "delta_sales", "growth_pct", "growth_contrib_pct"]]


def compute_product_copurchase_pairs(df_items: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Calculates factual co-purchased category pairs across confirmed orders.
    Identifies which print categories are frequently bought together in the same invoice.
    """
    if df_items.empty:
        return pd.DataFrame(columns=["kategori_1", "kategori_2", "pasangan", "frekuensi_transaksi", "persentase_bersama"])
        
    valid_items = df_items[df_items["invoice_status"].astype(str).str.lower() != "cancel"].copy()
    valid_items["clean_category"] = valid_items["product_category"].astype(str).str.replace("Sales ", "")
    
    inv_cats = valid_items.groupby("invoice_id")["clean_category"].apply(lambda s: sorted(list(set(s.dropna())))).reset_index()
    multi_cats = inv_cats[inv_cats["clean_category"].apply(len) >= 2]
    
    if multi_cats.empty:
        return pd.DataFrame(columns=["kategori_1", "kategori_2", "pasangan", "frekuensi_transaksi", "persentase_bersama"])
        
    from collections import Counter
    from itertools import combinations
    
    pairs = Counter()
    for cats in multi_cats["clean_category"]:
        for c1, c2 in combinations(cats, 2):
            pairs[(c1, c2)] += 1
            
    tot_multi = len(multi_cats)
    rows = []
    for (c1, c2), count in pairs.most_common(top_n):
        pct = (count / tot_multi * 100) if tot_multi > 0 else 0
        rows.append({
            "kategori_1": c1,
            "kategori_2": c2,
            "pasangan": f"{c1} + {c2}",
            "frekuensi_transaksi": count,
            "persentase_bersama": round(pct, 1)
        })
    return pd.DataFrame(rows)


def analyze_support_umkm_intelligence(
    df_cust: pd.DataFrame, 
    df_intel: pd.DataFrame, 
    df_sales: pd.DataFrame, 
    df_items: pd.DataFrame, 
    branch: str = "All Branches"
) -> dict:
    """Comprehensive analytical engine for the SupportUMKM program:
    Evaluates real customer behavior, printing category mix, product opportunities,
    and field visit data readiness for micro, small & medium enterprises.
    """
    # 1. Filter Customer Master by Branch & UMKM
    umkm_c = df_cust[df_cust["customer_category"].astype(str).str.upper() == "UMKM"].copy()
    if branch != "All Branches" and "division_name" in umkm_c.columns:
        umkm_c = umkm_c[umkm_c["division_name"] == branch]
        
    umkm_cust_ids = set(umkm_c["customer_id"].dropna().unique())
    total_reg = len(umkm_c)
    
    # 2. Filter Customer Intel
    umkm_i = df_intel[df_intel["customer_id"].isin(umkm_cust_ids)].copy()
    buyers = umkm_i[umkm_i["total_orders"] > 0]
    total_buyers = len(buyers)
    prospects = max(0, total_reg - total_buyers)
    
    active_buyers = len(buyers[buyers["days_since_last_purchase"] <= 45])
    new_buyers = len(buyers[(buyers["total_orders"] <= 2) & (buyers["days_since_last_purchase"] <= 45)])
    at_risk_buyers = len(buyers[(buyers["days_since_last_purchase"] > 45) & (buyers["days_since_last_purchase"] <= 90)])
    dormant_buyers = len(buyers[buyers["days_since_last_purchase"] > 90])
    high_val_buyers = len(buyers[buyers["lifetime_sales"] >= 1000000])
    
    # 3. Filter Items for UMKM
    umkm_items = df_items[df_items["customer_id"].isin(umkm_cust_ids)].copy()
    if "invoice_status" in umkm_items.columns:
        umkm_items = umkm_items[umkm_items["invoice_status"].astype(str).str.lower() != "cancel"]
    umkm_items["clean_category"] = umkm_items["product_category"].astype(str).str.replace("Sales ", "")
    
    # Top Categories
    top_cats = umkm_items.groupby("clean_category").agg(
        total_omzet=("sales_amount", "sum"),
        total_qty=("qty", "sum"),
        pembeli_unik=("customer_id", "nunique"),
        transaksi=("invoice_id", "nunique")
    ).reset_index().sort_values(by="total_omzet", ascending=False)
    
    # Top Products
    top_prods = umkm_items.groupby("product_name").agg(
        clean_category=("clean_category", "first"),
        total_omzet=("sales_amount", "sum"),
        total_qty=("qty", "sum"),
        pembeli_unik=("customer_id", "nunique")
    ).reset_index().sort_values(by="total_omzet", ascending=False)
    
    # Cross-product opportunities within UMKM
    pnames = umkm_items["product_name"].fillna("").astype(str).str.lower()
    pcats = umkm_items["product_category"].fillna("").astype(str).str.lower()
    
    is_kemasan = pnames.str.contains("box|kemasan|packaging|dus|paper bag|art carton|lunch box") | pcats.str.contains("packaging")
    is_stiker = pnames.str.contains("stiker|sticker|chromo|vynil") | pcats.str.contains("sticker")
    is_banner = pnames.str.contains("flexy|banner|spanduk") & ~pnames.str.contains("x banner|roll up|mini x")
    is_display = pnames.str.contains("x banner|x-banner|roll up|rollup|standee|tripod|event desk|display")
    
    cust_kemasan = set(umkm_items[is_kemasan]["customer_id"].dropna().unique())
    cust_stiker = set(umkm_items[is_stiker]["customer_id"].dropna().unique())
    cust_banner = set(umkm_items[is_banner]["customer_id"].dropna().unique())
    cust_display = set(umkm_items[is_display]["customer_id"].dropna().unique())
    
    umkm_kemasan_no_stiker = cust_kemasan - cust_stiker
    umkm_stiker_no_kemasan = cust_stiker - cust_kemasan
    umkm_banner_no_display = cust_banner - cust_display
    
    # UMKM Worklist
    merged_umkm = umkm_c.merge(
        umkm_i[["customer_id", "lifetime_sales", "total_orders", "days_since_last_purchase", "customer_health", "average_order_value"]],
        on="customer_id",
        how="left"
    )
    
    def _assign_umkm_promo(row):
        cid = row["customer_id"]
        orders = row.get("total_orders", 0) or 0
        r = row.get("days_since_last_purchase", 999)
        if orders == 0:
            return "Peluang Kunjungan Akuisisi Perdana"
        if cid in umkm_kemasan_no_stiker:
            return "Peluang Paket Kemasan + Stiker Label"
        if cid in umkm_banner_no_display:
            return "Peluang Penawaran Display Stand / Roll Up"
        if r <= 45 and (row.get("lifetime_sales", 0) or 0) >= 1000000:
            return "Kandidat Program Referral B2B UMKM"
        if 45 < r <= 90:
            return "Peluang Re-Aktivasi & Cek Kebutuhan Cetak"
        return "Pendampingan Usaha & Update Katalog"
        
    merged_umkm["peluang_promosi"] = merged_umkm.apply(_assign_umkm_promo, axis=1)
    
    return {
        "kpis": {
            "total_registered": total_reg,
            "total_buyers": total_buyers,
            "prospects": prospects,
            "active_buyers": active_buyers,
            "new_buyers": new_buyers,
            "at_risk_buyers": at_risk_buyers,
            "dormant_buyers": dormant_buyers,
            "high_val_buyers": high_val_buyers
        },
        "top_categories": top_cats,
        "top_products": top_prods,
        "cross_opps": {
            "kemasan_no_stiker_ids": umkm_kemasan_no_stiker,
            "kemasan_no_stiker_count": len(umkm_kemasan_no_stiker),
            "stiker_no_kemasan_ids": umkm_stiker_no_kemasan,
            "stiker_no_kemasan_count": len(umkm_stiker_no_kemasan),
            "banner_no_display_ids": umkm_banner_no_display,
            "banner_no_display_count": len(umkm_banner_no_display)
        },
        "worklist": merged_umkm
    }


def compute_marketing_campaign_intelligence(
    df_cust: pd.DataFrame, 
    df_intel: pd.DataFrame, 
    df_sales: pd.DataFrame, 
    df_items: pd.DataFrame, 
    branch: str = "All Branches", 
    segment: str = "All Segments",
    retarget_days: int = 30
) -> dict:
    """Comprehensive Marketing Campaign Intelligence Engine:
    Identifies factual customer behavior, cross-category purchase gaps,
    referral eligibility, seasonal purchasing momentum, and behavioral retargeting.
    """
    # 1. Filter customers by Branch & Segment
    c_df = df_cust.copy()
    if branch != "All Branches" and "division_name" in c_df.columns:
        c_df = c_df[c_df["division_name"] == branch]
    if segment != "All Segments" and "customer_category" in c_df.columns:
        c_df = c_df[c_df["customer_category"].astype(str).str.upper() == segment.upper()]
        
    valid_cids = set(c_df["customer_id"].dropna().unique())
    
    # 2. Filter items and sales
    items = df_items[df_items["customer_id"].isin(valid_cids)].copy()
    if "invoice_status" in items.columns:
        items = items[items["invoice_status"].astype(str).str.lower() != "cancel"]
        
    intel = df_intel[df_intel["customer_id"].isin(valid_cids)].copy()
    
    # 3. Product categorization masks
    pnames = items["product_name"].fillna("").astype(str).str.lower()
    pcats = items["product_category"].fillna("").astype(str).str.lower()
    
    is_kemasan = pnames.str.contains("box|kemasan|packaging|dus|paper bag|art carton|lunch box") | pcats.str.contains("packaging")
    is_stiker = pnames.str.contains("stiker|sticker|chromo|vynil") | pcats.str.contains("sticker")
    is_banner = pnames.str.contains("flexy|banner|spanduk") & ~pnames.str.contains("x banner|roll up|mini x")
    is_display = pnames.str.contains("x banner|x-banner|roll up|rollup|standee|tripod|event desk|display")
    is_flyer = pnames.str.contains("brosur|flyer|art paper|leaflet")
    is_merch = pnames.str.contains("mug|pin|tumbler|payung|souvenir|merchandise|id card") | pcats.str.contains("souvenir|merchandise")
    
    cust_kemasan = set(items[is_kemasan]["customer_id"].dropna().unique())
    cust_stiker = set(items[is_stiker]["customer_id"].dropna().unique())
    cust_banner = set(items[is_banner]["customer_id"].dropna().unique())
    cust_display = set(items[is_display]["customer_id"].dropna().unique())
    cust_flyer = set(items[is_flyer]["customer_id"].dropna().unique())
    cust_merch = set(items[is_merch]["customer_id"].dropna().unique())
    
    # Opportunity 1: Kemasan -> Belum Stiker (Voucher Candidate)
    target_voucher_ids = cust_kemasan - cust_stiker
    
    # Opportunity 2: Referral Candidates (Repeat, high value, active)
    ref_mask = (intel["total_orders"] >= 3) & (intel["lifetime_sales"] >= 1000000) & (intel["days_since_last_purchase"] <= 60)
    target_referral_ids = set(intel[ref_mask]["customer_id"].dropna().unique())
    
    # Opportunity 3: Seasonal / Thematic momentum (Kalender, Agenda, Buku, Institusi/Korporat)
    is_seasonal_prod = pnames.str.contains("kalender|agenda|notebook|buku|corporate id|map")
    target_seasonal_ids = set(items[is_seasonal_prod]["customer_id"].dropna().unique())
    
    # Opportunity 4: Behavioral Retargeting (Recent Banner buyers without Display)
    if not items.empty and "invoice_date" in items.columns:
        items["invoice_date_norm"] = pd.to_datetime(items["invoice_date"], errors="coerce")
        max_trans_date = items["invoice_date_norm"].max()
        if pd.notnull(max_trans_date):
            cutoff_date = max_trans_date - pd.Timedelta(days=retarget_days)
            recent_banner_items = items[is_banner & (items["invoice_date_norm"] >= cutoff_date)]
            recent_banner_cids = set(recent_banner_items["customer_id"].dropna().unique())
            target_retarget_ids = recent_banner_cids - cust_display
        else:
            target_retarget_ids = set()
    else:
        target_retarget_ids = set()
        
    # Unique audience & overlap
    all_targeted_ids = target_voucher_ids | target_referral_ids | target_seasonal_ids | target_retarget_ids
    
    from collections import Counter
    target_counter = Counter()
    for cid in target_voucher_ids: target_counter[cid] += 1
    for cid in target_referral_ids: target_counter[cid] += 1
    for cid in target_seasonal_ids: target_counter[cid] += 1
    for cid in target_retarget_ids: target_counter[cid] += 1
    
    multi_opp_count = sum(1 for cid, c in target_counter.items() if c >= 2)
    
    # Cross-product opportunities overview
    cross_pairs = [
        {
            "sudah_dibeli": "Kemasan (Box, Dus, Karton)",
            "belum_dibeli": "Stiker Label Roll / Lembaran",
            "jumlah_customer": len(cust_kemasan - cust_stiker),
            "peluang": "Voucher Paket Bundling Kemasan + Stiker",
            "relevansi": "Pelanggan sudah butuh kemasan produk, stiker label adalah pelengkap esensial identitas merek."
        },
        {
            "sudah_dibeli": "Spanduk / Banner (Flexy)",
            "belum_dibeli": "Display Stand (X-Banner, Roll Up, Tripod)",
            "jumlah_customer": len(cust_banner - cust_display),
            "peluang": "Promosi Stand Display Praktis",
            "relevansi": "Pelanggan sudah mencetak media promosi visual, memerlukan penyangga display untuk pameran atau toko."
        },
        {
            "sudah_dibeli": "Brosur / Flyer (Art Paper)",
            "belum_dibeli": "Merchandise / Souvenir (Mug, Pin, Tumbler)",
            "jumlah_customer": len(cust_flyer - cust_merch),
            "peluang": "Paket Promosi Event & Branding Usaha",
            "relevansi": "Pelanggan sedang melakukan pemasaran lapangan, suvenir melipatgandakan retensi daya ingat konsumen."
        }
    ]
    
    # Opportunity Table
    opp_table_data = [
        {
            "Peluang Promosi": "🎟️ Voucher Promosi Pelengkap",
            "Target Pelanggan": "Pelaku Usaha / Pembeli Kemasan",
            "Kondisi Belanja Aktual": "Sudah membeli Kemasan, belum pernah membeli Stiker",
            "Jumlah Target Customer": f"{len(target_voucher_ids):,} Akun",
            "Produk yang Ditawarkan": "Stiker Label Roll / Cutting Kiss Cut",
            "Rekomendasi Aksi Marketing": "Tawarkan voucher diskon paket bundling Kemasan + Stiker via WhatsApp/CS"
        },
        {
            "Peluang Promosi": "🤝 Program Referral Antar-Bisnis",
            "Target Pelanggan": "Pelanggan Loyal Aktif",
            "Kondisi Belanja Aktual": "Transaksi ≥ 3 kali, Total Belanja ≥ Rp 1 Juta, Aktif berbelanja",
            "Jumlah Target Customer": f"{len(target_referral_ids):,} Akun",
            "Produk yang Ditawarkan": "Reward Cashback / Diskon Pesanan Berikutnya",
            "Rekomendasi Aksi Marketing": "Undang menjadi mitra referral: berikan insentif saat merekomendasikan rekanan bisnis"
        },
        {
            "Peluang Promosi": "📅 Momentum Kampanye Musiman",
            "Target Pelanggan": "Instansi, Korporasi & Sekolah",
            "Kondisi Belanja Aktual": "Memiliki histori pesanan Kalender, Agenda, Buku & Corporate ID",
            "Jumlah Target Customer": f"{len(target_seasonal_ids):,} Akun",
            "Produk yang Ditawarkan": "Early Bird Kalender Meja & Agenda Kerja",
            "Rekomendasi Aksi Marketing": "Hubungi sebelum akhir kuartal/tahun untuk mengamankan kapasitas produksi cetak"
        },
        {
            "Peluang Promosi": f"🔄 Promosi Perilaku ({retarget_days} Hari)",
            "Target Pelanggan": "Pembeli Banner Terkini",
            "Kondisi Belanja Aktual": f"Membeli Banner dalam {retarget_days} hari terakhir, belum memiliki rangka display",
            "Jumlah Target Customer": f"{len(target_retarget_ids):,} Akun",
            "Produk yang Ditawarkan": "Display Standee X-Banner / Roll Up Portable",
            "Rekomendasi Aksi Marketing": "Kirim penawaran pelengkap display standee dalam kurun 7-14 hari pasca cetak banner"
        }
    ]
    
    return {
        "voucher_target_ids": target_voucher_ids,
        "referral_target_ids": target_referral_ids,
        "seasonal_target_ids": target_seasonal_ids,
        "retarget_target_ids": target_retarget_ids,
        "all_target_ids": all_targeted_ids,
        "total_unique_target": len(all_targeted_ids),
        "multi_opp_count": multi_opp_count,
        "cross_pairs": pd.DataFrame(cross_pairs),
        "opp_table": pd.DataFrame(opp_table_data),
        "counts": {
            "voucher": len(target_voucher_ids),
            "referral": len(target_referral_ids),
            "seasonal": len(target_seasonal_ids),
            "retarget": len(target_retarget_ids)
        }
    }


# -------------------------------------------------------------
# NEW CUSTOMER GROWTH INTELLIGENCE ENGINE (BUSINESS-DRIVEN)
# -------------------------------------------------------------
def get_growth_status(net_change: int, growth_pct: float, prev_count: int, curr_count: int) -> tuple:
    """
    Returns (status_label, hex_color):
    - NEW: Previous = 0 and Current > 0
    - NO ACTIVITY: Previous = 0 and Current = 0
    - LOW BASE: Previous > 0 and Previous < 5 (prevents alarming flags on tiny samples)
    - VOLUME DROP: Net loss <= -20 accounts (prevents misleading 'STABLE' on large baseline drops)
    - SHARP DECLINE: Growth <= -30%
    - DECLINING: Growth < -10% and > -30%
    - STABLE: -10% <= Growth <= +10%
    - GROWING: Growth > +10%
    """
    if prev_count == 0 and curr_count > 0:
        return "NEW", "#10B981"
    if prev_count == 0 and curr_count == 0:
        return "NO ACTIVITY", "#9CA3AF"
    if prev_count > 0 and prev_count < 5:
        if net_change > 0:
            return "GROWING [LOW BASE]", "#10B981"
        elif net_change < 0:
            return "DIP [LOW BASE]", "#6B7280"
        else:
            return "STABLE [LOW BASE]", "#9CA3AF"
    if curr_count == 0 and prev_count >= 5:
        return "SHARP DECLINE", "#EF4444"
    if growth_pct is None:
        return "NEW", "#10B981"
    # Volume safety check: losing 20+ customers should never be flagged as harmless STABLE
    if net_change <= -20:
        return "VOLUME DROP", "#EF4444"
    if growth_pct > 10.0:
        return "GROWING", "#10B981"
    elif -10.0 <= growth_pct <= 10.0:
        return "STABLE", "#6B7280"
    elif -30.0 < growth_pct < -10.0:
        return "DECLINING", "#F59E0B"
    else:
        return "SHARP DECLINE", "#EF4444"

def get_category_business_status(
    net_change: int,
    growth_pct: float,
    prev_count: int,
    curr_count: int,
    is_en: bool = False
) -> tuple:
    """
    Evaluates category growth with user-friendly, non-misleading, business-first rules:
    - If baseline < 5: flags as Low Base / Basis Kecil so extreme % does not confuse laymen.
    - If real volume drops heavily (net <= -20): flags as Volume Drop even if % looks small.
    - Clearly distinguishes fast growth, positive growth, stable, mild softening, and sharp drop.
    Returns: (status_label, hex_color, explanation_str)
    """
    if prev_count == 0 and curr_count > 0:
        lbl = "Segmen Baru" if not is_en else "New Intake"
        desc = f"+{curr_count} customer baru pertama kali" if not is_en else f"+{curr_count} new accounts from zero base"
        return lbl, "#10B981", desc

    if prev_count == 0 and curr_count == 0:
        lbl = "Tidak Ada Aktivitas" if not is_en else "No Activity"
        desc = "Belum ada customer baru di kedua periode" if not is_en else "No new customers in either period"
        return lbl, "#9CA3AF", desc

    # 1. Low baseline (< 5 accounts)
    if prev_count < 5:
        if net_change > 0:
            lbl = "Tumbuh [Basis Kecil]" if not is_en else "Growth [Low Base]"
            desc = f"Bertambah +{net_change} customer (basis awal hanya {prev_count} akun)" if not is_en else f"Added +{net_change} accounts on small baseline of {prev_count}"
            return lbl, "#10B981", desc
        elif net_change < 0:
            lbl = "Fluktuasi [Basis Kecil]" if not is_en else "Minor Dip [Low Base]"
            desc = f"Menyusut {net_change} customer (basis awal hanya {prev_count} akun, fluktuasi wajar)" if not is_en else f"Contracted {net_change} on small baseline of {prev_count} (normal variation)"
            return lbl, "#6B7280", desc
        else:
            lbl = "Tetap [Basis Kecil]" if not is_en else "Flat [Low Base]"
            desc = f"Volume tetap {curr_count} customer" if not is_en else f"Volume maintained at {curr_count} accounts"
            return lbl, "#9CA3AF", desc

    # 2. Normal baseline (>= 5 accounts)
    # Check for large real volume loss (e.g. net <= -20)
    if net_change <= -20:
        lbl = "Pelemahan Volume Signifikan" if not is_en else "Significant Volume Drop"
        desc = f"Kehilangan {abs(net_change)} customer riil (dampak volume terbesar, evaluasi saluran)" if not is_en else f"Lost {abs(net_change)} real accounts (largest volume impact, pipeline audit advised)"
        return lbl, "#EF4444", desc

    # High growth
    if growth_pct is not None and growth_pct >= 20.0 and net_change >= 5:
        lbl = "Tumbuh Pesat" if not is_en else "Fast Growing"
        desc = f"Melonjak +{net_change} customer (+{growth_pct:.1f}%), pendorong ekspansi utama" if not is_en else f"Surged +{net_change} accounts (+{growth_pct:.1f}%), key expansion driver"
        return lbl, "#10B981", desc
    elif net_change > 0:
        lbl = "Tumbuh Positif" if not is_en else "Growing"
        desc = f"Bertambah +{net_change} customer ({growth_pct:+.1f}%)" if not is_en else f"Added +{net_change} accounts ({growth_pct:+.1f}%)"
        return lbl, "#10B981", desc
    elif net_change == 0:
        lbl = "Stabil (Tetap)" if not is_en else "Stable (Unchanged)"
        desc = f"Sama persis dengan periode lalu ({curr_count} customer)" if not is_en else f"Maintained exact same count ({curr_count} accounts)"
        return lbl, "#6B7280", desc
    elif -10.0 <= growth_pct < 0 and net_change > -10:
        lbl = "Relatif Stabil" if not is_en else "Relatively Stable"
        desc = f"Fluktuasi ringan ({net_change:+d} customer / {growth_pct:+.1f}%)" if not is_en else f"Mild variation ({net_change:+d} accounts / {growth_pct:+.1f}%)"
        return lbl, "#6B7280", desc
    elif growth_pct < -30.0:
        lbl = "Penurunan Tajam" if not is_en else "Sharp Contraction"
        desc = f"Menyusut drastis {abs(net_change)} customer ({growth_pct:.1f}%)" if not is_en else f"Steep drop of {abs(net_change)} accounts ({growth_pct:.1f}%)"
        return lbl, "#EF4444", desc
    else:
        lbl = "Mengalami Penurunan" if not is_en else "Declining"
        desc = f"Berkurang {abs(net_change)} customer ({growth_pct:.1f}%)" if not is_en else f"Decreased by {abs(net_change)} accounts ({growth_pct:.1f}%)"
        return lbl, "#F59E0B", desc

def compute_new_customer_kpis(
    df: pd.DataFrame,
    start_date,
    end_date,
    division: str = "All Branches",
    category: str = "All Segments"
) -> dict:
    """Computes all New Customer KPIs comparing Current Period vs Previous Comparable Period of identical length."""
    if df.empty:
        return {
            "curr_count": 0, "prev_count": 0, "net_growth": 0, "growth_pct": 0.0,
            "growth_display": "0.0%", "delta_color": "neutral", "status": "NO ACTIVITY",
            "top_category": "-", "top_category_count": 0, "top_category_pct": 0.0,
            "period_days": 0, "prev_start_date": None, "prev_end_date": None,
            "df_curr": df, "df_prev": df
        }

    # Filter by Division & Category
    df_filtered = df.copy()
    if division and division not in ["All Branches", "Semua Cabang"]:
        df_filtered = df_filtered[df_filtered["division_name"] == division]
    if category and category not in ["All Segments", "Semua Segmen"]:
        df_filtered = df_filtered[df_filtered["category_name"] == category.upper()]

    # Convert start_date and end_date to datetime.date if needed
    if isinstance(start_date, (pd.Timestamp, str)):
        start_date = pd.to_datetime(start_date).date()
    if isinstance(end_date, (pd.Timestamp, str)):
        end_date = pd.to_datetime(end_date).date()

    # Calculate equal-duration comparison period
    period_days = (end_date - start_date).days + 1
    prev_end_date = start_date - pd.Timedelta(days=1)
    prev_start_date = prev_end_date - pd.Timedelta(days=period_days - 1)

    # Filter data based on new_customer_valid_date
    df_curr = df_filtered[(df_filtered["new_customer_valid_date"] >= start_date) & (df_filtered["new_customer_valid_date"] <= end_date)]
    df_prev = df_filtered[(df_filtered["new_customer_valid_date"] >= prev_start_date) & (df_filtered["new_customer_valid_date"] <= prev_end_date)]

    curr_count = int(df_curr["customer_id"].nunique())
    prev_count = int(df_prev["customer_id"].nunique())
    net_growth = curr_count - prev_count

    # Growth percentage calculation with edge cases
    if prev_count > 0:
        growth_pct = round(((curr_count - prev_count) / prev_count) * 100.0, 1)
        growth_display = f"{growth_pct:+.1f}%"
        status, _ = get_growth_status(net_growth, growth_pct, prev_count, curr_count)
    elif curr_count > 0:
        growth_pct = None
        growth_display = "NEW"
        status = "NEW"
    else:
        growth_pct = 0.0
        growth_display = "-"
        status = "NO ACTIVITY"

    # Delta color
    if net_growth > 0:
        delta_color = "positive"
    elif net_growth < 0:
        delta_color = "negative"
    else:
        delta_color = "neutral"

    # Top Category
    if curr_count > 0 and not df_curr.empty:
        top_cat_series = df_curr.groupby("category_name")["customer_id"].nunique().sort_values(ascending=False)
        top_category = top_cat_series.index[0]
        top_category_count = int(top_cat_series.iloc[0])
        top_category_pct = round((top_category_count / curr_count) * 100.0, 1)
    else:
        top_category = "-"
        top_category_count = 0
        top_category_pct = 0.0

    return {
        "curr_count": curr_count,
        "prev_count": prev_count,
        "net_growth": net_growth,
        "growth_pct": growth_pct,
        "growth_display": growth_display,
        "delta_color": delta_color,
        "status": status,
        "top_category": top_category,
        "top_category_count": top_category_count,
        "top_category_pct": top_category_pct,
        "period_days": period_days,
        "prev_start_date": prev_start_date,
        "prev_end_date": prev_end_date,
        "df_curr": df_curr,
        "df_prev": df_prev
    }

def compute_new_customer_trend(df_curr: pd.DataFrame, df_prev: pd.DataFrame, start_date, end_date) -> tuple:
    """Computes daily, weekly, or monthly time series trend for Line Chart."""
    if isinstance(start_date, (pd.Timestamp, str)):
        start_date = pd.to_datetime(start_date).date()
    if isinstance(end_date, (pd.Timestamp, str)):
        end_date = pd.to_datetime(end_date).date()

    period_days = (end_date - start_date).days + 1
    if period_days <= 31:
        granularity = "Daily"
    elif period_days <= 90:
        granularity = "Weekly"
    else:
        granularity = "Monthly"

    if df_curr.empty:
        return pd.DataFrame(columns=["date_label", "new_customers", "period"]), granularity

    df_c = df_curr.copy()
    if granularity == "Daily":
        df_c["_group"] = pd.to_datetime(df_c["new_customer_valid_date"])
        df_c["date_label"] = df_c["_group"].dt.strftime("%d %b")
    elif granularity == "Weekly":
        df_c["_group"] = pd.to_datetime(df_c["registration_week_start"])
        df_c["date_label"] = "W-" + df_c["_group"].dt.strftime("%U (%d %b)")
    else:
        df_c["_group"] = pd.to_datetime(df_c["registration_month_start"])
        df_c["date_label"] = df_c["_group"].dt.strftime("%b %Y")

    trend_curr = df_c.groupby(["_group", "date_label"])["customer_id"].nunique().reset_index()
    trend_curr = trend_curr.sort_values(by="_group")
    trend_curr = trend_curr.rename(columns={"customer_id": "new_customers"})
    trend_curr["period"] = "Periode Terpilih"

    return trend_curr, granularity

def compute_new_customer_category_growth(df_curr: pd.DataFrame, df_prev: pd.DataFrame) -> pd.DataFrame:
    """Computes category-level acquisition, volume, growth %, status, and low-base indicator."""
    curr_cat = df_curr.groupby("category_name")["customer_id"].nunique().rename("current") if not df_curr.empty else pd.Series(dtype=int)
    prev_cat = df_prev.groupby("category_name")["customer_id"].nunique().rename("previous") if not df_prev.empty else pd.Series(dtype=int)

    all_cats = sorted(list(set(curr_cat.index.tolist() + prev_cat.index.tolist())))
    if not all_cats:
        return pd.DataFrame(columns=["category_name", "previous", "current", "net_change", "growth_pct", "growth_display", "status", "status_color", "is_low_base", "contribution_pct"])

    cat_df = pd.DataFrame(index=all_cats)
    cat_df["previous"] = cat_df.index.map(prev_cat).fillna(0).astype(int)
    cat_df["current"] = cat_df.index.map(curr_cat).fillna(0).astype(int)
    cat_df["net_change"] = cat_df["current"] - cat_df["previous"]

    total_curr = cat_df["current"].sum()
    cat_df["contribution_pct"] = cat_df["current"].apply(lambda c: round((c / total_curr * 100.0), 1) if total_curr > 0 else 0.0)

    def _calc_row(row):
        prev = int(row["previous"])
        curr = int(row["current"])
        net = curr - prev
        is_low_base = (prev > 0 and prev < 5)

        if prev == 0 and curr > 0:
            growth_pct = None
            growth_disp = "NEW"
            status, color = "NEW", "#10B981"
        elif prev == 0 and curr == 0:
            growth_pct = 0.0
            growth_disp = "-"
            status, color = "NO ACTIVITY", "#9CA3AF"
        else:
            pct = round((net / prev) * 100.0, 1)
            growth_pct = pct
            base_badge = " [Low Base]" if is_low_base else ""
            growth_disp = f"{pct:+.1f}%{base_badge}"
            status, color = get_growth_status(net, pct, prev, curr)

        status_id, bus_color, desc_id = get_category_business_status(net, growth_pct, prev, curr, is_en=False)
        status_en, _, desc_en = get_category_business_status(net, growth_pct, prev, curr, is_en=True)
        growth_disp_id = f"{growth_pct:+.1f}%{' [Basis Kecil]' if is_low_base else ''}" if growth_pct is not None else ("BARU" if curr > 0 else "-")
        growth_disp_en = f"{growth_pct:+.1f}%{' [Low Base]' if is_low_base else ''}" if growth_pct is not None else ("NEW" if curr > 0 else "-")

        return pd.Series([
            growth_pct, growth_disp, status, color, is_low_base,
            status_id, status_en, bus_color, desc_id, desc_en,
            growth_disp_id, growth_disp_en
        ], index=[
            "growth_pct", "growth_display", "status", "status_color", "is_low_base",
            "status_id", "status_en", "business_color", "desc_id", "desc_en",
            "growth_display_id", "growth_display_en"
        ])

    calc_res = cat_df.apply(_calc_row, axis=1)
    cat_df = pd.concat([cat_df, calc_res], axis=1).reset_index().rename(columns={"index": "category_name"})
    return cat_df.sort_values(by="current", ascending=False)

def compute_new_customer_division_matrix(df_curr: pd.DataFrame) -> pd.DataFrame:
    """Computes Division vs Customer Category cross-segment matrix."""
    if df_curr.empty:
        return pd.DataFrame()
    piv = df_curr.pivot_table(
        index="division_name",
        columns="category_name",
        values="customer_id",
        aggfunc="nunique",
        fill_value=0
    )
    piv["TOTAL"] = piv.sum(axis=1)
    piv.loc["TOTAL"] = piv.sum(axis=0)
    return piv

def compute_new_customer_growth_drivers(df_curr: pd.DataFrame, df_prev: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Computes ranked Division x Category pairs driving positive customer growth, sorted by Net Change DESC."""
    curr_dc = df_curr.groupby(["division_name", "category_name"])["customer_id"].nunique().rename("current") if not df_curr.empty else pd.Series(dtype=int)
    prev_dc = df_prev.groupby(["division_name", "category_name"])["customer_id"].nunique().rename("previous") if not df_prev.empty else pd.Series(dtype=int)

    all_keys = list(set(curr_dc.index.tolist() + prev_dc.index.tolist()))
    if not all_keys:
        return pd.DataFrame(columns=["division_name", "category_name", "previous", "current", "net_change", "growth_display"])

    rows = []
    for div, cat in all_keys:
        p = int(prev_dc.get((div, cat), 0))
        c = int(curr_dc.get((div, cat), 0))
        net = c - p
        if net > 0: # Only positive growth drivers
            if p == 0:
                disp = "NEW"
            else:
                pct = round((net / p) * 100.0, 1)
                low = " [Low Base]" if p < 5 else ""
                disp = f"{pct:+.1f}%{low}"
            rows.append({
                "division_name": div,
                "category_name": cat,
                "previous": p,
                "current": c,
                "net_change": net,
                "growth_display": disp
            })

    driver_df = pd.DataFrame(rows)
    if not driver_df.empty:
        driver_df = driver_df.sort_values(by=["net_change", "current"], ascending=[False, False]).head(top_n)
    return driver_df

def compute_new_customer_declining_segments(df_curr: pd.DataFrame, df_prev: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Computes categories that experienced net customer decline."""
    cat_growth = compute_new_customer_category_growth(df_curr, df_prev)
    declining_cats = cat_growth[cat_growth["net_change"] < 0].sort_values(by="net_change", ascending=True)

    if declining_cats.empty:
        return pd.DataFrame(columns=["category_name", "previous", "current", "net_change", "growth_display", "most_impacted_division", "action_cta"])

    rows = []
    for _, row in declining_cats.head(top_n).iterrows():
        cat = row["category_name"]
        # Find which division had the biggest decline in this category
        sub_curr = df_curr[df_curr["category_name"] == cat].groupby("division_name")["customer_id"].nunique() if not df_curr.empty else pd.Series(dtype=int)
        sub_prev = df_prev[df_prev["category_name"] == cat].groupby("division_name")["customer_id"].nunique() if not df_prev.empty else pd.Series(dtype=int)

        all_divs = list(set(sub_curr.index.tolist() + sub_prev.index.tolist()))
        div_declines = {}
        for d in all_divs:
            div_declines[d] = int(sub_curr.get(d, 0)) - int(sub_prev.get(d, 0))

        worst_div = min(div_declines.items(), key=lambda x: x[1])[0] if div_declines else "Semua Divisi"
        worst_val = div_declines.get(worst_div, 0)

        rows.append({
            "category_name": cat,
            "previous": int(row["previous"]),
            "current": int(row["current"]),
            "net_change": int(row["net_change"]),
            "growth_display": row["growth_display"],
            "most_impacted_division": f"{worst_div} ({worst_val:+d})",
            "action_cta": f"Evaluasi saluran leads {cat} dan aktivitas sales di cabang {worst_div}."
        })

    return pd.DataFrame(rows)

def generate_new_customer_insights(
    kpis: dict,
    cat_growth: pd.DataFrame,
    drivers: pd.DataFrame,
    declining: pd.DataFrame,
    matrix: pd.DataFrame,
    lang: str = "ID"
) -> list:
    """Generates dynamic 3-part business insights: TEMUAN -> MAKNA BISNIS -> RECOMMENDED CTA in ID or EN."""
    insights = []
    curr_total = kpis.get("curr_count", 0)
    prev_total = kpis.get("prev_count", 0)
    growth_disp = kpis.get("growth_display", "0.0%")
    is_en = (lang == "EN")

    # Insight 1: Kategori Utama & Konsentrasi Portofolio
    if not cat_growth.empty and curr_total > 0:
        top1 = cat_growth.iloc[0]
        top1_name = top1["category_name"]
        top1_cnt = top1["current"]
        top1_pct = top1["contribution_pct"]

        if len(cat_growth) > 1:
            top2 = cat_growth.iloc[1]
            top2_name = top2["category_name"]
            top2_pct = top2["contribution_pct"]
            two_share = top1_pct + top2_pct
        else:
            top2_name, top2_pct, two_share = "", 0.0, top1_pct

        if is_en:
            if two_share >= 70.0:
                temuan = f"The {top1_name} category accounts for {top1_pct:.1f}% ({top1_cnt:,} customers) and combined with {top2_name} captures {two_share:.1f}% of all new customers in this period."
                makna = f"Cipta Grafika customer acquisition is heavily concentrated in two primary segments. Total volume expansion relies disproportionately on the {top1_name} segment."
                cta = f"Maintain acquisition channel momentum for {top1_name}, while actively expanding B2B categories (AGENTS, INDUSTRY, SME) to strengthen portfolio diversification."
                title = f"Category Concentration: {top1_name} Dominance"
            else:
                temuan = f"The {top1_name} category is the leading contributor with {top1_pct:.1f}% ({top1_cnt:,} customers), followed by {top2_name} ({top2_pct:.1f}%)."
                makna = "The new customer acquisition portfolio exhibits a healthy, balanced spread across multiple market segments."
                cta = f"Scale targeted promotional campaigns for the second-ranked category ({top2_name}) to accelerate overall market share expansion."
                title = f"Category Distribution: {top1_name} Intake Engine"
            metric = f"{top1_name} {top1_pct:.1f}% ({top1_cnt:,} Accounts)"
            context = f"Total {curr_total:,} New Customers ({growth_disp} growth vs previous period {prev_total:,})."
            who_impacted = "Marketing Team, Merchandising, and Retail Store Managers."
        else:
            if two_share >= 70.0:
                temuan = f"Kategori {top1_name} menyumbang {top1_pct:.1f}% ({top1_cnt:,} customer) dan bersama {top2_name} mencakup {two_share:.1f}% seluruh New Customer pada periode ini."
                makna = f"Akuisisi customer Cipta Grafika masih sangat terkonsentrasi pada dua kategori utama. Pertumbuhan volume sangat bergantung pada segmen {top1_name}."
                cta = f"Pertahankan efektivitas channel akuisisi {top1_name}, namun dorong pertumbuhan kategori B2B (AGEN, INDUSTRI, UMKM) untuk memperkuat diversifikasi portofolio."
                title = f"Konsentrasi Kategori: Dominasi {top1_name}"
            else:
                temuan = f"Kategori {top1_name} menjadi kontributor terbesar dengan {top1_pct:.1f}% ({top1_cnt:,} customer), diikuti oleh {top2_name} ({top2_pct:.1f}%)."
                makna = "Portofolio akuisisi customer relatif terdiversifikasi dengan sehat lintas segmen pasar."
                cta = f"Tingkatkan alokasi kampanye promosi pada kategori nomor dua ({top2_name}) untuk mempercepat ekspansi pangsa pasar."
                title = f"Distribusi Kategori: Lokomotif {top1_name}"
            metric = f"{top1_name} {top1_pct:.1f}% ({top1_cnt:,} Akun)"
            context = f"Total {curr_total:,} New Customer (Pertumbuhan {growth_disp} vs periode lalu {prev_total:,})."
            who_impacted = "Tim Marketing, Merchandising, dan Retail Store Manager."

        insights.append({
            "title": title,
            "metric": metric,
            "context": context,
            "insight": makna,
            "who_impacted": who_impacted,
            "action": cta,
            "badge": "PORTFOLIO CONCENTRATION"
        })

    # Insight 2: Area Pelemahan (Needs Attention)
    if not declining.empty:
        worst = declining.iloc[0]
        w_cat = worst["category_name"]
        w_prev = worst["previous"]
        w_curr = worst["current"]
        w_chg = worst["net_change"]
        w_growth = worst["growth_display"]
        w_div = worst["most_impacted_division"]

        if is_en:
            title = f"Category Contraction Warning: {w_cat}"
            metric = f"{w_cat} Contracted {w_chg:+d} Accounts ({w_growth})"
            context = f"Previous period registered {w_prev:,} new customers, contracting to {w_curr:,} in the current period."
            makna = f"Lead generation or acquisition channel momentum softened for {w_cat}, indicating potential conversion friction or competitor pressure in {w_div}."
            cta = f"Commercial leadership and branch managers at {w_div.split()[0]} should immediately audit lead pipelines, CS response times, and price competitiveness for {w_cat}."
            who_impacted = f"Sales Leadership & Branch Management ({w_div})."
        else:
            title = f"Peringatan Pelemahan Kategori: {w_cat}"
            metric = f"{w_cat} Turun {w_chg:+d} Akun ({w_growth})"
            context = f"Periode lalu mencatatkan {w_prev:,} customer baru, kini turun menjadi {w_curr:,}."
            makna = f"Terjadi pelemahan saluran akuisisi atau potensi kehilangan prospek {w_cat} kepada kompetitor pada cabang terkait."
            cta = f"Manajer Penjualan dan Branch Manager {w_div.split()[0]} segera evaluasi sumber lead, kecepatan follow-up CS, dan kesesuaian harga penawaran kategori {w_cat}."
            who_impacted = f"Sales Manager & Branch Manager {w_div}."

        insights.append({
            "title": title,
            "metric": metric,
            "context": context,
            "insight": makna,
            "who_impacted": who_impacted,
            "action": cta,
            "badge": "NEEDS ATTENTION"
        })

    # Insight 3: Pendorong Pertumbuhan Utama (Top Growth Driver)
    if not drivers.empty:
        top_drv = drivers.iloc[0]
        d_div = top_drv["division_name"]
        d_cat = top_drv["category_name"]
        d_net = top_drv["net_change"]
        d_curr = top_drv["current"]
        d_growth = top_drv["growth_display"]

        if is_en:
            title = f"Primary Growth Engine: {d_div} × {d_cat}"
            metric = f"+{d_net:,} Net New Customers ({d_growth})"
            context = "Generated the highest positive acquisition surge across all Division × Category pairings."
            makna = f"Sales approach and regional initiatives at {d_div} demonstrated superior effectiveness in converting new {d_cat} accounts."
            cta = f"Document successful sales workflows and channel playbooks from {d_div} and replicate them across other branches where {d_cat} adoption is lagging."
            who_impacted = f"Branch Manager of {d_div} & Commercial Sales Team."
        else:
            title = f"Lokomotif Pertumbuhan: {d_div} × {d_cat}"
            metric = f"+{d_net:,} Customer Baru ({d_growth})"
            context = "Menyumbang lonjakan tertinggi di antara seluruh kombinasi Divisi × Kategori."
            makna = f"Strategi operasional dan pendekatan sales {d_div} sangat efektif dalam menjaring customer baru pada segmen {d_cat}."
            cta = f"Dokumentasikan taktik akuisisi sukses dari {d_div} dan replikasikan ke cabang lain yang performa segmen {d_cat}-nya masih rendah."
            who_impacted = f"Branch Manager {d_div} & Tim Komersial."

        insights.append({
            "title": title,
            "metric": metric,
            "context": context,
            "insight": makna,
            "who_impacted": who_impacted,
            "action": cta,
            "badge": "GROWTH DRIVER"
        })

    return insights

def compute_cetakia_realtime_acquisition_stats(
    df: pd.DataFrame,
    division: str = None,
    category: str = None,
    ref_time: datetime.datetime = None
) -> dict:
    """Computes exact acquisition metrics mirroring Cetakia API's getNewCustomersStats query:
    - last_3_days: created_at >= NOW() - INTERVAL '3 days'
    - previous_3_days: created_at >= NOW() - INTERVAL '6 days' AND created_at < NOW() - INTERVAL '3 days'
    - last_7_days: created_at >= NOW() - INTERVAL '7 days'
    - previous_7_days: created_at >= NOW() - INTERVAL '14 days' AND created_at < NOW() - INTERVAL '7 days'
    - last_30_days: created_at >= NOW() - INTERVAL '30 days'
    - previous_30_days: created_at >= NOW() - INTERVAL '60 days' AND created_at < NOW() - INTERVAL '30 days'
    - total_customers: active customers (customer_deleted_at IS NULL)
    """
    if df.empty:
        return {
            "last_3_days": 0, "previous_3_days": 0, "diff_3": 0, "growth_3": 0.0,
            "last_7_days": 0, "previous_7_days": 0, "diff_7": 0, "growth_7": 0.0,
            "last_30_days": 0, "previous_30_days": 0, "diff_30": 0, "growth_30": 0.0,
            "total_customers": 0, "ref_time": datetime.datetime.now()
        }

    # Filter active customers (deleted_at IS NULL)
    data = df.copy()
    if "customer_deleted_at" in data.columns:
        data = data[data["customer_deleted_at"].isna()]
    if "is_deleted_customer" in data.columns:
        data = data[data["is_deleted_customer"] == False]

    # Filter by division & category if selected
    if division and division not in ["All Branches", "Semua Cabang", "Semua Cabang / All"]:
        data = data[data["division_name"] == division]
    if category and category not in ["All Segments", "Semua Segmen", "Semua Kategori / All"]:
        data = data[data["category_name"] == category.upper()]

    # Normalized timestamp
    if "created_at_jakarta" in data.columns:
        data["created_dt"] = pd.to_datetime(data["created_at_jakarta"])
    elif "customer_created_at" in data.columns:
        data["created_dt"] = pd.to_datetime(data["customer_created_at"])
    else:
        data["created_dt"] = pd.to_datetime(data["created_at"])

    # Reference time: if None, use max timestamp in data
    if ref_time is None:
        ref_time = data["created_dt"].max() if not data.empty else pd.Timestamp.now()
    elif isinstance(ref_time, (datetime.date, str)):
        ref_time = pd.to_datetime(ref_time)

    # Intervals calculation
    l3 = data[data["created_dt"] >= ref_time - pd.Timedelta(days=3)]
    p3 = data[(data["created_dt"] >= ref_time - pd.Timedelta(days=6)) & (data["created_dt"] < ref_time - pd.Timedelta(days=3))]
    l7 = data[data["created_dt"] >= ref_time - pd.Timedelta(days=7)]
    p7 = data[(data["created_dt"] >= ref_time - pd.Timedelta(days=14)) & (data["created_dt"] < ref_time - pd.Timedelta(days=7))]
    l30 = data[data["created_dt"] >= ref_time - pd.Timedelta(days=30)]
    p30 = data[(data["created_dt"] >= ref_time - pd.Timedelta(days=60)) & (data["created_dt"] < ref_time - pd.Timedelta(days=30))]

    tot = len(data)
    l3_count = len(l3)
    p3_count = len(p3)
    l7_count = len(l7)
    p7_count = len(p7)
    l30_count = len(l30)
    p30_count = len(p30)

    # 3-Day growth
    diff_3 = l3_count - p3_count
    if p3_count > 0:
        growth_3 = round((diff_3 / p3_count) * 100.0, 1)
    else:
        growth_3 = 100.0 if l3_count > 0 else 0.0

    # 7-Day growth
    diff_7 = l7_count - p7_count
    if p7_count > 0:
        growth_7 = round((diff_7 / p7_count) * 100.0, 1)
    else:
        growth_7 = 100.0 if l7_count > 0 else 0.0

    # 30-Day growth
    diff_30 = l30_count - p30_count
    if p30_count > 0:
        growth_30 = round((diff_30 / p30_count) * 100.0, 1)
    else:
        growth_30 = 100.0 if l30_count > 0 else 0.0

    # Breakdown by category for 30 days
    cat_30 = l30.groupby("category_name")["customer_id"].nunique().sort_values(ascending=False) if not l30.empty else pd.Series(dtype=int)
    top_cat = cat_30.index[0] if not cat_30.empty else "-"
    top_cat_cnt = int(cat_30.iloc[0]) if not cat_30.empty else 0
    top_cat_pct = round((top_cat_cnt / l30_count * 100.0), 1) if l30_count > 0 else 0.0

    # Breakdown by division for 30 days
    div_30 = l30.groupby("division_name")["customer_id"].nunique().sort_values(ascending=False) if not l30.empty else pd.Series(dtype=int)
    top_div = div_30.index[0] if not div_30.empty else "-"
    top_div_cnt = int(div_30.iloc[0]) if not div_30.empty else 0

    return {
        "last_3_days": l3_count,
        "previous_3_days": p3_count,
        "diff_3": diff_3,
        "growth_3": growth_3,
        "last_7_days": l7_count,
        "previous_7_days": p7_count,
        "diff_7": diff_7,
        "growth_7": growth_7,
        "last_30_days": l30_count,
        "previous_30_days": p30_count,
        "diff_30": diff_30,
        "growth_30": growth_30,
        "total_customers": tot,
        "ref_time": ref_time,
        "top_category": top_cat,
        "top_category_count": top_cat_cnt,
        "top_category_pct": top_cat_pct,
        "top_division": top_div,
        "top_division_count": top_div_cnt,
        "df_l3": l3,
        "df_p3": p3,
        "df_l30": l30
    }

