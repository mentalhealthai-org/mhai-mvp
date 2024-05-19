from __future__ import annotations

import sqlite3

from datetime import datetime, timedelta
from typing import Any, List

DB_PATH = "loveai.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT
        )
    """)
    conn.commit()

    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_input TEXT,
            ai_response TEXT,
            sentiment_level INTEGER,
            neutral FLOAT,
            joy FLOAT,
            disgust FLOAT,
            sadness FLOAT,
            anger FLOAT,
            surprise FLOAT,
            fear FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()

    conn.close()


def get_user_id(username: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user is None:
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        user_id = c.lastrowid
    else:
        user_id = user[0]
    conn.close()
    return user_id


def save_conversation(
    user_id: int,
    user_input: str,
    ai_response: str,
    sentiment_level: int,
    emotions: dict[str, float],
) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO conversations (
            user_id,
            user_input,
            ai_response,
            sentiment_level,
            neutral,
            joy,
            disgust,
            sadness,
            anger,
            surprise,
            fear
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            user_id,
            user_input,
            ai_response,
            sentiment_level,
            emotions["neutral"],
            emotions["joy"],
            emotions["disgust"],
            emotions["sadness"],
            emotions["anger"],
            emotions["surprise"],
            emotions["fear"],
        ),
    )
    conn.commit()
    conn.close()


def load_conversation_history(user_id: int) -> List[dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT user_input, ai_response FROM conversations
        WHERE user_id = ?
    """,
        (user_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"role": "user", "content": row[0]}
        if i % 2 == 0
        else {"role": "assistant", "content": row[1]}
        for i, row in enumerate(rows)
    ]


def load_emotions_and_sentiment_level(user_id: int) -> List[dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT
            user_id,
            sentiment_level,
            neutral,
            joy,
            disgust,
            sadness,
            anger,
            surprise,
            fear
        WHERE user_id = ?
    """,
        (user_id,),
    )
    rows = c.fetchall()
    conn.close()
    return rows


def preprocess_emotions(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for row in data:
        emotions = {
            "neutral": row["neutral"],
            "joy": row["joy"],
            "disgust": row["disgust"],
            "sadness": row["sadness"],
            "anger": row["anger"],
            "surprise": row["surprise"],
            "fear": row["fear"],
        }
        top_emotions = sorted(
            emotions.items(), key=lambda x: x[1], reverse=True
        )

        if top_emotions[0][1] > 0.75:
            for emotion in emotions.keys():
                row[emotion] = 1 if emotion == top_emotions[0][0] else 0
        else:
            top_3_emotions = [emotion[0] for emotion in top_emotions[:3]]
            for emotion in emotions.keys():
                row[emotion] = 1 if emotion in top_3_emotions else 0

    return data


def load_conversation_history_last_24h(user_id: int) -> List[dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    last_24h = datetime.now() - timedelta(days=1)
    c.execute(
        """
        SELECT
            user_input,
            ai_response,
            sentiment_level,
            neutral,
            joy,
            disgust,
            sadness,
            anger,
            surprise,
            fear,
            timestamp
        FROM conversations
        WHERE user_id = ? AND timestamp >= ?
    """,
        (user_id, last_24h),
    )
    rows = c.fetchall()
    conn.close()

    data = [
        {
            "user_input": row[0],
            "ai_response": row[1],
            "sentiment_level": row[2],
            "neutral": row[3],
            "joy": row[4],
            "disgust": row[5],
            "sadness": row[6],
            "anger": row[7],
            "surprise": row[8],
            "fear": row[9],
            "timestamp": row[10],
        }
        for row in rows
    ]

    return preprocess_emotions(data)
