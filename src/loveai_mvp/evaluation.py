from __future__ import annotations

from typing import Union, cast

import tiktoken

from transformers import pipeline

encoding_cl100k_base = tiktoken.get_encoding("cl100k_base")

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

mentbert_pipeline = pipeline("text-classification", model="reab5555/mentBERT")

psychbert_pipeline = pipeline(
    "text-classification", model="mnaylor/psychbert-finetuned-multiclass"
)

MAX_TOKENS = 450


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding_cl100k_base.encode(string))
    return num_tokens


def truncate_tokens(string: str, max_num_tokens: int) -> int:
    """Returns the number of tokens in a text string."""
    tokens = encoding_cl100k_base.encode(string)
    return encoding_cl100k_base.decode(tokens[:max_num_tokens])


def get_sentiment(text: str) -> int:
    """
    Get the level of the sentimental.

    Restriction of 512 tokens.

    Return
    ------
    int:
        Where 1, is not good, and 5 is really good.
        Returns -1 if the input is invalid.
    """
    if not text:
        return -1

    if num_tokens_from_string(text) > MAX_TOKENS:
        text = truncate_tokens(text, MAX_TOKENS)

    try:
        result = sentiment_pipeline(text)
    except Exception:
        return -1
    label = result[0][0]["label"]
    return int(label.split(" ")[0])


# Example function to get emotions
def get_emotions(text: str) -> dict[str, float]:
    """
    Return
    ------
    dict[str, float]:
        Example:
            {'neutral': 0.8584240078926086,
            'joy': 0.062253180891275406,
            'disgust': 0.029055433347821236,
            'sadness': 0.019559673964977264,
            'anger': 0.01465342566370964,
            'surprise': 0.010109353810548782,
            'fear': 0.0059448955580592155}
    """
    if not text:
        return {}

    if num_tokens_from_string(text) > MAX_TOKENS:
        text = truncate_tokens(text, MAX_TOKENS)

    try:
        results = emotion_pipeline(text)
    except Exception:
        return {}
    emotions = {result["label"]: result["score"] for result in results[0]}
    return cast(dict[str, float], emotions)


def get_psychbert_classification(text: str) -> int:
    """
    This is a version of
    https://huggingface.co/mnaylor/psychbert-cased
    which was fine-tuned to illustrate performance on a multi-class
    classification problem involving the detection of different
    types of language relating to mental health.

    The classes are as follows:

    0: Negative / unrelated to mental health
    1: Mental illnesses
    2: Anxiety
    3: Depression
    4: Social anxiety
    5: Loneliness
    The dataset for this model was taken from Reddit and Twitter, and labels were assigned based on the post appearing in certain subreddits or containing certain hashtags. For more information, see the PsychBERT paper.

    References
    ----------
    https://huggingface.co/mnaylor/psychbert-finetuned-multiclass
    """
    if not text:
        return {}

    label_map = {
        "LABEL_0": "negative",
        "LABEL_1": "mental illnesses",
        "LABEL_2": "anxiety",
        "LABEL_3": "depression",
        "LABEL_4": "social anxiety",
        "LABEL_5": "loneliness",
    }

    if num_tokens_from_string(text) > MAX_TOKENS:
        text = truncate_tokens(text, MAX_TOKENS)

    try:
        result_raw = psychbert_pipeline(text)
    except Exception:
        return {}

    label = result_raw[0]["label"]
    result = {
        "psychbert_label": label_map.get(label, label),
        "psychbert_score": result_raw[0]["score"],
    }
    return result


def get_mentbert_classification(text: str) -> dict[str, Union[str, float]]:
    """
    This model is a finetuned BERT (bert-base-uncased)
    model that predict different mental disorders.

    It is trained on a costume dataset of texts or posts
    (from Reddit) about general experiences of users with mental
    health problems.

    Dataset was cleaned and all direct mentions of the disorder
    names in the texts were removed.

    It includes the following classes:

    - Borderline
    - Anxiety
    - Depression
    - Bipolar
    - OCD
    - ADHD
    - Schizophrenia
    - Asperger
    - PTSD

    References
    ----------
    https://huggingface.co/reab5555/mentBERT
    """
    if not text:
        return {}

    if num_tokens_from_string(text) > MAX_TOKENS:
        text = truncate_tokens(text, MAX_TOKENS)

    try:
        result_raw = mentbert_pipeline(text)
    except Exception:
        return {}

    result = {
        "mentbert_label": result_raw[0]["label"].lower(),
        "mentbert_score": result_raw[0]["score"],
    }
    return result
