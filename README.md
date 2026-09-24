# Cetakia BI — Business Intelligence Decision Support System

**Version:** V1.0 (Streamlit Prototype & Documentation Package)  
**Repository:** `cetakia-bi`  
**Platform:** Cipta Grafika Printing Management Platform  

---

## 1. Project Overview

**Cetakia BI** is a customer-oriented **Business Intelligence Decision Support System (DSS)** built for **Cipta Grafika**. Unlike traditional static reporting dashboards that merely present retrospective totals (e.g. *"Revenue: Rp 20B"*), Cetakia BI transforms raw operational printing telemetry into structured, actionable business recommendations.

Every dashboard component and visualization strictly enforces the **`Metric + Context + Insight + Action`** design paradigm and answers 4 core questions:
1. **What happened?** (Observed metric & baseline delta)
2. **Why did it happen?** (Root-cause driver & segment breakdown)
3. **Who is affected?** (Specific customer accounts, sales representatives, product lines, branches)
4. **What action should be taken?** (Assigned operational business action & target SLA)

---

## 2. System Architecture

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
│                             READ-ONLY DATA LOADING LAYER                         │
│                              utils/data_loader.py                                │
│                     (@st.cache_data for instant caching)                        │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         GLOBAL DESIGN & COMPONENT SYSTEM                         │
│                            components/ui_components.py                           │
│  • Dark Enterprise SaaS Theme (#111827 / #1F2937)                                │
│  • metric_card()    • render_insight_card()    • global_sidebar_filters()        │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                       MULTI-PAGE STREAMLIT APPLICATION                           │
│                                   app.py                                         │
│  ┌─────────────────────────────┬─────────────────────────────┐                  │
│  │ 1_Executive_Dashboard.py    │ 2_Customer_Intelligence.py  │                  │
│  ├─────────────────────────────┼─────────────────────────────┤                  │
│  │ 3_Customer_360.py           │ 4_Sales_Intelligence.py     │                  │
│  ├─────────────────────────────┼─────────────────────────────┤                  │
│  │ 5_Product_Intelligence.py   │ 6_Market_Intelligence.py    │                  │
│  └─────────────────────────────┴─────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Dataset Explanation

The prototype operates on five core analytical master datasets:

1. `01_customer_master_raw.csv` (23,768 records)
   * **Purpose:** Customer profile metadata, division branches (Cipta Graha, Cipta Digital, Cipta Galuh, Cipta Cianjur, Cipta Purwakarta, Cipta Online), customer segments / categories (Instansi, End User, Agen, Sekolah, UMKM, Industri, Employee, Divisi), registration dates, prospect status.
2. `02_sales_transaction_extract.csv` (58,521 records)
   * **Purpose:** Billed sales invoice ledgers, net sales amounts, order counts, tax/discounts, sales rep codes.
3. `03_sales_item_extract.csv` (92,626 records)
   * **Purpose:** Line-item transactional details, product codes, quantities sold, category classifications (Large Format, Packaging, Sticker & Label, Digital Printing, Offset Printing, Merchandise).
4. `04_customer_intelligence_analysis.csv` (23,777 records)
   * **Purpose:** Customer RFM scores ($R$, $F$, $M$), health status classification (Healthy, Active, At Risk, Dormant, New), recency days, average reorder gaps, lifetime observed spend.
5. `05_quotation_funnel_master.csv` (3,904 records)
   * **Purpose:** Quotation pipeline status, conversion milestone flags, expired quotation values, assigned sales reps, days to expiry.

---

## 4. Dashboard Module Breakdown

Cetakia BI features 6 specialized, role-tailored dashboard modules:

### Module A: Executive Business Dashboard (`pages/1_Executive_Dashboard.py`)
* **Target Users:** Owner, Executive Management
* **Key Features:** KPI Summary Cards (Total Sales, Total Orders, Active Customers, AOV), Monthly Revenue Trajectory Chart, Customer Segment Contribution Treemap, Top Customer Concentration Leaderboard, and Executive Growth Driver Insight Card.

### Module B: Customer Intelligence Dashboard (`pages/2_Customer_Intelligence.py`)
* **Target Users:** Customer Service Manager, Marketing Lead, Sales AE
* **Key Features:** Customer Health Portfolio Donut Chart (Healthy, Active, At Risk, Dormant), RFM Loyalty Distribution Bar Chart, High-Value At-Risk Customer Worklist, Segment Opportunity Scatter Map, and Churn Risk Alert.

### Module C: Customer 360 Profile (`pages/3_Customer_360.py`)
* **Target Users:** Account Managers, Customer Service Representatives, Credit Analysts
* **Key Features:** Interactive account search, Single-View Profile Header, Lifetime Spend & Order Count, Purchase Velocity Interval Gap, Product Category Preference Bar Chart, Recent Invoices Ledger, and Automated Dynamic Business Action Recommendation.

### Module D: Sales Intelligence Dashboard (`pages/4_Sales_Intelligence.py`)
* **Target Users:** Sales Manager, Commercial Operations, Sales Staff
* **Key Features:** Multi-Stage Quotation Conversion Funnel (Quotes -> Orders -> Invoices -> Payments), Expired Lost Opportunity Pipeline Leaderboard, Salesperson Win Rate Matrix, and Urgent 72-Hour Quote Expiry Action Worklist.

### Module E: Product Intelligence Dashboard (`pages/5_Product_Intelligence.py`)
* **Target Users:** Marketing Manager, Product Category Managers
* **Key Features:** Category Revenue & Volume Mix Treemap, Top 10 Product Revenue Leaders, Revenue vs. Customer Penetration Opportunity Scatter Matrix, Market Basket Co-Purchase Affinity Pairs (Support, Confidence, Lift), and Commercial Product Bundles.

### Module F: Market Intelligence Dashboard (`pages/6_Market_Intelligence.py`)
* **Target Users:** Owner, Strategy Director, Business Development
* **Key Features:** Customer Segment Contribution Share (Industry, UMKM, Corporate, End User), Regional Branch Market Catchment Benchmarking, Market Opportunity Density Scatter Map, and Strategic Portfolio Guidance.

---

## 5. How to Run the Prototype

### Prerequisites
Ensure Python 3.9+ is installed on your system.

### Installation & Execution

```bash
# 1. Navigate to repository directory
cd /home/zen/Documents/Cetakia/cetakia-bi

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Streamlit BI Prototype
streamlit run app.py
```

The application will launch automatically in your web browser at `http://localhost:8501`.

---

## 6. Future Production Integration Roadmap

The Streamlit BI Prototype V1 represents the functional baseline for Cetakia's production decision support system.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION INTEGRATION ROADMAP                           │
├───────────────────┬──────────────────────────────────────────────────────────────┤
│ PHASE             │ ARCHITECTURAL EVOLUTION                                      │
├───────────────────┼──────────────────────────────────────────────────────────────┤
│ Phase 1 (Current) │ Local CSV Master Extract ──► Pandas Analytical Engine ──►     │
│                   │ Streamlit BI Prototype V1                                    │
├───────────────────┼──────────────────────────────────────────────────────────────┤
│ Phase 2           │ PostgreSQL Operational DB ──► ETL Pipeline / dbt ──►         │
│                   │ ClickHouse / Snowflake Analytical Data Warehouse             │
├───────────────────┼──────────────────────────────────────────────────────────────┤
│ Phase 3           │ Analytical Data Warehouse ──► FastAPI Unified BI REST API    │
│                   │ (/api/bi/* endpoints with Redis caching & RBAC)              │
├───────────────────┼──────────────────────────────────────────────────────────────┤
│ Phase 4 (Final)   │ Unified BI REST API ──► Embedded Cetakia SaaS Dashboard      │
│                   │ (React / Next.js Production UI with Automated Action Triggers)│
└───────────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 7. Documentation Index

Detailed architectural and metric specifications are available in the [`docs/`](file:///home/zen/Documents/Cetakia/cetakia-bi/docs) directory:
* [`docs/Dashboard_Visualization_Requirement_V1.md`](file:///home/zen/Documents/Cetakia/cetakia-bi/docs/Dashboard_Visualization_Requirement_V1.md) — Functional baseline, user personas, visualization specs, decision rules.
* [`docs/BI_Insight_Catalog_V1.xlsx`](file:///home/zen/Documents/Cetakia/cetakia-bi/docs/BI_Insight_Catalog_V1.xlsx) — Excel workbook containing Dashboard Overview, Insight Catalog (24+ insights), Metric Dictionary, and REST API Requirements.
