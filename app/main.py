import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Set up Streamlit page config
st.set_page_config(
    page_title="Solar Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------
# 1) Load data function
# ----------------------------------------
@st.cache_data
def load_data():
    """
    Loads cleaned CSVs for Benin, Sierra Leone, and Togo (or more if desired).
    Returns a single combined DataFrame with a 'Country' column.
    """
    data_path = Path(__file__).parent.parent / "data" / "cleaned"

    # CSV paths
    benin_path        = data_path / "benin-clean.csv"
    sierraleone_path  = data_path / "sierraleone-clean.csv"
    togo_path         = data_path / "togo-clean.csv"

    # Load
    df_benin        = pd.read_csv(benin_path)
    df_sierraleone  = pd.read_csv(sierraleone_path)
    df_togo         = pd.read_csv(togo_path)

    # Tag each dataset
    df_benin['Country']        = 'Benin'
    df_sierraleone['Country']  = 'Sierra Leone'
    df_togo['Country']         = 'Togo'

    # Combine
    combined_df = pd.concat([df_benin, df_sierraleone, df_togo], ignore_index=True)
    return combined_df

# ----------------------------------------
# 2) Main App
# ----------------------------------------
def main():
    st.title("Solar Irradiance Dashboard")

    # Load data
    df = load_data()

    # Sidebar: Country Selection
    all_countries = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select country (or countries):",
        options=all_countries,
        default=all_countries  # default: all
    )

    # Filter data based on selection
    if len(selected_countries) == 0:
        st.warning("No country selected. Please select at least one.")
        return

    filtered_df = df[df['Country'].isin(selected_countries)]

    # Metric selection
    metrics = ["GHI", "DNI", "DHI"]
    selected_metric = st.sidebar.selectbox(
        "Select a metric for boxplot:",
        options=metrics,
        index=0
    )

    # ----------------------------------------
    # Boxplot of chosen metric
    # ----------------------------------------
    st.subheader(f"Boxplot: {selected_metric}")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(
        x="Country",
        y=selected_metric,
        data=filtered_df,
        palette="Set2"
    )
    ax.set_title(f"{selected_metric} Distribution by Country")
    ax.set_ylabel(f"{selected_metric} (W/m²)")
    st.pyplot(fig)

    # ----------------------------------------
    # Table of top-average-GHI countries
    # ----------------------------------------
    st.subheader("Countries Ranked by Average GHI")
    avg_ghi = (
        df.groupby('Country')['GHI']
          .mean()
          .sort_values(ascending=False)
          .reset_index(name="Mean GHI")
    )
    st.table(avg_ghi)

    # ----------------------------------------
    # Additional optional elements
    # ----------------------------------------
    st.markdown("""
    **Observations**:  
    - Choose different countries in the sidebar to see how the boxplots change.  
    - The table above shows overall average GHI across all data points per country.  
    - Add more interactive plots or summary stats to extend functionality.
    """)

if __name__ == "__main__":
    main()
