import os
import asyncio
from playwright.async_api import async_playwright
from PIL import Image
from google import genai
from google.genai import types

# 1. API Client initialiseren
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY ontbreekt!")

client = genai.Client(api_key=api_key)

async def capture_screenshots(url="https://renesanti.github.io/autonome-website/"):
    """ Start een headless browser en maakt screenshots van de hele pagina. """
    screenshots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Maak screenshots voor zowel Mobiel als Desktop
        viewports = [
            {"name": "desktop", "width": 1280, "height": 800},
            {"name": "mobile", "width": 375, "height": 667}
        ]
        
        for vp in viewports:
            page = await browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            await page.goto(url, wait_until="networkidle")
            
            # Volledige pagina screenshot
            path = f"screenshot_{vp['name']}.png"
            await page.screenshot(path=path, full_page=True)
            screenshots.append(path)
            
        await browser.close()
    return screenshots

def analyze_and_optimize_design(screenshot_paths, html_file_path="index.html"):
    # Lees de huidige HTML-code in
    with open(html_file_path, "r", encoding="utf-8") as f:
        current_html = f.read()

    # Laad de afbeeldingen voor Gemini
    images = [Image.open(p) for p in screenshot_paths]

    prompt = f"""
    Je bent een World-Class UI/UX Designer en Front-end Developer.
    
    Hier zijn recente screenshots van de live website (zowel desktop als mobiele weergave) én de huidige HTML/CSS code.
    
    Huidige HTML:
    ```html
    {current_html}
    ```
    
    Jouw taak:
    1. Analyseer de afbeeldingen visueel op:
       - Vormgeving, typografie en contrast.
       - Lelijke witruimtes, verkeerde uitlijning of overlap op mobiel/desktop.
       - Visuele hiërarchie en leesbaarheid van artikelen.
    2. Als de pagina er al strak en optimaal uitziet, behoud dan de huidige opmaak.
    3. Als er visuele verbeteringen mogelijk zijn, verbeter dan de CSS/HTML-structuur direct.
    
    Richtlijnen:
    - Zorg dat alle inhoud en blogposts behouden blijven!
    - Geef UITSLUITEND de volledige, geldige HTML5-code terug (inclusief inlined CSS in <style>).
    - Geen markdown backticks (geen ```html), geen uitleg.
    """

    # Stuur zowel de HTML-tekst als de Screenshots naar Gemini 3.5 Flash
    contents = [prompt] + images

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents
    )

    # Schoon de output op
    new_html = response.text.strip()
    if new_html.startswith("```html"):
        new_html = new_html[7:]
    if new_html.startswith("```"):
        new_html = new_html[3:]
    if new_html.endswith("```"):
        new_html = new_html[:-3]

    # Overschrijf de index.html met de visueel verbeterde versie
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(new_html.strip())

    print("Visuele analyse voltooid en index.html eventueel geoptimaliseerd!")

if __name__ == "__main__":
    # Voer screenshot capture en analyse uit
    paths = asyncio.run(capture_screenshots())
    analyze_and_optimize_design(paths)
