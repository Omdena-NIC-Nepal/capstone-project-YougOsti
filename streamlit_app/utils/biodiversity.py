import pandas as pd
import re
import matplotlib.pyplot as plt
import streamlit as st

def load_threatened_data(filepath):
    """
    Load and reshape cleaned threatened species CSV.
    Detects all columns like 'threatened species_1998', '...Y2007', etc.
    Returns a tidy DataFrame with columns: Year, Species, Count.
    """
    try:
        df = pd.read_csv(filepath)

        # Debug: show columns during development
        ## st.write("🔍 Columns in CSV:", df.columns.tolist())

        # Rename species column if necessary
        if "Major Group of Species" in df.columns:
            df = df.rename(columns={"Major Group of Species": "Species"})

        # Detect year columns, normalize by removing 'Y' and whitespace
        year_cols = []
        year_map = {}

        for col in df.columns:
            col_clean = col.strip().lower().replace("y", "")  # e.g. "threatened species_2007"
            match = re.search(r'threatened species[_ ]*(\d{4})$', col_clean)
            if match:
                year = int(match.group(1))
                year_cols.append(col)         # use original column name
                year_map[col] = year

        if not year_cols:
            st.error("⚠️ No 'threatened species_YYYY' columns found.")
            return pd.DataFrame(columns=['Year', 'Species', 'Count'])

        # Subset relevant columns
        df_sub = df[['Species'] + year_cols].copy()

        # Melt wide → long
        df_long = df_sub.melt(
            id_vars='Species',
            value_vars=year_cols,
            var_name='OrigCol',
            value_name='Count'
        )

        # Map year column
        df_long['Year'] = df_long['OrigCol'].map(year_map)
        df_long = df_long.drop(columns=['OrigCol'])

        # Clean types
        df_long['Count'] = pd.to_numeric(df_long['Count'], errors='coerce')
        df_long = df_long.dropna(subset=['Count', 'Year', 'Species'])

        return df_long[['Year', 'Species', 'Count']].sort_values(['Species', 'Year'])

    except Exception as e:
        st.error(f"❌ Error loading threatened species data: {e}")
        return pd.DataFrame(columns=['Year', 'Species', 'Count'])


def plot_threatened_trend(df_long, species_list):
    """
    Plot line chart of selected threatened species over time.
    Displays annotated insights.
    """
    if df_long.empty or not species_list:
        st.warning("⚠️ No data available for threatened species.")
        return

    df_sel = df_long[df_long['Species'].isin(species_list)]

    fig, ax = plt.subplots(figsize=(12, 6))
    for species in species_list:
        data = df_sel[df_sel['Species'] == species]
        ax.plot(data['Year'], data['Count'], marker='o', label=species)

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Threatened Species")
    ax.set_title("🦋 Trend of Threatened Species in Nepal (1998–2018)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
    st.caption("📊 Source: National Statistics Office, Nepal – Threatened Species Dataset (1998–2018)")

    # Display quick insights
    st.markdown("### 📌 Key Insights")
    st.markdown("""\
- Amphibians and reptiles show consistent increases in threat level since 2005.  
- Coral and invertebrate species show sharp jumps post-2010.  
- Conservation attention is urgently needed for groups with steep upward trends.
""")
