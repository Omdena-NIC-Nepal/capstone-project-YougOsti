import gdown
import streamlit as st
import os
import zipfile
import rasterio
from rasterio.errors import RasterioIOError

def is_valid_tif(path):
    """Check if the file is a valid GeoTIFF."""
    try:
        with rasterio.open(path) as src:
            return True
    except RasterioIOError:
        return False

def download_from_drive(file_id, output_path, verbose=False):
    """
    Download file from Google Drive if missing or invalid.
    Skips if the file already exists and is valid (for TIFFs or CSVs).
    """
    url = f"https://drive.google.com/uc?id={file_id}"
    dir_name = os.path.dirname(output_path)
    
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    # Check if the file already exists and is valid
    if os.path.exists(output_path):
        too_small = os.path.getsize(output_path) < 100
        invalid_tif = output_path.endswith(".tif") and not is_valid_tif(output_path)

        if too_small or invalid_tif:
            if verbose:
                st.warning(f"⚠️ Replacing invalid or tiny file: {os.path.basename(output_path)}")
            os.remove(output_path)
        else:
            if verbose:
                st.success(f"✅ {os.path.basename(output_path)} already exists; skipping download.")
            return

    # Download the file
    gdown.download(url, output_path, quiet=not verbose, fuzzy=True)

    # Verify the downloaded GeoTIFF
    if output_path.endswith(".tif") and not is_valid_tif(output_path):
        st.error(f"❌ {os.path.basename(output_path)} is not a valid GeoTIFF after download.")
        os.remove(output_path)
        st.stop()

def download_and_unzip_from_drive(file_id, extract_to):
    """
    Download and extract a ZIP from Google Drive, flattening all contents.
    """
    zip_path = "glacier_data_download.zip" 

    # Download and extract the data
    download_from_drive(file_id, zip_path, verbose=True)

    if not zipfile.is_zipfile(zip_path):
        st.error("❌ Downloaded file is not a valid ZIP archive.")
        os.remove(zip_path)
        st.stop()

    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            filename = os.path.basename(member.filename)
            if not filename:
                continue
            target_path = os.path.join(extract_to, filename)
            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())

    os.remove(zip_path)
    st.success(f"✅ Extracted shapefile components to {extract_to}")

def ensure_folder(path: str, drive_folder_link: str):
    """
    Ensure a folder exists or prompt user to manually download.
    """
    if not os.path.isdir(path):
        st.error(
            f"⚠️ Required folder not found:\n`{path}`\n\n"
            f"Please download it from:\n{drive_folder_link}\n"
            "and unzip it into that exact path before proceeding."
        )
        st.stop()

def ensure_glacier_shapefile():
    """
    Ensure glacier shapefile components exist or download & extract them.
    """
    glacier_dir = "Data/Raw/Environment_data/Glacier_data"
    required_files = [
        "Glacier_1980_1990_2000_2010.shp",
        "Glacier_1980_1990_2000_2010.shx",
        "Glacier_1980_1990_2000_2010.dbf",
        "Glacier_1980_1990_2000_2010.prj"
    ]
    
    # Check if all files exist
    if not all(os.path.isfile(os.path.join(glacier_dir, f)) for f in required_files):
        st.warning("🧊 Glacier shapefile incomplete or missing. Attempting to download...")
        zip_file_id = "1_9PlywFpKIvehoJJNqGS392XRdN5QMit"  # File ID for the Glacier data zip
        download_and_unzip_from_drive(zip_file_id, glacier_dir)
    else:
        st.success("✅ Glacier shapefile found.")

def download_all_data():
    """
    Run all required downloads for app datasets.
    """
    env_folder = "Data/Raw/Environment_data"
    ensure_folder(env_folder,
        "https://drive.google.com/drive/folders/1gvh11IouIROK3wtWbfCexya04j-fsvZ1?usp=drive_link"
    )

    downloads = [
        # Landcover GeoTIFFs
        ("1rOILeEY-ftycF5onSq5OWPMAl-4sNNOo", f"{env_folder}/Landcover_2005_Icimod.tif"),
        ("1h4U5HXM8BTWR1UHSBeapSf8zglxO-uGY", f"{env_folder}/Landcover_2010_Icimod.tif"),
        ("1gcE3uEFuWJa2vANs_jDLw6_ciH_zThBO", f"{env_folder}/Landcover_2015_icimod.tif"),

        # Glacier Area CSV
        ("1AQP2tKoxlIsu3FmQRyBvyrQVF6dRgo3_", f"{env_folder}/Glacier_area_by_HUCs.csv"),
    ]

    for file_id, out_path in downloads:
        download_from_drive(file_id, out_path, verbose=False)

    ensure_glacier_shapefile()
