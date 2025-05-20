"""
Utility helpers for the Solar Dashboard
---------------------------------------
All heavy lifting (loading, aggregations, plots, stats) lives here so
main.py stays tidy.
"""
from io import BytesIO
from typing import Dict, List, Tuple

from pathlib import Path

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from windrose import WindroseAxes


# ──────────────────────────────────────────────────────────────────────────────
# Data I/O
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=600)
def load_data(file_dict: Dict[str, BytesIO | Path]) -> pd.DataFrame:
    """
    Concatenate user-uploaded CSVs and add a Country column.

    Parameters
    ----------
    file_dict : dict
        Keys = country names, values = file-like objects from st.file_uploader
        or Path objects on disk.

    Returns
    -------
    pd.DataFrame
    """
    frames: list[pd.DataFrame] = []
    for country, fh in file_dict.items():
        if fh is None:
            continue
        df = pd.read_csv(fh, parse_dates=["Timestamp"], infer_datetime_format=True)
        df["Country"] = country
        frames.append(df)

    if not frames:
        raise ValueError("No CSVs supplied")

    return pd.concat(frames, ignore_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# Quick EDA helpers
# ──────────────────────────────────────────────────────────────────────────────
def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    desc = df[numeric_cols].describe().T
    nulls = df[numeric_cols].isna().sum()
    desc["Missing #"] = nulls
    desc["Missing %"] = (nulls / len(df)).round(3) * 100
    return desc.reset_index().rename(columns={"index": "Column"})


@st.cache_data(show_spinner=False)
def missing_heatmap(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(df.isna(), cbar=False, ax=ax)
    ax.set_title("Missing-value pattern")
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# Plot helpers (each cached)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def time_series(df: pd.DataFrame, metric: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(data=df, x="Timestamp", y=metric, hue="Country", ax=ax)
    ax.set_title(f"{metric} over time")
    ax.set_ylabel(f"{metric} (W/m²)")
    return fig


@st.cache_data(show_spinner=False)
def correlation_heatmap(df: pd.DataFrame, metrics: List[str]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(df[metrics].corr(), annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation matrix")
    return fig


@st.cache_data(show_spinner=False)
def scatter_plot(df: pd.DataFrame, x: str, y: str) -> plt.Figure:
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, hue="Country", alpha=0.6, ax=ax)
    ax.set_title(f"{y} vs {x}")
    return fig


@st.cache_data(show_spinner=False)
def wind_rose(df: pd.DataFrame, ws_col: str = "WS", wd_col: str = "WD") -> plt.Figure:
    fig = plt.figure(figsize=(4, 4))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(df[wd_col], df[ws_col], normed=True, opening=0.8, edgecolor="white")
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
        alpha=0.6,
        ax=ax,
    )
    ax.set_title("Tamb vs GHI (bubble ~ RH)")
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# Cross-country stats
# ──────────────────────────────────────────────────────────────────────────────
def compare_stats(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    rows = []
    for m in metrics:
        s = df.groupby("Country")[m].agg(["mean", "median", "std"]).reset_index()
        s.insert(1, "Metric", m)
        rows.append(s)
    return pd.concat(rows, ignore_index=True)


def one_way_anova(df: pd.DataFrame, metric: str) -> float:
    groups = [g[metric].dropna() for _, g in df.groupby("Country")]
    return stats.f_oneway(*groups).pvalue
