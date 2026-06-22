import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')
 
st.set_page_config(
    page_title="Global Superstore Dashboard",
    page_icon="📊",
    layout="wide"
)
 
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)
 
@st.cache_data
def load_data():
    df = pd.read_csv("clean_superstore.csv")
    df.columns = df.columns.str.strip()
    return df
 
df = load_data()
 
# ── Sidebar Filters ──────────────────────────────────────
st.sidebar.title("📌 Filters")
 
region = st.sidebar.multiselect(
    "🌍 Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)
 
category = st.sidebar.multiselect(
    "📦 Category",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)
 
subcategory = st.sidebar.multiselect(
    "🏷️ Sub-Category",
    options=sorted(df["Sub.Category"].unique()),
    default=sorted(df["Sub.Category"].unique())
)
 
# ── Apply Filters ────────────────────────────────────────
filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Sub.Category"].isin(subcategory))
]
 
# ── Title ────────────────────────────────────────────────
st.markdown("# 📊 Global Superstore Business Dashboard")
st.markdown("**Interactive sales, profit & customer performance analysis**")
st.markdown("---")
 
# ── KPI Cards ────────────────────────────────────────────
total_sales     = filtered_df["Sales"].sum()
total_profit    = filtered_df["Profit"].sum()
total_orders    = filtered_df["Order.ID"].nunique()
total_customers = filtered_df["Customer.ID"].nunique()
profit_margin   = (total_profit / total_sales * 100) if total_sales > 0 else 0
 
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Sales",    f"${total_sales:,.0f}")
col2.metric("📈 Total Profit",   f"${total_profit:,.0f}")
col3.metric("🛒 Total Orders",   f"{total_orders:,}")
col4.metric("👥 Customers",      f"{total_customers:,}")
col5.metric("📊 Profit Margin",  f"{profit_margin:.1f}%")
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── Row 1: Sales by Region | Profit by Category ─────────
col1, col2 = st.columns(2)
 
with col1:
    st.subheader("🌍 Sales by Region")
    region_sales = (
        filtered_df.groupby("Region")["Sales"]
        .sum().reset_index()
        .sort_values("Sales", ascending=True)
    )
    fig1 = px.bar(
        region_sales, x="Sales", y="Region",
        orientation="h", color="Sales",
        color_continuous_scale="Blues",
        text=region_sales["Sales"].apply(lambda x: f"${x:,.0f}")
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        margin=dict(l=10, r=40, t=10, b=10), height=320
    )
    st.plotly_chart(fig1, use_container_width=True)
 
with col2:
    st.subheader("📦 Profit by Category")
    cat_profit = (
        filtered_df.groupby("Category")["Profit"]
        .sum().reset_index()
        .sort_values("Profit", ascending=True)
    )
    cat_profit["Color"] = cat_profit["Profit"].apply(
        lambda x: "#2ecc71" if x >= 0 else "#e74c3c"
    )
    fig2 = px.bar(
        cat_profit, x="Profit", y="Category",
        orientation="h", color="Color",
        color_discrete_map="identity",
        text=cat_profit["Profit"].apply(lambda x: f"${x:,.0f}")
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=40, t=10, b=10), height=320
    )
    st.plotly_chart(fig2, use_container_width=True)
 
# ── Row 2: Top 10 Sub-Categories | Segment Pie ──────────
col1, col2 = st.columns(2)
 
with col1:
    st.subheader("🏷️ Top 10 Sub-Categories by Sales")
    subcat_sales = (
        filtered_df.groupby("Sub.Category")["Sales"]
        .sum().reset_index()
        .sort_values("Sales", ascending=False)
        .head(10)
    )
    fig3 = px.bar(
        subcat_sales, x="Sub.Category", y="Sales",
        color="Sales", color_continuous_scale="Teal",
        text=subcat_sales["Sales"].apply(lambda x: f"${x/1000:.0f}K")
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        xaxis=dict(tickangle=30),
        margin=dict(l=10, r=10, t=10, b=60), height=350
    )
    st.plotly_chart(fig3, use_container_width=True)
 
with col2:
    st.subheader("👥 Sales by Customer Segment")
    segment_sales = (
        filtered_df.groupby("Segment")["Sales"]
        .sum().reset_index()
    )
    fig4 = px.pie(
        segment_sales, values="Sales", names="Segment",
        color_discrete_sequence=["#3498db", "#2ecc71", "#e67e22"],
        hole=0.4
    )
    fig4.update_traces(textposition="inside", textinfo="percent+label")
    fig4.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=350
    )
    st.plotly_chart(fig4, use_container_width=True)
 
# ── Row 3: Top 5 Customers ───────────────────────────────
st.subheader("🏆 Top 5 Customers by Sales")
top_customers = (
    filtered_df.groupby("Customer.Name")["Sales"]
    .sum().reset_index()
    .sort_values("Sales", ascending=True)
    .tail(5)
)
fig5 = px.bar(
    top_customers, x="Sales", y="Customer.Name",
    orientation="h", color="Sales",
    color_continuous_scale="Oranges",
    text=top_customers["Sales"].apply(lambda x: f"${x:,.0f}")
)
fig5.update_traces(textposition="outside")
fig5.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    coloraxis_showscale=False,
    margin=dict(l=10, r=60, t=10, b=10), height=300
)
st.plotly_chart(fig5, use_container_width=True)
 
# ── Data Table ───────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Filtered Data Preview")
st.dataframe(
    filtered_df[[
        "Order.ID", "Customer.Name", "Region",
        "Category", "Sub.Category", "Sales", "Profit", "Quantity"
    ]].head(100),
    use_container_width=True,
    height=300
)
st.caption(f"Showing {min(100, len(filtered_df))} of {len(filtered_df):,} records")