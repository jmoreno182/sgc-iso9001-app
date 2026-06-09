import asyncio
from playwright.async_api import async_playwright

async def capture_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        # Navigate to Streamlit app
        await page.goto("http://localhost:8501", wait_until="networkidle")

        # Wait a bit for Streamlit to fully render
        await page.wait_for_timeout(3000)

        # Take screenshot
        await page.screenshot(path="streamlit_screenshot.png", full_page=True)

        await browser.close()
        print("Screenshot saved: streamlit_screenshot.png")

asyncio.run(capture_screenshot())
