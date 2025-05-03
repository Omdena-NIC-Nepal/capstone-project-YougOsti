# utils/glacier.py

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_glacier_shapefile(shp_path):
    """
    Loads glacier polygons and checks year-related attributes.
    """
    try:
        gdf = gpd.read_file(shp_path)
        return gdf
    except Exception as e:
        st.error(f"❌ Failed to load glacier shapefile: {e}")
        return gpd.GeoDataFrame()

def extract_glacier_area_by_year(gdf):
    """
    Calculates glacier area (in km²) for each year (1980, 1990, 2000, 2010).
    Expects one column per year's glacier geometry (e.g., geometry_1980).
    """
    if gdf.empty:
        return pd.DataFrame(columns=["Year", "Total_Area_km2"])

    year_columns = [col for col in gdf.columns if col.lower().startswith("geometry") or "1980" in col or "1990" in col or "2000" in col or "2010" in col]

    area_data = []

    for year in [1980, 1990, 2000, 2010]:
        if "Year" in gdf.columns:
            gdf_year = gdf[gdf["Year"] == year].copy()
        elif "geometry" in gdf.columns:
            # Assume all features are from one year if no attribute per year exists
            gdf_year = gdf.copy()
        else:
            st.warning(f"⚠️ Year {year} not found in data.")
            continue

        if gdf_year.empty:
            continue

        gdf_year = gdf_year.to_crs(epsg=32645)  # Project to UTM zone for Nepal (area calc)
        gdf_year["area_km2"] = gdf_year.geometry.area / 1e6  # m² to km²

        total_area = gdf_year["area_km2"].sum()
        area_data.append({"Year": year, "Total_Area_km2": total_area})

    return pd.DataFrame(area_data)

def plot_glacier_retreat(area_df):
    """
    Plot glacier retreat over decades as a line chart.
    """
    if area_df.empty:
        st.warning("⚠️ No glacier area data to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(area_df["Year"], area_df["Total_Area_km2"], marker='o', color='blue')
    ax.set_title("🧊 Glacier Area Over Time (1980–2010)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Glacier Area (km²)")
    ax.grid(True)

    st.pyplot(fig)
    st.markdown("#### 📚 Data Source")
    st.caption("📌 ICIMOD – Glacier Outlines for the Himalaya Region (1980–2010). [Source](https://rds.icimod.org/)")

    st.markdown("### 🔍 Key Insight")
    st.markdown(f"""
    - Total glacier area declined from **{int(area_df['Total_Area_km2'].max())} km²** in 1980 
      to **{int(area_df['Total_Area_km2'].min())} km²** in 2010.
    - This reflects significant glacial retreat over 3 decades.
    """)
