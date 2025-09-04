from langgraph.graph import StateGraph, START, END

# --- Define your state ---
class State(dict):
    text: str
    summary: str
    sentiment: str

# --- Node functions ---
def summarize(state: State):
    return {"summary": f"Summary of: {state['text']}"}

def sentiment_analysis(state: State):
    return {"sentiment": f"Sentiment of: {state['text']}"}

def combine_results(state: State):
    return {
        "text": state["text"],
        "summary": state["summary"],
        "sentiment": state["sentiment"],
    }

# --- Build graph ---
graph = StateGraph(State)

# Add nodes
graph.add_node("summarizer", summarize)
graph.add_node("sentimenter", sentiment_analysis)
graph.add_node("combine", combine_results)

# Connect nodes in parallel
graph.add_edge(START, "summarizer")
graph.add_edge(START, "sentimenter")

# Both go to combine
graph.add_edge("summarizer", "combine")
graph.add_edge("sentimenter", "combine")
graph.add_edge("combine", END)

# Compile graph
app = graph.compile()

# --- Run ---
result = app.invoke({"text": "LangGraph makes AI workflows modular and parallel!"})
print(result)

# Get PNG bytes directly from LangGraph
png_bytes = app.get_graph().draw_mermaid_png()

# Save to file
with open("../../../Ai/pythonProject/code_usage_examples/graph.png", "wb") as f:
    f.write(png_bytes)

print("Graph saved as graph.png")
