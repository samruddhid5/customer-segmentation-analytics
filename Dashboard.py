import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- Data Loading: Fetch from API instead of CSV ---
api_url = "http://127.0.0.1:5000/api/transactions"  # Use your actual endpoint

try:
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Error fetching data from API: {e}")
    df = pd.read_csv('synthetic_transactions.csv')

# Convert transaction_date column to datetime if it exists
if 'transaction_date' in df.columns:
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

# Sidebar: Global Filters
st.sidebar.header("Global Filters")

# Filter by product category if available
if 'product_category' in df.columns:
    categories = df['product_category'].unique().tolist()
    selected_categories = st.sidebar.multiselect("Product Categories", options=categories, default=categories)
    df = df[df['product_category'].isin(selected_categories)]

# Filter by payment method if available
if 'payment_method' in df.columns:
    payment_methods = df['payment_method'].unique().tolist()
    selected_payments = st.sidebar.multiselect("Payment Methods", options=payment_methods, default=payment_methods)
    df = df[df['payment_method'].isin(selected_payments)]

# Filter by date range if available
if 'transaction_date' in df.columns:
    min_date = df['transaction_date'].min().date()
    max_date = df['transaction_date'].max().date()
    selected_date = st.sidebar.date_input("Date Range", [min_date, max_date])
    df = df[(df['transaction_date'] >= pd.to_datetime(selected_date[0])) &
            (df['transaction_date'] <= pd.to_datetime(selected_date[1]))]

# Define tabs for different sections of the dashboard
tabs = st.tabs(["Overview & KPIs", "Trends", "Clustering", "Customer History"])

# --------------------------
# Tab 1: Overview & KPIs
# --------------------------
with tabs[0]:
    st.header("Overview & Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", f"{df.shape[0]}")
    with col2:
        total_revenue = df['transaction_amount'].sum() if 'transaction_amount' in df.columns else 0
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col3:
        avg_trans = df['transaction_amount'].mean() if 'transaction_amount' in df.columns else 0
        st.metric("Average Transaction", f"${avg_trans:,.2f}")
    with col4:
        unique_customers = df['customer_id'].nunique() if 'customer_id' in df.columns else 0
        st.metric("Unique Customers", f"{unique_customers}")

    st.write("### Transaction Amount Distribution")
    if 'transaction_amount' in df.columns:
        fig_hist = px.histogram(df, x="transaction_amount", nbins=50, title="Transaction Amount Distribution")
        st.plotly_chart(fig_hist)

# --------------------------
# Tab 2: Trends
# --------------------------
with tabs[1]:
    st.header("Trends Analysis")
    if 'transaction_date' in df.columns and 'transaction_amount' in df.columns:
        # Monthly Trend
        df_monthly = df.groupby(df['transaction_date'].dt.to_period("M")).agg({"transaction_amount": "sum"}).reset_index()
        df_monthly['transaction_date'] = df_monthly['transaction_date'].dt.to_timestamp()
        fig_line = px.line(df_monthly, x="transaction_date", y="transaction_amount", title="Monthly Revenue Trend")
        st.plotly_chart(fig_line)

        # Weekly Trend (Optional)
        df_weekly = df.groupby(df['transaction_date'].dt.to_period("W")).agg({"transaction_amount": "sum"}).reset_index()
        df_weekly['transaction_date'] = df_weekly['transaction_date'].dt.to_timestamp()
        fig_weekly = px.line(df_weekly, x="transaction_date", y="transaction_amount", title="Weekly Revenue Trend")
        st.plotly_chart(fig_weekly)
    else:
        st.write("Trend data is not available.")

# --------------------------
# Tab 3: Clustering Insights
# --------------------------
with tabs[2]:
    st.header("Clustering Insights")
    if 'transaction_amount' in df.columns and 'quantity' in df.columns:
        features = df[['transaction_amount', 'quantity']]
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        kmeans = KMeans(n_clusters=4, random_state=42)
        df['cluster'] = kmeans.fit_predict(features_scaled)

        fig_cluster = px.scatter(
            df,
            x='transaction_amount',
            y='quantity',
            color='cluster',
            hover_data=['customer_id', 'product_category', 'payment_method'],
            title="Clusters by Transaction Amount and Quantity"
        )
        st.plotly_chart(fig_cluster)
    else:
        st.write("Clustering cannot be performed due to missing data.")

# --------------------------
# Tab 4: Customer History
# --------------------------
with tabs[3]:
    st.header("Customer Transaction History")
    if 'customer_id' in df.columns:
        customer_ids = df['customer_id'].unique().tolist()
        selected_customer = st.selectbox("Select a Customer ID", customer_ids)
        customer_history = df[df['customer_id'] == selected_customer].sort_values(by='transaction_date')
        with st.expander("View Transaction Details"):
            st.write(customer_history[['transaction_date', 'transaction_amount', 'quantity', 
                                         'product_category', 'payment_method', 'purchase_channel']])
    else:
        st.write("No customer transaction history available.")

# --------------------------
# Additional: Data Overview
# --------------------------
st.header("Data Overview")
st.write(df.describe())
