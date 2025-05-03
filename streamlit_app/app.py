# streamlit_app/app.py

import os
import streamlit as st
import pandas as pd

from utils.preprocess import load_data, clean_data
from utils.eda_plot import plot_temperature_trend, plot_precipitation_distribution
from utils.eda_plot import plot_extreme_event_trends  # assuming it’s defined there
from utils.agriculture import load_agriculture_data, plot_crop_trends
from utils.biodiversity import load_threatened_data, plot_threatened_trend
from utils.landcover import load_raster_resampled, compute_landcover_change, plot_landcover_change

# ─── Load & clean climate data once ────────────────────────────────────────────
from utils.download_data import download_all_data

# Ensure data is available
download_all_data()

csv_path = "Data/Raw/Weather&Climate_data/dailyclimate_OpenDataNpl.csv"
df_raw   = load_data(csv_path)
df_clean = clean_data(df_raw)

# ─── cleaned climate data  ────────────────────────────────────
processed_folder = "processed"
os.makedirs(processed_folder, exist_ok=True)
df_clean.to_csv(os.path.join(processed_folder, "cleaned_dailyclimate.csv"), index=False)

# ─── Sidebar: Select dashboard category ─────────────────────────────────────────
dashboard = st.sidebar.radio(
    "Choose Dashboard",
    ["Home", "Climate", "Environment", "Socio-Economic"]
)

# ─── Sidebar: Select page within category ──────────────────────────────────────
if dashboard == "Home":
    page = "Home"
   

elif dashboard == "Climate":
    page = st.sidebar.selectbox(
        "Climate Dashboard",
        [
            "Temperature Trend",
            "Precipitation Distribution",
            "Extreme Weather Trend",
            "Climate Prediction"
        ]
    )


elif dashboard == "Environment":
    page = st.sidebar.selectbox(
        "Environment Dashboard",
        [
            "Biodiversity Trends",
            "Landcover Change",
            "Climate News Trends",
            "Glacier Retreat",
            "Extreme Weather vs Glacier Loss"
        ]
    )

else:  # Socio-Economic
    page = st.sidebar.selectbox(
        "Socio-Economic Dashboard",
        ["Agricultural Trends", "Crop Forecast", "Climate Agriculture Correlation"]
    )

# ─── Main Content ────────────────────────────────────────────────────────────────
if page == "Home":
    st.title("Climate Change Impact Assessment System for Nepal")
    st.success("✅ Climate data loaded and cleaned successfully!")
    st.markdown("###  Data Preview (Daily Climate)")
    st.dataframe(df_clean.head())
    st.markdown("#### Dashboard Features")
    st.markdown("""
    - Visualize temperature and precipitation trends  
    - Explore extreme weather events  
    - Analyze agricultural production patterns  
    - Track threatened species trends  
    - Detect landcover change 
    - Forecast future climate variables
    - Predict crop yields
    - Shows correlation between climate and agriculture
    - Analyze climate-related news using NLP techniques 
    - Assess glacier retreat over time
    - Investigate the impact of extreme weather on glacier loss  
    """)

# ─── Climate Pages ──────────────────────────────────────────────────────────────
elif page == "Temperature Trend":
    st.subheader("Temperature Trend")
    plot_temperature_trend(df_clean)
    
elif page == "Precipitation Distribution":
    st.subheader("🌧️ Precipitation Distribution")
    plot_precipitation_distribution(df_clean)

elif page == "Extreme Weather Trend":
    st.subheader("Extreme Weather Trend")
    plot_extreme_event_trends(df_clean)

# ─── Environment Pages ──────────────────────────────────────────────────────────
elif page == "Biodiversity Trends":
    st.subheader("Threatened Species Trends")
    df_bio = load_threatened_data("Data/processed/threatened_species_cleaned.csv")
    if not df_bio.empty:
        st.dataframe(df_bio.head())
        species = st.multiselect(
            "Select species to plot:",
            sorted(df_bio['Species'].unique()),
            default=sorted(df_bio['Species'].unique())[:3]
        )
        if species:
            plot_threatened_trend(df_bio, species)
    else:
        st.warning("⚠️ No biodiversity data available.")

elif page == "Landcover Change":
    st.subheader("Landcover Change Detection (2005 → 2015)")
    lc1, _ = load_raster_resampled("Data/Raw/Environment_data/Landcover_2005_Icimod.tif", scale_factor=10)
    lc2, _ = load_raster_resampled("Data/Raw/Environment_data/Landcover_2015_icimod.tif", scale_factor=10)
    if lc1 is not None and lc2 is not None:
        change_map = compute_landcover_change(lc1, lc2)
        plot_landcover_change(change_map, title="Landcover Change (2005→2015)")
        st.markdown("### Key Insights")
        st.markdown("""
        - Downsampled by 10× for performance.  
        - Warm colors = increased class code; cool = decreased; white = no change.  
        - Use this overview to locate hotspots for deeper analysis.
        """)
    else:
        st.error("❌ Could not load/process landcover rasters.")

# ─── Socio-Economic Pages ───────────────────────────────────────────────────────
elif page == "Agricultural Trends":
    st.subheader("🌾 Agricultural Production Trends")
    df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")
    st.dataframe(df_agri.head())
    crops = st.multiselect(
        "Select crops to plot:",
        list(df_agri.columns[1:]),
        default=["Paddy", "Maize", "Wheat"]
    )
    if crops:
        plot_crop_trends(df_agri, crops)
        
elif page == "Climate Prediction":
    from utils.climate_model import prepare_yearly_variable, train_forecast_model, plot_forecast

    st.subheader("📈 Climate Forecasting Tool")

    # User selects variable to forecast
    variable = st.selectbox("Choose variable to predict:", {
        "Temp_2m": "Average Temperature (°C)",
        "Precipitation": "Total Precipitation (mm)",
        "WindSpeed": "Wind Speed (km/h)"
    })

    # Forecast horizon
    forecast_year = st.slider("Select forecast horizon (final year):", 2030, 2050, 2035)

    # Prepare and model
    df_yearly = prepare_yearly_variable(df_clean, variable)
    model, df_forecast = train_forecast_model(df_yearly, forecast_until=forecast_year)

    # Plot
    label = dict(Temp_2m="Temperature (°C)", Precipitation="Precipitation (mm)", WindSpeed="Wind Speed (km/h)")[variable]
    plot_forecast(df_forecast, df_yearly, variable_label=label)

    # Summary
    future_val = df_forecast[df_forecast['Year'] == forecast_year]['Predicted'].values[0]
    st.markdown("### Forecast Summary")
    st.markdown(f"""
    - Data used: **{df_yearly['Year'].min()} to {df_yearly['Year'].max()}**
    - Forecasted up to **{forecast_year}**
    - Predicted value in {forecast_year}: **{future_val:.2f} {label.split()[0]}**
    """)
elif page == "Crop Forecast":
    from utils.agriculture import prepare_crop_data, train_crop_model, plot_crop_forecast

    st.subheader("🌾 Crop Yield Forecasting")

    agri_path = "processed/cleaned_agricultural_data.csv"
    df_agri = load_agriculture_data(agri_path)

    crop_list = list(df_agri.columns[1:])  # Exclude "Year"
    selected_crop = st.selectbox("Select a crop to forecast:", crop_list, index=crop_list.index("Paddy"))

    forecast_year = st.slider("Select forecast year (up to):", 2025, 2040, 2035)

    crop_df = prepare_crop_data(df_agri, selected_crop)
    if crop_df is not None:
        model, all_years = train_crop_model(crop_df, forecast_year)
        plot_crop_forecast(all_years, crop_df, selected_crop)

        # Summary
        future_val = all_years[all_years['Year'] == forecast_year]['Predicted_Yield'].values[0]
        st.markdown("### Forecast Summary")
        st.markdown(f"""
        - Forecasting crop: **{selected_crop}**  
        - Observed range: **{crop_df['Year'].min()}–{crop_df['Year'].max()}**  
        - Forecasted up to **{forecast_year}**  
        - Predicted yield in {forecast_year}: **{future_val:.2f} thousand metric tons**
        """)
elif page == "Climate Agriculture Correlation":
    from utils.climate_agri_corr import merge_climate_agriculture, plot_climate_crop_correlation, calculate_correlation
    from utils.agriculture import load_agriculture_data

    st.subheader("🌿 Climate–Agriculture Correlation Explorer")

    # Load agri and climate data
    df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")

    climate_variable = st.selectbox("Select climate variable:", ["Temp_2m", "Precipitation"])
    crop = st.selectbox("Select agricultural crop:", list(df_agri.columns[1:]))

    df_merged = merge_climate_agriculture(df_clean, df_agri, climate_variable, crop)

    if not df_merged.empty:
        st.dataframe(df_merged.head())
        plot_climate_crop_correlation(df_merged, climate_variable, crop)
        calculate_correlation(df_merged, climate_variable)
elif page == "Climate News Trends":
    from utils.nlp_tools import load_sample_texts, analyze_sentiment, extract_keywords, plot_wordcloud

    st.subheader("🗞️ NLP Analysis of Climate-Related News and Reports")

    # Load climate-related sentences
    texts = load_sample_texts()

    # Display source sentences
    with st.expander("Climate-Related Report Sentences"):
        for sentence in texts:
            st.markdown(f"- {sentence}")

    # Sentiment Analysis
    st.markdown("### Sentiment Analysis")
    df_sentiment = analyze_sentiment(texts)
    st.dataframe(df_sentiment)

    # Word Cloud
    st.markdown("### ☁️ Word Cloud of Report Keywords")
    plot_wordcloud(texts)

    # Keyword Frequency
    st.markdown("###  Most Frequent Keywords")
    df_keywords = extract_keywords(texts, num_keywords=10)
    st.dataframe(df_keywords)

    # Source citation
    st.markdown("#### Data Source")
    st.caption("Adapted from: [ReliefWeb – Climate Crisis is a Water Crisis (Nepal)](https://reliefweb.int/report/nepal/climate-crisis-water-crisis)")


elif page == "Glacier Retreat":
    from utils.glacier import load_glacier_shapefile, extract_glacier_area_by_year, plot_glacier_retreat

    st.subheader("Glacier Retreat Analysis (1980–2010)")

    shp_path = "Data/Raw/Environment_data/Glacier_data/Glacier_1980_1990_2000_2010.shp"
    st.write("📁 Shapefile path:", shp_path)
    st.write("🔍 File exists:", os.path.exists(shp_path))

    gdf = load_glacier_shapefile(shp_path)

    if not gdf.empty:
        st.write("🗺️ Shapefile loaded. Columns:")
        st.write(gdf.columns)
        area_df = extract_glacier_area_by_year(gdf)
        st.dataframe(area_df)
        plot_glacier_retreat(area_df)
    else:
        st.warning("⚠️ Glacier shapefile could not be loaded.")

elif page == "Extreme Weather vs Glacier Loss":
    from utils.glacier import load_glacier_shapefile, extract_glacier_area_by_year
    from utils.glacier_weather_corr import summarize_extremes, merge_glacier_weather, plot_weather_vs_glacier


    st.subheader("🌡️ Effect of Extreme Weather on Glacier Retreat")

    shp_path = "Data/Raw/Environment_data/Glacier_data/Glacier_1980_1990_2000_2010.shp"
    gdf = load_glacier_shapefile(shp_path)

    if not gdf.empty:
        glacier_df = extract_glacier_area_by_year(gdf)
        climate_summary = summarize_extremes(df_clean)

        df_merged = merge_glacier_weather(glacier_df, climate_summary)

        if not df_merged.empty:
            st.markdown("### 🔗 Merged Glacier & Weather Data")
            st.dataframe(df_merged)

            plot_weather_vs_glacier(df_merged)

            st.markdown("#### Data Sources")
            st.caption("Glacier data: ICIMOD (1980–2010)  \n Climate data: Department of Hydrology and Meteorology, Nepal")
        else:
            st.warning("⚠️ No overlapping years between glacier and climate data.")
    else:
        st.error("❌ Could not load glacier shapefile.")


