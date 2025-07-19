import streamlit as st
import pandas as pd
import plotly.express as px

# Load cleaned data
df = pd.read_csv("Cleaned_Superstore.csv", parse_dates=['Order Date'])

# Add Month column
df['Month'] = df['Order Date'].dt.to_period('M').astype(str)

# Sidebar Filters
st.sidebar.title("Filter Data")
selected_region = st.sidebar.multiselect("Select Region", options=df['Region'].unique(), default=df['Region'].unique())
selected_category = st.sidebar.multiselect("Select Category", options=df['Category'].unique(), default=df['Category'].unique())

# Filter DataFrame
filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

# KPIs
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_margin = (total_profit / total_sales) * 100

# --- Dashboard Title ---
st.title("📊 Sales Performance Dashboard")
st.markdown("Explore performance metrics by Region and Category.")

# --- KPIs ---
st.metric("💰 Total Sales", f"₹{total_sales:,.0f}")
st.metric("📈 Total Profit", f"₹{total_profit:,.0f}")
st.metric("🧮 Avg Profit Margin", f"{avg_margin:.2f}%")

st.markdown("---")

# --- Profit by Sub-Category ---
subcat_profit = filtered_df.groupby('Sub-Category')['Profit'].sum().sort_values()
fig1 = px.bar(subcat_profit, x=subcat_profit.index, y=subcat_profit.values,
              labels={"x": "Sub-Category", "y": "Profit"}, title="Profit by Sub-Category")
st.plotly_chart(fig1)

# --- Monthly Sales Trend ---
monthly_sales = filtered_df.groupby('Month')['Sales'].sum()
fig2 = px.line(monthly_sales, x=monthly_sales.index, y=monthly_sales.values,
               labels={"x": "Month", "y": "Sales"}, title="Monthly Sales Trend")
st.plotly_chart(fig2)

# --- Category Distribution ---
cat_counts = filtered_df['Category'].value_counts()
fig3 = px.pie(names=cat_counts.index, values=cat_counts.values, title="Category Distribution")
st.plotly_chart(fig3)

# --- Discount vs Profit Scatter ---
fig4 = px.scatter(filtered_df, x='Discount', y='Profit', color='Category', title="Discount vs Profit")
st.plotly_chart(fig4)

# --- Map (if State column exists) ---
if 'State' in filtered_df.columns:
    state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index()
    fig5 = px.choropleth(state_sales,
                         locations='State',
                         locationmode="USA-states",
                         scope="usa",
                         color='Sales',
                         title="Sales by State")
    st.plotly_chart(fig5)

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit")
