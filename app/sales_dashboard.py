import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
# Set page config
st.set_page_config(
    page_title="Sales Performance Dashboard",  # <-- Custom browser tab title
    page_icon="📊",                            # <-- Emoji or path to custom icon
    layout="wide",                             # 'wide' or 'centered'
    initial_sidebar_state="expanded",          # or "collapsed"
)

st.title("📊 Sales Performance Dashboard")

# --- Load Data ---
df = pd.read_csv("Cleaned_Superstore.csv", parse_dates=['Order Date', 'Ship Date'])

# --- Preprocess ---
df['Month'] = df['Order Date'].dt.to_period('M').astype(str)
df['Year'] = df['Order Date'].dt.year

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter the Data")
selected_year = st.sidebar.multiselect("Select Year", options=sorted(df['Year'].unique()), default=sorted(df['Year'].unique()))
selected_segment = st.sidebar.multiselect("Select Segment", options=df['Segment'].unique(), default=df['Segment'].unique())
selected_region = st.sidebar.multiselect("Select Region", options=df['Region'].unique(), default=df['Region'].unique())
selected_category = st.sidebar.multiselect("Select Category", options=df['Category'].unique(), default=df['Category'].unique())

filtered_df = df[
    (df['Year'].isin(selected_year)) &
    (df['Segment'].isin(selected_segment)) &
    (df['Region'].isin(selected_region)) &
    (df['Category'].isin(selected_category))
]

# --- Title ---
st.title("📊 Superstore Sales Performance Dashboard")
st.markdown("This dashboard gives insights into sales, profit, and product performance across multiple regions and categories.")

# --- KPIs ---
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_discount = filtered_df['Discount'].mean() * 100
avg_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"₹{total_sales:,.0f}")
col2.metric("📈 Total Profit", f"₹{total_profit:,.0f}")
col3.metric("🔻 Avg Discount", f"{avg_discount:.2f}%")
col4.metric("💹 Profit Margin", f"{avg_margin:.2f}%")

st.markdown("---")

# --- Visualizations ---

# 1. Monthly Sales Trend
monthly_sales = filtered_df.groupby('Month')['Sales'].sum().sort_index()
fig1 = px.line(monthly_sales, x=monthly_sales.index, y=monthly_sales.values,
               title="📅 Monthly Sales Trend", markers=True,
               labels={"x": "Month", "y": "Sales"})
st.plotly_chart(fig1, use_container_width=True)

# 2. Profit by Sub-Category
subcat_profit = filtered_df.groupby('Sub-Category')['Profit'].sum().sort_values()
fig2 = px.bar(subcat_profit, x=subcat_profit.index, y=subcat_profit.values,
              title="📦 Profit by Sub-Category",
              labels={"x": "Sub-Category", "y": "Profit"})
st.plotly_chart(fig2, use_container_width=True)

# 3. Category Distribution (Pie Chart)
cat_sales = filtered_df.groupby('Category')['Sales'].sum()
fig3 = px.pie(values=cat_sales.values, names=cat_sales.index, title="🧩 Sales Distribution by Category")
st.plotly_chart(fig3, use_container_width=True)

# 4. Sales by Region (Bar)
region_sales = filtered_df.groupby('Region')['Sales'].sum().sort_values()
fig4 = px.bar(region_sales, x=region_sales.index, y=region_sales.values,
              title="🌍 Sales by Region",
              labels={"x": "Region", "y": "Sales"})
st.plotly_chart(fig4, use_container_width=True)

# 5. Discount vs Profit (Scatter)
fig5 = px.scatter(filtered_df, x='Discount', y='Profit', color='Category',
                  title="💸 Discount vs Profit", size='Sales',
                  hover_data=['Product Name', 'Sub-Category'])
st.plotly_chart(fig5, use_container_width=True)

# 6. Top Products
top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
fig6 = px.bar(top_products, x=top_products.values, y=top_products.index,
              orientation='h', title="🏆 Top 10 Products by Sales",
              labels={"x": "Sales", "y": "Product Name"})
st.plotly_chart(fig6, use_container_width=True)

# 7. Optional: Map View (if you want to extend)
# Requires mapping States to coordinates or using custom GeoJSON

# --- Footer ---

with st.expander("🔍 Business Insights"):
    st.subheader("📌 Key Findings")

    st.markdown("""
    - ✅ **South Region** has the **highest profit margin** — a strategic area to expand.
    - ⚠️ **Office Supplies** category gives **low profit despite high discounts** — pricing or supplier strategy needs review.
    - 🗓️ **Q4 (Oct–Dec)** has **peak sales** — allocate marketing budget and inventory accordingly.
    - 🏆 Top 5 products contribute disproportionately to total sales — consider bundling or promoting these.
    """)
# --- Optional: Sales Forecast using Prophet ---
from prophet import Prophet
import plotly.graph_objs as go

with st.expander("📈 Sales Forecast (Next 3 Months)"):
    st.subheader("🔮 Predictive Sales Forecast")

    # Prepare monthly sales data
    monthly_df = filtered_df.groupby('Order Date')['Sales'].sum().resample('M').sum().reset_index()
    monthly_df.columns = ['ds', 'y']

    # Fit Prophet model
    m = Prophet()
    m.fit(monthly_df)

    # Create future dataframe and forecast
    future = m.make_future_dataframe(periods=3, freq='M')
    forecast = m.predict(future)

    # Plot actual vs forecast
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=monthly_df['ds'], y=monthly_df['y'],
        mode='lines+markers', name="Actual Sales", line=dict(color='blue')
    ))
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines', name="Forecast", line=dict(color='orange', dash='dash')
    ))
    fig_forecast.update_layout(
        title="📊 Forecasted Monthly Sales",
        xaxis_title="Date", yaxis_title="Sales",
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(x=0, y=1.1, orientation="h")
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Show next month's forecast (optional)
    next_month_pred = forecast[forecast['ds'] > monthly_df['ds'].max()]['yhat'].iloc[0]
    st.metric("📅 Forecast for Next Month", f"₹{next_month_pred:,.0f}")

st.caption("📍 Built with ❤️ by Sai Kiran using Streamlit | Powered by Python and Plotly")

