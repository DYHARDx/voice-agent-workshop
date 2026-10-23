"""
voice_test.py — Automatic voice-to-voice test, no microphone needed.

It makes the computer SPEAK a sentence (macOS `say`), streams that audio to the
server exactly like a browser mic would, and prints every step of the pipeline:

    audio -> transcript -> tool call -> AI reply -> AI voice (saved as .wav)

    python voice_test.py "open youtube and play lofi music"   # macOS speaks the sentence
    python voice_test.py my_command.mp3                       # any OS: send a recorded voice file

Needs: server running (uvicorn app.main:app --port 8000), ffmpeg, macOS.
"""

import asyncio
import base64
import json
import subprocess
import sys
import tempfile
import wave

import websockets

URL = "ws://localhost:8000/ws/stream"


AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".aiff", ".ogg", ".flac")


def to_pcm(path: str) -> bytes:
    """Any audio file -> raw 16 kHz mono 16-bit PCM (what the server expects)."""
    out = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ar", "16000", "-ac", "1", "-"],
        check=True, capture_output=True,
    )
    return out.stdout


def speak_to_pcm(sentence: str) -> bytes:
    """Sentence (or path to an audio file) -> 16 kHz PCM. Sentences use macOS `say`."""
    if sentence.lower().endswith(AUDIO_EXTS):
        return to_pcm(sentence)
    with tempfile.NamedTemporaryFile(suffix=".aiff") as f:
        subprocess.run(["say", "-o", f.name, sentence], check=True)
        return to_pcm(f.name)


async def main(sentence: str):
    pcm = speak_to_pcm(sentence)
    silence = b"\x00" * 32000 * 2  # 2 seconds of silence so the server notices we stopped
    print(f"🗣️  Speaking: \"{sentence}\"")

    audio_out, rate = bytearray(), 24000
    async with websockets.connect(URL, max_size=None) as ws:
        await ws.send(json.dumps({"type": "set_config"}))

        async def sender():
            await asyncio.sleep(1)
            chunk = 1024  # bytes per packet (~32 ms)
            for i in range(0, len(pcm + silence), chunk):
                await ws.send((pcm + silence)[i:i + chunk])
                await asyncio.sleep(0.016)  # a bit faster than real time

        send_task = asyncio.create_task(sender())
        async for raw in ws:
            ev = json.loads(raw)
            t = ev.get("type")
            if t == "final_transcript":
                print(f"📝 Heard:      {ev['text']}  ({ev['latency_ms']}ms)")
            elif t == "tool_call":
                print(f"🔧 Tool call:  {ev['name']}({ev['arguments']})")
            elif t == "tool_result":
                print(f"   ↳ result:   {ev['result']}  ({ev['ms']}ms, ok={ev['ok']})")
            elif t == "llm_final_response":
                print(f"🤖 AI says:    {ev['text']}  (1st token {ev['first_token_ms']}ms)")
            elif t == "assistant_audio_chunk":
                audio_out.extend(base64.b64decode(ev["audio_b64"]))
                rate = ev["sample_rate"]
            elif t == "turn_metrics":
                print(f"⏱️  Metrics:    {ev['metrics']}")
            elif t == "assistant_finished":
                break
            elif t == "error":
                print("❌ error:", ev)
                break
        send_task.cancel()

    if audio_out:
        with wave.open("ai_reply.wav", "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(bytes(audio_out))
        print(f"🔊 AI voice saved to ai_reply.wav ({len(audio_out) / (rate * 2):.1f}s of audio)")


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "open youtube and play lofi music"))
