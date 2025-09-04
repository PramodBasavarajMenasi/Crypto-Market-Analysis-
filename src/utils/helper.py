import os
import requests as re
from datetime import datetime,timezone
from dotenv import load_dotenv
from src.utils.format import clean_text

from src.data.data_file import coins ,currencies

# env variables
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

#helper functions
def get_price(coin_id,vs_currency):
    coin_id = coins[coin_id]
    vs_currency = currencies[vs_currency]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
    response = re.get(url)
    data = response.json()
    return data[coin_id][vs_currency]


def get_historical_prices(coin_id ,vs_currency ,days = 30):
    coin_id = coins[coin_id]
    vs_currency = currencies[vs_currency]
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"
    response = re.get(url).json()
    data = response.get("prices",[])

    # Convert timestamp to readable date
    formatted_data = [{'date' :  datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).strftime('%Y-%m-%d'), 'price':p[1]} for p in data]
    return formatted_data

def get_news(keyword):
    url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&sortBy=publishedAt&pageSize=10&apiKey={NEWSAPI_KEY}"
    response = re.get(url).json()
    return [a["description"] for a in response.get("articles", [])]

def get_reddit_post_news(subreddit,limit=5):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {"User-Agent": "streamlit-app"}
    response = re.get(url , headers=headers).json()
    data = response.get("data", {})
    posts = data.get("children", [])

    out = []

    for p in posts:
        data = p["data"]
        title = data.get("title", "No Title")
        summary = data.get("selftext","")
        text = clean_text(summary)

        if text == "":
            text = "No text content (maybe a link or image post)."
        out.append((title,text))
    return out

if __name__ == "__main__":
    print(get_price("bitcoin","usd"))
