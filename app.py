
import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# ⚙️ Page Config
# ==============================
st.set_page_config(page_title="Data Analytics Dashboard", layout="wide")

# ==============================
# 🎨 Custom Styling
# ==============================
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #2c3e50;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🚀 Load Data
# ==============================
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# ==============================
# 🔝 HEADER
# ==============================
st.title("📊 Interactive Data Analytics Dashboard")
st.markdown("Analyze, clean, and visualize your data in one place")
st.info("📂 Upload your dataset from the sidebar to start analysis")
st.divider()

# ==============================
# 📂 Sidebar Upload
# ==============================
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Identify column types
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # ==============================
    # 🎛️ FILTER BAR (TOP)
    # ==============================
    st.subheader("🔍 Filters")

    selected_cols = st.multiselect("Select Columns to Filter", df.columns)

    for col in selected_cols:
        values = df[col].dropna().unique()
        selected = st.multiselect(f"{col}", values, default=values)
        df = df[df[col].isin(selected)]

    if df.empty:
        st.warning("No data available after filtering")
        st.stop()

    st.divider()

    # ==============================
    # 📊 KPI SECTION
    # ==============================
    st.subheader("📊 Key Metrics")

    if len(numeric_cols) > 0:
        metric_col = st.selectbox("Select KPI Column", numeric_cols)

        k1, k2, k3 = st.columns(3)
        k1.metric("Total", f"{df[metric_col].sum():,.2f}")
        k2.metric("Average", f"{df[metric_col].mean():,.2f}")
        k3.metric("Max", f"{df[metric_col].max():,.2f}")

    st.divider()

    # ==============================
    # 📈 VISUALIZATION GRID
    # ==============================
    st.subheader("📈 Visualizations")

    c1, c2 = st.columns(2)

    with c1:
        if len(numeric_cols) > 0:
            col = st.selectbox("Histogram Column", numeric_cols)
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if len(numeric_cols) > 1:
            x_col = st.selectbox("X-axis", numeric_cols)
            y_col = st.selectbox("Y-axis", numeric_cols)
            fig = px.scatter(df, x=x_col, y=y_col, color=y_col, hover_data=df.columns)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==============================
    # 🧹 DATA CLEANING (EXPANDER)
    # ==============================
    with st.expander("🧹 Data Cleaning Options"):

        clean_option = st.selectbox(
            "Handle Missing Values",
            ["None", "Drop Rows", "Fill Mean", "Fill Median", "Fill Mode"]
        )

        if clean_option == "Drop Rows":
            df = df.dropna()

        elif clean_option == "Fill Mean" and len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

        elif clean_option == "Fill Median" and len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

        elif clean_option == "Fill Mode":
            df = df.fillna(df.mode().iloc[0])

        if st.button("Remove Duplicates"):
            df = df.drop_duplicates()
            st.success("Duplicates Removed")

    # ==============================
    # 🔥 ADVANCED ANALYSIS
    # ==============================
    st.subheader("📊 Advanced Analysis")

    a1, a2 = st.columns(2)

    with a1:
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig = px.imshow(corr, text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

    with a2:
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            group_col = st.selectbox("Group By", categorical_cols)
            agg_col = st.selectbox("Value Column", numeric_cols)

            grouped = df.groupby(group_col)[agg_col].mean().reset_index()
            fig = px.bar(grouped, x=group_col, y=agg_col)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==============================
    # 🧠 INSIGHTS
    # ==============================
    st.subheader("🧠 Insights")

    if len(numeric_cols) > 0:
        col = st.selectbox("Select Column", numeric_cols)

        mean = df[col].mean()
        median = df[col].median()

        if mean > median:
            st.success(f"{col} is right-skewed (outliers present)")
        else:
            st.info(f"{col} is left-skewed")

        st.write(f"📊 Average: {mean:.2f}")
        st.write(f"📦 IQR: {df[col].quantile(0.25):.2f} - {df[col].quantile(0.75):.2f}")

    st.divider()

    # ==============================
    # ⬇️ DOWNLOAD
    # ==============================
    st.subheader("⬇️ Download Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "cleaned_data.csv")

else:
    st.info("👆 Upload a file to begin")

# ==============================
# ⬇️ FOOTER
# ==============================
st.markdown("---")
st.markdown("Built with Streamlit | Data Analyst Portfolio Project")
