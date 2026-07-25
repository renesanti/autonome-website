import os
from google import genai

# Laad de API-sleutel uit GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY niet gevonden in environment variabelen.")

client = genai.Client(api_key=api_key)

# Lees de huidige index.html
try:
    with open("index.html", "r", encoding="utf-8") as f:
        current_html = f.read()
except FileNotFoundError:
    current_html = ""


prompt = f"""
Genereer een complete HTML pagina inclusief CSS.
Zorg voor een modern design en een actuele blogpost.
​Current HTML:
{current_html}
"""
