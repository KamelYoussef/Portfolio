import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Streamlit app configuration
st.title("Investment Performance Dashboard")
st.sidebar.header("Date Range")

# User inputs for date range
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

# Fetch data from FastAPI backend
st.sidebar.subheader("Data Loading")
if st.sidebar.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        try:
            response = requests.get(
                f"http://127.0.0.1:8000/data",
                params={"start_date": start_date, "end_date": end_date},
            )
            response.raise_for_status()
            data = pd.DataFrame(response.json())
            st.success("Data loaded successfully!")

            # Display raw data
            st.subheader("Raw Data")
            st.write(data)

            # Visualization
            st.subheader("Performance Comparison")
            fig, ax = plt.subplots()
            data.plot(ax=ax)
            plt.title("Investment vs. S&P 500")
            plt.xlabel("Date")
            plt.ylabel("Value")
            st.pyplot(fig)

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch data: {e}")

