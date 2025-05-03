# streamlit_app/app.py

import os
import streamlit as st
from utils.preprocess import load_data, clean_data
from utils.eda_plot import (
    plot_temperature_trend,
    plot_precipitation_distribution,
    plot_extreme_event_trends
)
from utils.agriculture import load_agriculture_data, plot_crop_trends
from utils.biodiversity import load_threatened_data, plot_threatened_trend
from utils.landcover import load_raster_resampled, compute_landcover_change, plot_landcover_change
from utils.climate_model import prepare_yearly_variable, train_forecast_model, plot_forecast
from utils.climate_agri_corr import merge_climate_agriculture, plot_climate_crop_correlation, calculate_correlation
from utils.nlp_tools import load_sample_texts, analyze_sentiment, extract_keywords, plot_wordcloud
from utils.glacier import load_glacier_shapefile, extract_glacier_area_by_year, plot_glacier_retreat
from utils.glacier_weather_corr import summarize_extremes, merge_glacier_weather, plot_weather_vs_glacier

# ─── Load & clean climate data once ────────────────────────────────────────────
csv_path = "Data/Raw/Weather&Climate_data/dailyclimate_OpenDataNpl.csv"
gdrive_file_id = "1WlyTmR7PNXsOsxcdBDfvYrugn3tfyT5f"
df_raw   = load_data(csv_path, gdrive_file_id)
df_clean = clean_data(df_raw)

# ─── Save cleaned climate data (optional) ──────────────────────────────────────
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
    st.markdown("### Data Preview (Daily Climate)")
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
    - Explore climate–agriculture correlations
    - Analyze climate-related news using NLP  
    - Assess glacier retreat over time
    - Investigate extreme weather vs glacier loss  
    """)

# ─── Climate Pages ──────────────────────────────────────────────────────────────

elif page == "Temperature Trend":
    st.subheader("🌡️ Temperature Trend")
    plot_temperature_trend(df_clean)

elif page == "Precipitation Distribution":
    st.subheader("🌧️ Precipitation Distribution")
    plot_precipitation_distribution(df_clean)

elif page == "Extreme Weather Trend":
    st.subheader("⚡ Extreme Weather Trend")
    plot_extreme_event_trends(df_clean)

elif page == "Climate Prediction":
    st.subheader("📈 Climate Forecasting Tool")
    variable = st.selectbox("Select variable:", {
        "Temp_2m": "Temperature (°C)",
        "Precipitation": "Precipitation (mm)",
        "WindSpeed": "Wind Speed (km/h)"
    })
    forecast_year = st.slider("Forecast until year:", 2030, 2050, 2035)
    df_yearly = prepare_yearly_variable(df_clean, variable)
    model, df_forecast = train_forecast_model(df_yearly, forecast_until=forecast_year)
    label = {"Temp_2m":"°C","Precipitation":"mm","WindSpeed":"km/h"}[variable]
    plot_forecast(df_forecast, df_yearly, variable_label=label)
    future_val = df_forecast.loc[df_forecast['Year']==forecast_year, 'Predicted'].iloc[0]
    st.markdown(f"**Forecast for {forecast_year}:** {future_val:.2f} {label}")

# ─── Environment Pages ──────────────────────────────────────────────────────────

elif page == "Biodiversity Trends":
    st.subheader("🦋 Threatened Species Trends")
    df_bio = load_threatened_data("Data/processed/threatened_species_cleaned.csv")
    if df_bio.empty:
        st.warning("No biodiversity data available.")
    else:
        st.dataframe(df_bio.head())
        species = st.multiselect("Select species:", df_bio['Species'].unique().tolist(), default=df_bio['Species'].unique()[:3])
        if species:
            plot_threatened_trend(df_bio, species)

elif page == "Landcover Change":
    st.subheader("🗺️ Landcover Change (2005→2015)")
    lc1,_ = load_raster_resampled("Data/Raw/Environment_data/Landcover_2005_Icimod.tif", scale_factor=10)
    lc2,_ = load_raster_resampled("Data/Raw/Environment_data/Landcover_2015_icimod.tif", scale_factor=10)
    if lc1 is not None and lc2 is not None:
        change_map = compute_landcover_change(lc1, lc2)
        plot_landcover_change(change_map, title="Landcover Change (2005→2015)")
    else:
        st.error("Could not load landcover rasters.")

elif page == "Climate News Trends":
    st.subheader("🗞️ Climate News NLP Analysis")
    texts = load_sample_texts()
    with st.expander("Source Sentences"):
        for s in texts:
            st.write("-", s)
    st.markdown("### Sentiment Analysis")
    st.dataframe(analyze_sentiment(texts))
    st.markdown("### Word Cloud")
    plot_wordcloud(texts)
    st.markdown("#### Keywords")
    st.dataframe(extract_keywords(texts, num_keywords=10))
    st.caption("Source: ReliefWeb – Climate Crisis is a Water Crisis (Nepal)")

elif page == "Glacier Retreat":
    st.subheader("🧊 Glacier Retreat (1980–2010)")
    shp = "Data/Raw/Environment_data/Glacier_data/Glacier_1980_1990_2000_2010.shp"
    gdf = load_glacier_shapefile(shp)
    if gdf.empty:
        st.warning("Glacier shapefile not found.")
    else:
        df_area = extract_glacier_area_by_year(gdf)
        st.dataframe(df_area)
        plot_glacier_retreat(df_area)

elif page == "Extreme Weather vs Glacier Loss":
    st.subheader("🌡️ vs 🧊 Weather vs Glacier Loss")
    shp = "Data/Raw/Environment_data/Glacier_data/Glacier_1980_1990_2000_2010.shp"
    gdf = load_glacier_shapefile(shp)
    if gdf.empty:
        st.warning("Glacier data missing.")
    else:
        df_area = extract_glacier_area_by_year(gdf)
        df_ext = summarize_extremes(df_clean)
        df_merge = merge_glacier_weather(df_area, df_ext)
        if df_merge.empty:
            st.warning("No overlapping years.")
        else:
            st.dataframe(df_merge)
            plot_weather_vs_glacier(df_merge)
            st.caption("Glacier: ICIMOD | Climate: DHM Nepal")

# ─── Socio-Economic Pages ────────────────────────────────────────────────────────

elif page == "Agricultural Trends":
    st.subheader("🌾 Agricultural Trends")
    df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")
    st.dataframe(df_agri.head())
    crops = st.multiselect("Crops:", df_agri.columns[1:].tolist(), default=["Paddy","Maize","Wheat"])
    if crops:
        plot_crop_trends(df_agri, crops)

elif page == "Crop Forecast":
    st.subheader("🌾 Crop Forecasting")
    df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")
    crop = st.selectbox("Select crop:", df_agri.columns[1:].tolist(), index=0)
    year = st.slider("Forecast year:", 2025, 2040, 2035)
    df_c = prepare_yearly_variable(df_agri, crop)  # assuming same util exists
    model, df_fore = train_forecast_model(df_c, forecast_until=year)
    plot_forecast(df_fore, df_c, variable_label=crop)
    val = df_fore.loc[df_fore['Year']==year, 'Predicted'].iloc[0]
    st.markdown(f"**{crop} in {year}:** {val:.2f}")

elif page == "Climate Agriculture Correlation":
    st.subheader("🌿 Climate–Agriculture Correlation Explorer")

    # Load agricultural data
    df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")

    # Select variables
    climate_var = st.selectbox("Climate variable:", ["Temp_2m", "Precipitation"])
    climate_label = "Temperature (°C)" if climate_var == "Temp_2m" else "Precipitation (mm)"

    crop = st.selectbox("Agricultural crop:", df_agri.columns[1:].tolist())

    # Merge datasets and display
    df_merge = merge_climate_agriculture(df_clean, df_agri, climate_var, crop)
    if df_merge.empty:
        st.warning("⚠️ No overlapping years for that variable and crop.")
    else:
        st.dataframe(df_merge.head())
        # Plot correlation
        plot_climate_crop_correlation(df_merge, climate_label)

        # Compute Pearson correlation
        corr = calculate_correlation(df_merge)
        if corr is None:
            st.warning("⚠️ Not enough data points to compute correlation.")
        else:
            st.markdown(f"**Pearson correlation (r):** {corr:.2f}")

            # Short summary based on correlation strength
            if abs(corr) >= 0.7:
                summary = "A strong correlation suggests that changes in the selected climate variable are closely linked to crop yield variations."
            elif abs(corr) >= 0.4:
                summary = "A moderate correlation indicates a noticeable relationship between the climate variable and crop yield."
            else:
                summary = "A weak correlation suggests other factors may play a larger role in influencing crop yield."

            st.markdown(f"**Summary:** {summary}")
