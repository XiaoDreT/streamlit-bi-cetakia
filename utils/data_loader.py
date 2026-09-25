import os
import pandas as pd
import streamlit as st

DATA_DIR_SEARCH_PATHS = [
    '/home/zen/Documents/Cetakia/Master Data Cetakia',
    '../Master Data Cetakia',
    './Master Data Cetakia',
    './data',
    './docs'
]

def resolve_data_path(filename: str) -> str:
    """Locates dataset file across predefined search paths."""
    for directory in DATA_DIR_SEARCH_PATHS:
        candidate = os.path.join(directory, filename)
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"Dataset file '{filename}' not found in any search path: {DATA_DIR_SEARCH_PATHS}")

def normalize_date_column(series: pd.Series) -> pd.Series:
    """Parses datetime strings and strips timezones to prevent comparison errors."""
    dt_series = pd.to_datetime(series, errors='coerce')
    if hasattr(dt_series.dt, 'tz') and dt_series.dt.tz is not None:
        dt_series = dt_series.dt.tz_localize(None)
    return dt_series

@st.cache_data(show_spinner=False)
def load_customer_data() -> pd.DataFrame:
    """Loads 01_customer_master_raw.csv with normalized datetime types."""
    path = resolve_data_path('01_customer_master_raw.csv')
    df = pd.read_csv(path)
    for date_col in ['customer_created_at', 'customer_updated_at']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])
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
    """Loads 04_customer_intelligence_analysis.csv with normalized datetime types
    and reconciles customer lifetime spend, order count, and health with confirmed
    non-cancelled sales transactions from 02_sales_transaction_extract.csv.
    """
    path = resolve_data_path('04_customer_intelligence_analysis.csv')
    df = pd.read_csv(path)
    for date_col in ['first_purchase_date', 'last_purchase_date']:
        if date_col in df.columns:
            df[date_col] = normalize_date_column(df[date_col])

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

        # Cancel-only customers: reset to 0 and reclassify health as 'New'
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
