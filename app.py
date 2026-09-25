import streamlit as st

st.set_page_config(
    page_title="Insight Catalog — Cetakia BI DSS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Centralized Multi-Page Navigation Structure (Streamlit Native DSS Routing)
pages = [
    st.Page("views/0_Insight_Catalog.py", title="Insight Catalog", icon="📊", url_path="Insight_Catalog", default=True),
    st.Page("views/1_Executive_Dashboard.py", title="Executive Dashboard", icon="📈", url_path="Executive_Dashboard"),
    st.Page("views/2_Customer_Intelligence.py", title="Customer Intelligence", icon="👥", url_path="Customer_Intelligence"),
    st.Page("views/3_Customer_360.py", title="Customer 360", icon="👤", url_path="Customer_360"),
    st.Page("views/4_Sales_Intelligence.py", title="Sales Intelligence", icon="🎯", url_path="Sales_Intelligence"),
    st.Page("views/5_Product_Intelligence.py", title="Product Intelligence", icon="📦", url_path="Product_Intelligence"),
    st.Page("views/6_Market_Intelligence.py", title="Market Intelligence", icon="🌐", url_path="Market_Intelligence"),
]

pg = st.navigation(pages)
pg.run()
