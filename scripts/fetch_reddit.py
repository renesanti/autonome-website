import datetime
import sqlite3
import requests

# 1. Database instellen (maakt 'trending.db' aan als deze nog niet bestaat)
DB_FILE = "trending.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trending_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            topic TEXT
        )
    """)
    conn.commit()
    conn.close()


# 2. Reddit topics ophalen
def get_reddit_trending():
    url = "https://www.reddit.com/r/popular/hot.json?limit=10"
    # Tip: Maak de User-Agent uniek om te voorkomen dat Reddit GitHub Actions blokkeert
    headers = {
        "User-Agent": "AutonomousBlogAgent/1.0 (by /u/GitHubActionsRunner)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        topics = []

        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            now = datetime.datetime.utcnow().isoformat()

            for post in posts:
                title = post.get("data", {}).get("title")
                if title:
                    topics.append((now, "reddit", title))
            return topics
        else:
            print(
                f"Fout bij ophalen Reddit: HTTP-status {response.status_code}"
            )
            return []
    except Exception as e:
        print(f"Fout tijdens request: {e}")
        return []


# 3. Opslaan in SQLite database
def save_to_db(topics):
    if not topics:
        print("Geen topics om op te slaan.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Voeg alle topics in één keer toe
    cursor.executemany(
        """
        INSERT INTO trending_topics (timestamp, source, topic)
        VALUES (?, ?, ?)
    """,
        topics,
    )

    conn.commit()
    conn.close()
    print(f"Succesvol {len(topics)} topics opgeslagen in {DB_FILE}!")


if __name__ == "__main__":
    init_db()
    trending_data = get_reddit_trending()
    save_to_db(trending_data)
