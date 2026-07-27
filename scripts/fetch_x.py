# fetch_x.py
import datetime


def get_x_trending():
    now = datetime.datetime.utcnow().isoformat()
    # Hier komt de Tweepy / X API v2 call zodra je je Bearer Token toevoegt
    return [
        {"timestamp": now, "source": "x", "topic": "#AI2026"},
        {"timestamp": now, "source": "x", "topic": "#TechNews"},
    ]
