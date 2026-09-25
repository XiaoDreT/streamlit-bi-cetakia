# Cetakia BI — Business Intelligence Decision Support System (DSS V1.1)

**Version:** V1.1 (Stricter Business Decision Support System)  
**Repository:** `cetakia-bi` (`https://github.com/XiaoDreT/streamlit-bi-cetakia`)  
**Target Platform:** Cipta Grafika Commercial Printing Platform  
**Architecture Role:** Senior Business Intelligence Engineer & Data Product Engineer  

---

## 1. Executive Summary: Evolution from V1.0 to V1.1

The **Cetakia BI V1.0 Prototype** successfully proved the feasibility of building analytical dashboards from Cipta Grafika's master data extracts. However, evaluation revealed that V1.0 functioned primarily as an *"Insight Visualization Prototype"* — explaining historical data without enforcing strict operational decision pathways.

**Cetakia BI V1.1** transforms the application into a **"Stricter Business Decision Support System (DSS)"**. Every visualization, metric card, and table is now engineered to guide operational teams (CS, Sales, Product Merchandising, Strategy, and Executive Leadership) on **exact actions to take, target accounts to contact, and expected SLA deadlines**.

### The 5-Part DSS Core Principle

Every analytical component in V1.1 strictly adheres to the standard 5-part decision framework:

$$\text{Decision Card} = \text{Metric} + \text{Context} + \text{Insight} + \text{Who is Impacted} + \text{Recommended Action}$$

| Element | Definition | Example in Cetakia DSS V1.1 |
| :--- | :--- | :--- |
| **1. Metric** | Observed business KPI with precise units | `3,555 Pelanggan At Risk` |
| **2. Context** | Baseline comparison, ratio, or operational benchmark | `Exceeded expected reorder cycle by >1.5x (15.0% of purchasing base)` |
| **3. Insight** | Root cause diagnosis and revenue jeopardy | `High-value accounts entering churn window without follow-up` |
| **4. Who is Impacted** | Concrete accounts, segment, branch, or product category | `Akun Tier A & B pada segmen UMKM & Instansi (Lini Kemasan)` |
| **5. Recommended Action** | Operational business workflow with target SLA | `CS outbound call dalam 48 jam dengan penawaran reorder diskon volume 5%` |

---

## 2. Key Improvements: V1.0 vs. V1.1 Detailed Matrix

| Dimension / Module | V1.0 Baseline (Insight Visualization) | V1.1 DSS (Stricter Decision Support System) |
| :--- | :--- | :--- |
| **Sales Intelligence — Opportunity Rebuild** | Displayed *"Nilai Belum Terkonversi = Rp0"* due to string mismatch (`"Unconverted"` vs `"Not Converted"`). | Rebuilt quotation calculation: **Total Pipeline Rp 27.10B**, **Converted Rp 3.63B**, **Open Opportunity Rp 2.18B**, and **Lost Opportunity Rp 21.30B**. |
| **Sales Funnel & Drop-off** | Static multi-stage bar chart without intermediate stage conversion rates. | Interactive Funnel Chart displaying exact **drop-off percentages between stages** (Quotation Created → Converted → Open Opportunity → Lost Opportunity). |
| **Sales Pipeline SLA** | Static expired quotation list without actionable urgency buckets. | **Urgent 72-Hour Pipeline Worklist** highlighting pending deals nearing deadline, assigned sales rep, and automated follow-up SLA. |
| **Customer Health Separation** | Conflated registered accounts having 0 orders with dormant customers. | **Strict 4-State Health Separation**: `Never Purchased` (Belum Pernah Transaksi), `Active Customer`, `At Risk` (>1.5x cycle), and `Dormant`. |
| **Customer Value Tiering** | No formal spend classification; treated all accounts uniformly. | **Customer Value Tier Engine**: `Tier A` (High Value, >Rp 25M), `Tier B` (Medium Value, Rp 5M–Rp 25M), `Tier C` (Low Value, <Rp 5M). |
| **Customer Prioritization** | Sortable table by historical revenue only. | **Customer Priority Score (0–100)** combining Value (40%), Recency Risk (35%), and Frequency (25%) into an actionable CS Outreach Worklist. |
| **Customer 360** | Informational profile with static metric summary. | **Value Tier Badge**, **Customer Journey Stage** (*New, Growing, Loyal, At Risk, Dormant*), and dynamic **Next Best Action Engine** with rule-based scripts. |
| **Product Cross-Sell** | Generic text callout (*"320 UMKM potential"*). | **Actionable Cross-Sell Target Table**: Exact customer accounts buying Packaging without Stickers, historical affinity (Lift 3.42, Conf 78%), and potential revenue. |
| **Market Intelligence** | Informational segment bar charts and regional shares. | **4-Quadrant Market Opportunity Matrix**: Categorizes segments into *Strategic Market*, *Growth Market*, *Retention Market*, and *Development Market*. |
| **UX & Layout Density** | Long, vertically sprawling pages with excessive whitespace. | Compact multi-tab interfaces (`st.tabs`), collapsible diagnostic sections (`st.expander`), and persistent KPI headers. |
| **Data Quality & Hygiene** | Vulnerable to displaying `0`, `NaN`, or `Infinity` for unobserved metrics. | Strict validation: renders **"Belum Ada Data"** / `"-"` for nulls, and strictly excludes **cancelled invoices** (`invoice_status == 'cancel'`) from revenue. |

---

## 3. System Architecture & Modular Engine

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           ANALYTICAL MASTER DATASET                              │
│  01_customer_master_raw.csv           02_sales_transaction_extract.csv          │
│  03_sales_item_extract.csv            04_customer_intelligence_analysis.csv     │
│  05_quotation_funnel_master.csv                                                 │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS & AUDIT HYGIENE LAYER                           │
│                             utils/data_loader.py                                 │
│  • Exclude cancelled invoices (invoice_status != 'cancel')                       │
│  • Reconcile customer spend totals with confirmed transaction ledgers            │
│  • Cached data loading (@st.cache_data) with fallback path search                │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    BUSINESS INTELLIGENCE DECISION ENGINE                         │
│                         utils/intelligence_engine.py                             │
│  • classify_customer_health()          • assign_customer_value_tier()            │
│  • compute_priority_score()            • assign_customer_journey()               │
│  • next_best_action_engine()           • rebuild_quotation_opportunity_metrics() │
│  • generate_cross_sell_target_list()   • calculate_market_opportunity_matrix()   │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     REUSABLE UI & DECISION CARD SYSTEM                           │
│                         components/ui_components.py                             │
│  • render_business_insight_card() [Metric + Context + Insight + Who + Action]    │
│  • format_data_value() [Guarantees "Belum Ada Data" instead of NaN / 0 / Inf]     │
│  • Enterprise Dark Theme CSS (#111827 / #1F2937) with Dual-Theme Cetakia Logo    │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      STREAMLIT MULTI-PAGE APPLICATION (st.navigation)            │
│                                  app.py (Router)                                 │
│  ├── views/0_Insight_Catalog.py         (System Philosophy & Module Catalog)     │
│  ├── views/1_Executive_Dashboard.py     (Macro Health, Net Revenue, Benchmark)   │
│  ├── views/2_Customer_Intelligence.py   (Health Radar, Tier A/B/C, CS Worklist)  │
│  ├── views/3_Customer_360.py            (Single Account, Next Best Action)       │
│  ├── views/4_Sales_Intelligence.py      (Rebuilt Funnel, Open/Lost Pipe, 72h SLA)│
│  ├── views/5_Product_Intelligence.py    (High Rev/Low Pen, Cross-Sell List)      │
│  └── views/6_Market_Intelligence.py     (4-Quadrant Market Opportunity Matrix)   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Analytical Decision Logic & Formulations

### A. Customer Health State Engine
Customers are strictly partitioned into 4 mutually exclusive states:
1. **Never Purchased (Belum Pernah Transaksi):** Registered in customer master, but lifetime order count $= 0$.
2. **Active Customer (Pelanggan Aktif):** Order count $\ge 1$ and recency days $\le \min(\text{expected reorder cycle} \times 1.25, 90\text{ days})$.
3. **At Risk (Pelanggan Berisiko Churn):** Order count $\ge 1$ and recency days $> \min(\text{expected reorder cycle} \times 1.5, 90\text{ days})$, but recency $\le 180\text{ days}$.
4. **Dormant (Pelanggan Dorman / Churned):** Order count $\ge 1$ and recency $> 180\text{ days}$.

### B. Customer Value Tiering
Classified based on lifetime sales volume, purchase frequency, and average order value (AOV):
* **Tier A (High Value):** Total spend $> \text{Rp } 25,000,000$ OR (Total spend $> \text{Rp } 15,000,000$ and Orders $\ge 5$).
* **Tier B (Medium Value):** Total spend between $\text{Rp } 5,000,000$ and $\text{Rp } 25,000,000$.
* **Tier C (Low Value):** Total spend $< \text{Rp } 5,000,000$.

### C. Customer Priority Score (0–100)
Calculated to answer the Customer Service team's daily question: *"Who should I contact first today?"*
$$\text{Priority Score} = (\text{Value Factor} \times 0.40) + (\text{Risk Factor} \times 0.35) + (\text{Frequency Factor} \times 0.25)$$
* **Value Factor (0–100):** Scaled rank of customer lifetime revenue within their category.
* **Risk Factor (0–100):** Ratio of overdue days beyond normal reorder cycle, capped at 100.
* **Frequency Factor (0–100):** Log-scaled order frequency score.

### D. Rebuilt Quotation Pipeline Engine
* **Total Pipeline Value:** $\sum \text{Quotation Value}$ across all quotes ($\text{Rp } 27,108,683,904$).
* **Converted Value:** $\sum \text{Quotation Value}$ where `conversion_status == 'Converted'` ($\text{Rp } 3,632,436,675$).
* **Open Opportunity Value:** $\sum \text{Quotation Value}$ where status is active (`draft`, `sent`, `accepted awaiting invoice`) and `conversion_status == 'Not Converted'` ($\text{Rp } 2,176,328,432$).
* **Lost Opportunity Value:** $\sum \text{Quotation Value}$ where status is `expired` or `rejected` ($\text{Rp } 21,299,918,797$).
* **Stage Drop-Off Percentage:**
  $$\text{Drop-off Rate}_{A \to B} = \frac{\text{Count}_A - \text{Count}_B}{\text{Count}_A} \times 100\%$$

### E. Market Opportunity Matrix (4 Quadrants)
Segments are benchmarked against median revenue contribution and median customer count:
1. **Strategic Market (High Revenue, High Customer Count):** Core cash cow segments (e.g. *Instansi*, *End User*). Action: Account management SLA & volume tier locks.
2. **Growth Market (Large Customer Base, Lower AOV):** High-volume, emerging customer segments (e.g. *UMKM*, *Sekolah*). Action: Digital cross-sell, self-service portals, product bundling.
3. **Retention Market (High Value, Concentrated Accounts):** Large industrial or agency clients with churn exposure. Action: Key Account Executive relationship coverage.
4. **Development Market (Low Volume, Low Spend):** High upside potential requiring targeted acquisition campaigns.

---

## 5. UI Theme & Visual Guidelines

Cetakia BI V1.1 adheres to the Enterprise Dark SaaS aesthetic:

| Health State | Hex Color | Status Definition |
| :--- | :--- | :--- |
| **Healthy / Converted** | `#10B981` (Emerald) | High recency, loyal reorder rhythm, converted deals |
| **Active Customer** | `#3B82F6` (Cobalt Blue) | Normal purchasing velocity within cycle |
| **At Risk** | `#F59E0B` (Amber Orange) | Exceeded reorder cycle by >1.5x, pending quote expiry |
| **Dormant / Lost** | `#EF4444` (Rose Red) | Severe inactivity (>180 days), rejected/expired quote |
| **Never Purchased** | `#8B5CF6` (Violet Purple) | Prospect registered in CRM without transactions |

---

## 6. Installation & Execution Guide

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/XiaoDreT/streamlit-bi-cetakia.git
cd streamlit-bi-cetakia

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required libraries
pip install -r requirements.txt

# 4. Run Streamlit DSS Prototype
streamlit run app.py
```

The application will run locally at `http://localhost:8501`.

---

## 7. Quality Assurance & Validation Checklist

- [x] **Revenue Integrity:** Cancelled invoices (`invoice_status == 'cancel'`) strictly removed from all sales metrics.
- [x] **Pipeline Accuracy:** Reconstructed quotation opportunities resolve the V1.0 `"Rp0"` bug; displays Rp 2.18B open deals and Rp 21.30B lost recovery potential.
- [x] **Customer Health Separation:** 11,636 accounts with 0 orders properly identified as `Never Purchased` rather than distorted as Dormant.
- [x] **Actionable Cross-Sell:** Displays concrete list of 88 packaging clients missing sticker orders (Lift 3.42) with ~Rp 239M incremental potential.
- [x] **Null Safety:** Replaced raw `NaN` and `0` placeholders with `"Belum Ada Data"`.
- [x] **Responsive Layout:** Tabbed views (`Overview`, `Behavior`, `Product`, `Transaction`, `Recommendation`) prevent endless vertical scrolling.
