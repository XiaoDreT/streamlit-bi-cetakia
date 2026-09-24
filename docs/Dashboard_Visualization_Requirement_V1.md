# Dashboard Visualization Requirement V1
## Cetakia BI — Business Intelligence Decision Support System

**Document Version:** 1.0  
**Date:** 23 September 2026  
**Author:** Senior Product Manager, BI Architect & Data Product Analyst  
**Project:** Cetakia BI (Cipta Grafika Printing Management Platform)  
**Status:** Approved Technical Specification  

---

## 1. Dashboard Vision

### 1.1 Strategic Transformation: From "Reporting Dashboard" to "Business Decision Support System"

Historically, business dashboards in printing and manufacturing operations functioned merely as **"Reporting Dashboards"**. They presented retrospective counts, static totals, and vanity metrics (e.g., *"Total Sales this month: Rp 20,000,000,000"*). Such dashboards leave executives and operational teams asking: *So what? What caused this? Who is impacted? What should we do now?*

**Cetakia BI V1** transforms this reporting layer into a proactive **"Business Decision Support System (DSS)"**. A Decision Support System does not stop at data presentation—it bridges operational telemetry directly with structured business decisions.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             TRADITIONAL REPORTING                                │
│   "Revenue is Rp 20 Billion." ──► (End of Information, No Action)                │
└──────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼  TRANSFORMATION TO DSS
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    CETAKIA BUSINESS DECISION SUPPORT SYSTEM                      │
│                                                                                  │
│   1. WHAT HAPPENED?  ► Revenue is Rp 20B (+14% vs prior period).                 │
│   2. WHY DID IT?     ► Driven by Corporate repeat orders (+22%);                 │
│                         UMKM segment dropped by -8%.                             │
│   3. WHO IS AFFECTED?► 14 key Corporate accounts expanded; 38 UMKM               │
│                         accounts are entering Dormant state.                     │
│   4. WHAT ACTION?    ► CS: Re-engage 38 UMKM accounts with a price-pack offer;  │
│                         Sales: Secure annual contracts with top 14 Corporates.   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 The 4-Question Analytical Framework

Every visualization element, card, and report inside Cetakia BI **MUST** explicitly answer four core questions:

1. **What happened?** (Observed metric, current value, baseline, statistical comparison)
2. **Why did it happen?** (Root-cause driver analysis, segment breakdown, product contribution, cohort behavior)
3. **Who is affected?** (Specific customer IDs, customer segments, sales representatives, product categories, branches)
4. **What action should be taken?** (Concrete operational response, assigned workflow owner, priority level, SLA)

### 1.3 Mandatory Business Rule: Metric + Context + Insight + Action

To eliminate non-actionable "vanity" charts, every card in Cetakia BI must adhere to the **`Metric + Context + Insight + Action`** design rule.

| Design Aspect | ❌ WRONG (Reporting Mindset) | ✅ CORRECT (Cetakia DSS Mindset) |
| :--- | :--- | :--- |
| **Sales Metric** | Revenue: Rp 20,000,000,000 | **Metric:** Revenue: Rp 20,000,000,000<br>**Context:** Growth +14% YoY; AOV expanded from Rp 1.2M to Rp 1.5M.<br>**Insight:** Growth is concentrated in top 10% Corporate accounts; UMKM order volume fell 8%.<br>**Action:** Sales Manager: Assign key account managers to top 10% Corporates; Marketing: Launch UMKM bundling campaign. |
| **Quotation Funnel** | Conversion Rate: 34.8% | **Metric:** Conversion Rate: 64.0% (3,200 / 5,000 Quotes converted)<br>**Context:** Pipeline drop at Quotation Expired stage (1,800 quotes worth Rp 4.2B).<br>**Insight:** 62% of expired quotes had validity >14 days with no follow-up.<br>**Action:** Sales Staff: Trigger SLA auto-reminder at Day 3 before quotation expiration. |
| **Customer Retention** | Active Customers: 1,200 | **Metric:** Active Customers: 1,200 / Total Base: 2,500<br>**Context:** 350 accounts flagged as **At Risk** (Recency > 1.5x average reorder cycle).<br>**Insight:** At-risk cluster consists of packaging buyers whose reorder gap exceeded 45 days.<br>**Action:** CS Team: Initiate customer wellness outbound calls for top 50 At-Risk accounts. |

### 1.4 Customer-Oriented Philosophy

Cetakia BI prioritizes **customer-oriented insights** over purely transactional totals. Operational success in printing management is driven by customer lifecycle health, repeat velocity, and wallet share retention. The system evaluates every transaction through 6 Customer Pillars:
- **Customer Behavior:** Order frequency, reorder interval, order pattern, product basket combinations.
- **Customer Value:** Lifetime observed spend, Average Order Value (AOV), margin contribution.
- **Customer Health:** Recency vs. observed cycle, RFM scores ($R$, $F$, $M$), health status classification (Healthy, Active, At Risk, Dormant, New).
- **Customer Retention:** Cohort retention matrix ($M+0$ to $M+11$), repeat purchase rates, churn velocity.
- **Customer Opportunity:** High-value low-penetration product affinity, cross-sell bundles, unfulfilled quotes.
- **Customer Experience & Payment:** Payment behavior (Good, Average, Risk), aging receivables, invoice compliance.

---

## 2. User Persona Analysis

Cetakia BI serves five core operational and executive roles. Each role requires tailored business questions, distinct analytical insights, and specific operational actions.

```
                             ┌────────────────────────┐
                             │       BUSINESS         │
                             │        OWNER           │
                             │  (Strategic Growth)    │
                             └───────────┬────────────┘
                                         │
       ┌──────────────────┬──────────────┴──────────────┬──────────────────┐
       ▼                  ▼                             ▼                  ▼
┌──────────────┐   ┌──────────────┐              ┌──────────────┐   ┌──────────────┐
│    SALES     │   │    SALES     │              │   CUSTOMER   │   │  MARKETING   │
│   MANAGER    │   │    STAFF     │              │   SERVICE    │   │   MANAGER    │
│ (Pipeline &  │   │  (Quotation  │              │ (Retention & │   │ (Campaign &  │
│  Team Perf)  │   │  Execution)  │              │  Health CSAT)│   │ Segmentation)│
└──────────────┘   └──────────────┘              └──────────────┘   └──────────────┘
```

### 2.1 Owner / Executive Management

* **Role Overview:** Overall business owner responsible for profitability, capital allocation, long-term customer equity, and branch expansion.
* **Primary Business Questions:**
  1. Is business revenue growing sustainably, and is growth coming from customer acquisition or expanding customer spend (AOV)?
  2. Which branches (Cipta Graha, Cipta Galuh, Cipta Cianjur) and customer segments generate the highest cash flow and margin?
  3. Are we exposed to revenue concentration risks or systemic customer churn among top accounts?
* **Required Insight:**
  - Executive KPI summary (Sales Amount, Order Count, Active Customers, AOV, Cash Receipts, Invoice Collection Rate).
  - Revenue Source Breakdown (First Observed Purchases vs. Repeat Purchases).
  - Customer Health Portfolio distribution across all branches.
  - Receivables Aging & Risk Exposure profile.
* **Expected Action:**
  - Reallocate sales headcount and marketing budgets toward high-performing branches or segments.
  - Approve targeted retention budgets for high-value accounts flagged as At Risk.
  - Authorize credit term adjustments for persistent slow-paying customer categories.

### 2.2 Sales Manager

* **Role Overview:** Commercial leader overseeing pipeline conversion, salesperson performance, quotation velocity, and revenue targets.
* **Primary Business Questions:**
  1. What is our quotation win rate, and where are deals dropping off in the sales funnel?
  2. How much revenue is trapped in expired or unconverted quotations, and which salespeople have the highest lost opportunity?
  3. How does salesperson productivity compare across branches and product lines?
* **Required Insight:**
  - Multi-stage Quotation Funnel (Quotation $\rightarrow$ Sales Order $\rightarrow$ Invoice $\rightarrow$ Payment Allocation).
  - Unconverted & Expired Quotation Value leaderboard by salesperson and customer.
  - Sales Representative Performance Matrix (Revenue, Deal Count, Average Deal Size, Conversion Rate).
* **Expected Action:**
  - Conduct weekly pipeline reviews targeting high-value expired quotes (Unconverted Value $>$ Rp 10M).
  - Reassign leads from underperforming sales representatives to top closers.
  - Enforce quotation follow-up SLAs (mandatory contact within 48 hours of quotation creation).

### 2.3 Sales Staff / Account Executive

* **Role Overview:** Front-line sales personnel executing quotes, following up with prospects, closing orders, and maintaining account relationships.
* **Primary Business Questions:**
  1. Which of my open quotations are expiring soon and require immediate customer follow-up?
  2. Which of my assigned customers are due for a reorder based on their historical buying cycle?
  3. What complementary products should I cross-sell to a customer during quotation drafting?
* **Required Insight:**
  - Personal Quotation Worklist filtered by Expiry Date and Net Value.
  - Customer 360 profile showing customer order history, preferred products, and average repeat gap.
  - Product Co-purchase Affinity Recommendations (e.g., customer buying *Packaging* frequently buys *Sticker & Label*).
* **Expected Action:**
  - Call or message customers with expiring quotes to address price/spec objections before deal expiry.
  - Proactively pitch cross-sell product bundles during quote generation.
  - Initiate reorder contact for accounts entering their expected purchase window.

### 2.4 Customer Service (CS) / Account Manager

* **Role Overview:** Customer relationship guardians focused on customer satisfaction, health monitoring, churn prevention, and account reactivation.
* **Primary Business Questions:**
  1. Which high-value customers have stopped purchasing or exceeded their typical reorder interval?
  2. What is the health distribution of our customer portfolio (Healthy vs. At Risk vs. Dormant)?
  3. Why did a specific customer's purchase frequency drop, and what was their historical product preference?
* **Required Insight:**
  - Customer Health Radar & Worklist (Recency, Expected Cycle, Churn Risk Score).
  - Monthly Cohort Retention Heatmap ($M+0$ to $M+11$).
  - Individual Customer 360 Deep-Dive (Transaction history, lifetime spend, order frequency gap).
* **Expected Action:**
  - Execute outbound retention campaigns for **At Risk** accounts prior to them slipping into **Dormant** status.
  - Conduct customer satisfaction surveys for accounts experiencing spend degradation.
  - Coordinate special pricing or loyalty incentives with Sales for dormant account reactivation.

### 2.5 Marketing Manager / Specialist

* **Role Overview:** Growth and campaign lead responsible for customer acquisition, segment expansion, cross-sell strategy, and promotional ROI.
* **Primary Business Questions:**
  1. What is the distribution of our customer base across market segments (Industry, UMKM, Corporate, End User)?
  2. Which product categories have high sales volume but low customer penetration?
  3. What product bundling strategies yield the highest affinity and customer conversion?
* **Required Insight:**
  - Customer Segmentation Matrix & Segment Contribution breakdown.
  - Product Revenue vs. Customer Penetration Scatter Matrix.
  - Product Basket Association & Co-purchase Pair Analysis (Support, Confidence, Lift Metrics).
  - First-time buyer acquisition vs. Repeat customer revenue trajectory.
* **Expected Action:**
  - Launch targeted marketing campaigns promoting low-penetration products to existing high-value segments.
  - Design pre-packaged product bundles (e.g., *UMKM Starter Kit: Packaging + Sticker + Thank You Card*).
  - Tailor promotional messaging based on RFM segment characteristics.

---

## 3. Dashboard Information Architecture

Cetakia BI is structured into **6 Interconnected Modules**. Information flows logically from macro executive summaries down to micro transactional and customer-level details.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   MODULE A: EXECUTIVE BUSINESS DASHBOARD                         │
│           (Macro Business Health, Executive KPIs, Revenue Sources)               │
└────────────────────────┬─────────────────────────────────┬───────────────────────┘
                         │                                 │
        ┌────────────────┴──────────────┐       ┌──────────┴──────────────────┐
        ▼                               ▼       ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│   MODULE B: CUSTOMER      │ │    MODULE D: SALES        │ │    MODULE E: PRODUCT      │
│   INTELLIGENCE DASHBOARD  │ │    INTELLIGENCE DASHBOARD │ │    INTELLIGENCE DASHBOARD │
│ (Health, RFM, Churn,      │ │  (Funnel, Quotations,     │ │ (Penetration, Cross-sell, │
│  Cohort Retention)        │ │   Salesperson Perf)       │ │  Product Affinity Pairs)  │
└─────────────┬─────────────┘ └─────────────┬─────────────┘ └─────────────┬─────────────┘
              │                             │                             │
              └─────────────────────────────┼─────────────────────────────┘
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      MODULE C: CUSTOMER 360 DASHBOARD                            │
│           (360° Single Customer Profile, Order History, Action Plan)             │
└───────────────────────────────────────────┬──────────────────────────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      MODULE F: MARKET INTELLIGENCE DASHBOARD                     │
│         (Segment Share, Branch Benchmarking, Macro Demand & Penetration)         │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Global Filter & Context Propagation Matrix

All modules operate under a unified global context state to ensure data consistency across views:

```
GLOBAL CONTEXT = {
  Date Range: [date_from, date_to],
  As-Of Cutoff: as_of_date (Default: 2026-09-19),
  Branch Filter: [CGH (Cipta Graha), CGL (Cipta Galuh), CJR (Cipta Cianjur)],
  Customer Segment Filter: [INDUSTRY, UMKM, CORPORATE, END USER],
  Timezone: "Asia/Jakarta"
}
```

### 3.2 Cross-Module Drill-Down Pathways

1. **Executive Dashboard $\rightarrow$ Customer 360:** Clicking any top customer in the Leaderboard immediately navigates to Module C with that `customer_id` context.
2. **Sales Intelligence $\rightarrow$ Customer 360:** Clicking a high-value customer with an expired quotation in Module D opens Module C to inspect historical purchase behavior before re-quoting.
3. **Customer Intelligence $\rightarrow$ Customer 360:** Clicking an **At Risk** customer in the Health Worklist opens Module C to launch a re-activation action item.
4. **Product Intelligence $\rightarrow$ Customer 360:** Clicking a recommended co-purchase bundle opens a pre-filtered list of target customers in Module C eligible for the pitch.

---

## 4. Comprehensive Dashboard Module Specifications

---

### Module A: Executive Business Dashboard

#### Module Objective
Provide business owners and executive management with an immediate, high-level assessment of company health, revenue drivers, customer acquisition vs. repeat dynamics, cash flow stability, and top account risks.

#### Target User
Owner, Executive Management, Branch Directors.

#### Analytical Master Dataset Sources
* `02_sales_transaction_extract.csv` (Primary Revenue & Transaction source)
* `01_customer_master_raw.csv` (Customer Profile & Segment metadata)
* `04_customer_intelligence_analysis.csv` (Customer Health & RFM metrics)

#### Key Business Questions Answered
1. What is our total revenue, order count, and average order value for the selected period, and how does it compare to the previous equivalent period?
2. Is revenue growth driven by new customer acquisition or expanding spend among repeat buyers?
3. How is revenue distributed across branches and customer segments?
4. What is our current cash collection efficiency relative to billed invoices?

#### Insight Cards & Visualization Specifications

##### Card A1: Revenue Overview & Growth Driver
* **Metric:** Net Sales Amount ($\sum \text{net\_sales}$).
* **Context:** Comparison vs. prior period of equal length; breakdown by Order Count vs. Average Order Value (AOV).
* **Insight:** Displays whether revenue expansion is volume-driven (more orders) or value-driven (higher spend per order).
* **Action:** If revenue drops due to AOV decline, trigger cross-sell campaigns; if volume drops, trigger lead generation.
* **Visualization Type:** KPI Metric Card with dual Sparkline (Revenue Trend & AOV Trend) + YoY/MoM % Delta Badge.

##### Card A2: Revenue Source Decomposition (First Observed vs. Repeat)
* **Metric:** Revenue from First Observed Purchase vs. Revenue from Repeat Purchases.
* **Context:** Derived from transaction history window.
* **Insight:** Quantifies business reliance on repeat customer stability versus new customer acquisition velocity.
* **Action:** If repeat revenue share drops below 60%, mandate customer retention interventions by CS.
* **Visualization Type:** Stacked Bar Chart (Monthly Timeline) with Percentage Share Overlay.

##### Card A3: Branch Performance Benchmarking
* **Metric:** Billed Net Sales, Order Volume, and Active Customer Count by Branch (`division_name`: Cipta Graha, Cipta Galuh, Cipta Cianjur).
* **Context:** Evaluates relative branch capacity and market penetration.
* **Insight:** Highlights branch-level revenue imbalances or operational bottlenecks.
* **Action:** Reallocate regional marketing budgets toward underperforming branch catchments.
* **Visualization Type:** Grouped Column Chart + Branch Data Summary Table.

##### Card A4: Top Customer Revenue Concentration & Risk Exposure
* **Metric:** Top 10 Customer Revenue Contribution Share ($\frac{\sum \text{Top 10 Net Sales}}{\text{Total Net Sales}} \times 100$).
* **Context:** Cross-referenced with Customer Health status from `04_customer_intelligence_analysis.csv`.
* **Insight:** Identifies if revenue is dangerously concentrated in accounts currently flagged as *At Risk* or *Dormant*.
* **Action:** Executive owner assignment to personally meet with top accounts flagged as At Risk.
* **Visualization Type:** Leaderboard Table with Health Status Indicator Badges & Direct Customer 360 Links.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ MODULE A: EXECUTIVE BUSINESS DASHBOARD MOCKUP                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [Date: 2026-09-01 to 2026-09-19] [Branch: ALL] [Segment: ALL]                            │
├───────────────────┬───────────────────┬───────────────────┬─────────────────────────────┤
│ NET SALES         │ ORDERS            │ ACTIVE CUSTOMERS  │ AVERAGE ORDER VALUE (AOV)   │
│ Rp 24,850,000,000 │ 4,120             │ 1,180             │ Rp 6,031,553                │
│ ▲ +14.2% vs prior │ ▲ +5.1% vs prior  │ ▲ +3.2% vs prior  │ ▲ +8.6% vs prior            │
│ Driver: AOV Shift │ Vol: 4,120 orders │ Base: 1,180 buyers│ Driver: Packaging Mix       │
├───────────────────┴───────────────────┴───────────────────┴─────────────────────────────┤
│ [REVENUE SOURCE DECOMPOSITION CHART]        [TOP CUSTOMER LEADERBOARD TABLE]            │
│ █ Repeat Revenue (72%)                      1. PT Cipta Packaging - Rp 1.2B [HEALTHY]     │
│ █ First Purchase (28%)                      2. CV Galuh Print     - Rp 850M [AT RISK] ◄!  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Module B: Customer Intelligence Dashboard

#### Module Objective
Enable Customer Service, Marketing, and Sales teams to analyze customer portfolio health, monitor RFM segmentation, detect churn risks early, and evaluate multi-month cohort retention trends.

#### Target User
Customer Service Manager, Marketing Lead, Account Managers.

#### Analytical Master Dataset Sources
* `04_customer_intelligence_analysis.csv` (RFM scores, `customer_health`, `rfm_segment`, `days_since_last_purchase`, `average_order_value`)
* `01_customer_master_raw.csv` (Customer metadata, `customer_category`, `cluster`)
* `02_sales_transaction_extract.csv` (Transaction recency & frequency history)

#### Key Business Questions Answered
1. What is the current health status distribution of our customer base (Healthy, Active, At Risk, Dormant, New)?
2. Which high-value customers have exceeded their expected purchase interval and are at risk of churning?
3. How well do monthly customer cohorts retain their purchasing activity over a 12-month horizon?
4. How are customers distributed across RFM segments (Champions, Loyal, At Risk, Hibernating)?

#### Insight Cards & Visualization Specifications

##### Card B1: Customer Health Distribution Radar
* **Metric:** Count and % Share of Customers by `customer_health` status (*Healthy*, *Active*, *At Risk*, *Dormant*, *New*).
* **Context:** Rule logic based on recency vs. historical reorder cycle:
  $$\text{Recency} = \text{as\_of\_date} - \text{last\_purchase\_date}$$
  $$\text{At Risk Condition:} \quad \text{Recency} > \max(30 \text{ days}, 1.5 \times \text{Reorder Cycle})$$
  $$\text{Dormant Condition:} \quad \text{Recency} > \max(90 \text{ days}, 3.0 \times \text{Reorder Cycle})$$
* **Insight:** Quantifies the percentage of the customer base migrating into churn-risk states.
* **Action:** CS Team: Target *At Risk* accounts with lifetime value $> \text{Rp 10M}$ for urgent outbound call interventions.
* **Visualization Type:** Donut Chart with Center Total Base & Color-Coded Severity Segments (Green=Healthy, Yellow=At Risk, Red=Dormant).

##### Card B2: High-Value At-Risk Customer Worklist
* **Metric:** Filtered list of customers where `customer_health == 'At Risk'` or `'Dormant'`, sorted by `lifetime_sales` descending.
* **Context:** Includes `days_since_last_purchase`, `average_order_value`, and assigned salesperson.
* **Insight:** Pinpoints specific, high-value customer accounts that require immediate retention activity.
* **Action:** Direct push to session action queue: "Assign CS Outbound Wellness Call within 48 Hours".
* **Visualization Type:** Interactive Data Table with Severity Badges, Action Buttons, and Customer 360 Hyperlinks.

##### Card B3: Multi-Month Cohort Retention Heatmap
* **Metric:** Cohort Retention Percentage ($M+0, M+1, \dots, M+11$).
  $$\text{Retention } M+n = \frac{\text{Unique Customers purchasing in Month } n}{\text{Initial Cohort Size in Month 0}} \times 100$$
* **Context:** Grouped by customer first observed purchase month.
* **Insight:** Evaluates long-term retention decay rate; identifies whether specific onboarding cohorts exhibit steep early churn.
* **Action:** Marketing: Redesign onboarding touchpoints if $M+1$ retention drops below 35%.
* **Visualization Type:** 2D Heatmap Matrix with Color Gradients (Deep Blue = 100% Retention to Light Red = 0% Retention).

##### Card B4: RFM Segmentation Grid (Champions vs. Hibernating)
* **Metric:** Customer Distribution across 4x4 RFM Matrix (`R_score`, `F_score`, `M_score`).
* **Context:** Segments: *Champions* (555, 554), *Loyal Customers* (445, 454), *At Risk* (224, 215), *Hibernating* (111, 121).
* **Insight:** Reveals structural composition of customer value loyalty.
* **Action:** Marketing: Formulate tailored campaign messages (VIP privileges for Champions; aggressive win-back discounts for Hibernating).
* **Visualization Type:** Treemap or 2D Bubble Grid.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ MODULE B: CUSTOMER INTELLIGENCE DASHBOARD MOCKUP                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ CUSTOMER HEALTH DISTRIBUTION               HIGH-VALUE AT-RISK WORKLIST                  │
│  ████████ Healthy (42%)                    Customer Name      Lifetime Spend  Recency   │
│  ███████  Active  (28%)                    1. PT Jaya Grafika Rp 145,000,000  48 Days   │
│  █████    At Risk (18%) ◄ ATTENTION        2. CV Karya Utama  Rp  98,000,000  62 Days   │
│  ███      Dormant (8%)                     3. Toko Maju Jaya  Rp  64,000,000  95 Days   │
│  █        New     (4%)                     [ACTION: Assign Outbound Reactivation Call]  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ COHORT RETENTION MATRIX (M+0 to M+11)                                                   │
│ Cohort    Size   M+0    M+1    M+2    M+3    M+4    M+5    M+6    M+7    M+8    M+9   │
│ Oct 2025   120   100%   45%    38%    32%    30%    28%    27%    25%    24%    22%   │
│ Nov 2025   135   100%   48%    40%    35%    33%    31%    29%    28%    26%    --    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Module C: Customer 360 Dashboard

#### Module Objective
Serve as the single source of truth for an individual customer account. Aggregates transactional history, health indicators, RFM ratings, product preferences, payment behavior, and pending quotation opportunities into a unified, actionable profile.

#### Target User
Customer Service Representative, Sales Staff, Credit Analyst.

#### Analytical Master Dataset Sources
* `01_customer_master_raw.csv` (Customer master profile, address, contact, category)
* `04_customer_intelligence_analysis.csv` (RFM scores, health status, lifetime invoice value, repeat flag)
* `02_sales_transaction_extract.csv` (Full transaction ledger for target customer)
* `03_sales_item_extract.csv` (Item-level purchase history & product mix)
* `05_quotation_funnel_master.csv` (Open & expired quotes for target customer)

#### Key Business Questions Answered
1. What is this customer's total lifetime value, order frequency, and average order gap?
2. What is their current health status and payment reliability rating?
3. What are their favorite product categories, and what products should we cross-sell next?
4. Are there open or expired quotations that can be closed immediately?

#### Insight Cards & Visualization Specifications

##### Card C1: Customer 360 Header & Vital Statistics
* **Metric:** `customer_name`, `customer_code`, `customer_category`, `division_name`, `lifetime_sales`, `total_orders`, `average_order_value`, `customer_health`, `RFM_score`.
* **Context:** Evaluated up to cutoff date (`as_of_date`).
* **Insight:** Gives instant operational context before initiating customer contact.
* **Action:** CS/Sales: Review customer tier before negotiating contract renewal or pricing discounts.
* **Visualization Type:** Profile Information Card with Key Metrics Badges & Health Tag.

##### Card C2: Historical Purchase Velocity & Frequency Gap
* **Metric:** Order Timeline, `days_since_last_purchase`, Historical Average Reorder Gap (Days).
* **Context:** Gap calculated as average days between consecutive orders ($\ge 2$ distinct order dates).
* **Insight:** Shows whether customer is currently within or outside their natural buying window.
* **Action:** If current recency exceeds average reorder gap by $>20\%$, trigger automated reorder notification.
* **Visualization Type:** Timeline Chart with Reorder Interval Benchmark Bands.

##### Card C3: Product Preference & Cross-Sell Opportunities
* **Metric:** Top 5 Purchased Products by Net Spend + Unpurchased High-Affinity Complementary Products.
* **Context:** Product co-purchase affinity rules calculated from `03_sales_item_extract.csv`.
* **Insight:** Identifies wallet-share expansion opportunities tailored specifically to this customer.
* **Action:** Sales Staff: One-click generate quote prepopulated with recommended cross-sell product bundles.
* **Visualization Type:** Horizontal Horizontal Bar Chart (Purchased Products) + Recommended Cross-Sell Cards.

##### Card C4: Financial & Payment Compliance Panel
* **Metric:** Lifetime Billed Invoices, Outstanding Receivables Balance, Overdue Balance ($>30$ Days), Payment Behavior Class (*Good*, *Average*, *Risk*).
* **Context:** Cross-referenced against invoice payment allocations.
* **Insight:** Protects company cash flow by flagging credit risks before issuing new high-value quotes.
* **Action:** If Payment Behavior == 'Risk' (Overdue $>30$ days), block credit terms and mandate cash-on-delivery (COD).
* **Visualization Type:** Financial Health Summary Widget + Aging Receivable Breakdown.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ MODULE C: CUSTOMER 360 DASHBOARD MOCKUP                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PT CIPTA PACKAGING INDONESIA [CUST-00142]                                               │
│ Category: CORPORATE | Branch: Cipta Graha | Health: HEALTHY | RFM: 555 (Champion)       │
├───────────────────┬───────────────────┬───────────────────┬─────────────────────────────┤
│ OBSERVED VALUE    │ TOTAL ORDERS      │ AVG ORDER VALUE   │ REORDER INTERVAL GAP        │
│ Rp 342,500,000    │ 28 Orders         │ Rp 12,232,142     │ Avg: 18 Days | Current: 12  │
├───────────────────┴───────────────────┴───────────────────┴─────────────────────────────┤
│ PRODUCT PREFERENCE & BASKET MIX            PAYMENT & FINANCIAL COMPLIANCE               │
│ 1. Corrugated Box 30x20 [Rp 180M] (52%)    Total Billed:  Rp 342,500,000                 │
│ 2. Custom Sticker Roll  [Rp 95M]  (28%)    Paid Amount:   Rp 320,000,000                 │
│ 3. Shipping Label A6   [Rp 67.5M](20%)    Outstanding:   Rp  22,500,000 [NOT DUE]       │
│                                            Payment Class: GOOD PAYER (0 Overdue)        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ RECOMMENDED NEXT ACTION                                                                 │
│ 💡 Cross-sell Opportunity: Pitch "Thank You Card Insert A6" (High affinity with Sticker)│
│ [BUTTON: Generate Pre-Filled Quotation Draft]  [BUTTON: Log Customer Outbound Contact]  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Module D: Sales Intelligence Dashboard

#### Module Objective
Equip Sales Managers and Sales Representatives with pipeline visibility, multi-stage conversion tracking, salesperson benchmarking, and high-value expired quotation recovery workflows.

#### Target User
Sales Manager, Sales Representatives, Commercial Operations.

#### Analytical Master Dataset Sources
* `05_quotation_funnel_master.csv` (`quotation_id`, `net_quotation_value`, `quotation_status`, `converted_flag`, `unconverted_quotation_value`, `sales_name`, `days_from_expiry`)
* `02_sales_transaction_extract.csv` (Converted invoice records)
* `01_customer_master_raw.csv` (Customer metadata)

#### Key Business Questions Answered
1. What is our overall quotation-to-sales conversion rate, and how much pipeline revenue drops at each funnel stage?
2. What is the total monetary value of expired, unconverted quotations, and who are the top assigned sales representatives?
3. Which sales representatives achieve the highest conversion efficiency and average deal size?
4. Which open quotations require urgent follow-up before expiring?

#### Insight Cards & Visualization Specifications

##### Card D1: Multi-Stage Quotation Conversion Funnel
* **Metric:** Stage Counts & Values across 4 Milestones:
  $$\text{Stage 1: Quotations Created} \longrightarrow \text{Stage 2: Sales Orders} \longrightarrow \text{Stage 3: Invoices Billed} \longrightarrow \text{Stage 4: Payment Allocated}$$
  $$\text{Quotation Conversion Rate} = \frac{\text{Count of Converted Quotations}}{\text{Total Quotation Cohort Count}} \times 100$$
* **Context:** Based strictly on quotation cohort creation date to ensure consistent denominator.
* **Insight:** Identifies structural leakage between quotation issuance and order confirmation.
* **Action:** Sales Manager: Investigate Stage 1 $\rightarrow$ Stage 2 drop-offs if conversion falls below 50%.
* **Visualization Type:** Horizontal Funnel Chart with Conversion Step Percentages and Value Totals.

##### Card D2: Expired & Lost Opportunity Pipeline Leaderboard
* **Metric:** Total Unconverted Quotation Value ($\sum \text{unconverted\_quotation\_value}$) where `quotation_status == 'Expired'`.
* **Context:** Grouped by Sales Representative (`sales_name`) and Customer (`customer_name`).
* **Insight:** Quantifies recoverable revenue lost to inactive quote management.
* **Action:** Mandate 7-day post-expiry call campaign for expired quotes worth $> \text{Rp 5M}$.
* **Visualization Type:** Bar Chart (Expired Value by Salesperson) + Actionable Quotations Detail Table.

##### Card D3: Sales Representative Efficiency Matrix
* **Metric:** Salesperson Net Sales, Quotation Volume, Deal Count, Win Rate (%), Average Deal Size (Rp).
* **Context:** Cross-comparison of sales team performance across branches.
* **Insight:** Differentiates high-volume/low-margin reps from high-conversion/high-value closers.
* **Action:** Pair low-conversion sales representatives with high-performing mentors for deal coaching.
* **Visualization Type:** Scatter Plot (X=Quotation Volume, Y=Win Rate %, Size=Net Sales Billed) + Data Table.

##### Card D4: Urgent Quotation Action Worklist
* **Metric:** Open Quotations (`conversion_status == 'Unconverted'`) where `days_from_expiry <= 3`.
* **Context:** Sorted by `net_quotation_value` descending.
* **Insight:** Prevents revenue loss by alerting reps to high-value quotes expiring within 72 hours.
* **Action:** Send automated push reminder to assigned salesperson's work queue.
* **Visualization Type:** Priority Worklist Table with Expiry Countdown Timers and Direct Action Trigger.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ MODULE D: SALES INTELLIGENCE DASHBOARD MOCKUP                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ MULTI-STAGE QUOTATION FUNNEL               EXPIRED QUOTATION RECOVERY LEADERBOARD       │
│ 1. Quotes Issued  : 7,300 (Rp 45.2B) [100%] Sales Rep       Expired Value   Quote Count │
│ 2. Sales Orders   : 4,818 (Rp 31.8B) [ 66%] 1. Budi Santoso   Rp 1,420,000,000   140      │
│ 3. Billed Invoices: 4,672 (Rp 30.5B) [ 64%] 2. Siti Rahma    Rp 1,150,000,000   112      │
│ 4. Payment Alloc. : 4,100 (Rp 26.2B) [ 56%] 3. Ahmad Dahlan  Rp   980,000,000    95      │
│ overall Win Rate  : 64.0%                  [ACTION: Trigger Expired Quote Follow-Up]   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ URGENT QUOTATION FOLLOW-UP WORKLIST (Expiring within 72 Hours)                          │
│ Quote Code   Customer Name           Value          Expiry Date  Assigned Rep    Action  │
│ QT-2026-0891 PT Indah Kertas         Rp 85,000,000  Tomorrow     Budi Santoso   [CALL]  │
│ QT-2026-0904 CV Prima Mandiri        Rp 42,000,000  2 Days Left  Siti Rahma     [CALL]  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Module E: Product Intelligence Dashboard

#### Module Objective
Provide Marketing and Sales teams with product performance metrics, revenue contribution vs. customer penetration matrices, co-purchase affinity patterns, and data-backed product bundling recommendations.

#### Target User
Marketing Manager, Product Category Lead, Commercial Strategy.

#### Analytical Master Dataset Sources
* `03_sales_item_extract.csv` (`product_id`, `product_name`, `product_category`, `qty`, `price`, `sales_amount`)
* `02_sales_transaction_extract.csv` (Transaction basket context)
* `01_customer_master_raw.csv` (Purchasing customer segment metadata)

#### Key Business Questions Answered
1. Which product categories (`product_category`: Large Format, Packaging, Sticker & Label, Digital Printing, Offset Printing, Merchandise) generate the highest sales volume and margin share?
2. Which products have high revenue contribution but low customer penetration across our active customer base?
3. What products are frequently co-purchased in the same transaction basket (Basket Affinity)?
4. Which evidence-backed product bundles should we introduce to increase wallet share?

#### Insight Cards & Visualization Specifications

##### Card E1: Category Revenue & Volume Mix
* **Metric:** Category Net Sales ($\sum \text{sales\_amount}$), Quantity Sold ($\sum \text{qty}$), Category Share (%).
* **Context:** Evaluated across the 6 master product categories.
* **Insight:** Identifies core revenue anchor categories vs. niche specialty categories.
* **Action:** Reallocate press capacity and material procurement based on category demand growth trends.
* **Visualization Type:** Donut Chart (Category Revenue Share) + Bar Chart (Quantity Units Sold).

##### Card E2: Revenue vs. Customer Penetration Opportunity Matrix
* **Metric:** Product Sales Volume (X-axis) vs. Customer Penetration Rate % (Y-axis).
  $$\text{Product Penetration Rate} = \frac{\text{Count of Unique Active Customers purchasing Product}}{\text{Total Unique Active Customers in Scope}} \times 100$$
* **Context:** High Revenue / Low Penetration products flagged as **Expansion Opportunities** (Threshold: Top 25% Revenue, $<20\%$ Penetration).
* **Insight:** Highlights star products bought repeatedly by a small subset of customers that can be scaled across the broader customer base.
* **Action:** Marketing: Create targeted product introduction campaigns focused on low-penetration star products.
* **Visualization Type:** 4-Quadrant Scatter Plot (Top-Right = Core Stars; Top-Left = Expansion Opportunities; Bottom-Right = Niche; Bottom-Left = Low Performers).

##### Card E3: Basket Co-Purchase Affinity Pairs (Market Basket Analysis)
* **Metric:** Co-purchase Count ($N_{AB}$), Support ($S_{AB}$), Confidence ($C_{A \rightarrow B}$), Lift ($L_{AB}$).
  $$\text{Support}(A, B) = \frac{N_{AB}}{N_{\text{Total Transactions}}}$$
  $$\text{Confidence}(A \rightarrow B) = \frac{N_{AB}}{N_A}$$
  $$\text{Lift}(A, B) = \frac{\text{Confidence}(A \rightarrow B)}{\text{Support}(B)} = \frac{N_{AB} \times N_{\text{Total}}}{N_A \times N_B}$$
* **Context:** Minimum evidence threshold: $N_{AB} \ge 10$ co-purchases, $\text{Lift} > 1.2$.
* **Insight:** Identifies statistically valid product pairs naturally bought together in single orders.
* **Action:** Sales Staff: When customer quotes Product A, automatically suggest Product B with a 5% bundle discount.
* **Visualization Type:** Co-purchase Network Graph or Matrix Data Table with Support/Confidence/Lift Badges.

##### Card E4: Evidence-Backed Bundle Recommendation Engine
* **Metric:** Recommended Bundle Candidates (e.g., *Packaging Box + Sticker Label + Insert Card*).
* **Context:** Cross-referenced against target segment purchasing propensity.
* **Insight:** Converts raw basket affinity metrics into packaged commercial offerings.
* **Action:** Marketing: Publish pre-configured bundle SKUs in Cetakia order entry system.
* **Visualization Type:** Product Bundle Action Cards with Historical Co-purchase Evidence & One-Click Campaign Launch.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ MODULE E: PRODUCT INTELLIGENCE DASHBOARD MOCKUP                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ REVENUE VS PENETRATION OPPORTUNITY MATRIX   BASKET CO-PURCHASE AFFINITY PAIRS           │
│ Penetration %                               Pair: Product A ──► Product B  Lift   Count │
│ 100%│ [Core Stars]                          1. Corrugated Box ➔ Sticker    3.42   142   │
│     │  * Packaging Box                      2. Acrylic Display➔ Poster     2.15    88   │
│  20%├───────────────┐                       3. Mug Print      ➔ Box Gift   1.85    64   │
│     │ [OPPORTUNITY] │                       [Evidence Threshold: Min 10 Orders, Lift >1.2]│
│   0%└───────────────┴────────────── Revenue ───────────────────────────────────────────┤
│      Low              High                                                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ RECOMMENDED COMMERCIAL BUNDLES                                                          │
│ 📦 "UMKM Packaging Bundle" : Custom Box (Packaging) + Roll Sticker (Sticker)            │
│    Co-purchase Evidence  : 142 Orders | Lift: 3.42 | Historical Conv: 78%               │
│    Target Eligible Audience: 320 UMKM Customers buying Box without Sticker.             │
│    [ACTION: Launch Bundle Campaign to Target Audience]                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Module F: Market Intelligence Dashboard

#### Module Objective
Provide executives and marketing strategist with macro market segmentation insights, customer cluster demographics, regional branch market share benchmarking, and customer acquisition channel dynamics.

#### Target User
Owner, Marketing Director, Business Development Lead.

#### Analytical Master Dataset Sources
* `01_customer_master_raw.csv` (`customer_category`, `division_name`, `cluster`, `prospect`, `inactive`, `customer_created_at`)
* `02_sales_transaction_extract.csv` (Segment revenue aggregation)
* `04_customer_intelligence_analysis.csv` (Segment health & LTV)

#### Key Business Questions Answered
1. What is the revenue and order volume breakdown across our primary customer categories (Industry, UMKM, Corporate, End User)?
2. How does customer acquisition velocity vary across regional branch territories?
3. Which customer clusters exhibit the highest growth potential and lifetime value?
4. What is our overall market penetration and prospect conversion rate by region?

#### Insight Cards & Visualization Specifications

##### Card F1: Market Segment Revenue & Share Contribution
* **Metric:** Total Net Sales, Customer Count, and Average LTV by `customer_category` (*INDUSTRY*, *UMKM*, *CORPORATE*, *END USER*).
* **Context:** Derived by joining customer master data with transaction ledgers.
* **Insight:** Evaluates reliance on industrial B2B clients versus retail UMKM clients.
* **Action:** If Corporate segment generates $>60\%$ of revenue but represents $<10\%$ of customer count, establish dedicated Key Account Management (KAM) team.
* **Visualization Type:** Treemap Chart (Box Area = Total Revenue, Color Intensity = Average LTV).

##### Card F2: Regional Branch Catchment Benchmarking
* **Metric:** Active Customer Penetration & Net Revenue by Regional Branch (`division_name`: Cipta Graha, Cipta Galuh, Cipta Cianjur).
* **Context:** Combined with prospect status (`prospect == True`).
* **Insight:** Identifies untapped regional growth opportunities and branch coverage gaps.
* **Action:** Direct regional marketing representatives to execute local prospect outreach in lagging branch territories.
* **Visualization Type:** Grouped Horizontal Bar Chart (Active Billed Customers vs. Unconverted Prospects).

##### Card F3: Customer Acquisition Velocity & Cohort Growth Trend
* **Metric:** Monthly New Customer Registration Count & First Purchase Conversion Rate.
* **Context:** Tracked over 12 calendar months (`customer_created_at` vs. `first_purchase_date`).
* **Insight:** Measures marketing acquisition efficiency and speed-to-first-order.
* **Action:** If speed-to-first-order exceeds 14 days, introduce first-order discount incentives for new registrants.
* **Visualization Type:** Dual-Axis Line Chart (Bar = Registrations, Line = % First Order Converted).

##### Card F4: Market Cluster Profiling & Spend Density
* **Metric:** Customer Count and Revenue Density grouped by `cluster` metadata.
* **Context:** Segmented by customer industry cluster classification.
* **Insight:** Reveals vertical market specialization (e.g., F&B Packaging, Pharmaceutical Labels, Retail Display).
* **Action:** Formulate specialized vertical product catalogs for high-density industry clusters.
* **Visualization Type:** Bubble Chart (X=Customer Count, Y=Total Revenue, Bubble Size=Average Order Value).

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ MODULE F: MARKET INTELLIGENCE DASHBOARD MOCKUP                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ MARKET SEGMENT REVENUE SHARE (TREEMAP)     REGIONAL BRANCH CATCHMENT                    │
│ ┌──────────────────────────┬───────────┐   Branch      Active Buyers  Unconverted Prosp │
│ │ CORPORATE                │ INDUSTRY  │   Cipta Graha  480 Buyers     120 Prospects    │
│ │ Rp 14.2 Billion (57%)    │ Rp 5.8B   │   Cipta Galuh  350 Buyers     210 Prospects ◄! │
│ ├──────────────────────────┼───────────┤   Cipta Cianjur 350 Buyers     180 Prospects    │
│ │ UMKM                     │ END USER  │   [ACTION: Deploy Local Lead Gen in Galuh]     │
│ │ Rp 3.2 Billion (13%)     │ Rp 1.65B  │                                                │
│ └──────────────────────────┴───────────┘                                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ CUSTOMER ACQUISITION VELOCITY & FIRST-PURCHASE CONVERSION                               │
│ Month    Registrations  First Purchases  Conversion Rate  Avg Speed to Purchase         │
│ Aug 2026   145           112              77.2%            4.2 Days                     │
│ Sep 2026   160           128              80.0%            3.8 Days                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Implementation & Data Lineage Architecture

### 5.1 Dataset Lineage Mapping

```
┌─────────────────────────────────────────┐
│         OPERATIONAL CSV MASTER          │
├─────────────────────────────────────────┤
│ 01_customer_master_raw.csv              │──┐
│ 02_sales_transaction_extract.csv        │──┼──┐
│ 03_sales_item_extract.csv               │──┤  │
│ 04_customer_intelligence_analysis.csv   │──┤  │
│ 05_quotation_funnel_master.csv          │──┘  │
└─────────────────────────────────────────┘     │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CETAKIA BI ANALYTICAL ENGINE                               │
│  - Normalizes timestamps to Asia/Jakarta timezone.                                     │
│  - Calculates deterministic RFM Scores & Health Rules.                                  │
│  - Computes Co-purchase Support, Confidence, and Lift.                                  │
│  - Enforces consistent cutoff date (as_of_date = 2026-09-19).                          │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            UNIFIED BI REST API LAYER (/api/bi)                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ GET /api/bi/dashboard-summary ──────► Powers Module A (Executive Dashboard)            │
│ GET /api/bi/customers/health  ──────► Powers Module B (Customer Intelligence)           │
│ GET /api/bi/customer/{id}     ──────► Powers Module C (Customer 360 Profile)            │
│ GET /api/bi/sales/funnel      ──────► Powers Module D (Sales Intelligence)              │
│ GET /api/bi/products/pairs    ──────► Powers Module E (Product Intelligence)            │
│ GET /api/bi/customers/segments ─────► Powers Module F (Market Intelligence)             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Mandatory UI Presentation Rules

1. **Numeric & Currency Formatting:** All monetary values must be rendered in Indonesian Rupiah (IDR) using standard Indonesian locale formatting (e.g., `Rp 24.850.000.000`), rounded to zero decimals for presentation.
2. **Date Boundaries & Partial Periods:** Whenever displaying monthly or partial-period data (such as September 2026 up to snapshot date 19 September 2026), UI components **MUST** render an explicit badge: `[PARTIAL PERIOD - 19 DAYS OBSERVED]` to prevent false YoY/MoM churn interpretation.
3. **Empty States & Zero Denominators:** If a calculated metric has a zero denominator (e.g., conversion rate when 0 quotes exist), the UI must display `N/A` or `Belum Ada Data` rather than `0%`, `NaN`, or `Infinity`.
4. **Color Semantics:** Status colors must remain strictly consistent across all 6 modules:
   - **Healthy / Good Payer / Converted:** `#10B981` (Emerald Green)
   - **Active / Average Payer / Open Quote:** `#3B82F6` (Royal Blue)
   - **At Risk / Expiring Soon / 1-30 Days Overdue:** `#F59E0B` (Amber Yellow)
   - **Dormant / Risk Payer / Expired Quote / >30 Days Overdue:** `#EF4444` (Crimson Red)

---

## 6. Document Sign-Off & Verification Gate

This document serves as the official functional and visualization baseline for Cetakia BI V1. Any subsequent feature modifications or metric additions must be reviewed against this specification.

| Stakeholder Role | Review Responsibility | Sign-Off Status |
| :--- | :--- | :--- |
| **Business Owner / Executive** | Alignment on vision, executive KPIs, and decision workflow philosophy | **APPROVED** |
| **Sales Manager** | Verification of quotation funnel stages, expired quote recovery, and sales rep KPIs | **APPROVED** |
| **Customer Service Manager** | Validation of customer health rules, churn thresholds, and Customer 360 details | **APPROVED** |
| **Marketing Manager** | Confirmation of customer segmentation, product penetration, and bundling logic | **APPROVED** |
| **BI Architect & Tech Lead** | Technical feasibility, dataset mapping, REST API contract alignment | **APPROVED** |
