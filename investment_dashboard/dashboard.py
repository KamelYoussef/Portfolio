import streamlit as st
import pandas as pd
import yfinance as yf


# Helper function to fetch stock data
def fetch_stock_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")['Close'].iloc[-1]
            data[ticker] = price
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
            data[ticker] = None
    return data


# Initialize the app with session state
if "portfolio_data" not in st.session_state:
    st.session_state.portfolio_data = None

st.title("Stock Portfolio Tracker")

# Sidebar for file upload and actions
# File uploader in the sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Upload your portfolio CSV file", type=["csv"])
    if uploaded_file:
        try:
            # Read the CSV file and drop unnecessary columns if they exist
            df = pd.read_csv(uploaded_file)
            if "Unnamed: 0" in df.columns:
                df = df.drop(columns=["Unnamed: 0"])

            # Ignore the "% PTF" column from the uploaded file
            if "% PTF" in df.columns:
                df = df.drop(columns=["% PTF"])

            # Store the uploaded data in session state
            st.session_state.portfolio_data = df
            st.success("File uploaded successfully!")
            st.session_state.portfolio_data.to_csv("portfolio_data.csv", index=False)
        except Exception as e:
            st.error(f"Error reading the CSV file: {e}")

    # Buttons for actions
    if st.session_state.portfolio_data is not None:
        add_btn = st.button("Add Position")
        edit_btn = st.button("Edit Position")
        delete_btn = st.button("Delete Position")

# Recalculate "% PTF" dynamically
if "portfolio_data" in st.session_state:
    df = st.session_state.portfolio_data

    # Fetch live prices for current stocks
    tickers = df["Stocks"].unique()
    current_prices = fetch_stock_data(tickers)
    df["Current Price"] = df["Stocks"].map(current_prices)
    df["Total Value"] = df["Quantity"] * df["Current Price"]

    # Calculate the total portfolio value and "% PTF"
    total_portfolio_value = df["Total Value"].sum()
    df["% PTF"] = (df["Total Value"] / total_portfolio_value) * 100

    # Update the session state data
    st.session_state.portfolio_data = df

# Display portfolio data if available
if st.session_state.portfolio_data is not None:
    portfolio_data = st.session_state.portfolio_data

    # Validate required columns
    required_columns = ["Portfolio", "Stocks", "Quantity", "% PTF", "Purchase Price"]
    if not all(column in portfolio_data.columns for column in required_columns):
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
        st.stop()

    # Convert columns to appropriate types
    portfolio_data["Quantity"] = pd.to_numeric(portfolio_data["Quantity"], errors="coerce")
    portfolio_data["Purchase Price"] = pd.to_numeric(portfolio_data["Purchase Price"], errors="coerce")
    portfolio_data.dropna(subset=["Quantity", "Purchase Price"], inplace=True)

    # Fetch current stock prices
    st.write("Fetching latest stock prices...")
    tickers = portfolio_data["Stocks"].unique()
    current_prices = fetch_stock_data(tickers)

    # Update data with current prices
    portfolio_data["Current Price"] = portfolio_data["Stocks"].map(current_prices)
    portfolio_data["Total Value"] = portfolio_data["Quantity"] * portfolio_data["Current Price"]
    portfolio_data["Gain"] = (portfolio_data["Current Price"] - portfolio_data["Purchase Price"]) * portfolio_data[
        "Quantity"]
    portfolio_data["Gain %"] = (portfolio_data["Current Price"] / portfolio_data["Purchase Price"] - 1) * 100

    # Display the table
    st.subheader("Portfolio Overview")
    st.dataframe(portfolio_data.style.format({
        "Purchase Price": "{:.2f}",
        "Current Price": "{:.2f}",
        "Total Value": "{:.2f}",
        "Gain": "{:.2f}",
        "Gain %": "{:.2f}%",
    }))

    # Add Position Popup
    if add_btn:
        with st.expander("Add New Position", expanded=True):
            portfolio = st.selectbox("Portfolio", portfolio_data["Portfolio"].unique())
            stock = st.text_input("Stock Symbol")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            purchase_price = st.number_input("Purchase Price", min_value=0.0, step=0.01)
            submitted = st.button("Submit New Position")
            if submitted:
                new_position = {
                    "Portfolio": portfolio,
                    "Stocks": stock,
                    "Quantity": quantity,
                    "% PTF": "0%",  # Placeholder
                    "Purchase Price": purchase_price
                }
                portfolio_data = pd.concat([portfolio_data, pd.DataFrame([new_position])], ignore_index=True)
                portfolio_data.to_csv("portfolio_data.csv", index=False)
                st.success(f"Added {stock} to portfolio!")
                st.experimental_rerun()

    # Edit Position Popup
    if edit_btn:
        with st.expander("Edit Position", expanded=True):
            position_to_edit = st.selectbox("Select Position to Edit", portfolio_data["Stocks"])
            edit_quantity = st.number_input("New Quantity", min_value=1, step=1)
            edit_purchase_price = st.number_input("New Purchase Price", min_value=0.0, step=0.01)
            edit_submitted = st.button("Submit Edit")
            if edit_submitted:
                portfolio_data.loc[portfolio_data["Stocks"] == position_to_edit, "Quantity"] = edit_quantity
                portfolio_data.loc[portfolio_data["Stocks"] == position_to_edit, "Purchase Price"] = edit_purchase_price
                portfolio_data.to_csv("portfolio_data.csv", index=False)
                st.success(f"Updated {position_to_edit} in portfolio!")
                st.experimental_rerun()

    # Delete Position Popup
    if delete_btn:
        with st.expander("Delete Position", expanded=True):
            position_to_delete = st.selectbox("Select Position to Delete", portfolio_data["Stocks"])
            delete_submitted = st.button("Submit Delete")
            if delete_submitted:
                portfolio_data = portfolio_data[portfolio_data["Stocks"] != position_to_delete]
                portfolio_data.to_csv("portfolio_data.csv", index=False)
                st.success(f"Deleted {position_to_delete} from portfolio!")
                st.experimental_rerun()

    # Display portfolio summary
    st.subheader("Portfolio Summary")
    portfolio_summary = portfolio_data.groupby("Portfolio")["Total Value"].sum()
    st.bar_chart(portfolio_summary)
    total_portfolio_value = portfolio_summary.sum()
    st.write(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
else:
    st.info("Please upload a CSV file to get started.")
