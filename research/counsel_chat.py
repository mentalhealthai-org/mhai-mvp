"""
Dataset: https://github.com/nbertagnolli/counsel-chat

Columns:
- questionID
- questionTitle
- questionText
- questionLink
- topic
- therapistInfo
- therapistURL
- answerText
- upvotes
- views
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from datasets import load_dataset
from tqdm import tqdm

from loveai_mvp.evaluation import (
    get_sentiment,
    get_emotions,
    get_mentbert_classification,
    get_psychbert_classification,
)


data_path = Path(__file__).parent / "data"
input_data_path = data_path / "counsel-chat.pkl"
result_data_path = data_path / "result.pkl"

if not data_path.exists():
    dataset = load_dataset("nbertagnolli/counsel-chat")
    df = dataset["train"].to_pandas()
    joblib.dump(df, data_path)
else:
    df = joblib.load(input_data_path)

results = []

for question in tqdm(df.questionText.unique()):
    result = {
        "question": question,
        "topic": "",
        "sentimental": -1,
        "mentbert_label": "",
        "mentbert_score": -1,
        "psychbert_label": "",
        "psychbert_score": -1,
    }
    topic = df[df.questionText == question].topic.unique()
    if isinstance(topic, np.ndarray):
        result["topic"] = ", ".join(topic).lower()
    else:
        result["topic"] = str(topic).lower()

    result["sentimental"] = get_sentiment(question)
    result.update(get_mentbert_classification(question))
    result.update(get_psychbert_classification(question))
    result.update(get_emotions(question))

    results.append(result)

df_result = pd.DataFrame(results)
joblib.dump(df_result, result_data_path)
