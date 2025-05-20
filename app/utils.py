"""
Utility helpers for the Solar Dashboard
---------------------------------------
Loads cleaned CSVs from data/cleaned, aggregates, and provides cached plot
functions to keep main.py tidy.
"""
from pathlib import Path
from typing import List

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
def load_data() -> pd.DataFrame:
    """
    Read benin-clean.csv, sierraleone-clean.csv, togo-clean.csv from
    data/cleaned/ and concatenate with a Country column.
    """
    # Adjust the path so that .parent.parent leads to your_project/ 
    # and then /data/cleaned
    data_path = Path(__file__).parent.parent / "data" / "cleaned"
    files = {
        "Benin": data_path / "benin-clean.csv",
        "Sierra Leone": data_path / "sierraleone-clean.csv",
        "Togo": data_path / "togo-clean.csv",
    }

    frames = []
    for country, path in files.items():
        # For debugging, you can print: print("[DEBUG] Reading:", path)
        df = pd.read_csv(path, parse_dates=["Timestamp"], infer_datetime_format=True)
        df["Country"] = country
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# Quick EDA helpers
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
# Plot helpers (each cached)
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
    sns.scatterplot(data=df, x=x, y=y, hue="Country", alpha=0.6, ax=ax)
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
        alpha=0.6,
        ax=ax,
    )
    ax.set_title("Tamb vs GHI (bubble ~ RH)")
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# Cross-country stats
# ──────────────────────────────────────────────────────────────────────────────
def compare_stats(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
   
