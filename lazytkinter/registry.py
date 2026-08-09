"""Runtime registry mapping widget ids to their built native widgets."""

_registry: dict[str, object] = {}


def register(name: str, widget) -> None:
    """Register a native widget under an id; duplicate ids raise ValueError."""
    if name in _registry:
        raise ValueError(f"duplicate widget id: {name!r}")
    _registry[name] = widget
    try:
        widget._ltk_id = name
    except Exception:
        pass


def get(name: str):
    """Return the native widget registered under ``name`` (KeyError if missing)."""
    return _registry[name]


def ids() -> list[str]:
    """Return all registered ids."""
    return list(_registry)


def clear() -> None:
    """Clear the registry (mainly for tests)."""
    _registry.clear()
