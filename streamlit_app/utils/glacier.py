import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_glacier_shapefile(shp_path):
    """
    Loads the glacier shapefile and checks for geometry and year columns.
    Displays basic info to help debug structure mismatches.
    """
    try:
        gdf = gpd.read_file(shp_path)

        if gdf.empty:
            st.warning("⚠️ The shapefile is empty or could not be loaded properly.")

        if gdf.geometry.is_empty.all():
            st.warning("⚠️ All geometries are empty.")

        # Show available columns to help with debugging
        st.markdown("### 🔍 Glacier Shapefile Columns")
        st.write(gdf.columns)

        # Preview first few rows
        st.markdown("### 🗂️ Sample Data")
        st.write(gdf.head())

        # Try to detect the year column
        possible_year_cols = [col for col in gdf.columns if "year" in col.lower()]
        if possible_year_cols:
            st.success(f"✅ Detected year column: `{possible_year_cols[0]}`")
        else:
            st.warning("⚠️ No column related to year was detected.")

        return gdf

    except Exception as e:
        st.error(f"❌ Failed to load glacier shapefile: {e}")
        return gpd.GeoDataFrame()

def extract_glacier_area_by_year(gdf):
    """
    Calculates total glacier area (in km²) for each target year.
    Works on GeoDataFrames with one geometry column and a year attribute column.
    """
    if gdf.empty:
        return pd.DataFrame(columns=["Year", "Total_Area_km2"])

    # Try to find a column with year info
    possible_year_cols = [col for col in gdf.columns if "year" in col.lower()]
    if not possible_year_cols:
        st.error("❌ No column containing year information found.")
        return pd.DataFrame(columns=["Year", "Total_Area_km2"])

    year_col = possible_year_cols[0]

    target_years = [1980, 1990, 2000, 2010]
    area_data = []

    for year in target_years:
        subset = gdf[gdf[year_col] == year]
        if subset.empty:
            st.warning(f"⚠️ Year {year} not found in the data.")
            continue

        subset = subset.to_crs(epsg=32645)  # Project to UTM for area calculation
        subset["area_km2"] = subset.geometry.area / 1e6
        total_area = subset["area_km2"].sum()

        area_data.append({"Year": year, "Total_Area_km2": total_area})

    return pd.DataFrame(area_data)

def plot_glacier_retreat(area_df):
    """
    Plots the change in glacier area over decades as a line chart.
    """
    if area_df.empty:
        st.warning("⚠️ No glacier area data to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(area_df["Year"], area_df["Total_Area_km2"], marker='o', color='blue', label="Glacier Area")

    ax.set_title("🧊 Glacier Area Over Time (1980–2010)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Glacier Area (km²)")
    ax.grid(True)

    st.pyplot(fig)

    # Add extra insights
    st.markdown("#### 📚 Data Source")
    st.caption("📌 ICIMOD – Glacier Outlines for the Himalaya Region (1980–2010). [Source](https://rds.icimod.org/)")

    st.markdown("### 🔍 Key Insights:")
    st.markdown(f"""
    - Total glacier area declined from **{int(area_df['Total_Area_km2'].max())} km²** in 1980  
      to **{int(area_df['Total_Area_km2'].min())} km²** in 2010.
    - This reflects significant glacial retreat over the 3 decades.
    """)
