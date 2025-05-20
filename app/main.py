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

sns.set_style("whitegrid")
st.set_page_config(
    page_title="Solar Irradiance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# 1. Load data immediately from data/cleaned
# ──────────────────────────────────────────────────────────────────────────────
with st.spinner("Loading cleaned CSVs…"):
    df = load_data()

# Country filter
selected = st.sidebar.multiselect(
    "Filter countries:",
    options=df["Country"].unique().tolist(),
    default=df["Country"].unique().tolist(),
)
df = df[df["Country"].isin(selected)]
if df.empty:
    st.warning("No data after filtering.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 2. Tabs for EDA & comparison
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 EDA (per country)", "🌍 Cross-country"])

# ----------------------------  TAB 1  ---------------------------------------
with tab1:
    st.header("Exploratory Data Analysis")

    st.subheader("Summary statistics")
    st.dataframe(summary_stats(df), use_container_width=True)

    st.subheader("Missing-value pattern")
    st.pyplot(missing_heatmap(df))

    plot_choice = st.selectbox(
        "Choose a plot type:",
        (
            "Time series",
            "Correlation heatmap",
            "Scatter (WS vs GHI)",
            "Wind rose",
            "Histogram (GHI)",
            "Bubble chart (GHI vs Tamb, bubble RH)",
        ),
    )

    if plot_choice == "Time series":
        metric = st.selectbox("Metric:", ("GHI", "DNI", "DHI", "Tamb"))
        st.pyplot(time_series(df, metric))
    elif plot_choice == "Correlation heatmap":
        st.pyplot(correlation_heatmap(df, ["GHI", "DNI", "DHI", "Tamb", "TModA", "TModB"]))
    elif plot_choice == "Scatter (WS vs GHI)":
        st.pyplot(scatter_plot(df, "WS", "GHI"))
    elif plot_choice == "Wind rose":
        st.pyplot(wind_rose(df))
    elif plot_choice == "Histogram (GHI)":
        st.pyplot(histogram(df, "GHI"))
    else:
        st.pyplot(bubble_chart(df))

# ----------------------------  TAB 2  ---------------------------------------
with tab2:
    st.header("Cross-country comparison")

    metric = st.selectbox("Metric for boxplot:", ("GHI", "DNI", "DHI"))

    st.subheader(f"{metric} distribution by country")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(x="Country", y=metric, data=df, palette="Set2", ax=ax)
    st.pyplot(fig)

    st.subheader("Summary (mean / median / std)")
    st.dataframe(compare_stats(df, [metric]), use_container_width=True)

    pval = one_way_anova(df, metric)
    st.markdown(
        f"**One-way ANOVA p-value:** `{pval:.4g}` "
        + ("(significant 🤔)" if pval < 0.05 else "(not significant)")
    )

    st.subheader("Average GHI ranking")
    avg = (
        df.groupby("Country")["GHI"]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="Mean GHI")
    )
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    sns.barplot(x="Mean GHI", y="Country", data=avg, palette="viridis", ax=ax2)
    st.pyplot(fig2)

st.caption("© 2025 Solar Challenge — Streamlit Dashboard")
