import rasterio
from rasterio.enums import Resampling
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from collections import Counter

def load_raster_resampled(path, target_shape=None, scale_factor=10):
    """
    Loads and resamples a raster to a target shape or using scale factor.
    """
    try:
        with rasterio.open(path) as src:
            if target_shape:
                out_shape = target_shape
            else:
                out_shape = (
                    int(src.height / scale_factor),
                    int(src.width / scale_factor)
                )
            data = src.read(
                1,
                out_shape=out_shape,
                resampling=Resampling.nearest
            )
            return data, src.transform
    except Exception as e:
        st.error(f"❌ Error loading/resampling raster {path}: {e}")
        return None, None

def compute_landcover_transition_matrix(lc1, lc2):
    """
    Computes a matrix of landcover class transitions (e.g., 12→14).
    Returns a DataFrame with transition labels and pixel frequencies.
    """
    if lc1.shape != lc2.shape:
        raise ValueError("Landcover arrays must be the same shape.")

    flat1 = lc1.flatten()
    flat2 = lc2.flatten()

    transitions = [f"{int(a)}→{int(b)}" for a, b in zip(flat1, flat2)]
    counter = Counter(transitions)

    df_trans = pd.DataFrame(counter.items(), columns=["Transition", "Count"])
    df_trans = df_trans.sort_values(by="Count", ascending=False).reset_index(drop=True)

    return df_trans

def plot_landcover_transition_matrix(df_trans):
    """
    Displays the landcover class transition matrix as a bar chart.
    """
    if df_trans.empty:
        st.warning("⚠️ No transitions to display.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df_trans["Transition"], df_trans["Count"], color='teal')
    ax.set_title("🗺️ Landcover Class Transitions (2005 → 2015)")
    ax.set_ylabel("Pixel Count")
    ax.set_xlabel("Transition (Class → Class)")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

    st.markdown("### 🔢 Top Class Transitions")
    st.dataframe(df_trans.head(10))

# (Optional legacy method for difference map)
def compute_landcover_change(lc1, lc2):
    """
    Computes direct difference between two rasters.
    """
    if lc1.shape != lc2.shape:
        raise ValueError("Arrays must have the same shape to compute landcover change.")
    delta = lc2 - lc1
    return delta

def plot_landcover_change(change_array):
    """
    Plots the landcover difference map using diverging color scale.
    """
    if change_array is None or change_array.size == 0:
        st.warning("❌ No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = plt.get_cmap("RdYlBu")
    im = ax.imshow(change_array, cmap=cmap)
    ax.set_title("🗺️ Landcover Change (2005 → 2015)")
    ax.axis("off")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Change in Class Code", rotation=270, labelpad=15)
    st.pyplot(fig)

    st.markdown("### 🔢 Change Class Frequency")
    unique, counts = np.unique(change_array, return_counts=True)
    summary = {int(k): int(v) for k, v in zip(unique, counts)}
    st.json(summary)
