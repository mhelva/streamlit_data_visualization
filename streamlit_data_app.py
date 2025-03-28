import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

sns.set_style("white")


def info_table(dataframe):
    n_miss = dataframe.isnull().sum().sort_values(ascending=False)
    ratio = (dataframe.isnull().sum() / dataframe.shape[0] * 100).sort_values(ascending=False)
    unique_count = dataframe.nunique()
    dtype = dataframe.dtypes
    info_df = pd.concat([n_miss, np.round(ratio, 2), unique_count, dtype],
                        axis=1, keys=['missing_values', 'missing_ratio', 'unique_values', 'dtype'])
    return info_df.reset_index()

# --- Sidebar Controls ---
st.sidebar.title("📁 Upload CSV")
uploaded_file = st.sidebar.file_uploader("Upload your file", type=["csv"])

st.title("📊 CSV Data Explorer & Visualizer")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col])

        tab1, tab2= st.tabs(["📋 Data Preview", "📈 Visualizations"])

        # --- Tab 1: Data Preview ---
        with tab1:
            st.subheader("Dataset Head")
            st.dataframe(df.head())

            st.subheader("Column Information")
            st.dataframe(info_table(df))

            st.subheader("Descriptive Statistics")
            st.dataframe(df.describe())

        # --- Tab 2: Visualizations ---
        with tab2:
            st.subheader("Select Columns to Plot")
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            all_cols = df.columns.tolist()

            plot_type = st.radio("Choose Plot Type", ["Line", "Histogram", "Distribution", "Scatter", "Pie"])

            if plot_type in ["Histogram", "Distribution", "Pie"]:
                y_col = st.selectbox("Y-axis", options=all_cols)
                x_col = None  # x_col is not used
                st.info("This plot uses only the **Y-axis** column. X-axis is ignored.")
            else:
                x_col = st.selectbox("X-axis", options=all_cols)
                y_col = st.selectbox("Y-axis", options=all_cols)
                
            if st.button("Generate Plot"):
                fig, ax = plt.subplots(figsize=(12, 8))

                if plot_type == "Line":
                    ax.plot(df[x_col], df[y_col])
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f"{y_col} vs {x_col}")

                elif plot_type == "Histogram":
                    ax.hist(df[y_col], bins=50)
                    ax.set_title(f"Histogram of {y_col}")
                    ax.set_xlabel(y_col)
                    ax.set_ylabel("Frequency")

                elif plot_type == "Distribution":
                    sns.histplot(df[y_col], bins=30, kde=True, ax=ax)
                    ax.set_title(f"Distribution of {y_col}")
                    ax.set_xlabel(y_col)
                    ax.set_ylabel("Density")

                elif plot_type == "Scatter":
                    ax.scatter(df[x_col], df[y_col])
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")

                elif plot_type == "Pie":
                    counts = df[y_col].value_counts()
                    fig, ax = plt.subplots(figsize=(8, 8))  # override fig, ax for pie chart (square is better)
                    ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
                    ax.set_title(f"Pie Chart of {y_col}")

                st.pyplot(fig)

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("Please upload a CSV file to get started.")
