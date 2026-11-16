import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://localhost:8080/game/index.html"
SHOTS = [
    ("1-start.jpg", "?shot=start&seed=1", 5000),
    ("2-play.jpg", "?shot=play&seed=1", 8000),
    ("3-end.jpg", "?shot=end&seed=1", 15000),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-web-security", "--disable-features=IsolateOrigins,site-per-process"]
        )
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        for name, query, wait_ms in SHOTS:
            url = f"{BASE}{query}"
            print(f"Loading {url}...")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for shot to be ready, with generous timeout
            try:
                await page.wait_for_function("window.__shotReady === true", timeout=wait_ms)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  __shotReady not set, waiting {wait_ms}ms anyway...")
                await asyncio.sleep(wait_ms / 1000)
            
            screenshot_path = os.path.join("screenshots", name)
            await page.screenshot(path=screenshot_path, full_page=False)
            size = os.path.getsize(screenshot_path)
            print(f"Saved {screenshot_path} ({size} bytes)")
        
        await browser.close()

asyncio.run(main())