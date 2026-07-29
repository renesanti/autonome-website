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
        model="gemini-2.5-flash",
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


def update_index_page(new_filename, title, date_str):
    index_file = "index.html"

    client = genai.Client()

    current_index_content = ""
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            current_index_content = f.read()

    # Eén schone, gecombineerde prompt voor Gemini
    prompt_index = f"""
    Je bent een conversie-gerichte UX/UI designer en webontwikkelaar.
    Hier is de huidige 'index.html':
    ```html
    {current_index_content}
    ```

    OPDRACHT EN EISEN:
    1. NIEUW ARTIKEL / ARCHIEF LINK:
       - Voeg een nieuwe kaart/link toe bovenaan het artikelenoverzicht/archief op de homepage naar het nieuwste artikel:
         * Link: {new_filename}
         * Titel: {title}
         * Datum: {date_str}
       - Zorg dat oude artikelen/links in de lijst BEWAARD blijven.

    2. NAVIGATIE (E-COMMERCE):
       - Zorg voor een opvallende Call-to-Action knop in de navigatiebalk: "Get The Blueprint (€9,99)".
       - Deze knop moet opvallen (bijv. moderne accentkleur/gradient) en linken/scrollen naar #blueprint.

    3. SHOWCASE SECTION (#blueprint):
       - Als deze nog niet bestaat, voeg op de homepage een dedicated, conversie-gerichte sectie toe over het product: "The Autonomous AI Company Playbook".
       - HOOK: Leg uit dat déze exacte website voor 100% autonoom draait door AI (de live demo), en dat deze PDF van A tot Z uitlegt hoe de lezer exact hetzelfde kan bouwen (IT-infrastructuur, trend-aggregatie, AI-UX, marketing en geautomatiseerde sales).
       - PRIJS: €9,99.
       - KOOPKNOP / CTA: Een duidelijke, aantrekkelijke koopknop: "Buy Blueprint PDF – €9,99".

    4. LAY-OUT:
       - Houd de lay-out strak, modern, responsive en mobielvriendelijk.

    Geef alleen de volledige, bijgewerkte geldige HTML terug.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_index,
    )

    updated_index = (
        response.text.replace("```html", "").replace("```", "").strip()
    )

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(updated_index)

    print("index.html succesvol bijgewerkt met het verkoopdeel en nieuwe artikel link!")


if __name__ == "__main__":
    generate_article_and_update_home()
