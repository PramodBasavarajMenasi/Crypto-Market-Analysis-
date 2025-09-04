import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
import time

# App.py
from src.agents.agent import app
from data.data_file import coins, currencies , reddits

# Title centered at the top
st.markdown(
    "<h1 style='text-align: center; color:green;'>Crypto Market Analysis Dashboard</h1>",
    unsafe_allow_html=True,
)

# Sidebar menu
st.sidebar.title("Menu")
selected_coin = st.sidebar.selectbox("Select a Cryptocurrency", list(coins.keys()))
selected_currency = st.sidebar.selectbox("Select Currency", list(currencies.keys()))
selected_subreddit = st.sidebar.selectbox("Select Subreddit for Latest Posts", reddits)

# Button
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if st.sidebar.button("Summary & Price Graph"):
    st.session_state.show_summary = False
    with st.spinner("Loading today's summary..."):
        time.sleep(2)  # simulate loading
    st.session_state.show_summary = True

# Summary
if not st.session_state.get("show_summary", False):
    st.markdown(
        """
        <div style='text-align: center; color: gray; margin-top: 50px; font-size: 20px;'>
            Welcome to the Crypto Market Analysis Dashboard.<br>
            <p style='font-size:15px'>Please select a cryptocurrency, currency, and subreddit for latest posts from the sidebar</p>
            Then click <b>Summary & Price Graph</b> to view analysis.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Your dashboard content when data is loaded

    initial_state = {
                "currency": selected_coin,
                "vs_currency": selected_currency,
                "subreddit": selected_subreddit
            }
    # final_result= final(selected_coin,selected_currency,selected_subreddit)
    final_result = app.invoke(initial_state)
    # 1. Current Price
    st.subheader(f"💰 Current {final_result['currency']} Price in {final_result['vs_currency'].upper()}:")
    st.metric(label="Price", value=f"{final_result['price']} {final_result['vs_currency'].upper()}")

    # 2. 30 Days Line Graph
    st.subheader("📊 30-Day Price Trend")

    df = final_result["price_30days"]
    # Create Altair chart for improved visualization
    df = pd.DataFrame(df)
    df['date'] = pd.to_datetime(df['date'])

    st.line_chart(df.set_index('date')['price'])

    # 3. Today’s Price & News summary
    st.subheader(f"📰 Today's Price & News Summary :")
    st.write(final_result["summary"])


