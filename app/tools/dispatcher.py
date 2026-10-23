"""
dispatcher.py — Turns "what the user said" into "tools that ran".

Flow:
    transcript ──► Ollama (with the tool list attached)
                      │  "should I call a tool?"
                      ▼
               tool_calls? ──no──► [] (just a normal chat answer)
                      │yes
                      ▼
               run each tool (registry.run_tool) ──► results

This is one small, separate LLM call. The normal streaming reply
(and the voice) is generated afterwards and told what just happened.
"""

import logging
import os
import time

from .registry import get_schemas, run_tool

logger = logging.getLogger(__name__)

TOOLS_ENABLED = os.environ.get("TOOLS_ENABLED", "1") == "1"

ROUTER_PROMPT = (
    "You are the action router of a voice assistant. "
    "If the user asks for something a tool can do (open a website, play a video, search, "
    "scroll, time...), call the matching tool. "
    "Use as FEW tools as possible: one tool is usually enough (to play something on YouTube, "
    "call only play_youtube). "
    "If the user is just chatting or asking a question, do NOT call any tool."
)


async def detect_and_run(llm, model: str, user_text: str) -> list[dict]:
    """
    Ask the LLM which tools to call, run them, and return one dict per call:
        {"name", "arguments", "ok", "result", "ms"}
    Returns [] when no action is needed.
    """
    if not TOOLS_ENABLED or not llm.is_ollama_available:
        return []

    payload = {
        "model": os.environ.get("TOOL_MODEL", model),
        "messages": [
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "tools": get_schemas(),
        "stream": False,
        "keep_alive": "30m",
        "options": {"temperature": 0, "num_ctx": 2048, "num_predict": 120},
    }

    t0 = time.perf_counter()
    try:
        async with llm._session.post(f"{os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/chat", json=payload) as resp:
            if resp.status != 200:
                logger.warning(f"[tools] router returned {resp.status}: {await resp.text()}")
                return []
            data = await resp.json()
    except Exception as e:
        logger.warning(f"[tools] router failed: {e}")
        return []

    tool_calls = data.get("message", {}).get("tool_calls") or []
    logger.info(f"[tools] router decided in {(time.perf_counter() - t0) * 1000:.0f}ms -> {len(tool_calls)} call(s)")

    results = []
    for call in tool_calls[:3]:  # safety cap: never more than 3 actions per sentence
        fn = call.get("function", {})
        name, args = fn.get("name", ""), fn.get("arguments") or {}
        t_tool = time.perf_counter()
        ok, result = await run_tool(name, args)
        ms = round((time.perf_counter() - t_tool) * 1000)
        logger.info(f"[tools] {name}({args}) -> ok={ok} '{result}' ({ms}ms)")
        results.append({"name": name, "arguments": args, "ok": ok, "result": result, "ms": ms})
    return results
