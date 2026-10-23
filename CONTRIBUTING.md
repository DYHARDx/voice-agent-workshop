# Contributing

Welcome! The easiest first contribution is **one new voice tool**.

1. Fork & clone, run `./setup.sh`.
2. Create a branch: `git checkout -b tool/<your-tool-name>`
3. Add your function to `app/tools/my_tools.py` (or a new file in `app/tools/` — it's auto-loaded).
4. Test it without a mic: `.venv/bin/python try_tools.py "say the phrase that should trigger it"`
5. Then try it by voice.
6. Open a Pull Request with: what the tool does, the phrase you used, and a screenshot or short clip.

## Tool checklist
- [ ] Has `@tool` and a clear one-line docstring (+ `Args:` for parameters)
- [ ] Returns a **short** string (it's spoken aloud)
- [ ] Safe: no shell commands, no deleting files, no sending messages/money
- [ ] Works when it fails — a clear error message instead of a crash

## Other ideas
Better prompts · faster routing · more languages (Whisper + Piper voices) · a "confirm before acting" step · tests for `registry.py`.
