from __future__ import annotations

from .containers import _resolve_column_slots, _resolve_row_slots
from .renderer import get_renderer

_WINDOW_PRESETS = {"large": "1200x800", "medium": "900x600", "small": "600x400"}


def _resolve_window_size(size):
    """Map a Window size value to an action: ("zoom", None) or ("geometry", "WxH")."""
    if size == "fill":
        return "zoom", None
    if isinstance(size, str):
        if size in _WINDOW_PRESETS:
            return "geometry", _WINDOW_PRESETS[size]
        raise ValueError(
            f"size() expects 'fill', 'large', 'medium', 'small' or a (width, height) "
            f"tuple, got {size!r}"
        )
    if isinstance(size, tuple) and len(size) == 2:
        width, height = size
        if isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            return "geometry", f"{width}x{height}"
        raise ValueError("size() tuple must contain two positive integers")
    raise ValueError(
        f"size() expects 'fill', 'large', 'medium', 'small' or a (width, height) "
        f"tuple, got {size!r}"
    )


def set_mode(mode: str) -> None:
    """Sets the application appearance mode ("light", "dark" or "system")."""
    get_renderer().set_mode(mode)


def set_theme(theme_name: str) -> None:
    """Sets the application theme.

    First tries to find the theme file in the built-in themes directory; if not
    found, attempts to load it directly through customtkinter.

    Raises:
        ValueError: When the theme file cannot be found.
    """
    get_renderer().set_theme(theme_name)


class Theme:
    """Built-in theme enumeration for autocompletion support.

    Attributes:
        Blue: CustomTkinter native blue theme.
        DarkBlue: CustomTkinter native dark-blue theme.
        Green: CustomTkinter native green theme.
        Catppuccin: Catppuccin Mocha theme.
        Gruvbox: Gruvbox theme.
        Dracula: Dracula theme.
        EVA02: EVA02 theme.
    """
    Blue = "blue"
    DarkBlue = "dark-blue"
    Green = "green"

    Catppuccin = "catppuccin-mocha"
    Gruvbox = "gruvbox-theme"
    Dracula = "dracula-theme"
    EVA02 = "eva02"


class Application:
    """LazyTkinter application wrapper around the renderer's root window.

    Attributes:
        base_frame: Root frame container that holds the single layout.
    """

    def __init__(self) -> None:
        """Initializes the application."""
        self._window = get_renderer().create_window()
        self._ipadx = 0
        self._ipady = 0
        self._layout_set = False
        self.base_frame = get_renderer().create_container(
            "RootFrame", self._window, {"corner_radius": 0}
        )
        self.base_frame.grid(row=0, column=0, sticky="nsew")

    def __getattr__(self, name):
        """Forward unknown attributes to the native root window."""
        return getattr(self._window, name)

    def _check_single_layout(self) -> None:
        if self._layout_set:
            raise RuntimeError(
                "Application layout is already set: call column()/row() exactly once. "
                "Use Row/Column containers to build more complex layouts."
            )

    def window_title(self, title: str) -> Application:
        """Sets window title."""
        self._window.title(title)
        return self

    def size(self, size) -> Application:
        """Sets window size.

        Args:
            size: "fill" (maximize), "large"/"medium"/"small" presets, or a
                (width, height) tuple.
        """
        action, value = _resolve_window_size(size)
        if action == "zoom":
            self._window.state("zoomed")
        else:
            self._window.geometry(value)
        return self

    def padding(self, pad: int) -> Application:
        """Sets the window inner padding (integer pixels)."""
        if not isinstance(pad, int) or pad < 0:
            raise ValueError("Application.padding() expects a non-negative integer")
        self._ipadx = pad
        self._ipady = pad
        self.base_frame.grid_configure(padx=pad, pady=pad)
        return self

    def column(self, *args) -> Application:
        """Adds widgets in column layout (single root layout call)."""
        self._check_single_layout()
        self.base_frame.columnconfigure(0, weight=1)
        slots = _resolve_column_slots(args, default_align="left", gap=0, padding=0)
        for slot in slots:
            the_ele = slot["child"].build(self.base_frame)
            self.base_frame.rowconfigure(slot["row"], weight=slot["weight"])
            the_ele.grid(
                row=slot["row"],
                column=0,
                sticky=slot["sticky"],
                padx=slot["padx"],
                pady=slot["pady"],
            )
        self._layout_set = True
        return self

    def row(self, *args) -> Application:
        """Adds widgets in row layout (single root layout call)."""
        self._check_single_layout()
        self.base_frame.rowconfigure(0, weight=1)
        slots = _resolve_row_slots(args, default_align="top", gap=0, padding=0)
        for slot in slots:
            the_ele = slot["child"].build(self.base_frame)
            self.base_frame.columnconfigure(slot["column"], weight=slot["weight"])
            the_ele.grid(
                row=0,
                column=slot["column"],
                sticky=slot["sticky"],
                padx=slot["padx"],
                pady=slot["pady"],
            )
        self._layout_set = True
        return self

    def build(self) -> None:
        """Builds the application layout (root grid weights)."""
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)

    def run(self) -> None:
        """Runs the application main loop."""
        self.build()
        self._window.mainloop()
