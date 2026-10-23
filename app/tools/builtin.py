"""
builtin.py — The tools that ship with the workshop.

Each function below is something the voice agent can DO.
Read one, then copy it into my_tools.py to make your own.
"""

import os
from datetime import datetime
from urllib.parse import quote_plus

from .browser import browser
from .registry import tool

# Friendly names the user might say -> real addresses
KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "amazon": "https://www.amazon.in",
    "netflix": "https://www.netflix.com",
    "chatgpt": "https://chatgpt.com",
}


@tool
async def open_website(site: str) -> str:
    """Open a website in the browser, for example YouTube, GitHub or Gmail. Use for "open X" or "go to X".

    Args:
        site: name of the website (like "youtube") or a web address (like "example.com")
    """
    name = site.strip().lower()
    if name in KNOWN_SITES:
        url = KNOWN_SITES[name]
    elif "." in name and " " not in name:
        url = name if name.startswith("http") else f"https://{name}"
    else:
        url = f"https://www.google.com/search?q={quote_plus(site)}"

    page = await browser.page()
    await page.goto(url, wait_until="domcontentloaded")
    return f"Opened {site}"


@tool
async def search_google(query: str) -> str:
    """Search Google for something.

    Args:
        query: what to search for
    """
    page = await browser.page()
    await page.goto(f"https://www.google.com/search?q={quote_plus(query)}", wait_until="domcontentloaded")
    return f"Searched Google for {query}"


@tool
async def search_youtube(query: str) -> str:
    """Search YouTube and show the list of results.

    Args:
        query: what to search for on YouTube
    """
    page = await browser.page()
    await page.goto(
        f"https://www.youtube.com/results?search_query={quote_plus(query)}",
        wait_until="domcontentloaded",
    )
    return f"Showing YouTube results for {query}"


@tool
async def play_youtube(query: str) -> str:
    """Find a video or song on YouTube and play it.

    Args:
        query: the video, song or topic to play
    """
    page = await browser.page()
    await page.goto(
        f"https://www.youtube.com/results?search_query={quote_plus(query)}",
        wait_until="domcontentloaded",
    )
    first_video = page.locator("ytd-video-renderer a#video-title").first
    await first_video.wait_for(timeout=15000)
    await first_video.click()
    # Keep results SHORT: the voice agent reads them out loud
    return f"Now playing the top YouTube result for {query}"


@tool
async def scroll_page(direction: str = "down") -> str:
    """Scroll the current web page up or down.

    Args:
        direction: either "up" or "down"
    """
    page = await browser.page()
    amount = -800 if direction.lower() == "up" else 800
    await page.mouse.wheel(0, amount)
    return f"Scrolled {direction}"


@tool
async def close_browser() -> str:
    """Close the browser window."""
    await browser.close()
    return "Browser closed"


@tool
def get_current_time() -> str:
    """Tell the current date and time."""
    return datetime.now().strftime("It is %I:%M %p on %A, %d %B %Y")


@tool
async def take_screenshot() -> str:
    """Take a screenshot of the current browser page and save it as an image."""
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/shot_{datetime.now().strftime('%H%M%S')}.png"
    page = await browser.page()
    await page.screenshot(path=path)
    return f"Screenshot saved to {path}"
