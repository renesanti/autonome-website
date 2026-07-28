import os
import subprocess
from google import genai
from PIL import Image
from playwright.sync_api import sync_playwright

# 1. Maak een screenshot van de live pagina met Playwright
print("Bezig met maken van screenshot...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    # Vervang onderstaande URL eventueel door jouw eigen GitHub Pages URL
    page.goto("https://renesanti.github.io/autonome-website/")
    page.screenshot(path="screenshot.png")
    browser.close()

# 2. Laad de huidige HTML in om te bewerken
with open("index.html", "r", encoding="utf-8") as f:
    current_html = f.read()

# 3. Roep Gemini aan via de nieuwe google-genai SDK
print("Screenshot en HTML worden naar Gemini gestuurd voor visuele UX-analyse...")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# We vragen Gemini om een korte samenvatting van de wijziging + de nieuwe HTML
prompt = f"""
Je bent een expert UX-designer en front-end ontwikkelaar. 
Bekijk de bijgevoegde screenshot van de website en de huidige HTML-code.
Verbeteer het ontwerp visueel (bijv. betere typografie, kleurgebruik, spacing, of modernere CSS).

Geef je antwoord ALS VOLGT in exact dit formaat:
1. De eerste regel begint met "SAMENVATTING: " gevolgd door een korte, duidelijke zin in het Nederlands waarin je uitlegt wat je hebt verbeterd (max 10 woorden).
2. Daarna, op een nieuwe regel, de volledige, schone HTML-code (omesloten door ```html ... ```).

Huidige HTML:
{current_html}
"""

image = Image.open("screenshot.png")

response = client.models.generate_content(
    model="gemini-3.5-flash",  # Pas dit aan als je een andere versie gebruikt
    contents=[prompt, image],
)

response_text = response.text
print("Visuele analyse voltooid!")

# 4. Splits de samenvatting en de nieuwe HTML van elkaar
try:
    # Zoek naar de HTML code blokken
    if "```html" in response_text:
        parts = response_text.split("```html")
        summary_part = parts[0].strip()
        html_part = parts[1].split("```")[0].strip()
    elif "```" in response_text:
        parts = response_text.split("```")
        summary_part = parts[0].strip()
        html_part = parts[1].strip()
    else:
        raise ValueError("Geen geldig codeblok gevonden in de respons van Gemini.")

    # Haal de nette samenvatting eruit voor de commit
    commit_msg = "UX update door AI"
    for line in summary_part.split("\n"):
        if "SAMENVATTING:" in line:
            commit_msg = line.replace("SAMENVATTING:", "").strip()

    # Sla de nieuwe HTML op
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_part)
    print(f"Nieuwe HTML opgeslagen. Reden: {commit_msg}")

except Exception as e:
    print(
        f"Fout bij het verwerken van de Gemini respons: {e}. Bestand blijft ongewijzigd."
    )
    exit(1)

# 5. Git configuratie en automatisch pushen naar GitHub
subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
subprocess.run(
    [
        "git",
        "config",
        "--global",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.io",
    ]
)

subprocess.run(["git", "add", "index.html"])
# We gebruiken hier dynamisch de gedachten/samenvatting van Gemini als commit-bericht!
subprocess.run(["git", "commit", "-m", f"AI UX: {commit_msg}"])
subprocess.run(["git", "push"])
print("Wijzigingen succesvol gepusht naar GitHub!")
