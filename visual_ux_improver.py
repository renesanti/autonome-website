import datetime
import os
import re
import sqlite3
import unicodedata
from google import genai

# Configuration
DB_NAME = "trending.db"


def slugify(text):
    """Zet een titel om naar een schone URL slug.

    Bijv: "Trend: 'Google AI' (Gezien in 5 artikelen)" -> "google-ai"
    """
    # Verwijder 'Trend:' of aantallen als die erin staan (re.IGNORECASE i.p.v. i)
    text = re.sub(r"^Trend:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(Gezien in.*?\)", "", text, flags=re.IGNORECASE)

    # Normalize unicode
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def get_latest_trends():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Haal de meest recente verzameling trends op
    cursor.execute(
        "SELECT timestamp, topic FROM trending_topics ORDER BY id DESC LIMIT 10"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def generate_article_and_update_home():
    trends = get_latest_trends()
    if not trends:
        print("Geen trends gevonden in DB.")
        return

    # Pak het primaire onderwerp voor de slug
    primary_topic = trends[0][1]
    slug = slugify(primary_topic)

    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{slug}-{date_str}.html"

    print(f"Nieuw artikelbestand wordt gegenereerd: {filename}")

    # --- GEMINI PROMPT (voor de losse artikelpagina) ---
    client = genai.Client()

    topics_summary = "\n".join([f"- {t[1]}" for t in trends])

    prompt_article = f"""
    Je bent een autonome webontwikkelaar. Bouw een volledige, standalone HTML-pagina voor een dashboard/artikel.
    Het hoofdonderwerp is: {primary_topic}
    Overige relevante trends van vandaag ({date_str}):
    {topics_summary}

    Eisen:
    - Inclusief moderne CSS styling (responsive, strak design).
    - Duidelijke navigatie terug naar 'index.html' (Homepage / Archiefoverzicht).
    - Schrijf een inhoudelijke analyse/samenvatting over deze trends.
    - Geef alleen geldige HTML terug.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt_article,
    )

    article_html = (
        response.text.replace("```html", "").replace("```", "").strip()
    )

    # Sla de nieuwe artikelpagina op
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article_html)

    # --- HOMEPAGE (index.html) BIJWERKEN / ARCHIEFOPBOUW ---
    update_index_page(filename, primary_topic, date_str)


import glob


def get_existing_articles():
    """Zoekt alle gegenereerde HTML bestanden in de root (behalve index.html)"""
    files = glob.glob("*.html")
    articles = [f for f in files if f != "index.html"]
    # Sorteer op meest recente datum/naam
    articles.sort(reverse=True)
    return articles


def update_index_page(new_filename, title, date_str):
    index_file = "index.html"
    client = genai.Client()

    current_index_content = ""
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            current_index_content = f.read()

    # Haal de echte bestandslijst op
    available_articles = get_existing_articles()
    if new_filename not in available_articles:
        available_articles.insert(0, new_filename)

    articles_list_str = "\n".join([f"- ./{art}" for art in available_articles])

    prompt_index = f"""
    Je bent een UX/UI designer en webontwikkelaar.
    Hier is de huidige 'index.html':
    ```html
    {current_index_content}
    ```

    WERKELIJK BESTAANDE ARTIKELEN IN DE REPO:
    {articles_list_str}

    BELANGRIJKE LINK- EN ARCHIEF-INSTRUCTIES:
    1. RELATIEVE LINKS (CRUCIAAL VOOR GITHUB PAGES):
       - Alle links naar artikelen MOETEN relatief zijn (bijv. href="./{new_filename}" of href="{new_filename}").
       - Gebruik NOOIT een absolute slash aan het begin (dus GEEN href="/artikel.html"), want dat veroorzaakt 404-fouten op GitHub Pages!
       
    2. ARCHIEF EN ARTIKELEN OVERZICHT:
       - Gebruik in het archief / artikelenlijst UITSLUITEND de bestanden uit de bovenstaande lijst van werkelijk bestaande artikelen.
       - Verzin GEEN niet-bestaande artikelen of dummy-links.
       - Zorg dat de nieuwste ({new_filename}) bovenaan staat.

    3. E-COMMERCE & LAY-OUT:
       - Behoud de "Get The Blueprint (€9,99)" navigatieknop en showcase sectie.
       - Zorg dat bullet points en iconen links uitgelijnd zijn.

    Geef alleen de volledige, bijgewerkte en geldige HTML terug.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt_index,
    )

    updated_index = (
        response.text.replace("```html", "").replace("```", "").strip()
    )

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(updated_index)

    print("index.html bijgewerkt met geldige relatieve links!")
if __name__ == "__main__":
    generate_article_and_update_home()
