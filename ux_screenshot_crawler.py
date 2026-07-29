import asyncio
import os
from playwright.async_api import async_playwright

URLS_TO_CRAWL = ["https://jouwgebruikersnaam.github.io/index.html"]

VIEWPORTS = {
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1440, "height": 900},
}


async def capture_screenshots():
    os.makedirs("screenshots", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for url in URLS_TO_CRAWL:
            for device, size in VIEWPORTS.items():
                context = await browser.new_context(viewport=size)
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle")

                # Maak een full-page screenshot
                filename = f"screenshots/{device}_fullpage.png"
                await page.screenshot(path=filename, full_page=True)
                print(f"Screenshot opgeslagen: {filename}")

                await context.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_screenshots())
