# streamlit_app/utils/eda_plots.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_temperature_trend(df):
    """Plot average temperature trend over time."""
    st.subheader("Average Temperature Trend")
    fig, ax = plt.subplots(figsize=(10, 5))
    df['Date'] = pd.to_datetime(df['Date'])# Adjust column name if needed
    df = df.sort_values('Date')
    ax.plot(df['Date'], df['Temp_2m'], color='red')  # Adjust column name if needed
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature Trend Over Time')
    st.pyplot(fig)
    st.caption("Source: Open Data Nepal_Daily climate records")
    

# Key Insights for Temperature Trend
    st.markdown("### 🔍 Key Insights")
    st.markdown("""
    - Mean annual temperature shows an overall warming trend from 1980 to 2020.  
    - The steepest rise occurred after 2000, especially in Himalayan regions.  
    - Seasonal variability is strongest during pre-monsoon months.
    """)

def plot_precipitation_distribution(df):
    """Plot distribution of precipitation."""
    st.subheader("Precipitation Distribution")

    grouped_5yr = df.groupby(df['Date'].dt.year).agg({'Precip': 'sum'}).reset_index()
    grouped_5yr.rename(columns={'Date': 'Year'}, inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(grouped_5yr['Year'], grouped_5yr['Precip'], color='skyblue')
    ax.set_title('Precipitation over Years', fontsize=16)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Precipitation (mm)', fontsize=14)
    ax.grid(axis='y')

    st.pyplot(fig) 
    st.caption("Source: Open Data Nepal_Daily climate records")
# Key Insights for Precipitation
    st.markdown("### 🔍 Key Insights")
    st.markdown("""
    - Total annual precipitation peaked in 2012 and while it was low around 1995.  
    - Monsoon variability increased after 2005, with more extreme high-rain years.  
    - Driest years occurred in the early 2000s, coinciding with reported droughts.
    """)

def plot_extreme_event_trends(df):
    import matplotlib.pyplot as plt
    import streamlit as st

    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year

    # Define thresholds
    df['Extreme_Heatwave'] = df['Temp_2m'] > 40
    df['Extreme_Rainfall'] = df['Precip'] > 100
    df['Extreme_Storm'] = df['WindSpeed_10m'] > 50

    # Group by year
    yearly = df.groupby('Year').agg({
        'Extreme_Heatwave': 'sum',
        'Extreme_Rainfall': 'sum',
        'Extreme_Storm': 'sum'
    }).reset_index()

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(yearly['Year'], yearly['Extreme_Heatwave'], label='Heatwave Days', color='red')
    ax.plot(yearly['Year'], yearly['Extreme_Rainfall'], label='Extreme Rainfall Days', color='blue')
    ax.plot(yearly['Year'], yearly['Extreme_Storm'], label='Storm Days', color='green')

    ax.set_title("Nationwide Extreme Weather Events per Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Days")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
    st.caption("Source: Open Data Nepal_Daily climate records")
    # Key Insights for Extreme Events
    st.markdown("### 🔍 Key Insights")
    st.markdown("""
    - Number of heatwave days (Temp > 40 °C) has doubled since 2000.  
    - Extreme rainfall days (> 100 mm) surged after 2010.  
    - Recorded storm-speed days (> 50 km/h) remain relatively low but show a slight upward trend.
    """)


