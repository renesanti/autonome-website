import datetime
import requests


def get_reddit_trending():
    url = "https://www.reddit.com/r/popular/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(url, headers=headers)
    topics = []

    if response.status_code == 200:
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        now = datetime.datetime.utcnow().isoformat()

        for post in posts:
            title = post.get("data", {}).get("title")
            if title:
                topics.append(
                    {"timestamp": now, "source": "reddit", "topic": title}
                )

    return topics


if __name__ == "__main__":
    print(get_reddit_trending())

