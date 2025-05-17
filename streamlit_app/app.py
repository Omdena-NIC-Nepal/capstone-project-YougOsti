import os
import streamlit as st
from utils.preprocess import load_data, clean_data
from utils.download_data import download_all_data
from utils.agriculture import (
    load_agriculture_data, plot_crop_trends, prepare_crop_data, train_crop_model, plot_crop_forecast
)
from utils.climate_agri_corr import merge_climate_agriculture, plot_climate_crop_correlation, calculate_correlation

# ─── Initial Setup ────────────────────────────────────────────────────
# Download all necessary datasets
download_all_data()

# Load climate data
csv_path = "Data/Raw/Weather&Climate_data/dailyclimate_OpenDataNpl.csv"
gdrive_file_id = "1WlyTmR7PNXsOsxcdBDfvYrugn3tfyT5f"
df_raw = load_data(csv_path, gdrive_file_id)
df_clean = clean_data(df_raw)

# Create directory for processed data and save cleaned data
os.makedirs("processed", exist_ok=True)
df_clean.to_csv("processed/cleaned_dailyclimate.csv", index=False)

# ─── Dashboard Selection ──────────────────────────────────────────────
dashboard = st.sidebar.radio("Choose Dashboard", ["Home", "Climate", "Environment", "Socio-Economic"])

# ─── Home ─────────────────────────────────────────────────────────────
if dashboard == "Home":
    st.title("Climate Change Impact Assessment System for Nepal")
    st.success("✅ Data loaded successfully!")
    st.dataframe(df_clean.head())
    st.markdown("### Features")
    st.markdown("""
    - 📈 Climate trends & predictions  
    - 🌾 Crop trends and forecasts  
    - 🦋 Biodiversity & glacier retreat  
    - 🌍 Landcover change  
    - 🔁 Climate–agriculture correlation  
    - 🗞️ NLP from climate reports  
    """)

# ─── Climate ──────────────────────────────────────────────────────────
elif dashboard == "Climate":
    from utils.eda_plot import (
        plot_temperature_trend, plot_precipitation_distribution, plot_extreme_event_trends
    )
    from utils.climate_model import prepare_yearly_variable, train_forecast_model, plot_forecast

    page = st.sidebar.selectbox("Climate Dashboard", [
        "Temperature Trend", "Precipitation Distribution", "Extreme Weather Trend", "Climate Prediction"
    ])

    if page == "Temperature Trend":
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
            "Precip": "Precipitation (mm)",
            "WindSpeed_10m": "Wind Speed (m/s)"
        })
        forecast_year = st.slider("Forecast year:", 2030, 2050, 2035)
        df_yearly = prepare_yearly_variable(df_clean, variable)
        model, df_forecast = train_forecast_model(df_yearly, forecast_until=forecast_year)
        label = {"Temp_2m": "°C", "Precip": "mm", "WindSpeed_10m": "m/s"}[variable]
        plot_forecast(df_forecast, df_yearly, variable_label=label)
        st.markdown(f"**Predicted in {forecast_year}:** {df_forecast.loc[df_forecast['Year']==forecast_year, 'Predicted'].iloc[0]:.2f} {label}")

# ─── Environment ──────────────────────────────────────────────────────
elif dashboard == "Environment":
    try:
        from utils.biodiversity import load_threatened_data, plot_threatened_trend
        from utils.landcover import (
            load_raster_resampled,
            compute_landcover_transition_matrix,
            plot_landcover_transition_matrix
        )
        from utils.glacier import load_glacier_shapefile, extract_glacier_area_by_year, plot_glacier_retreat
        from utils.glacier_weather_corr import summarize_extremes, merge_glacier_weather, plot_weather_vs_glacier
        from utils.nlp_tools import load_sample_texts, analyze_sentiment, extract_keywords, plot_wordcloud
        from utils.download_data import download_from_drive

        page = st.sidebar.selectbox("Environment Dashboard", [
            "Biodiversity Trends", "Landcover Change", "Climate News Trends", "Glacier Retreat", "Extreme Weather vs Glacier Loss"
        ])
    except Exception as e:
        st.error(f"❌ Failed to load environment dashboard: {e}")
        page = None  # fallback

    if page == "Biodiversity Trends":
        st.subheader("🦋 Threatened Species Trends")
        drive_id = "1nulzINJWa03itJJuYgZ-zb_ip9lKhTay"
        local_path = "Data/processed/threatened_species_cleaned.csv"
        download_from_drive(drive_id, local_path)
        df_bio = load_threatened_data(local_path)
        if not df_bio.empty:
            st.dataframe(df_bio.head())
            species = st.multiselect("Select species:", df_bio['Species'].unique(), default=df_bio['Species'].unique()[:3])
            if species:
                plot_threatened_trend(df_bio, species)

    elif page == "Landcover Change":
        st.subheader("🗺️ Landcover Change (2005 → 2015)")
        lc1, _ = load_raster_resampled("Data/Raw/Environment_data/Landcover_2005_Icimod.tif", scale_factor=10)
        if lc1 is not None:
            lc2, _ = load_raster_resampled(
                "Data/Raw/Environment_data/Landcover_2015_icimod.tif",
                target_shape=lc1.shape
            )
        else:
            lc2 = None
        if lc1 is not None and lc2 is not None:
            df_trans = compute_landcover_transition_matrix(lc1, lc2)
            plot_landcover_transition_matrix(df_trans)
        else:
            st.error("❌ Could not load one or both raster files.")

    elif page == "Climate News Trends":
        st.subheader("🗞️ NLP on Climate Reports")
        import nltk
        nltk.download('punkt')  # Ensure that 'punkt' tokenizer is available
        
        texts = load_sample_texts()

        if not texts:
            st.warning("⚠️ No text data available for analysis.")
        else:
            sentiment_df = analyze_sentiment(texts)
            st.dataframe(sentiment_df)

            plot_wordcloud(texts)

            keywords_df = extract_keywords(texts, num_keywords=10)
            st.dataframe(keywords_df)

    elif page == "Glacier Retreat":
        st.subheader("🧊 Glacier Retreat")
        try:
            shp_dir = "Data/Raw/Environment_data/Glacier_data"
            shp_files = [f for f in os.listdir(shp_dir) if f.endswith(".shp")]
            if not shp_files:
                st.error("❌ No shapefile (.shp) found in Glacier_data folder.")
            else:
                shp_path = os.path.join(shp_dir, shp_files[0])
                gdf = load_glacier_shapefile(shp_path)
                if not gdf.empty:
                    area_df = extract_glacier_area_by_year(gdf)
                    st.dataframe(area_df)
                    plot_glacier_retreat(area_df)
        except Exception as e:
            st.error(f"❌ Could not load glacier shapefile: {e}")

    elif page == "Extreme Weather vs Glacier Loss":
        st.subheader("🌡️ Extreme Weather vs Glacier Loss")
        try:
            shp_path = "Data/Raw/Environment_data/Glacier_data/Glacier_1980_1990_2000_2010.shp"
            gdf = load_glacier_shapefile(shp_path)
            if not gdf.empty:
                glacier_df = extract_glacier_area_by_year(gdf)
                climate_summary = summarize_extremes(df_clean)
                merged_df = merge_glacier_weather(glacier_df, climate_summary)
                if not merged_df.empty:
                    st.dataframe(merged_df)
                    plot_weather_vs_glacier(merged_df)
        except Exception as e:
            st.error(f"❌ Could not process Extreme Weather vs Glacier Loss: {e}")

# ─── Socio-Economic ───────────────────────────────────────────────────
elif dashboard == "Socio-Economic":
    page = st.sidebar.selectbox("Socio-Economic Dashboard", [
        "Agricultural Trends", "Crop Forecast", "Climate Agriculture Correlation"
    ])

    if page == "Agricultural Trends":
        st.subheader("🌾 Agricultural Production Trends")
        
        # Load agricultural data
        df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")

        # Print column names and the first few rows to debug
        st.write("Columns in DataFrame:", df_agri.columns)  # Show available column names
        st.dataframe(df_agri.head())  # Display first few rows to check data structure

        # Check available crops and display them (excluding the 'Year' column)
        available_crops = df_agri.columns[1:].tolist()  # Skip 'Year' column
        st.write("Available crops:", available_crops)  # Print available crops to debug

        # Ensure the default crops are in the available crops list
        default_crops = ["Paddy", "Maize", "Wheat"]
        valid_default_crops = [crop for crop in default_crops if crop in available_crops]

        if not valid_default_crops:
            valid_default_crops = available_crops[:3]

        crops = st.multiselect("Choose crops:", available_crops, default=valid_default_crops)

        # Ensure the selected crops have valid data to plot
        if crops:
            selected_data = df_agri[crops]

            if selected_data.isnull().all().any():
                st.warning("⚠️ No valid data available for the selected crops.")
            else:
                plot_crop_trends(df_agri, crops)

    elif page == "Crop Forecast":
        st.subheader("🌾 Crop Forecast")
        df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")
        crop = st.selectbox("Select a crop to forecast:", df_agri.columns[1:])
        year = st.slider("Forecast year:", 2025, 2040, 2035)
        crop_df = prepare_crop_data(df_agri, crop)
        model, all_years = train_crop_model(crop_df, year)
        plot_crop_forecast(all_years, crop_df, crop)

    elif page == "Climate Agriculture Correlation":
        st.subheader("🌿 Climate–Agriculture Correlation")
        df_agri = load_agriculture_data("processed/cleaned_agricultural_data.csv")
        climate_var = st.selectbox("Climate Variable:", ["Temp_2m", "Precip"])
        crop = st.selectbox("Select crop:", df_agri.columns[1:])
        merged_df = merge_climate_agriculture(df_clean, df_agri, climate_var, crop)
        st.dataframe(merged_df.head())

        label_map = {"Temp_2m": "Temperature (°C)", "Precip": "Precipitation (mm)"}
        climate_label = label_map.get(climate_var, climate_var)
        plot_climate_crop_correlation(merged_df, climate_label)

        corr = calculate_correlation(merged_df)
        if corr is not None:
            st.markdown(f"**Pearson r:** {corr:.2f}")
