# streamlit_app/utils/climate_agri_corr.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def merge_climate_agriculture(df_climate: pd.DataFrame,
                              df_agri: pd.DataFrame,
                              climate_var: str,
                              crop: str) -> pd.DataFrame:
    """
    Merge annual aggregated climate variable with agricultural crop yield by year.

    Parameters
    ----------
    df_climate : pd.DataFrame
        Daily climate data with 'Date', 'Temp_2m', 'Precipitation', etc.
    df_agri : pd.DataFrame
        Agricultural data with columns ['Year', <crop1>, <crop2>, ...].
    climate_var : str
        Which climate variable to use: 'Temp_2m' or 'Precipitation'.
    crop : str
        Name of one crop column in df_agri.

    Returns
    -------
    pd.DataFrame
        ['Year', 'Climate_Value', 'Crop_Yield'] merged on Year.
    """
    df = df_climate.copy()
    df['Year'] = df['Date'].dt.year

    # Aggregate climate by year
    if climate_var == 'Temp_2m':
        climate_agg = df.groupby('Year')['Temp_2m'] \
                      .mean().reset_index(name='Climate_Value')
    elif climate_var == 'Precipitation':
        climate_agg = df.groupby('Year')['Precipitation'] \
                      .sum().reset_index(name='Climate_Value')
    else:
        raise ValueError("climate_var must be 'Temp_2m' or 'Precipitation'")

    # Check agri
    if 'Year' not in df_agri.columns or crop not in df_agri.columns:
        raise ValueError("df_agri must contain 'Year' and the specified crop column")

    agri_subset = df_agri[['Year', crop]].rename(columns={crop: 'Crop_Yield'})

    # Merge
    merged = pd.merge(climate_agg, agri_subset, on='Year', how='inner')
    return merged

def plot_climate_crop_correlation(df_merged: pd.DataFrame, climate_var_label: str):
    """
    Scatter + regression of Climate_Value vs Crop_Yield.

    Parameters
    ----------
    df_merged : pd.DataFrame
        Output of merge_climate_agriculture.
    climate_var_label : str
        Friendly label for the climate variable (e.g. "Temperature (°C)").
    """
    st.subheader(f"🌿 {climate_var_label} vs Crop Yield")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(data=df_merged, x='Climate_Value', y='Crop_Yield', ax=ax)
    ax.set_xlabel(climate_var_label)
    ax.set_ylabel("Crop Yield")
    ax.set_title(f"{climate_var_label} vs Crop Yield")
    st.pyplot(fig)

def calculate_correlation(df_merged: pd.DataFrame) -> float:
    """
    Compute Pearson correlation between Climate_Value and Crop_Yield.

    Parameters
    ----------
    df_merged : pd.DataFrame
        Output of merge_climate_agriculture.

    Returns
    -------
    float
        Pearson r (or None if insufficient data).
    """
    if df_merged.shape[0] < 2:
        return None
    return df_merged['Climate_Value'].corr(df_merged['Crop_Yield'])
