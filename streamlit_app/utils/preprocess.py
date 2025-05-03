# streamlit_app/utils/preprocess.py

import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads a CSV file and returns a DataFrame.
    Uses Streamlit caching to avoid reloading on every page.
    """
    df = pd.read_csv(file_path)
    return df

@st.cache_data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the daily climate dataset.

    - Converts 'Date' column to datetime
    - Drops rows with missing dates
    - Fills other missing values with forward/backward fill
    """
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

    # Fill other missing values
    df = df.fillna(method='ffill').fillna(method='bfill')

    return df
