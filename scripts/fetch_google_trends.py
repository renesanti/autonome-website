import datetime
from pytrends.request import TrendReq


def get_google_trends(geo="NL"):
    pytrends = TrendReq(hl="nl-NL", tz=120)
    topics = []

    try:
        # Haalt de realtime trending zoekopdrachten op
        trending_df = pytrends.realtime_trending_searches(pn=geo)
        now = datetime.datetime.utcnow().isoformat()

        # Neem de top 10 trends
        top_trends = trending_df["title"].head(10).tolist()

        for topic in top_trends:
            topics.append(
                {"timestamp": now, "source": "google_trends", "topic": topic}
            )
    except Exception as e:
        print(f"Fout bij ophalen Google Trends: {e}")

    return topics


if __name__ == "__main__":
    print(get_google_trends())
