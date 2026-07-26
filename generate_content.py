import os
from google import genai

# 1. Initialiseer de Gemini client met je API-sleutel uit de environment variables
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is niet ingesteld!")

client = genai.Client(api_key=api_key)

# 2. Lees de bestaande index.html in (als deze bestaat)
html_file_path = "index.html"
existing_content = ""

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        existing_content = f.read()

# 3. Stel de uitgebreide prompt samen inclusief de bestaande HTML-context
prompt = f"""
Je bent een professionele webdesigner en webredacteur.

Jouw taak is om de onderstaande bestaande HTML-pagina bij te werken. Voeg een splinternieuwe, actuele en waardevolle blogpost toe aan de pagina over technologie, innovatie of kunstmatige intelligentie. Houd bestaande artikelen/historie waar mogelijk netjes intact in een archief- of overzichtsectie.

Bestaande HTML van de pagina:
---
{existing_content}
---

Richtlijnen voor de output:
1. Genereer een complete, geldige HTML5-pagina (inclusief <!DOCTYPE html>, <head>, <body>).
2. Gebruik een strak, modern en responsief design met schone CSS in de <head>.
3. Zorg voor een duidelijke indeling met een header, het nieuwste blogartikel bovenaan, en een overzicht van eerdere artikelen.
4. Zorg voor uitstekende typografie en leesbaarheid op zowel mobiel als desktop.
5. Geef UITSLUITEND de rauwe HTML-code terug. Gebruik GEEN Markdown-codeblocks (zoals ```html ... ```) en geen introductie of uitleg voor/na de code.
"""

# 4. Roep het Gemini 3.5 Flash model aan
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt,
)

# 5. Schoon de output op (verwijder eventuele hardnekkige backticks)
new_html = response.text.strip()
if new_html.startswith("```html"):
    new_html = new_html[7:]
if new_html.startswith("```"):
    new_html = new_html[3:]
if new_html.endswith("```"):
    new_html = new_html[:-3]

new_html = new_html.strip()

# 6. Overschrijf/update index.html met de nieuwe gegenereerde content
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("index.html is succesvol gegenereerd en bijgewerkt!")
