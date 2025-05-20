"""
Utility helpers for the Solar Dashboard
---------------------------------------
• Finds every *-clean.csv inside any data/cleaned/ directory
  beneath the repo or app folder.
• Caches heavy plots so reruns are fast.
"""
from pathlib import Path
from typing import List, Dict

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from windrose import WindroseAxes


# ──────────────────────────────────────────────────────────────────────────────
# 1. Data I/O
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=600)
def load_data() -> pd.DataFrame:
    """
    Scan for *.csv whose name ends with '-clean.csv' inside any data/cleaned/
    folder below the project.  Adds a Country column (title-cased stem before
    '-clean') and concatenates them.

    Returns
    -------
    pd.DataFrame (possibly empty if no files found)
    """
    root = Path(__file__).resolve().parent.parent  # repo root
    candidates: List[Path] = []

    # search two typical spots: repo/data/cleaned and anywhere deeper
    for dirpath in (root / "data" / "cleaned").rglob("*.csv"):
        candidates.append(dirpath)
    for dirpath in root.rglob("data/cleaned/*.csv"):
        if dirpath not in candidates:
            candidates.append(dirpath)

    frames = []
    for csv in candidates:
        if not csv.name.endswith("-clean.csv"):
            continue
        country = csv.stem.replace("-clean", "").replace("_", " ").title()
        try:
            df = pd.read_csv(csv, parse_dates=["Timestamp"], infer_datetime_format=True)
        except Exception as exc:
            st.warning(f"⚠️  Skipping {csv.name}: {exc}")
            continue
        df["Country"] = country
        frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ──────────────────────────────────────────────────────────────────────────────
# 2. Quick EDA helpers
# ──────────────────────────────────────────────────────────────────────────────
def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number])
    desc = numeric.describe().T
    nulls = numeric.isna().sum()
    desc["Missing #"] = nulls
    desc["Missing %"] = (nulls / len(df) * 100).round(2)
    return desc.reset_index().rename(columns={"index": "Column"})


@st.cache_data(show_spinner=False)
def missing_heatmap(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(df.isna(), cbar=False, ax=ax)
    ax.set_title("Missing-value pattern")
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# 3. Cached plot builders
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def time_series(df: pd.DataFrame, metric: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(data=df, x="Timestamp", y=metric, hue="Country", ax=ax)
    ax.set_ylabel(f"{metric} (W/m²)")
    ax.set_title(f"{metric} over time")
    return fig


@st.cache_data(show_spinner=False)
def correlation_heatmap(df: pd.DataFrame, cols: List[str]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(df[cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation matrix")
    return fig


@st.cache_data(show_spinner=False)
def scatter_plot(df: pd.DataFrame, x: str, y: str) -> plt.Figure:
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, hue="Country", alpha=.6, ax=ax)
    ax.set_title(f"{y} vs {x}")
    return fig


@st.cache_data(show_spinner=False)
def wind_rose(df: pd.DataFrame, ws: str = "WS", wd: str = "WD") -> plt.Figure:
    fig = plt.figure(figsize=(4, 4))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(df[wd], df[ws], normed=True, opening=0.8, edgecolor="white")
    ax.set_legend()
    return fig


@st.cache_data(show_spinner=False)
def histogram(df: pd.DataFrame, col: str) -> plt.Figure:
    fig, ax = plt.subplots()
    sns.histplot(df[col].dropna(), kde=True, ax=ax)
    ax.set_title(f"Distribution of {col}")
    return fig


@st.cache_data(show_spinner=False)
def bubble_chart(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=df,
        x="GHI",
        y="Tamb",
        size="RH",
        hue="Country",
        sizes=(20, 400),
        alpha=.6,
        ax=ax,
    )
    ax.set_title("Tamb vs GHI (bubble ~ RH)")
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# 4. Cross-country stats
# ──────────────────────────────────────────────────────────────────────────────
def compare_stats(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    rows = []
    for m in metrics:
        grp = df.groupby("Country")[m].agg(["mean", "median", "std"]).reset_index()
        grp.insert(1, "Metric", m)
        rows.append(grp)
    return pd.concat(rows, ignore_index=True)


def one_way_anova(df: pd.DataFrame, metric: str) -> float:
    groups = [g[metric].dropna() for _, g in df.groupby("Country")]
    return stats.f_oneway(*groups).pvalue
