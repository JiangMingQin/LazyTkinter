"""Semantic design tokens per built-in theme.

Tokens give colors (and a few constants) semantic names such as "primary",
"surface" or "danger", so UI code can reference meaning instead of raw hex
values. Color setters accept token names and resolve them at build time.
"""

import colorsys

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
        "red": "#f38ba8",
        "orange": "#fab387",
        "yellow": "#f9e2af",
        "green": "#a6e3a1",
        "cyan": "#89dceb",
        "blue": "#89b4fa",
        "purple": "#cba6f7",
        "black": "#11111b",
        "white": "#ffffff",
        "gray": "#6c7086",
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
        "red": "#fb4934",
        "orange": "#fe8019",
        "yellow": "#fabd2f",
        "green": "#b8bb26",
        "cyan": "#8ec07c",
        "blue": "#83a598",
        "purple": "#d3869b",
        "black": "#1d2021",
        "white": "#fbf1c7",
        "gray": "#928374",
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
        "red": "#ff5555",
        "orange": "#ffb86c",
        "yellow": "#f1fa8c",
        "green": "#50fa7b",
        "cyan": "#8be9fd",
        "blue": "#6272a4",
        "purple": "#bd93f9",
        "black": "#21222c",
        "white": "#f8f8f2",
        "gray": "#44475a",
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
        "red": "#C62712",
        "orange": "#E07200",
        "yellow": "#d4a32a",
        "green": "#3bb273",
        "cyan": "#4bb8ce",
        "blue": "#4b8bbe",
        "purple": "#a58fe0",
        "black": "#121212",
        "white": "#f8f5f0",
        "gray": "#808080",
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
        "red": "#cf222e",
        "orange": "#bc4c00",
        "yellow": "#9a6700",
        "green": "#1a7f37",
        "cyan": "#3192a0",
        "blue": "#1f6aa5",
        "purple": "#8250df",
        "black": "#1f2328",
        "white": "#ffffff",
        "gray": "#6e7781",
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
        "red": "#f85149",
        "orange": "#db6d28",
        "yellow": "#d29922",
        "green": "#3fb950",
        "cyan": "#39c5cf",
        "blue": "#58a6ff",
        "purple": "#bc8cff",
        "black": "#010409",
        "white": "#f0f6fc",
        "gray": "#8b949e",
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
        "red": "#cf222e",
        "orange": "#bc4c00",
        "yellow": "#9a6700",
        "green": "#2ea043",
        "cyan": "#3192a0",
        "blue": "#0969da",
        "purple": "#8250df",
        "black": "#1f2328",
        "white": "#ffffff",
        "gray": "#6e7781",
    },
}

_COLOR_TOKENS = (
    "red",
    "orange",
    "yellow",
    "green",
    "cyan",
    "blue",
    "purple",
    "black",
    "white",
    "gray",
)

# hover shifts lightness up on dark themes and down on light themes
_HOVER_DIRECTION = {
    "catppuccin-mocha": 12,
    "gruvbox-theme": 12,
    "dracula-theme": 12,
    "eva02": 12,
    "dark-blue": 12,
    "blue": -12,
    "green": -12,
}


def _adjust_lightness(hex_color: str, delta: float) -> str:
    """Shift a hex color's HSL lightness by ``delta`` percentage points."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    lightness = min(1.0, max(0.0, lightness + delta / 100.0))
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return "#{:02x}{:02x}{:02x}".format(
        round(r * 255), round(g * 255), round(b * 255)
    )


for _theme_name, _theme in _THEMES.items():
    _delta = _HOVER_DIRECTION[_theme_name]
    for _token in _COLOR_TOKENS:
        _theme[f"{_token}_hover"] = _adjust_lightness(_theme[_token], _delta)

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
