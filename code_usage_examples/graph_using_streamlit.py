import streamlit as st
import requests
import pandas as pd
import altair as alt
from typing_extensions import TypedDict
from langgraph.graph import StateGraph

class AgentChat(TypedDict):
    fetch_data: pd.DataFrame

def fetch_data_tool(state: AgentChat) -> AgentChat:
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    data = response.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["Timestamp", "Price"])
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms")
    return {"fetch_data": df[["Date", "Price"]]}

graph = StateGraph(AgentChat)
graph.add_node("fetch_data", fetch_data_tool)
graph.set_entry_point("fetch_data")
app = graph.compile()

st.title("30 Days Bitcoin Price Viewer")

if st.button("Get 30 Days Data"):
    result = app.invoke({"fetch_data": None})
    df = result["fetch_data"]
    # Create Altair chart for improved visualization
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('Price:Q', axis=alt.Axis(title='Price (USD)')),
        tooltip=[alt.Tooltip('Date:T', title='Date'), alt.Tooltip('Price:Q', title='Price (USD)')]
    ).properties(
        width=700,
        height=400,
        title='Bitcoin Price Over Last 30 Days'
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
