"""
check_browser.py — Test which browser / profile the agent will use.

    python check_browser.py

It reads BROWSER and BROWSER_PROFILE_DIR from .env, opens the browser, visits a
page, proves whether the profile is being remembered, and closes again.
Run it twice with a profile set: the second run should say "welcome back".
"""

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from app.tools.browser import browser  # noqa: E402


async def main():
    print(f"BROWSER             = {os.environ.get('BROWSER', 'chromium')}")
    print(f"BROWSER_PROFILE_DIR = {os.environ.get('BROWSER_PROFILE_DIR') or '(none: fresh browser each run)'}")
    page = await browser.page()
    await page.goto("https://example.com")
    print(f"✅ Opened: {await page.title()}  —  {(await page.evaluate('navigator.userAgent'))[:70]}…")

    seen = await page.evaluate("localStorage.getItem('workshop_visited')")
    if seen:
        print(f"🔁 Profile works — welcome back! (first visit was {seen})")
    else:
        await page.evaluate("localStorage.setItem('workshop_visited', new Date().toISOString())")
        print("🆕 First visit saved. With a profile set, run this again to see it remembered.")
    await asyncio.sleep(2)
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
