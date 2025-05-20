import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from utils import (
    load_data,
    summary_stats,
    missing_heatmap,
    time_series,
    correlation_heatmap,
    scatter_plot,
    wind_rose,
    histogram,
    bubble_chart,
    compare_stats,
    one_way_anova,
)

sns.set_style("whitegrid")  # consistent look

st.set_page_config(
    page_title="Solar Irradiance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# Sidebar – global filters
# -------------------------------------------------------------
df = load_data()

all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select country (or countries):",
    options=all_countries,
    default=all_countries,
)

if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

df = df[df["Country"].isin(selected_countries)]

# Tabs for Task-2 EDA and Task-3 Comparison
tab1, tab2 = st.tabs(["📊 EDA (per country)", "🌍 Cross-country"])

# -------------------------------------------------------------
# TAB 1 – EDA
# -------------------------------------------------------------
with tab1:
    st.header("Exploratory Data Analysis")

    # ---- Stats & Missing Report ----
    st.subheader("Summary statistics")
    st.dataframe(summary_stats(df), use_container_width=True)

    st.subheader("Missing-value pattern")
    st.pyplot(missing_heatmap(df))

    # ---- Plot selector ----
    eda_plot = st.selectbox(
        "Choose an EDA plot type:",
        (
            "Time series",
            "Correlation heatmap",
            "Scatter (WS vs. GHI)",
            "Wind rose",
            "Histogram (GHI)",
            "Bubble chart (GHI vs Tamb, bubble RH)",
        ),
    )

    if eda_plot == "Time series":
        metric = st.selectbox("Metric:", ("GHI", "DNI", "DHI", "Tamb"))
        st.pyplot(time_series(df, metric))

    elif eda_plot == "Correlation heatmap":
        st.pyplot(correlation_heatmap(df, ["GHI", "DNI", "DHI", "Tamb", "TModA", "TModB"]))

    elif eda_plot == "Scatter (WS vs. GHI)":
        st.pyplot(scatter_plot(df, "WS", "GHI"))

    elif eda_plot == "Wind rose":
        st.pyplot(wind_rose(df))

    elif eda_plot == "Histogram (GHI)":
        st.pyplot(histogram(df, "GHI"))

    else:  # bubble chart
        st.pyplot(bubble_chart(df))

# -------------------------------------------------------------
# TAB 2 – Cross-country comparison
# -------------------------------------------------------------
with tab2:
    st.header("Cross-country Comparison")

    metric = st.selectbox("Metric for boxplot:", ("GHI", "DNI", "DHI"))

    # ---- Boxplot ----
    st.subheader(f"{metric} distribution by country")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(x="Country", y=metric, data=df, palette="Set2", ax=ax)
    st.pyplot(fig)

    # ---- Summary table ----
    st.subheader("Summary (mean / median / std)")
    st.dataframe(compare_stats(df, [metric]), use_container_width=True)

    # ---- ANOVA ----
    pval = one_way_anova(df, metric)
    st.markdown(
        f"**One-way ANOVA p-value:** `{pval:.4g}`  "
        + ("(significant 🤔)" if pval < 0.05 else "(not significant)")
    )

    # ---- Ranking bar ----
    st.subheader("Average GHI ranking (all data)")
    avg_ghi = (
        df.groupby("Country")["GHI"]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="Mean GHI")
    )
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    sns.barplot(x="Mean GHI", y="Country", data=avg_ghi, palette="viridis", ax=ax2)
    st.pyplot(fig2)

# -------------------------------------------------------------
st.caption("© 2025 Solar Challenge — Streamlit Dashboard")
