
import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Data Analyst Dashboard", layout="wide")

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.markdown("Upload and filter your data")

# Title
st.title("📊 Data Analyst Dashboard")
st.markdown("### Upload • Clean • Analyze • Visualize")

# Upload file
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # ==============================
    # 🔍 Sidebar Filters
    # ==============================
    st.sidebar.subheader("🔍 Filters")
    columns = df.columns.tolist()
    selected_column = st.sidebar.selectbox("Select Column", columns)

    unique_values = df[selected_column].dropna().unique()
    selected_values = st.sidebar.multiselect(
        "Select Values", unique_values, default=unique_values
    )

    df = df[df[selected_column].isin(selected_values)]

    # ==============================
    # 📌 Data Preview & Info
    # ==============================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Data Preview")
        st.dataframe(df.head())

    with col2:
        st.subheader("📊 Data Info")
        st.write("Shape:", df.shape)
        st.write(df.describe())

    # ==============================
    # 🧹 Data Cleaning
    # ==============================
    st.subheader("🧹 Data Cleaning")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("Remove Duplicates"):
            df = df.drop_duplicates()
            st.success("Duplicates Removed")

    with col4:
        if st.button("Fill Missing Values"):
            df = df.fillna(df.mean(numeric_only=True))
            st.success("Missing Values Filled")

    # ==============================
    # 📈 Visualization
    # ==============================
    st.subheader("📈 Visualization")

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    chart_type = st.selectbox(
        "Select Chart Type",
        ["Histogram", "Bar Chart", "Line Chart"]
    )

    if chart_type == "Histogram" and len(numeric_cols) > 0:
        col = st.selectbox("Select Numeric Column", numeric_cols)
        fig = px.histogram(df, x=col, color=col)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Bar Chart" and len(categorical_cols) > 0:
        col = st.selectbox("Select Categorical Column", categorical_cols)
        fig = px.bar(df[col].value_counts().reset_index(),
                     x='index', y=col, color='index')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line Chart" and len(numeric_cols) > 0:
        col = st.selectbox("Select Numeric Column", numeric_cols)
        fig = px.line(df, y=col)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Suitable columns not available for this chart")

    # ==============================
    # 📊 KPI Metrics
    # ==============================
    st.subheader("📊 Key Metrics")

    col1, col2, col3 = st.columns(3)

    if len(numeric_cols) > 0:
        selected_metric = st.selectbox("Select Column for KPI", numeric_cols)

        with col1:
            st.metric("Total", round(df[selected_metric].sum(), 2))

        with col2:
            st.metric("Average", round(df[selected_metric].mean(), 2))

        with col3:
            st.metric("Max Value", round(df[selected_metric].max(), 2))
    else:
        st.warning("No numeric columns available")

    # ==============================
    # 🔥 Correlation Heatmap
    # ==============================
    st.subheader("🔥 Correlation Heatmap")

    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale='RdBu_r'
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough numeric columns")

    # ==============================
    # 📌 GroupBy Analysis
    # ==============================
    st.subheader("📌 GroupBy Analysis")

    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        group_col = st.selectbox("Group By (Category)", categorical_cols)
        agg_col = st.selectbox("Select Value Column", numeric_cols)

        agg_func = st.selectbox(
            "Aggregation Function",
            ["sum", "mean", "max", "min"]
        )

        grouped_df = df.groupby(group_col)[agg_col].agg(agg_func).reset_index()

        st.dataframe(grouped_df)

        fig = px.bar(grouped_df, x=group_col, y=agg_col, color=group_col)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Need categorical and numeric columns")

    # ==============================
    # 🎯 Column Insights
    # ==============================
    st.subheader("🎯 Column Insights")

    selected_col = st.selectbox(
    "Select Column for Insights",
    df.columns,
    key="insight_column_unique"
)

    st.write("Data Type:", df[selected_col].dtype)
    st.write("Missing Values:", df[selected_col].isnull().sum())
    st.write("Unique Values:", df[selected_col].nunique())

    # ==============================
    # ⬇️ Download
    # ==============================
    st.subheader("⬇️ Download Cleaned Data")

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "cleaned_data.csv")

else:
    st.info("👆 Upload a CSV file from the sidebar to begin")