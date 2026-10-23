"""
my_tools.py — ✏️  YOUR PLAYGROUND. Add your own voice-callable tools here!

How it works (3 rules):
  1. Write a normal Python function.
  2. Put @tool on top of it.
  3. Write a clear docstring — the AI reads it to decide WHEN to use your tool.

Restart the server and say it out loud. Done — no other file to edit.

Tips:
  • The first docstring line = what the tool does (be specific!)
  • "Args:" lines describe each parameter so the AI fills them correctly
  • Always return a SHORT string — the voice agent will say it back to you
  • Use `async def` if you call a browser or network; plain `def` is fine otherwise
"""

import random

from .registry import tool


@tool
def roll_dice(sides: int = 6) -> str:
    """Roll a dice and report the number that came up.

    Args:
        sides: how many sides the dice has (default 6)
    """
    return f"The dice rolled {random.randint(1, sides)}"


# ── Ideas for the workshop (pick one and build it!) ─────────────────
#   • tell_joke()                 -> return a random joke from a list
#   • open_maps(place: str)       -> use browser.page() to open Google Maps
#   • play_spotify(song: str)     -> open open.spotify.com/search/<song>
#   • take_screenshot()           -> page.screenshot(path="shot.png")
#   • convert_currency(...)       -> call a free public API with aiohttp
#   • weather(city: str)          -> call https://wttr.in/<city>?format=3
