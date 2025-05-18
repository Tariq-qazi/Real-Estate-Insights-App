# real_estate_insights_app.py

import streamlit as st

import streamlit as st
import pandas as pd
import gdown
import os
import matplotlib.pyplot as plt


# === CONFIG ===
PARQUET_DRIVE_ID = "17tWMJLlBIpxirNTi2JntwJZ0Pt7lMgC9"

@st.cache_data
def load_data():
    url = f"https://drive.google.com/uc?id={PARQUET_DRIVE_ID}"
    output = "cleaned_real_estate_ready.parquet"
    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)
    return pd.read_parquet(output)

# === LOAD ===
df = load_data()
st.set_page_config(page_title="Dubai Real Estate Insights", layout="wide")
st.title("🏙️ Dubai Real Estate Market Explorer")
st.markdown("Explore price trends, growth stages, and market segments with real transaction data.")

# === FILTERS ===
col1, col2, col3 = st.columns(3)
with col1:
    area = st.selectbox("Select Area", sorted(df['area_name_en'].dropna().unique()))
with col2:
    property_type = st.selectbox("Select Property Type", sorted(df['property_type_en'].dropna().unique()))
with col3:
    stage = st.selectbox("Select Growth Stage", ["All"] + df['growth_stage'].dropna().unique().tolist())

# === FILTERED VIEW ===
df_filtered = df[
    (df['area_name_en'] == area) &
    (df['property_type_en'] == property_type)
]

if stage != "All":
    df_filtered = df_filtered[df_filtered['growth_stage'] == stage]

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# === KPI DISPLAY ===
avg_price = df_filtered['actual_worth'].sum() / df_filtered['procedure_area'].sum()
st.metric("Average Price/sqm", f"AED {avg_price:,.0f}")
st.metric("Transactions", f"{len(df_filtered):,}")

# === TREND OVER TIME ===
df_filtered['transaction_year'] = df_filtered['year']
df_filtered['price_per_sqm'] = df_filtered['actual_worth'] / df_filtered['procedure_area']

trend = df_filtered.groupby('transaction_year')['price_per_sqm'].mean()
st.subheader("📈 Yearly Price/sqm Trend")
st.line_chart(trend)

# === GROWTH STAGE COMPARISON ===
st.subheader("📊 Growth Stage Comparison (within Area)")
growth_comparison = df[(df['area_name_en'] == area) & (df['property_type_en'] == property_type)].copy()
growth_comparison['price_per_sqm'] = growth_comparison['actual_worth'] / growth_comparison['procedure_area']
growth_group = growth_comparison.groupby('growth_stage')['price_per_sqm'].mean().reindex([
    'Off-Plan or Launch', 'Early Growth', 'Maturity', 'Stabilized / Legacy'
])

st.bar_chart(growth_group)

st.markdown("---")
st.caption("Built with ❤️ to help you understand Dubai's real estate dynamics.")
