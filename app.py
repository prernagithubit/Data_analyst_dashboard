
import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
h1, h2, h3 {
    color: #2c3e50;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# ⚙️ Page Config
# ==============================
st.set_page_config(page_title="Data Analyst Dashboard", layout="wide")

# ==============================
# 🚀 Caching
# ==============================
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# ==============================
# 🎛️ Sidebar
# ==============================
st.sidebar.title("⚙️ Dashboard Controls")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])

# Navigation
page = st.sidebar.radio(
    "📂 Navigate",
    ["Overview", "Data Cleaning", "Visualization", "Advanced Analysis", "Insights"]
)

# ==============================
# 🏠 Main Title
# ==============================
st.title("📊 Interactive Data Analytics Dashboard")
st.markdown("### Upload • Clean • Analyze • Visualize")

# ==============================
# 📂 Load Data
# ==============================
if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Identify column types
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # ==============================
    # 🔍 Multi Filters
    # ==============================
    st.sidebar.subheader("🔍 Filters")
    filter_cols = st.sidebar.multiselect("Select Columns", df.columns)

    for col in filter_cols:
        values = df[col].dropna().unique()
        selected = st.sidebar.multiselect(f"{col}", values, default=values)
        df = df[df[col].isin(selected)]

    # ==============================
    # 📌 OVERVIEW
    # ==============================
    if page == "Overview":

        st.subheader("📌 Data Preview")
        st.dataframe(df.head())

        st.subheader("📊 Data Info")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Shape:", df.shape)

        with col2:
            st.write(df.describe())

        # KPI Section
        st.subheader("📊 Key Metrics")

        if len(numeric_cols) > 0:
            metric_col = st.selectbox("Select KPI Column", numeric_cols)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", f"{df[metric_col].sum():,.2f}")
            c2.metric("Average", f"{df[metric_col].mean():,.2f}")
            c3.metric("Max", f"{df[metric_col].max():,.2f}")

    # ==============================
    # 🧹 DATA CLEANING
    # ==============================
    elif page == "Data Cleaning":

        st.subheader("🧹 Data Cleaning Panel")

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

        st.dataframe(df.head())

    # ==============================
    # 📈 VISUALIZATION
    # ==============================
    elif page == "Visualization":

        st.subheader("📈 Visualization Studio")

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Histogram", "Bar Chart", "Line Chart", "Scatter Plot", "Box Plot"]
        )

        if chart_type == "Histogram" and len(numeric_cols) > 0:
            col = st.selectbox("Column", numeric_cols)
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar Chart" and len(categorical_cols) > 0:
            col = st.selectbox("Column", categorical_cols)
            data = df[col].value_counts().reset_index()
            fig = px.bar(data, x='index', y=col, color='index')
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Line Chart" and len(numeric_cols) > 0:
            col = st.selectbox("Column", numeric_cols)
            fig = px.line(df, y=col)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter Plot" and len(numeric_cols) > 1:
            x_col = st.selectbox("X-axis", numeric_cols)
            y_col = st.selectbox("Y-axis", numeric_cols)
            fig = px.scatter(df, x=x_col, y=y_col, color=y_col)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Box Plot" and len(numeric_cols) > 0:
            col = st.selectbox("Column", numeric_cols)
            fig = px.box(df, y=col)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Suitable columns not available")

    # ==============================
    # 📊 ADVANCED ANALYSIS
    # ==============================
    elif page == "Advanced Analysis":

        st.subheader("🔥 Correlation Heatmap")

        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig = px.imshow(corr, text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough numeric columns")

        st.subheader("📌 GroupBy Analysis")

        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            group_col = st.selectbox("Group By", categorical_cols)
            agg_col = st.selectbox("Value Column", numeric_cols)
            agg_func = st.selectbox("Aggregation", ["sum", "mean", "max", "min"])

            grouped_df = df.groupby(group_col)[agg_col].agg(agg_func).reset_index()

            st.dataframe(grouped_df)

            fig = px.bar(grouped_df, x=group_col, y=agg_col, color=group_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need categorical and numeric columns")

    # ==============================
    # 🧠 INSIGHTS
    # ==============================
    elif page == "Insights":

        st.subheader("🧠 Automated Insights")

        if len(numeric_cols) > 0:
            col = st.selectbox("Select Column", numeric_cols)

            mean = df[col].mean()
            median = df[col].median()
            max_val = df[col].max()
            min_val = df[col].min()

            if mean > median:
                st.write(f"📌 {col} is right-skewed (high outliers)")
            else:
                st.write(f"📌 {col} is left-skewed")

            st.write(f"📊 Average: {mean:.2f}")
            st.write(f"🔝 Max: {max_val}")
            st.write(f"🔻 Min: {min_val}")

            # IQR
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)

            st.write(f"📦 IQR Range: {q1:.2f} - {q3:.2f}")

        else:
            st.warning("No numeric columns available")

    # ==============================
    # ⬇️ DOWNLOAD
    # ==============================
    st.subheader("⬇️ Download Cleaned Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "cleaned_data.csv")

else:
    st.info("👆 Upload a file to begin")
