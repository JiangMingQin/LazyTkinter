"""Runtime registry mapping widget ids to their config wrappers."""

import tkinter as tk
from typing import Any

_registry: dict[str, Any] = {}


def register(name: str, wrapper, native: tk.Widget) -> None:
    """Register a config wrapper under an id; duplicate ids raise ValueError.

    The wrapper keeps fluent setters working after build (they push to the
    native widget), and the native widget is tagged with the id for debugging.
    """
    if name in _registry:
        raise ValueError(f"duplicate widget id: {name!r}")
    _registry[name] = wrapper
    try:
        native._ltk_id = name
    except Exception:
        pass


def get(name: str) -> Any:
    """Return the config wrapper registered under ``name`` (KeyError if missing)."""
    return _registry[name]


def ids() -> list[str]:
    """Return all registered ids."""
    return list(_registry)


def clear() -> None:
    """Clear the registry (mainly for tests)."""
    _registry.clear()
