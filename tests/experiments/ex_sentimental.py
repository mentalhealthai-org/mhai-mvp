from transformers import pipeline

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
)


# Example function to get sentiment
def get_sentiment(text: str) -> str:
    result = sentiment_pipeline(text)
    label = result[0]["label"]
    return label


# Initialize emotion detection pipeline (may need fine-tuning or finding a suitable model)
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True,
)


# Example function to get emotions
def get_emotions(text: str) -> dict:
    results = emotion_pipeline(text)
    emotions = {result["label"]: result["score"] for result in results[0]}
    return emotions


# Example usage
text = "Estou muito feliz hoje!"
print("Sentiment:", get_sentiment(text))
print("Emotions:", get_emotions(text))
