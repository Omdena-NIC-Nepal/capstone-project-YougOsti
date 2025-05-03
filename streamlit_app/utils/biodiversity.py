# utils/biodiversity.py

import pandas as pd
import re
import matplotlib.pyplot as plt
import streamlit as st

def load_threatened_data(filepath):
    """
    Load and reshape cleaned threatened species CSV.
    Keeps only columns matching 'threatened species_YYYY' pattern,
    extracts year, and returns a tidy DataFrame with columns:
    Year (int), Species (str), Count (float).
    """
    try:
        df = pd.read_csv(filepath)

        # Identify threatened-species columns and extract years
        pattern = re.compile(r'threatened species_(\d{4})$', re.IGNORECASE)
        year_cols = []
        year_map = {}
        for col in df.columns:
            m = pattern.search(col)
            if m:
                yr = int(m.group(1))
                year_cols.append(col)
                year_map[col] = yr

        if not year_cols:
            st.error("⚠️ No 'threatened species_YYYY' columns found.")
            return pd.DataFrame(columns=['Year', 'Species', 'Count'])

        # Keep only Species + threatened-species columns
        df_sub = df[['Species'] + year_cols].copy()

        # Melt to long format
        df_long = df_sub.melt(
            id_vars='Species',
            value_vars=year_cols,
            var_name='OrigCol',
            value_name='Count'
        )

        # Map original column names to Year
        df_long['Year'] = df_long['OrigCol'].map(year_map)

        # Clean up
        df_long = df_long.drop(columns=['OrigCol'])
        df_long['Count'] = pd.to_numeric(df_long['Count'], errors='coerce')
        df_long = df_long.dropna(subset=['Count', 'Year', 'Species'])
        df_long = df_long.sort_values(['Species', 'Year'])

        return df_long[['Year', 'Species', 'Count']]

    except Exception as e:
        st.error(f"❌ Error loading threatened species data: {e}")
        return pd.DataFrame(columns=['Year', 'Species', 'Count'])

def plot_threatened_trend(df_long, species_list):
    """
    Plot line chart of selected threatened species over time.
    Also displays static insights summary.
    """
    if df_long.empty:
        st.warning("⚠️ No data available for threatened species.")
        return

    df_sel = df_long[df_long['Species'].isin(species_list)]

    fig, ax = plt.subplots(figsize=(12, 6))
    for species in species_list:
        data = df_sel[df_sel['Species'] == species]
        ax.plot(data['Year'], data['Count'], marker='o', label=species)

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Threatened Species")
    ax.set_title("Trend of Threatened Species in Nepal (1998–2018)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
    st.caption("Source: National Statistics Office, Nepal – Threatened Species Dataset (1998–2018)")


    # ✅ Now inside the plotting function
    st.markdown("### Key Insights")
    st.markdown("""
    - Some species show steep increases in threatened counts after 2010.  
    - Amphibians and reptiles have the highest rate of increase.  
    - Corals remained relatively stable until 2008, then spiked.
    """)
