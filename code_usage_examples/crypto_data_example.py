import re
import requests
import streamlit as st
from datetime import datetime
import pandas as pd

st.title("Crypto Price & News Dashboard")

coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Dogecoin": "dogecoin"
}

currencies = {
    "US Dollar (USD)": "usd",
    "Indian Rupee (INR)": "inr",
    "Euro (EUR)": "eur",
    "British Pound (GBP)": "gbp",
    "Japanese Yen (JPY)": "jpy"
}

reddits = ["CryptoCurrency", "Bitcoin", "Ethereum"]

selected_coin = st.selectbox("Select a Cryptocurrency", list(coins.keys()))
selected_currency = st.selectbox("Select Currency", list(currencies.keys()))
selected_subreddit = st.selectbox("Select Reddit Subreddit for Latest Posts", reddits)

NEWSAPI_KEY = "your api key"  # Replace with your NewsAPI key

def get_price(coin_id, vs_currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
    r = requests.get(url).json()
    return r[coin_id][vs_currency]

def get_historical_prices(coin_id, vs_currency, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"
    r = requests.get(url).json()
    prices = r.get("prices", [])
    # Convert timestamp to readable date
    formatted_prices = [{"date": datetime.utcfromtimestamp(p[0] / 1000).strftime('%Y-%m-%d'), "price": p[1]} for p in prices]
    return formatted_prices

def get_news(keyword):
    url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWSAPI_KEY}"
    r = requests.get(url).json()
    return [a["title"] for a in r.get("articles", [])]

def clean_text(text):
    """Remove links from Reddit post text."""
    return re.sub(r"http\S+|www\S+", "", text).strip()

def get_reddit_posts(subreddit, limit=10):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {"User-Agent": "streamlit-app"}
    r = requests.get(url, headers=headers).json()
    posts = r.get("data", {}).get("children", [])
    out = []
    for p in posts:
        data = p["data"]
        title = data.get("title", "No Title")
        summary = clean_text(data.get("selftext", ""))
        if summary == "":
            summary = "No text content (maybe a link or image post)."
        out.append((title, summary))
    return out

if st.button("Get Price"):
    currency_code = currencies[selected_currency]
    price = get_price(coins[selected_coin], currency_code)
    st.write(f"The current price of {selected_coin} is **{price} {currency_code.upper()}**")

if st.button("Get Historical Prices (Last 30 Days)"):
    currency_code = currencies[selected_currency]
    historical_prices = get_historical_prices(coins[selected_coin], currency_code, 30)
    st.write(f"Historical prices for {selected_coin} (Last 30 Days):")
    st.table(historical_prices)

    df = pd.DataFrame(historical_prices)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    st.line_chart(df["price"])

if st.button("Get News"):
    news = get_news(selected_coin)
    st.write("Latest News:")
    for n in news:
        st.write("-", n)

if st.button("Get Reddit Posts"):
    posts = get_reddit_posts(selected_subreddit)
    st.write(f"Latest posts from r/{selected_subreddit}:")
    for title, summary in posts:
        st.subheader(title)
        st.write(summary)
        st.write("---")
