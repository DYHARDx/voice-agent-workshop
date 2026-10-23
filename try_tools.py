"""
try_tools.py — Test the action layer WITHOUT a microphone.

    python try_tools.py "play lofi music on youtube"
    python try_tools.py            # interactive: type commands, Ctrl+C to quit

Great for debugging a new tool before you try it by voice.
"""

import asyncio
import os
import sys

import aiohttp
from dotenv import load_dotenv

load_dotenv()

import app.tools  # noqa: F401  (loads all tools)
from app.tools.browser import browser
from app.tools.dispatcher import detect_and_run


class _MiniLLM:
    """Just enough of AIAgent for the dispatcher."""
    is_ollama_available = True

    def __init__(self, session):
        self._session = session


async def main():
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
    async with aiohttp.ClientSession() as session:
        llm = _MiniLLM(session)
        commands = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else None
        try:
            while True:
                text = commands.pop(0) if commands else (await asyncio.to_thread(input, "🎤 you say > ") if commands is None else None)
                if text is None:
                    break
                results = await detect_and_run(llm, model, text)
                if not results:
                    print("   (no tool needed — this would be a normal chat reply)")
                for r in results:
                    mark = "✅" if r["ok"] else "❌"
                    print(f"   {mark} {r['name']}({r['arguments']}) -> {r['result']}  [{r['ms']}ms]")
                if commands == []:
                    await asyncio.sleep(5)  # leave the browser open briefly
                    break
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
