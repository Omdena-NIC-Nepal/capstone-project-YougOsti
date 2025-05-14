import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def summarize_extremes(df_climate):
    """
    Returns annual max temperature and precipitation for key glacier years.
    """
    try:
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

    except Exception as e:
        st.error(f"❌ Error summarizing extreme weather data: {e}")
        return None

def merge_glacier_weather(glacier_df, climate_summary):
    """
    Merge glacier area and extreme weather by year.
    """
    try:
        # Merge the glacier and climate data on 'Year'
        merged_df = pd.merge(glacier_df, climate_summary, on='Year', how='inner')
        return merged_df

    except Exception as e:
        st.error(f"❌ Error merging glacier and weather data: {e}")
        return None

def plot_weather_vs_glacier(df_merged):
    """
    Scatter plots and correlation between weather extremes and glacier area.
    """
    if df_merged is None or df_merged.empty:
        st.error("❌ No data to plot.")
        return

    st.subheader("Extreme Weather vs Glacier Area")

    # Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot max temperature vs glacier area
    sns.regplot(data=df_merged, x='Max_Temp', y='Total_Area_km2', ax=axes[0], color='red')
    axes[0].set_title("Max Temperature vs Glacier Area")
    axes[0].set_xlabel("Max Temperature (°C)")
    axes[0].set_ylabel("Glacier Area (km²)")

    # Plot max precipitation vs glacier area
    sns.regplot(data=df_merged, x='Max_Precip', y='Total_Area_km2', ax=axes[1], color='blue')
    axes[1].set_title("Max Precipitation vs Glacier Area")
    axes[1].set_xlabel("Max Precipitation (mm)")
    axes[1].set_ylabel("Glacier Area (km²)")

    # Display the plots in Streamlit
    st.pyplot(fig)

    # Calculate and display correlations
    corr_temp = df_merged['Max_Temp'].corr(df_merged['Total_Area_km2'])
    corr_precip = df_merged['Max_Precip'].corr(df_merged['Total_Area_km2'])

    st.markdown("### Correlation Insights")
    st.markdown(f"""
    - 📈 **Correlation between max temperature and glacier area**: **{corr_temp:.2f}**  
    - 🌧️ **Correlation between max precipitation and glacier area**: **{corr_precip:.2f}**
    """)

    # Add context for the plots
    st.markdown("### What These Plots Show")
    st.markdown("""
    - The plots show how glacier area has changed in relation to extreme weather conditions (maximum temperature and precipitation).
    - The **regression line** (trendline) helps to visualize whether there's a relationship between temperature or precipitation and glacier area:
        - A **downward-sloping line** suggests that higher temperature or precipitation is linked to a **smaller glacier area**.
        - A **steeper slope** indicates a **stronger effect** of the weather variable on glacier shrinkage.
    - These plots can help assess whether **climate extremes are contributing to glacier retreat** in Nepal.
    """)

    # Optional: Add a more visual explanation of the correlation strength
    if corr_temp < -0.5:
        st.markdown("⚠️ **Strong negative correlation** between max temperature and glacier area. Higher temperatures are likely linked to glacier retreat.")
    elif corr_temp > 0.5:
        st.markdown("👍 **Strong positive correlation** between max temperature and glacier area.")
    
    if corr_precip < -0.5:
        st.markdown("⚠️ **Strong negative correlation** between max precipitation and glacier area. Higher precipitation might be associated with glacier shrinkage.")
    elif corr_precip > 0.5:
        st.markdown("👍 **Strong positive correlation** between max precipitation and glacier area.")
