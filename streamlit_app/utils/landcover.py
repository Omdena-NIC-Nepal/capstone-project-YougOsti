# utils/landcover.py

import rasterio
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def load_raster_resampled(file_path, scale_factor=10):
    """
    Load and downsample a single‐band raster by the given scale_factor.
    Returns the smaller array and metadata.
    """
    try:
        with rasterio.open(file_path) as src:
            # Calculate the new shape
            out_height = src.height // scale_factor
            out_width  = src.width  // scale_factor

            # Read and resample in one step
            array = src.read(
                1,
                out_shape=(out_height, out_width),
                resampling=rasterio.enums.Resampling.nearest
            )
            # Update metadata to reflect new shape and transform
            meta = src.meta.copy()
            meta.update({
                "height": out_height,
                "width": out_width,
                "transform": src.transform * src.transform.scale(
                    (src.width  / out_width),
                    (src.height / out_height)
                )
            })
        return array.astype(np.int16), meta

    except Exception as e:
        st.error(f"❌ Error loading/resampling raster {file_path}: {e}")
        return None, None

def compute_landcover_change(array1, array2):
    """
    Compute pixel-wise difference (int16) between two downsampled arrays.
    """
    return (array2.astype(np.int16) - array1.astype(np.int16))

def plot_landcover_change(change_array, title="Landcover Change Map"):
    """
    Visualize the downsampled landcover change array.
    """
    if change_array is None:
        st.error("❌ No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = plt.get_cmap('PiYG')
    cax  = ax.imshow(change_array, cmap=cmap, interpolation='nearest')
    ax.set_title(title)
    ax.axis('off')
    plt.colorbar(cax, ax=ax, fraction=0.036, pad=0.04, label="Δ class")
    st.pyplot(fig)
    st.caption("Source: ICIMOD – Landcover Raster Data (2005, 2015)")

