import rasterio 
from rasterio.enums import Resampling
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

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

def compute_landcover_change(lc1, lc2):
    """
    Computes difference between two landcover arrays.
    Assumes classes are integers and of same shape.
    """
    if lc1.shape != lc2.shape:
        raise ValueError("Arrays must have the same shape to compute landcover change.")

    delta = lc2 - lc1  # simple subtraction (change detection)
    return delta

def plot_landcover_change(change_array):
    """
    Plots the landcover change map with a simple diverging color scale.
    """
    if change_array is None or change_array.size == 0:
        st.warning("❌ No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = plt.get_cmap("RdYlBu")  # Red = loss, Blue = gain
    im = ax.imshow(change_array, cmap=cmap)
    ax.set_title("🗺️ Landcover Change (2005 → 2015)")
    ax.axis("off")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Change in Class Code", rotation=270, labelpad=15)
    st.pyplot(fig)

    # Optional: Summary table
    st.markdown("### 🔢 Change Class Frequency")
    unique, counts = np.unique(change_array, return_counts=True)
    summary = {int(k): int(v) for k, v in zip(unique, counts)}
    st.json(summary)
