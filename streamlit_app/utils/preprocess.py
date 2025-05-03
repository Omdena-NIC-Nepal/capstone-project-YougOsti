import os
import pandas as pd
import streamlit as st
import gdown

@st.cache_data
def load_data(file_path: str, gdrive_file_id: str = None) -> pd.DataFrame:
    """
    Load a CSV from disk or, if missing, download it from Google Drive.

    Parameters
    ----------
    file_path : str
        Local path where the CSV should live.
    gdrive_file_id : str, optional
        Google Drive file ID to download if `file_path` is not found.

    Returns
    -------
    pd.DataFrame
        The loaded data.
    """
    # If the file doesn't exist locally, pull from Google Drive
    if not os.path.exists(file_path):
        if not gdrive_file_id:
            raise FileNotFoundError(
                f"{file_path} not found locally and no Google Drive file ID provided."
            )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        url = f"https://drive.google.com/uc?export=download&id={gdrive_file_id}"
        st.info(f"Downloading data to `{file_path}` from Google Drive…")
        gdown.download(url, file_path, quiet=False)

    # Read and return
    return pd.read_csv(file_path)

@st.cache_data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the daily climate DataFrame in place.

    - Parse 'Date' column as datetime
    - Drop rows where 'Date' failed to parse
    - Forward/backward fill other missing values

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame to clean.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    # Parse dates
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

    # Fill other missing values
    df = df.fillna(method='ffill').fillna(method='bfill')

    return df
