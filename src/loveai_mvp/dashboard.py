from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from db import load_conversation_history_last_24h, get_user_id

# Initialize the Dash app
app = Dash(__name__)

# Assume the username is 'ivan'
username = "ivan"
user_id = get_user_id(username)

# Load data from the last 24 hours
data = load_conversation_history_last_24h(user_id)

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Define the layout of the app
app.layout = html.Div(
    [
        html.H1("LoveAI Dashboard"),
        html.H2("Emotions and Sentiments Analysis (Last 24 Hours)"),
        dcc.Graph(id="emotion-graph"),
        dcc.Graph(id="sentiment-graph"),
        dcc.Interval(
            id="interval-component",
            interval=60 * 1000,  # Refresh every minute
            n_intervals=0,
        ),
    ]
)


# Update the graphs every minute
@app.callback(
    [Output("emotion-graph", "figure"), Output("sentiment-graph", "figure")],
    [Input("interval-component", "n_intervals")],
)
def update_graphs(n):
    # Reload data
    data = load_conversation_history_last_24h(user_id)
    df = pd.DataFrame(data)

    if df.empty:
        return {}, {}

    # Emotion Graph
    emotion_counts = (
        df[
            [
                "neutral",
                "joy",
                "disgust",
                "sadness",
                "anger",
                "surprise",
                "fear",
            ]
        ]
        .sum()
        .reset_index()
    )
    emotion_counts.columns = ["emotion", "count"]

    # Define color map for emotions
    color_map = {
        "neutral": "grey",
        "joy": "yellow",
        "disgust": "green",
        "sadness": "blue",
        "anger": "red",
        "surprise": "purple",
        "fear": "black",
    }

    emotion_fig = px.bar(
        emotion_counts,
        x="emotion",
        y="count",
        title="Emotion Distribution (Last 24 Hours)",
        color="emotion",
        color_discrete_map=color_map,
    )

    # Sentiment Graph
    df["sentiment_level"] = df["sentiment_level"].astype(str)
    sentiment_color_map = {
        "1": "red",
        "2": "orange",
        "3": "yellow",
        "4": "lightgreen",
        "5": "green",
    }

    sentiment_fig = px.histogram(
        df,
        x="timestamp",
        y="sentiment_level",
        title="Sentiment Levels Over Time",
        nbins=24,
        color="sentiment_level",
        color_discrete_map=sentiment_color_map,
    )

    return emotion_fig, sentiment_fig


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
