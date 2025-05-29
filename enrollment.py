import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ Set Streamlit page configuration
st.set_page_config(page_title="PH School Enrollment Dashboard", layout="wide")

# ✅ Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("philippines_school_enrollment.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace('[^a-z0-9_]', '_', regex=True)

    if 'ay_start' in df.columns and 'ay_end' in df.columns:
        df['year'] = df['ay_start'].astype(str) + '-' + df['ay_end'].astype(str)

    grade_cols = [col for col in df.columns if col.startswith('grade')]
    df['total_enrollment'] = df[grade_cols].sum(axis=1)

    return df, grade_cols

# Load the dataset
df, grade_cols = load_data()

# ✅ Page title
st.title("📊 Philippine School Enrollment Dashboard")

# ✅ Region and Sector filters (shared across all tabs)
region = st.selectbox("Select Region", sorted(df['region'].dropna().unique()))
sector = st.radio("Select Sector", df['sector'].dropna().unique(), horizontal=True)

# ✅ Tabs for each dashboard view
tabs = st.tabs([
    "Enrollment Trends",
    "Total Enrollment per Year",
    "Sector Distribution",
    "Top Regions (Latest Year)"
])

# 🎓 Enrollment Trends Tab
with tabs[0]:
    st.subheader(f"Enrollment Trends in {region} - {sector}")
    filtered = df[(df['region'] == region) & (df['sector'] == sector)]
    melted = filtered.melt(id_vars='year', value_vars=grade_cols,
                           var_name='Grade Level', value_name='Enrollment')
    grouped = melted.groupby(['year', 'Grade Level'])['Enrollment'].sum().reset_index()
    fig = px.line(grouped, x='year', y='Enrollment', color='Grade Level',
                  title=f'Enrollment Trends in {region} ({sector})', markers=True)
    st.plotly_chart(fig, use_container_width=True)

# 📊 Total Enrollment per Year Tab
with tabs[1]:
    st.subheader("Total Enrollment per Year")
    totals = df.groupby('year')['total_enrollment'].sum().reset_index()
    fig = px.bar(totals, x='year', y='total_enrollment', title="Total Enrollment per Year")
    st.plotly_chart(fig, use_container_width=True)

# 🧩 Sector Distribution Tab
with tabs[2]:
    st.subheader("Enrollment Share by Sector")
    sector_totals = df.groupby('sector')['total_enrollment'].sum().reset_index()
    fig = px.pie(sector_totals, names='sector', values='total_enrollment',
                 title="Enrollment Share by Sector", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

# 🏅 Top Regions Tab
with tabs[3]:
    latest_year = df['year'].max()
    st.subheader(f"Top 5 Regions by Enrollment ({latest_year})")
    latest = df[df['year'] == latest_year]
    region_totals = latest.groupby('region')['total_enrollment'].sum().nlargest(5).reset_index()
    fig = px.bar(region_totals, x='total_enrollment', y='region', orientation='h',
                 title=f"Top 5 Regions by Enrollment ({latest_year})")
    st.plotly_chart(fig, use_container_width=True)
