from fastapi import FastAPI
import yfinance as yf
from datetime import datetime
import pandas as pd

app = FastAPI()


# Function to fetch S&P 500 data from Yahoo Finance
def get_sp500_data(start_date: str, end_date: str):
    sp500 = yf.Ticker('^GSPC')
    data = sp500.history(start=start_date, end=end_date)
    # Ensure the index is timezone-naive
    data.index = data.index.tz_localize(None)
    return data[['Close']]


# Function to fetch your investment data from a CSV or API (placeholder)
def get_investment_data(start_date: str, end_date: str):
    # Placeholder for your investment data
    data = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
    investment_data = pd.DataFrame({'Date': data, 'Value': range(len(data))})
    return investment_data.set_index('Date')


@app.get("/data")
async def get_comparison_data(start_date: str = "2023-01-01", end_date: str = datetime.now().strftime('%Y-%m-%d')):
    sp500_data = get_sp500_data(start_date, end_date)
    investment_data = get_investment_data(start_date, end_date)

    # Combine the data
    combined_data = pd.concat([investment_data, sp500_data], axis=1)
    combined_data.columns = ['Investment', 'S&P 500']

    # Replace NaN values with 0 or None
    combined_data = combined_data.fillna(0)  # Or use .fillna(None) for JSON nulls

    return combined_data.to_dict()
