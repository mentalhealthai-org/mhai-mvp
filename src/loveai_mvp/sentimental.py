from __future__ import annotations

from typing import cast

from transformers import pipeline

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    top_k=1,
)

# Initialize emotion detection pipeline
# (may need fine-tuning or finding a suitable model)
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
)


def get_sentiment(text: str) -> str:
    """
    Get the level of the sentimental.

    Where 1, is not good, and 5 is really good.
    """
    result = sentiment_pipeline(text)
    label = result[0][0]["label"]
    return int(label.split(" ")[0])


# Example function to get emotions
def get_emotions(text: str) -> dict[str, float]:
    """
    Return
    ------
        {'neutral': 0.8584240078926086,
         'joy': 0.062253180891275406,
         'disgust': 0.029055433347821236,
         'sadness': 0.019559673964977264,
         'anger': 0.01465342566370964,
         'surprise': 0.010109353810548782,
         'fear': 0.0059448955580592155}
    """
    results = emotion_pipeline(text)
    emotions = {result["label"]: result["score"] for result in results[0]}
    return cast(dict[str, float], emotions)
