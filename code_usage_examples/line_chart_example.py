import streamlit as st
import pandas as pd
from crypto_data_example import historical_prices
# Example data format


# Convert to DataFrame
df = pd.DataFrame(historical_prices)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")

# Plot line chart
st.line_chart(df["price"])