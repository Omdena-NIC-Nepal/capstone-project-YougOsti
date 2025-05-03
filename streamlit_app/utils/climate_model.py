# utils/climate_model.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.linear_model import LinearRegression

def prepare_yearly_variable(df, target_column):
    """
    Group daily data by year and compute average of selected column.
    """
    df['Year'] = df['Date'].dt.year
    yearly_avg = df.groupby('Year')[target_column].mean().reset_index()
    return yearly_avg

def train_forecast_model(df_yearly, forecast_until=2035):
    """
    Train a regression model and predict up to forecast_until year.
    """
    X = df_yearly[['Year']]
    y = df_yearly.iloc[:, 1]  # second column is the selected variable
    
    model = LinearRegression()
    model.fit(X, y)

    future_years = pd.DataFrame({'Year': np.arange(df_yearly['Year'].max() + 1, forecast_until + 1)})
    all_years = pd.concat([df_yearly[['Year']], future_years], ignore_index=True)
    all_years['Predicted'] = model.predict(all_years[['Year']])

    return model, all_years

def plot_forecast(all_years, historical, variable_label):
    """
    Plot forecast with historical data.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(historical['Year'], historical.iloc[:, 1], label='Observed', marker='o')
    ax.plot(all_years['Year'], all_years['Predicted'], label='Predicted', linestyle='--', color='red')

    ax.set_title(f"📈 {variable_label} Forecast (Observed vs Predicted)")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"{variable_label}")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
