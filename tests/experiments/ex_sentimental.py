from transformers import pipeline

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    top_k=None,
)

# Initialize emotion detection pipeline (may need fine-tuning or finding a suitable model)
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
)


# Example function to get sentiment
def get_sentiment(text: str) -> str:
    """
    Get the level of the sentimental.

    Where 1, is not good, and 5 is really good.
    """
    result = sentiment_pipeline(text)
    label = result[0][0]["label"]
    return int(label.split(" ")[0])


# Example function to get emotions
def get_emotions(text: str) -> dict:
    results = emotion_pipeline(text)
    emotions = {result["label"]: result["score"] for result in results[0]}
    return emotions


# Example usage
text = "I am really happy today"
print("Sentiment:", get_sentiment(text))
print("Emotions:", get_emotions(text))
