from collections import Counter
import datetime
import re
import sqlite3
import feedparser

RSS_FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.wired.com/feed/rss",
    "https://arstechnica.com/feed/",
    "https://www.reddit.com/r/technology/.rss",
    "https://www.reddit.com/r/webdev/.rss",
    "https://www.reddit.com/r/programming/.rss",
]

# Uitgebreide lijst met ruiswoorden die geen trend vormen
STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at", "to",
    "for",
    "with",
    "by",
    "of",
    "is",
    "it",
    "this",
    "that",
    "from",
    "as",
    "are",
    "was",
    "your",
    "you",
    "best",
    "top",
    "new",
    "how",
    "has",
    "more",
    "off",
    "promo",
    "codes",
    "code",
    "july",
    "august",
    "today",
    "deals",
    "deal",
}


def get_phrases_from_title(title):
    # Schoon de tekst op en maak kleine letters
    words = re.findall(r"\b[A-Za-z]{3,}\b", title.lower())
    # Filter losse stopwoorden
    clean_words = [w for w in words if w not in STOP_WORDS]

    phrases = []

    # 1. Bekijk waardevolle losse woorden (bijv. "Google", "Apple", "Linux")
    for w in clean_words:
        phrases.append(w.capitalize())

    # 2. Bekijk combinaties van 2 opeenvolgende woorden (bijv. "Artificial Intelligence")
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if w1 not in STOP_WORDS and w2 not in STOP_WORDS:
            phrases.append(f"{w1.capitalize()} {w2.capitalize()}")

    return phrases


def fetch_and_aggregate_rss():
    all_titles = []

    print("Bezig met ophalen van RSS-feeds...")
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if "title" in entry:
                    all_titles.append(entry.title)
        except Exception as e:
            print(f"Fout bij ophalen {url}: {e}")

    phrase_counter = Counter()

    for title in all_titles:
        phrases = get_phrases_from_title(title)
        # Gebruik set() per titel om te voorkomen dat 1 artikel een term 5x telt
        for phrase in set(phrases):
            phrase_counter[phrase] += 1

    # Haal de top 10 meest voorkomende onderwerpen/frases op
    common_topics = phrase_counter.most_common(10)

    now = datetime.datetime.utcnow().isoformat()
    trending_records = []

    for topic, count in common_topics:
        if count > 1:  # Moet minimaal in 2 artikelen voorkomen
            topic_str = f"Trend: '{topic}' (Gezien in {count} artikelen)"
            trending_records.append((now, "rss_aggregated", topic_str))

    return trending_records


def save_to_db(records):
    conn = sqlite3.connect("trending.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trending_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            topic TEXT
        )
    """)

    cursor.executemany(
        """
        INSERT INTO trending_topics (timestamp, source, topic)
        VALUES (?, ?, ?)
    """,
        records,
    )

    conn.commit()
    conn.close()
    print(f"{len(records)} geaggregeerde trends opgeslagen.")


if __name__ == "__main__":
    records = fetch_and_aggregate_rss()
    if records:
        save_to_db(records)
