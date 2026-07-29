import sqlite3
import datetime
import feedparser
from collections import Counter
import re

# Lijst met RSS-feeds (je kunt dit uitbreiden naar tientallen of honderden bronnen)
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

def extract_keywords(title):
    # Verwijder stopwoorden en speciale tekens, haal belangrijke termen over
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "of", "is", "it", "this", "that", "from", "as", "are", "was"}
    words = re.findall(r'\b[A-Za-z]{3,}\b', title.lower())
    filtered = [w for w in words if w not in stop_words]
    return filtered

def fetch_and_aggregate_rss():
    all_titles = []
    
    print("Bezig met ophalen van RSS-feeds...")
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if 'title' in entry:
                    all_titles.append(entry.title)
        except Exception as e:
            print(f"Fout bij ophalen {url}: {e}")
            
    print(f"Totaal {len(all_titles)} artikelen opgehaald uit RSS bronnen.")

    # Aggregatie: tel welke woorden/onderwerpen het meest voorkomen
    word_counter = Counter()
    for title in all_titles:
        keywords = extract_keywords(title)
        # We kijken naar unieke woorden per titel om dubbeltelling door dezelfde titel te voorkomen
        for kw in set(keywords):
            word_counter[kw] += 1

    # Pak de meest voorkomende betekenisvolle onderwerpen als "trending topics"
    # We filteren woorden die te algemeen zijn weg als dat nodig is
    common_topics = word_counter.most_common(15)
    
    now = datetime.datetime.utcnow().isoformat()
    trending_records = []
    
    # We bewaren zowel de geaggregeerde trend als een paar opvallende koppen
    for topic, count in common_topics:
        if count > 1: # Moet minstens in 2 verschillende artikelen/bronnen voorkomen om een trend te zijn
            topic_str = f"Trend: '{topic.capitalize()}' (Gezien in {count} artikelen)"
            trending_records.append((now, "rss_aggregated", topic_str))

    # Als fallback als er te weinig overlap is
    if not trending_records and all_titles:
        for title in all_titles[:5]:
            trending_records.append((now, "rss_top_story", title))

    return trending_records

def save_to_db(records):
    conn = sqlite3.connect("trending.db")
    cursor = conn.cursor()
    
    # Zorg dat de tabel bestaat
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trending_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            topic TEXT
        )
    """)
    
    # Voeg de nieuwe records toe
    cursor.executemany("""
        INSERT INTO trending_topics (timestamp, source, topic)
        VALUES (?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    print(f"{len(records)} records succesvol opgeslagen in trending.db.")

if __name__ == "__main__":
    records = fetch_and_aggregate_rss()
    if records:
        save_to_db(records)
