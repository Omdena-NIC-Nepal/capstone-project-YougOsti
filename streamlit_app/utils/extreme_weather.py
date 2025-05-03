import pandas as pd

def detect_extreme_events(df):
    """Adds columns for extreme heat, rainfall, and storm detection"""
    df['Date'] = pd.to_datetime(df['Date'])
    df['Extreme_Heatwave'] = df['Temp_2m'] > 40
    df['Extreme_Rainfall'] = df['Precip'] > 100
    df['Extreme_Storm'] = df['Wind'] > 50
    return df