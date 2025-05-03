# utils/climate_agri_corr.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
import numpy as np

def merge_climate_agriculture(df_climate, df_agri, climate_col, crop_col):
    """
    Merges annual climate averages and crop yields by year.
    """
    try:
        # Prepare climate data (yearly average)
        df_climate['Year'] = df_climate['Date'].dt.year
        df_climate_yearly = df_climate.groupby('Year')[climate_col].mean().reset_index()

        # Prepare agriculture data (already has Year column)
        df_agri_sel = df_agri[['Year', crop_col]].copy()
        df_agri_sel.rename(columns={crop_col: "Crop_Yield"}, inplace=True)

        # Merge on Year
        df_merged = pd.merge(df_climate_yearly, df_agri_sel, on='Year', how='inner')

        return df_merged
    except Exception as e:
        st.error(f"Error merging data: {e}")
        return pd.DataFrame()

def plot_climate_crop_correlation(df_merged, climate_col, crop_col):
    """
    Scatter plot with regression line showing crop vs. climate variable.
    """
    if df_merged.empty:
        st.warning("No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(
        data=df_merged,
        x=climate_col,
        y="Crop_Yield",
        ax=ax,
        scatter_kws={"s": 60, "alpha": 0.8},
        line_kws={"color": "red"}
    )

    ax.set_title(f"📈 {crop_col} vs. {climate_col}")
    ax.set_xlabel(f"{climate_col}")
    ax.set_ylabel("Crop Yield (in 000 MT)")
    ax.grid(True)

    st.pyplot(fig)
    st.caption("Sources: Climate – Open Data Nepal; Crop Yields – Ministry of Agriculture")


def calculate_correlation(df_merged, climate_col):
    """
    Calculate and display Pearson correlation between climate variable and crop yield.
    """
    try:
        r, p = pearsonr(df_merged[climate_col], df_merged["Crop_Yield"])
        st.markdown(f"### Correlation Coefficient: **r = {r:.3f}**")
        if abs(r) >= 0.7:
            st.success("Strong correlation")
        elif abs(r) >= 0.4:
            st.info("Moderate correlation")
        else:
            st.warning("Weak or no linear correlation")

        st.markdown(f"**p-value = {p:.4f}** — {'statistically significant' if p < 0.05 else 'not significant'}")
    except Exception as e:
        st.error(f"❌ Error calculating correlation: {e}")
