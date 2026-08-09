"""Semantic design tokens per built-in theme.

Tokens give colors (and a few constants) semantic names such as "primary",
"surface" or "danger", so UI code can reference meaning instead of raw hex
values. Color setters accept token names and resolve them at build time.
"""

_THEMES = {
    "catppuccin-mocha": {
        "primary": "#cba6f7",
        "primary_hover": "#bb9af7",
        "surface": "#313244",
        "surface_alt": "#45475a",
        "text": "#cdd6f4",
        "text_secondary": "#a6adc8",
        "border": "#45475a",
        "success": "#a6e3a1",
        "danger": "#f38ba8",
        "warning": "#f9e2af",
        "bg": "#1e1e2e",
        "radius": 10,
        "spacing": 8,
    },
    "gruvbox-theme": {
        "primary": "#b8bb26",
        "primary_hover": "#fabd2f",
        "surface": "#3c3836",
        "surface_alt": "#504945",
        "text": "#ebdbb2",
        "text_secondary": "#a89984",
        "border": "#504945",
        "success": "#b8bb26",
        "danger": "#fb4934",
        "warning": "#fabd2f",
        "bg": "#282828",
        "radius": 10,
        "spacing": 8,
    },
    "dracula-theme": {
        "primary": "#bd93f9",
        "primary_hover": "#caa9fa",
        "surface": "#282a36",
        "surface_alt": "#44475a",
        "text": "#f8f8f2",
        "text_secondary": "#6272a4",
        "border": "#44475a",
        "success": "#50fa7b",
        "danger": "#ff5555",
        "warning": "#f1fa8c",
        "bg": "#21222c",
        "radius": 10,
        "spacing": 8,
    },
    "eva02": {
        "primary": "#2c9f8f",
        "primary_hover": "#3bb9a8",
        "surface": "#2a2f3a",
        "surface_alt": "#383d4a",
        "text": "#dce2ea",
        "text_secondary": "#8a919e",
        "border": "#383d4a",
        "success": "#3bb273",
        "danger": "#e5533d",
        "warning": "#e1c34f",
        "bg": "#1e2128",
        "radius": 10,
        "spacing": 8,
    },
    "blue": {
        "primary": "#1f6aa5",
        "primary_hover": "#2a7fb8",
        "surface": "#dbdbdb",
        "surface_alt": "#c9c9c9",
        "text": "#1a1a1a",
        "text_secondary": "#666666",
        "border": "#999999",
        "success": "#2ea043",
        "danger": "#d73a49",
        "warning": "#d29922",
        "bg": "#f0f0f0",
        "radius": 10,
        "spacing": 8,
    },
    "dark-blue": {
        "primary": "#1f6aa5",
        "primary_hover": "#2a7fb8",
        "surface": "#2b2b2b",
        "surface_alt": "#3a3a3a",
        "text": "#e0e0e0",
        "text_secondary": "#999999",
        "border": "#555555",
        "success": "#2ea043",
        "danger": "#f85149",
        "warning": "#d29922",
        "bg": "#1e1e1e",
        "radius": 10,
        "spacing": 8,
    },
    "green": {
        "primary": "#2ea043",
        "primary_hover": "#3fb950",
        "surface": "#dbdbdb",
        "surface_alt": "#c9c9c9",
        "text": "#1a1a1a",
        "text_secondary": "#666666",
        "border": "#999999",
        "success": "#2ea043",
        "danger": "#d73a49",
        "warning": "#d29922",
        "bg": "#f0f0f0",
        "radius": 10,
        "spacing": 8,
    },
}

_DEFAULT_THEME = "catppuccin-mocha"
_current = _DEFAULT_THEME


def set_theme(name: str) -> None:
    """Switch the active token set; unknown themes keep the default tokens."""
    global _current
    _current = name if name in _THEMES else _DEFAULT_THEME


def color(name: str):
    """Return the current theme's value for a semantic token."""
    try:
        return _THEMES[_current][name]
    except KeyError:
        raise ValueError(f"unknown token {name!r}") from None


def resolve(value):
    """Resolve a token name to its value; non-token values pass through."""
    if isinstance(value, str) and value in _THEMES[_current]:
        return _THEMES[_current][value]
    return value


class _Tokens:
    """Access the current theme's tokens as attributes (e.g. ``Tokens.radius``)."""

    def __getattr__(self, name: str):
        if name in _THEMES[_current]:
            return _THEMES[_current][name]
        raise AttributeError(name)


Tokens = _Tokens()
