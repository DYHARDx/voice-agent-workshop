"""
app.tools — the "action layer" of the voice agent.

Importing this package auto-loads every tool file in this folder, so
dropping a new .py file here (or editing my_tools.py) is all it takes.
"""

import importlib
import pkgutil

from .registry import TOOLS, get_schemas, list_tools, run_tool  # noqa: F401

_INFRA_MODULES = {"registry", "browser", "dispatcher"}

for _mod in pkgutil.iter_modules(__path__):
    if _mod.name not in _INFRA_MODULES:
        importlib.import_module(f"{__name__}.{_mod.name}")
