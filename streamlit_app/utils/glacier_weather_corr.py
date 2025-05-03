# utils/glacier_weather_corr.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def summarize_extremes(df_climate):
    """
    Returns annual max temperature and precipitation for key glacier years.
    """
    df = df_climate.copy()
    df['Year'] = df['Date'].dt.year

    # Use 'Precip' instead of 'Precipitation'
    summary = df.groupby('Year').agg({
        'MaxTemp_2m': 'max',   # Maximum temperature in a year
        'Precip': 'max'        # Maximum precipitation in a year
    }).reset_index()

    summary.rename(columns={
        'MaxTemp_2m': 'Max_Temp',
        'Precip': 'Max_Precip'
    }, inplace=True)

    # Keep only glacier years
    glacier_years = [1980, 1990, 2000, 2010]
    summary = summary[summary['Year'].isin(glacier_years)]

    return summary

def merge_glacier_weather(glacier_df, climate_summary):
    """
    Merge glacier area and extreme weather by year.
    """
    return pd.merge(glacier_df, climate_summary, on='Year', how='inner')

def plot_weather_vs_glacier(df_merged):
    """
    Scatter plots and correlation between weather extremes and glacier area.
    """
    st.subheader("Extreme Weather vs Glacier Area")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    sns.regplot(data=df_merged, x='Max_Temp', y='Total_Area_km2', ax=axes[0], color='red')
    axes[0].set_title("Max Temperature vs Glacier Area")
    axes[0].set_xlabel("Max Temperature (°C)")
    axes[0].set_ylabel("Glacier Area (km²)")

    sns.regplot(data=df_merged, x='Max_Precip', y='Total_Area_km2', ax=axes[1], color='blue')
    axes[1].set_title("Max Precipitation vs Glacier Area")
    axes[1].set_xlabel("Max Precipitation (mm)")
    axes[1].set_ylabel("Glacier Area (km²)")

    st.pyplot(fig)

    # Correlation summary
    corr_temp = df_merged['Max_Temp'].corr(df_merged['Total_Area_km2'])
    corr_precip = df_merged['Max_Precip'].corr(df_merged['Total_Area_km2'])

    st.markdown("### Correlation Insights")
    st.markdown(f"""
    - 📈 Correlation between **max temperature** and glacier area: **{corr_temp:.2f}**  
    - 🌧️ Correlation between **max precipitation** and glacier area: **{corr_precip:.2f}**
    """)
    st.markdown("### What These Plots Show")
    st.markdown("""
    - Each ** plot** shows how glacier area has changed in relation to **extreme weather conditions** (maximum temperature and maximum precipitation).
    - The **trendline** (regression line) helps visualize whether there's a positive or negative relationship:
        - A **downward-sloping line** means that higher temperature or precipitation is linked to **smaller glacier area**.
        - A **steeper slope** suggests a **stronger effect** of that weather variable on glacier loss.
    - This can help assess whether **climate extremes are accelerating glacier retreat** in Nepal.
    """)
