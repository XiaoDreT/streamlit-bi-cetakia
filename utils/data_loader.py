import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR_SEARCH_PATHS = [
    os.path.join(BASE_DIR, 'data'),
    os.path.join(BASE_DIR, 'docs'),
    os.path.join(BASE_DIR, 'docs', 'EDA Dataset Summary'),
    '/home/zen/Documents/Cetakia/Master Data Cetakia',
    os.path.join(BASE_DIR, '..', 'Master Data Cetakia'),
    './data',
    './docs',
    './docs/EDA Dataset Summary',
    '../Master Data Cetakia',
    './Master Data Cetakia'
]

def resolve_data_path(filename: str) -> str:
    """Locates dataset file across predefined search paths, supporting .csv and .csv.gz."""
    for directory in DATA_DIR_SEARCH_PATHS:
        candidate = os.path.join(directory, filename)
        if os.path.exists(candidate):
            return candidate
        if not candidate.endswith('.gz'):
            candidate_gz = candidate + '.gz'
            if os.path.exists(candidate_gz):
                return candidate_gz
    raise FileNotFoundError(f"Dataset file '{filename}' not found in any search path: {DATA_DIR_SEARCH_PATHS}")

def normalize_date_column(series: pd.Series) -> pd.Series:
    """Parses datetime strings and strips timezones to prevent comparison errors."""
    dt_series = pd.to_datetime(series, format='mixed', errors='coerce')
    if hasattr(dt_series.dt, 'tz') and dt_series.dt.tz is not None:
        dt_series = dt_series.dt.tz_localize(None)
    return dt_series

@st.cache_data(show_spinner=False)
def load_customer_data() -> pd.DataFrame:
    """Loads the latest customer master dataset (data_customer.csv / customer_data.csv up to 12 Nov 2026)
    enriched with contact fields from 01_customer_master_raw.csv for backwards compatibility across all dashboards."""
    try:
        df_latest = load_new_customer_master().copy()
        if 'is_deleted_customer' in df_latest.columns:
            df_latest = df_latest[~df_latest['is_deleted_customer']].copy()
        df_latest['customer_category'] = df_latest['category_name']

        # Enrich with contact details (phone, email, address_ship, address_bill, contact_name, cluster) from 01_customer_master_raw.csv
        try:
            raw_path = resolve_data_path('01_customer_master_raw.csv')
            df_raw = pd.read_csv(raw_path, low_memory=False)
            extra_cols = [c for c in ['customer_id', 'contact_name', 'phone', 'email', 'address_ship', 'address_bill', 'cluster', 'customer_updated_at'] if c in df_raw.columns]
            df_raw_sub = df_raw[extra_cols].drop_duplicates(subset=['customer_id'])
            df_latest = df_latest.merge(df_raw_sub, on='customer_id', how='left')
            if 'customer_updated_at' in df_latest.columns:
                df_latest['customer_updated_at'] = normalize_date_column(df_latest['customer_updated_at'])
        except Exception:
            pass
        return df_latest
    except Exception:
        path = resolve_data_path('01_customer_master_raw.csv')
        df = pd.read_csv(path, low_memory=False)
        for date_col in ['customer_created_at', 'customer_updated_at']:
            if date_col in df.columns:
                df[date_col] = normalize_date_column(df[date_col])
        if 'customer_category' in df.columns:
            df = df[df['customer_category'].astype(str).str.strip().str.upper() != 'DIVISI'].copy()
        return df

load_customer_master = load_customer_data

@st.cache_data(show_spinner=False)
def load_sales_data(include_cancelled: bool = False) -> pd.DataFrame:
    """Loads 02_sales_transaction_extract.csv with normalized datetime types.
    By default (include_cancelled=False), filters out invoices with status 'cancel'
    so that revenue, order counts, and customer leaderboards reflect confirmed transactions.
    """
    path = resolve_data_path('02_sales_transaction_extract.csv')
    df = pd.read_csv(path)
    for date_col in ['invoice_date', 'created_at', 'updated_at']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])
    if not include_cancelled and 'invoice_status' in df.columns:
        df = df[df['invoice_status'].astype(str).str.lower() != 'cancel']
    return df

@st.cache_data(show_spinner=False)
def load_product_data(include_cancelled: bool = False) -> pd.DataFrame:
    """Loads 03_sales_item_extract.csv with normalized datetime types.
    By default (include_cancelled=False), filters out items with status 'cancel'
    so that product sales amount and quantities reflect confirmed transactions.
    """
    path = resolve_data_path('03_sales_item_extract.csv')
    df = pd.read_csv(path)
    for date_col in ['invoice_date', 'item_created_at']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])
    if not include_cancelled and 'invoice_status' in df.columns:
        df = df[df['invoice_status'].astype(str).str.lower() != 'cancel']
    return df

@st.cache_data(show_spinner=False)
def load_customer_intelligence() -> pd.DataFrame:
    """Loads 04_customer_intelligence_analysis.csv, synchronizes customer master population
    with the latest customer dataset (data_customer.csv up to 12 Nov 2026), and reconciles
    customer lifetime spend, order count, and health with confirmed non-cancelled sales transactions.
    """
    path = resolve_data_path('04_customer_intelligence_analysis.csv')
    df = pd.read_csv(path, low_memory=False)
    for date_col in ['first_purchase_date', 'last_purchase_date']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])

    # Synchronize with latest master customer dataset (12 Nov 2026) so newly registered customers are included
    try:
        df_master = load_customer_data()
        master_cols = ['customer_id', 'customer_code', 'customer_name', 'customer_category', 'division_code', 'division_name']
        avail_master_cols = [c for c in master_cols if c in df_master.columns]
        df_master_sub = df_master[avail_master_cols].drop_duplicates(subset=['customer_id'])

        # Filter df to valid non-deleted master customers and update latest metadata
        valid_ids = set(df_master_sub['customer_id'])
        df = df[df['customer_id'].isin(valid_ids)].copy()

        # Update metadata columns from latest master data
        meta_update = df_master_sub.set_index('customer_id')
        for col in ['customer_code', 'customer_name', 'customer_category', 'division_code', 'division_name']:
            if col in meta_update.columns:
                df[col] = df['customer_id'].map(meta_update[col]).fillna(df.get(col))

        # Append new customers from latest master data not yet in 04_customer_intelligence_analysis.csv
        existing_ids = set(df['customer_id'])
        new_cust_df = df_master_sub[~df_master_sub['customer_id'].isin(existing_ids)].copy()
        if not new_cust_df.empty:
            new_cust_df['total_orders'] = 0
            new_cust_df['first_purchase_date'] = pd.NaT
            new_cust_df['last_purchase_date'] = pd.NaT
            new_cust_df['lifetime_sales'] = 0.0
            new_cust_df['average_order_value'] = 0.0
            new_cust_df['total_discount'] = 0.0
            new_cust_df['lifetime_invoice_value'] = 0.0
            new_cust_df['active_purchase_month'] = 0
            new_cust_df['days_since_last_purchase'] = float('nan')
            new_cust_df['repeat_flag'] = 'One Time Customer'
            new_cust_df['customer_health'] = 'New'
            new_cust_df['R_score'] = float('nan')
            new_cust_df['F_score'] = 1
            new_cust_df['M_score'] = float('nan')
            new_cust_df['RFM_score'] = 'nan1nan'
            new_cust_df['rfm_segment'] = 'Low Engagement'
            df = pd.concat([df, new_cust_df], ignore_index=True)
    except Exception:
        pass

    # Reconcile with confirmed non-cancelled sales to ensure cancelled invoices are not counted as revenue
    try:
        sales_path = resolve_data_path('02_sales_transaction_extract.csv')
        sales = pd.read_csv(sales_path)
        valid_sales = sales[sales['invoice_status'].astype(str).str.lower() != 'cancel']
        valid_agg = valid_sales.groupby('customer_id').agg(
            _actual_orders=('invoice_id', 'nunique'),
            _actual_ltv=('net_sales', 'sum')
        ).reset_index()

        df = df.merge(valid_agg, on='customer_id', how='left')

        # Customers with valid confirmed sales: update metrics
        valid_mask = df['_actual_orders'].notnull() & (df['_actual_orders'] > 0)
        df.loc[valid_mask, 'lifetime_sales'] = df.loc[valid_mask, '_actual_ltv']
        df.loc[valid_mask, 'total_orders'] = df.loc[valid_mask, '_actual_orders']
        df.loc[valid_mask, 'average_order_value'] = df.loc[valid_mask, '_actual_ltv'] / df.loc[valid_mask, '_actual_orders']

        # Cancel-only or 0-order customers: reset to 0 and reclassify health as 'New'
        cancel_only_mask = df['_actual_orders'].isna() | (df['_actual_orders'] == 0)
        df.loc[cancel_only_mask, 'lifetime_sales'] = 0.0
        df.loc[cancel_only_mask, 'total_orders'] = 0
        df.loc[cancel_only_mask, 'average_order_value'] = 0.0
        df.loc[cancel_only_mask, 'customer_health'] = 'New'

        df.drop(columns=['_actual_orders', '_actual_ltv'], inplace=True)
    except Exception:
        pass

    return df

@st.cache_data(show_spinner=False)
def load_quotation_data() -> pd.DataFrame:
    """Loads 05_quotation_funnel_master.csv with normalized datetime types."""
    path = resolve_data_path('05_quotation_funnel_master.csv')
    df = pd.read_csv(path)
    for date_col in ['quotation_date', 'quotation_expired', 'quotation_created_at', 'quotation_updated_at']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])
    return df

@st.cache_data(show_spinner=False)
def load_finance_data(include_internal: bool = True) -> pd.DataFrame:
    """Loads 06_collection_payment_analysis.csv with normalized datetime and numeric types.
    Optionally filters out internal division transactions if include_internal=False.
    """
    path = resolve_data_path('06_collection_payment_analysis.csv')
    df = pd.read_csv(path, low_memory=False)
    for date_col in ['invoice_date', 'due_date', 'first_payment_date', 'last_payment_date']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])
    
    # Ensure numeric columns are properly typed
    numeric_cols = [
        'invoice_sub_total', 'invoice_discount_amount', 'invoice_tax_amount', 'invoice_amount',
        'invoice_amount_clean', 'paid_raw_clean', 'settled_amount_eda', 'outstanding_eda',
        'overdue_outstanding_eda', 'days_overdue_current', 'collection_rate_pct_receipt_basis'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    if not include_internal and 'market_scope' in df.columns:
        df = df[df['market_scope'] != 'Internal Division']
    return df

@st.cache_data(show_spinner=False)
def load_customer_payment_behavior() -> pd.DataFrame:
    """Loads 06_customer_payment_behavior_summary_readable.csv."""
    path = resolve_data_path('06_customer_payment_behavior_summary_readable.csv')
    df = pd.read_csv(path, low_memory=False)
    numeric_cols = [
        'total_invoices', 'billed_amount', 'settled_amount', 'paid_raw_amount',
        'outstanding_amount', 'overdue_outstanding', 'overdue_invoice_count',
        'fully_paid_invoices', 'late_paid_invoices', 'max_days_overdue',
        'collection_rate_pct', 'overdue_ratio_pct'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

@st.cache_data(show_spinner=False)
def load_collection_data_quality_exceptions() -> pd.DataFrame:
    """Loads 06_collection_data_quality_exceptions.csv."""
    path = resolve_data_path('06_collection_data_quality_exceptions.csv')
    df = pd.read_csv(path, low_memory=False)
    for date_col in ['invoice_date', 'due_date', 'first_payment_date', 'last_payment_date']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])
    return df

@st.cache_data(show_spinner=False)
def load_aging_receivable_summary() -> pd.DataFrame:
    """Loads 06_aging_receivable_summary.csv."""
    path = resolve_data_path('06_aging_receivable_summary.csv')
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_finance_market_scope_summary() -> pd.DataFrame:
    """Loads 06_finance_market_scope_summary.csv."""
    path = resolve_data_path('06_finance_market_scope_summary.csv')
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_finance_segment_summary() -> pd.DataFrame:
    """Loads 06_finance_segment_summary.csv."""
    path = resolve_data_path('06_finance_segment_summary.csv')
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_finance_division_summary() -> pd.DataFrame:
    """Loads 06_finance_division_summary.csv."""
    path = resolve_data_path('06_finance_division_summary.csv')
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_payment_method_summary() -> pd.DataFrame:
    """Loads 06_payment_method_frequency_summary.csv."""
    path = resolve_data_path('06_payment_method_frequency_summary.csv')
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_finance_cohort_summary() -> pd.DataFrame:
    """Loads 06_invoice_cohort_collection_summary.csv."""
    path = resolve_data_path('06_invoice_cohort_collection_summary.csv')
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_new_customer_master() -> pd.DataFrame:
    """Loads and standardizes master customer dataset for New Customer & Customer Growth Dashboards.
    Prioritizes data/data_customer.csv (and data/new_customer_eda.csv).
    Falls back to 01_customer_master_raw.csv if not found.
    Applies Cetakia Business Rule: new_customer_valid_date = registration_date + 2 days.
    """
    path = None
    for candidate_name in ['data_customer.csv', 'customer_data.csv', 'new_customer_eda.csv', '01_customer_master_raw.csv']:
        try:
            path = resolve_data_path(candidate_name)
            break
        except Exception:
            continue
    if path is None:
        raise FileNotFoundError("Could not locate data_customer.csv, customer_data.csv, new_customer_eda.csv, or 01_customer_master_raw.csv")

    df = pd.read_csv(path, low_memory=False)

    # Normalize datetime columns
    if 'created_at_jakarta' in df.columns:
        df['customer_created_at'] = normalize_date_column(df['created_at_jakarta'])
    elif 'customer_created_at' in df.columns:
        df['customer_created_at'] = normalize_date_column(df['customer_created_at'])
    elif 'created_at' in df.columns:
        df['customer_created_at'] = normalize_date_column(df['created_at'])

    if 'customer_updated_at' in df.columns:
        df['customer_updated_at'] = normalize_date_column(df['customer_updated_at'])

    # Cetakia Business Rule: Valid date = registration_date + 2 days
    if 'registration_date' in df.columns and 'new_customer_valid_date' in df.columns:
        df['registration_date'] = pd.to_datetime(df['registration_date']).dt.date
        df['new_customer_valid_date'] = pd.to_datetime(df['new_customer_valid_date']).dt.date
    else:
        reg_dt = df['customer_created_at'].dt.date
        valid_dt = reg_dt + pd.Timedelta(days=2)
        df['registration_date'] = reg_dt
        df['new_customer_valid_date'] = valid_dt

    reg_dt = df['registration_date']
    df['created_at'] = df['customer_created_at']
    df['created_at_jakarta'] = df['customer_created_at']

    # Calendar hierarchy
    df['registration_year'] = pd.to_datetime(reg_dt).dt.year
    df['registration_month_number'] = pd.to_datetime(reg_dt).dt.month
    df['registration_year_month'] = pd.to_datetime(reg_dt).dt.strftime('%Y-%m')
    df['registration_month_start'] = pd.to_datetime(reg_dt).dt.to_period('M').dt.to_timestamp().dt.date
    df['registration_week_start'] = (pd.to_datetime(reg_dt) - pd.to_timedelta(pd.to_datetime(reg_dt).dt.weekday, unit='D')).dt.date

    # Category standardization
    if 'category_name' in df.columns:
        df['category_name'] = df['category_name'].fillna('Uncategorized').astype(str).str.strip().str.upper()
    elif 'customer_category' in df.columns:
        df['category_name'] = df['customer_category'].fillna('Uncategorized').astype(str).str.strip().str.upper()
    else:
        df['category_name'] = 'UNCATEGORIZED'

    if 'category_code' in df.columns:
        df['category_code'] = df['category_code'].fillna('UNCAT').astype(str).str.strip().str.upper()
    else:
        df['category_code'] = df['category_name']

    # Exclude internal company division accounts ('DIVISI') so customer analytics focus strictly on external customers
    df = df[df['category_name'].astype(str).str.upper() != 'DIVISI'].copy()

    # Division standardization
    df['division_name'] = df['division_name'].fillna('Unknown Division').astype(str).str.strip()
    df['division_code'] = df['division_code'].fillna('UNK').astype(str).str.strip().str.upper() if 'division_code' in df.columns else 'UNK'
    df['division_id'] = df['division_id'].astype(str) if 'division_id' in df.columns else '0'
    df['customer_category_id'] = df['category_code'] + '_' + df['division_code']

    # Safe boolean parsing helper
    def _to_bool(series: pd.Series) -> pd.Series:
        if series.dtype == bool:
            return series.fillna(False)
        return series.fillna(False).astype(str).str.strip().str.lower().isin(['true', '1', 'yes', 'y', 't'])

    # Status & Flags
    df['prospect'] = _to_bool(df['prospect']) if 'prospect' in df.columns else False
    df['inactive'] = _to_bool(df['inactive']) if 'inactive' in df.columns else False
    df['is_deleted_customer'] = _to_bool(df['is_deleted_customer']) if 'is_deleted_customer' in df.columns else False

    if 'customer_deleted_at' not in df.columns:
        df['customer_deleted_at'] = None
        df['deleted_date'] = None
    else:
        del_dt = normalize_date_column(df['customer_deleted_at'])
        df['deleted_date'] = del_dt.dt.date

    # Churn / Berhenti tracking (Deleted or Inactive)
    df['is_churned'] = df['is_deleted_customer'] | df['inactive']
    # If churned via deletion, use deleted_date; if churned via inactive without deleted_date, use registration_date
    df['churn_date'] = df['deleted_date'].where(df['deleted_date'].notna(), df['registration_date'].where(df['inactive'], None))

    # Flag initial system migration baseline (Jan 5-8, 2026 bulk import of existing customer database)
    df['is_initial_baseline'] = df['registration_date'] <= pd.to_datetime('2026-01-08').date()

    df['company_id'] = df['company_id'].fillna('CG-001') if 'company_id' in df.columns else 'CG-001'
    if 'data_quality_status' not in df.columns:
        df['data_quality_status'] = 'OK'
    df['category_division_match'] = True

    return df

@st.cache_data(show_spinner=False)
def load_customer_growth_data() -> pd.DataFrame:
    """Loads data/data_customer.csv specifically for the Customer Growth Orientation Dashboard."""
    return load_new_customer_master()

