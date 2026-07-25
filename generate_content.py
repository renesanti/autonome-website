import os
import re
from google import genai

# 1. Laad de API-sleutel uit GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY niet gevonden in environment variabelen.")

client = genai.Client(api_key=api_key)

# 2. Lees de huidige index.html
try:
    with open("index.html", "r", encoding="utf-8") as f:
        current_html = f.read()
except FileNotFoundError:
    current_html = ""

# 3. Stel de prompt samen
prompt = f"""
Genereer een complete HTML pagina inclusief CSS in de head.
Zorg voor een prachtig, modern design en een actuele blogpost.
Geef enkel de schone HTML-code terug, zonder extra uitleg.

Current HTML:
{current_html}
"""

# 4. Roep het Gemini model aan


response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
)



new_html = response.text

# 5. Verwijder eventuele markdown codeblock tags (zoals ```html en ```)
new_html = re.sub(r"^```html\s*", "", new_html, flags=re.MULTILINE)
new_html = re.sub(r"^```\s*", "", new_html, flags=re.MULTILINE)

# 6. Sla de nieuwe content op in index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_html.strip())

print("index.html is succesvol bijgewerkt!")
