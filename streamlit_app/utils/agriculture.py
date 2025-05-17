import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.linear_model import LinearRegression

# ─────────────────────────────────────────────────────────────
# ✅ 1. Load and clean agriculture data
# ─────────────────────────────────────────────────────────────

def load_agriculture_data(filepath):
    """
    Loads and processes agricultural production data.
    Transposes to make 'Year' a column and converts '1998/99' → 1998.
    Also cleans up column names.
    """
    try:
        df = pd.read_csv(filepath, index_col=0)

        # Strip leading/trailing whitespaces from column names and ensure no extra metadata
        df.columns = df.columns.str.strip()
        # Remove any column names that may be non-crop metadata (e.g., "oid sha256", "size")
        df = df.loc[:, ~df.columns.str.contains("oid|size", case=False)]

        df = df.transpose()
        df.index.name = "Year"
        df.reset_index(inplace=True)

        # Convert '1998/99' to 1998 (integer)
        df['Year'] = df['Year'].astype(str).str[:4].astype(int)

        # Convert all other columns to numeric where possible
        df = df.apply(pd.to_numeric, errors='ignore')

        return df
    except Exception as e:
        st.error(f"❌ Error loading agricultural data: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────────
# ✅ 2. EDA: Plot selected crop trends
# ─────────────────────────────────────────────────────────────

def plot_crop_trends(df, crops):
    """
    Plots line charts for selected crops over the years.
    """
    if df.empty:
        st.warning("⚠️ No data available to plot.")
        return

    st.subheader("📈 Agricultural Production Trends")

    fig, ax = plt.subplots(figsize=(14, 8))

    for crop in crops:
        if crop in df.columns:
            ax.plot(df['Year'], df[crop], label=crop)
        else:
            st.warning(f"⚠️ Crop '{crop}' not found in data.")

    ax.set_xlabel("Year")
    ax.set_ylabel("Production (in '000 Metric Tons)")
    ax.set_title("Crop-wise Agricultural Production Over Time")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
    st.caption("Source: Nepal Ministry of Agriculture: Annual Crop Production Statistics")

    # Key Insights for Agriculture
    st.markdown("### Key Insights")
    st.markdown("""
    - Paddy and Maize production steadily increased, peaking in 2011/12.  
    - Potato and Vegetable outputs show consistent growth each year.  
    - Spice crops like Ginger saw a three-fold increase from 1998 to 2013.
    """)

# ─────────────────────────────────────────────────────────────
# ✅ 3. Forecast: Prepare, model, and visualize crop prediction
# ─────────────────────────────────────────────────────────────

def prepare_crop_data(df, crop):
    """
    Prepares crop yield data for a given crop.
    Extracts yearly values and converts to numeric.
    """
    try:
        if crop not in df.columns:
            st.error(f"❌ Crop '{crop}' not found in dataset.")
            return None

        crop_data = df[['Year', crop]].dropna().copy()
        crop_data.rename(columns={crop: "Yield"}, inplace=True)
        crop_data["Year"] = crop_data["Year"].astype(int)
        crop_data["Yield"] = crop_data["Yield"].astype(float)
        return crop_data
    except Exception as e:
        st.error(f"❌ Error preparing data for '{crop}': {e}")
        return None

def train_crop_model(crop_df, forecast_until):
    """
    Train linear regression model on crop yield data.
    """
    try:
        X = crop_df[['Year']]
        y = crop_df['Yield']
        
        model = LinearRegression()
        model.fit(X, y)

        future_years = pd.DataFrame({'Year': np.arange(crop_df['Year'].max() + 1, forecast_until + 1)})
        all_years = pd.concat([crop_df[['Year']], future_years], ignore_index=True)
        all_years['Predicted_Yield'] = model.predict(all_years[['Year']])
        
        return model, all_years
    except Exception as e:
        st.error(f"❌ Model training failed: {e}")
        return None, None

def plot_crop_forecast(all_years, historical_df, crop):
    """
    Plot historical and forecasted crop yields.
    """
    if all_years is None or historical_df is None:
        st.error("❌ Cannot plot forecast due to missing data.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(historical_df['Year'], historical_df['Yield'], marker='o', label='Observed')
    ax.plot(all_years['Year'], all_years['Predicted_Yield'], linestyle='--', color='red', label='Predicted')
    
    ax.set_title(f"🌾 {crop} Yield Forecast")
    ax.set_xlabel("Year")
    ax.set_ylabel("Yield (in 000 metric tons)")
    ax.grid(True)
    ax.legend()
    
    st.pyplot(fig)
