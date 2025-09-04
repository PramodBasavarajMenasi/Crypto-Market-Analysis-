from typing import  Sequence, TypedDict
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph
from langchain_core.messages import HumanMessage # Passes data back to LLM after it calls a tool such as the content and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
import pandas as pd
from langgraph.graph import StateGraph ,START ,END

from src.agents.model import huggingface_model, perplexity_model
from src.utils.helper import get_news, get_price, get_historical_prices, get_reddit_post_news

# data type
class AgenticState(TypedDict):
    currency : str
    vs_currency : str
    subreddit : str
    price : float
    price_30days :  pd.DataFrame
    News : Sequence[BaseMessage]
    Analysis_price : str
    Analysis_news: str
    summary : str

# nodes - functions
def price_node(state : AgenticState )-> AgenticState:
    """This node helps us obtain the current price and the last 30 days of historical data"""
    state["price"] = get_price(state["currency"] , state["vs_currency"])
    state["price_30days"] = get_historical_prices(state["currency"] , state["vs_currency"])
    return state

def price_Analysis(state : AgenticState)->AgenticState:
    """ This node helps us analyze the last 30 days of historical data"""
    messages = [
        SystemMessage(content=f"You are a helpful agent. Your task is to analyze {state['currency']}-{state['vs_currency']} price data"),
        HumanMessage(content=f"Analyze the given {state['currency']}-{state['vs_currency']} price dataset and explain how the price is varying day by day. Also, extract any relevant news that could explain these variations. output in text from : {state['price_30days']}.")
    ]
    result = huggingface_model.invoke(messages)
    state["Analysis_price"] = result.content
    return state

def News_node(state : AgenticState)-> AgenticState:
    """This node helps us collect news from Perplexity, Reddit, and NewsAPI"""
    state['News'] = get_reddit_post_news(state["subreddit"])
    state['News'] += get_news(state["currency"])
    messages = [
        SystemMessage(content="You are a helpful agent. Your work is to extract the present or current top 5 news."),
        HumanMessage(content=f"Give me the top 5 helpful news for {state['currency']}.")
    ]
    state['News'] += [(perplexity_model.invoke(messages)).content]
    return state


def News_Analysis(state : AgenticState )-> AgenticState:
    """This node assists in providing a concise and precise summary of the extracted news"""
    messages = [
        SystemMessage(
            content="You are a helpful agent. Your task is to analyze a list of news and provide insights, summaries, or key points from them."),
        HumanMessage(
            content=f"Please analyze the following news and give a brief summary or important analysis for each:\n{state['News']}")
    ]

    result = huggingface_model.invoke(messages)
    state["Analysis_news"] = result.content
    return state

def combine_Analysis(state : AgenticState)-> AgenticState:
    """This node helps us get a summary of both price and news"""
    messages = [
        SystemMessage(
            content="You are a helpful agent. Your task is to generate a concise summary by combining the Bitcoin-USD price analysis and news analysis."),
        HumanMessage(
            content=f"Using the following data:\nPrice Analysis: {state['Analysis_price']}\nNews Analysis: {state['Analysis_news']}\n\nPlease provide a brief summary explaining the key insights and overall trends.")
    ]

    result = huggingface_model.invoke(messages)

    state["summary"] = result.content
    return state

# langgraph app
def build_app():
    graph = StateGraph(AgenticState)

    graph.add_node("Price", price_node)
    graph.add_node("Price_analysis", price_Analysis)
    graph.add_node("News", News_node)
    graph.add_node("News_analysis", News_Analysis)
    graph.add_node("Summary", combine_Analysis)

    # Execution flow
    graph.add_edge(START, "Price")
    graph.add_edge("Price", "Price_analysis")
    graph.add_edge("Price_analysis", "News")  # ensure sequential flow
    graph.add_edge("News", "News_analysis")
    graph.add_edge("News_analysis", "Summary")
    graph.add_edge("Summary", END)

    return graph.compile()
app = build_app()
# initial_state = {
#     "currency": "bitcoin",
#     "vs_currency": "usd",
#     "subreddit": "CryptoCurrency"
# }
# result = app.invoke(initial_state)
#
# png_bytes = app.get_graph().draw_mermaid_png()
#
# # Save to file
# with open("graph.png", "wb") as f:
#     f.write(png_bytes)
#
# def final(selected_coin,selected_currency,selected_subreddit):
#     initial_state = {
#         "currency": selected_coin,
#         "vs_currency": selected_currency,
#         "subreddit": selected_subreddit
#     }
#
#     result = app1.invoke(initial_state)
#
#     return result
if __name__ == "__main__":
    n = News_node({"currency": "bitcoin","vs_currency": "usd","subreddit":"bitcoin"})
    n1 =News_Analysis({"News": n["News"]})

    n =price_node({"currency": "bitcoin","vs_currency": "usd"})
    n2 = price_Analysis({"currency": "bitcoin","vs_currency": "usd","price_30days":n['price_30days']})

    combine_Analysis({"currency": "bitcoin","vs_currency": "usd","subreddit":"bitcoin","price_30days":n['price_30days'],"News": n1["News"],"Analysis_news":n1["Analysis_news"],"Analysis_price" : n2["Analysis_price"]})





