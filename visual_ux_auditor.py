import os
from google import genai
from google.genai import types

client = genai.Client()


def analyze_and_fix_ux():
    # 1. Laad het mobiele screenshot in (waar de uitlijnfout op te zien was)
    screenshot_path = "screenshots/mobile_fullpage.png"

    with open(screenshot_path, "rb") as f:
        image_bytes = f.read()

    with open("index.html", "r", encoding="utf-8") as f:
        current_html = f.read()

    # --- STAP 1: DE UX SPECIALIST ANALYSEERT DE SCREENSHOT ---
    ux_prompt = """
    Je bent een World-Class Lead UX/UI Designer. 
    Bekijk deze screenshot van de mobiele weergave van onze website kritisch.
    
    Identificeer alle visuele en conversie-fouten (zoals verkeerd uitgelijnde bullets, slecht contrast, vreemde marges, etc.).
    Geef een hele concrete, technische 'Fix Specification' lijst in bullet points wat de developer exact moet aanpassen in de CSS/HTML.
    """

    ux_response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ux_prompt,
        ],
    )

    technical_specs = ux_response.text
    print(f"--- UX SPECIFICATIES VOOR DEVELOPER ---\n{technical_specs}\n")

    # --- STAP 2: DE DEVELOPER (ANTIGRAVITY) VOERT DE FIXES UIT ---
    dev_prompt = f"""
    Je bent een Senior Frontend Developer.
    
    HUIDIGE HTML:
    ```html
    {current_html}
    ```
    
    OPDRACHT VAN DE UX SPECIALIST:
    {technical_specs}
    
    Pas de HTML en inline/embedded CSS van 'index.html' aan om ALLE bovenstaande UX-punten perfect op te lossen.
    Zorg specifiek dat bullet points en pictogram-lijstjes op mobiel strak links uitgelijnd zijn (`text-align: left`).
    
    Geef alleen de volledige, bijgewerkte en geldige HTML terug.
    """

    dev_response = client.models.generate_content(
        model="gemini-3.5-flash", contents=dev_prompt
    )

    fixed_html = (
        dev_response.text.replace("```html", "").replace("```", "").strip()
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(fixed_html)

    print("index.html is succesvol door de Developer-agent gecorrigeerd!")


if __name__ == "__main__":
    analyze_and_fix_ux()
