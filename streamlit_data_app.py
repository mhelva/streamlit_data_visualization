import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

sns.set_style("whitegrid")
st.set_option('deprecation.showPyplotGlobalUse', False)


def info_table(dataframe):
    n_miss = dataframe.isnull().sum().sort_values(ascending=False)
    ratio = (dataframe.isnull().sum() / dataframe.shape[0] * 100).sort_values(ascending=False)
    unique_count = dataframe.nunique()
    dtype = dataframe.dtypes
    info_df = pd.concat([n_miss, np.round(ratio, 2), unique_count, dtype],
                        axis=1, keys=['missing_values', 'missing_ratio', 'unique_values', 'dtype'])
    return info_df.reset_index().rename(columns={"index": "column_name"})

def grab_col_names(dataframe, cat_th=10, car_th=20):
    # cat_cols, cat_but_car
    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "O"]
    num_but_cat = [col for col in dataframe.columns if dataframe[col].nunique() < cat_th and
                   dataframe[col].dtypes != "O"]
    cat_but_car = [col for col in dataframe.columns if dataframe[col].nunique() > car_th and
                   dataframe[col].dtypes == "O"]
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]

    # num_cols
    num_cols = [col for col in dataframe.columns if dataframe[col].dtypes != "O"]
    num_cols = [col for col in num_cols if col not in num_but_cat]

    return cat_cols, num_cols, cat_but_car

# Sidebar Controls and Main App
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

        # Data Preview Tab
        with tab1:
            st.subheader("Dataset Head")
            st.dataframe(df.head())

            st.subheader("Information about Dataset")
            st.dataframe(info_table(df))

            st.subheader("Descriptive Statistics")
            st.dataframe(df.describe().T)

        #  Visualizations Tab
        with tab2:
            st.subheader("Choose Plot Type")
            #numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            all_cols = df.columns.tolist()
            cat_cols, num_cols, cat_but_car = grab_col_names(df)
            plot_type = st.radio("For histogram, distribution and pie plot, select only **X-axis** column.",
                                 ["Line", "Histogram", "Distribution", "Boxplot", "Violinplot",
                                   "Scatter", "Pie"])
            st.subheader("Select Columns to Plot")
            if plot_type == "Pie":
                x_col = st.selectbox("X-axis", options=cat_cols)
                y_col = None
            elif plot_type in ["Histogram", "Distribution"]:
                x_col = st.selectbox("X-axis", options=cat_cols+num_cols)
                y_col = None
            else:
                x_col = st.selectbox("X-axis", options=all_cols)
                y_col = st.selectbox("Y-axis", options=all_cols)

            if st.button("Generate Plot"):
                fig, ax = plt.subplots(figsize=(12, 8))

                if plot_type == "Line" and y_col:
                    ax.plot(df[x_col], df[y_col])
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f"{y_col} vs {x_col}")

                elif plot_type == "Histogram":
                    sns.histplot(df[x_col], bins=50, kde=False, ax=ax, palette="viridis")
                    ax.set_title(f"Histogram of {x_col}")
                    ax.set_xlabel(x_col)
                    ax.set_ylabel("Count")

                elif plot_type == "Boxplot" and y_col:
                    sns.boxplot(x=x_col, y=y_col, data=df, ax=ax, palette="viridis")
                    ax.set_title(f"Boxplot: {y_col} vs {x_col}")
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)

                elif plot_type == "Violinplot" and y_col:
                    sns.violinplot(x=x_col, y=y_col, data=df, ax=ax, palette="viridis")
                    ax.set_title(f"Violin Plot: {y_col} vs {x_col}")
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)

                elif plot_type == "Distribution":
                    sns.distplot(df[x_col], bins=50, kde=True, ax=ax)
                    ax.set_title(f"Distribution of {x_col}")
                    ax.set_xlabel(x_col)
                    ax.set_ylabel("Density")

                elif plot_type == "Scatter" and y_col:
                    ax.scatter(df[x_col], df[y_col])
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")

                elif plot_type == "Pie":
                    counts = df[x_col].value_counts()
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
                    ax.set_title(f"Pie Chart of {x_col}")

                st.pyplot(fig)

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("Please upload a CSV file to get started.")
