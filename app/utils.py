"""
Reusable helpers for the Solar Dashboard
----------------------------------------

All heavy lifting (loading, aggregations, plots, stats) lives here so
`main.py` stays tidy.  Every function takes a dataframe that already
contains all three countries plus a `Country` column.
"""
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from windrose import WindroseAxes


# ------------------------------------------------------------------ #
# Data I/O
# ------------------------------------------------------------------ #
def load_data() -> pd.DataFrame:
    """Load cleaned CSVs, tag by country, and concatenate."""
    data_path = Path(__file__).parent.parent / "data" / "cleaned"
    files = {
        "Benin": data_path / "benin-clean.csv",
        "Sierra Leone": data_path / "sierraleone-clean.csv",
        "Togo": data_path / "togo-clean.csv",
    }
    frames = []
    for name, fpath in files.items():
        df = pd.read_csv(fpath, parse_dates=["Timestamp"], infer_datetime_format=True)
        df["Country"] = name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ------------------------------------------------------------------ #
# EDA utilities
# ------------------------------------------------------------------ #
def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return describe() plus null counts & % for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    desc = df[numeric_cols].describe().T
    # null information
    nulls = df[numeric_cols].isna().sum()
    desc["Missing #"] = nulls
    desc["Missing %"] = (nulls / len(df)).round(3) * 100
    return desc.reset_index().rename(columns={"index": "Column"})


def missing_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Heat-map of missing values."""
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(df.isna(), cbar=False, ax=ax)
    ax.set_title("Missing-value pattern")
    ax.set_xlabel("Columns")
    ax.set_ylabel("Rows")
    return fig


def zscore_outliers(df: pd.DataFrame,
                    cols: List[str],
                    threshold: float = 3.0) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Flag outliers using |Z| > threshold and return:
    (cleaned_dataframe, boolean_mask_of_outliers)
    """
    z = np.abs(stats.zscore(df[cols], nan_policy="omit"))
    mask = (z > threshold).any(axis=1)
    cleaned = df[~mask].copy()
    return cleaned, mask


# ------------------------------------------------------------------ #
# Plot helpers (each returns a matplotlib Figure ready for st.pyplot)
# ------------------------------------------------------------------ #
def time_series(df: pd.DataFrame, metric: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(data=df, x="Timestamp", y=metric, hue="Country", ax=ax)
    ax.set_title(f"{metric} over time")
    ax.set_ylabel(f"{metric} (W/m²)")
    ax.legend(title="Country")
    return fig


def correlation_heatmap(df: pd.DataFrame,
                        metrics: List[str]) -> plt.Figure:
    corr = df[metrics].corr()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation matrix")
    return fig


def scatter_plot(df: pd.DataFrame,
                 x: str,
                 y: str,
                 hue: str = "Country") -> plt.Figure:
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, alpha=.6)
    ax.set_title(f"{y} vs. {x}")
    return fig


def wind_rose(df: pd.DataFrame,
              ws_col: str = "WS",
              wd_col: str = "WD") -> plt.Figure:
    fig = plt.figure(figsize=(4, 4))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(df[wd_col], df[ws_col], normed=True, opening=0.8, edgecolor="white")
    ax.set_legend()
    return fig


def histogram(df: pd.DataFrame, col: str) -> plt.Figure:
    fig, ax = plt.subplots()
    sns.histplot(df[col].dropna(), kde=True, ax=ax)
    ax.set_title(f"Distribution of {col}")
    return fig


def bubble_chart(df: pd.DataFrame,
                 x: str = "GHI",
                 y: str = "Tamb",
                 size: str = "RH") -> plt.Figure:
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, size=size,
                    hue="Country", sizes=(20, 400), alpha=.6, ax=ax)
    ax.set_title(f"{y} vs {x} (bubble ~ {size})")
    return fig


# ------------------------------------------------------------------ #
# Cross-country statistics
# ------------------------------------------------------------------ #
def compare_stats(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Return mean, median, std for each metric by country."""
    out = []
    for m in metrics:
        stats_df = df.groupby("Country")[m].agg(["mean", "median", "std"])
        stats_df["Metric"] = m
        out.append(stats_df.reset_index())
    return pd.concat(out, ignore_index=True)[
        ["Metric", "Country", "mean", "median", "std"]
    ]


def one_way_anova(df: pd.DataFrame, metric: str) -> float:
    """Return p-value from ANOVA across countries on the given metric."""
    groups = [g[metric].dropna().values for _, g in df.groupby("Country")]
    fstat, pval = stats.f_oneway(*groups)
    return pval
