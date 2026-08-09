from __future__ import annotations

from .containers import (
    _COLUMN_ALIGN_STICKY,
    _ROW_ALIGN_STICKY,
    _resolve_column_slots,
    _resolve_row_slots,
)
from .renderer import get_renderer
from .registry import get as _registry_get
from .registry import ids as _registry_ids

_WINDOW_PRESETS = {"large": "1200x800", "medium": "900x600", "small": "600x400"}
_WINDOW_ALIGNMENTS = ("left", "center", "right", "top", "bottom")


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
        self._layout_gap = 0
        self._layout_justify = "start"
        self._layout_align = None  # None -> column() uses "left", row() uses "top"
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
        """Sets the window inner padding (integer pixels).

        The padding is applied to the root layout's children, so the base frame
        still covers the whole window (no visible border from the window's own
        background).
        """
        if not isinstance(pad, int) or pad < 0:
            raise ValueError("Application.padding() expects a non-negative integer")
        self._ipadx = pad
        self._ipady = pad
        return self

    def gap(self, space: int) -> Application:
        """Sets the spacing between root layout children (integer pixels)."""
        if not isinstance(space, int) or space < 0:
            raise ValueError("Application.gap() expects a non-negative integer")
        self._layout_gap = space
        return self

    def align(self, value: str) -> Application:
        """Sets the root layout cross-axis alignment.

        ``column()`` accepts "left"/"center"/"right"; ``row()`` accepts
        "top"/"center"/"bottom". The axis is validated when the root layout is
        built.
        """
        if value not in _WINDOW_ALIGNMENTS:
            raise ValueError(
                f"Application.align() expects one of {_WINDOW_ALIGNMENTS!r}, got {value!r}"
            )
        self._layout_align = value
        return self

    def justify(self, value: str) -> Application:
        """Sets the root layout main-axis distribution ("start"/"center"/"end")."""
        if value not in ("start", "center", "end"):
            raise ValueError(
                "Application.justify() expects one of ('start', 'center', 'end'), "
                f"got {value!r}"
            )
        self._layout_justify = value
        return self

    def center(self) -> Application:
        """Centers the root layout children on both axes."""
        return self.justify("center").align("center")

    def column(self, *args) -> Application:
        """Adds widgets in column layout (single root layout call)."""
        self._check_single_layout()
        align = self._layout_align if self._layout_align is not None else "left"
        if align not in _COLUMN_ALIGN_STICKY:
            raise ValueError(
                f"Application.column() cannot use align {align!r}; "
                f"expected one of {list(_COLUMN_ALIGN_STICKY)}"
            )
        self.base_frame.columnconfigure(0, weight=1)
        slots = _resolve_column_slots(
            args,
            default_align=align,
            gap=self._layout_gap,
            padding=self._ipadx,
            justify=self._layout_justify,
        )
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
        align = self._layout_align if self._layout_align is not None else "top"
        if align not in _ROW_ALIGN_STICKY:
            raise ValueError(
                f"Application.row() cannot use align {align!r}; "
                f"expected one of {list(_ROW_ALIGN_STICKY)}"
            )
        self.base_frame.rowconfigure(0, weight=1)
        slots = _resolve_row_slots(
            args,
            default_align=align,
            gap=self._layout_gap,
            padding=self._ipady,
            justify=self._layout_justify,
        )
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

    def get(self, name: str):
        """Return the native widget registered under an id (see ``.id()``)."""
        return _registry_get(name)

    def ids(self) -> list[str]:
        """Return all ids registered via ``.id()``."""
        return _registry_ids()

    def layout_tree(self) -> str:
        """Return a tree of the built widgets (class names and registered ids)."""
        lines = []

        def walk(widget, depth):
            cls = widget.winfo_class()
            ltk_id = getattr(widget, "_ltk_id", None)
            label = cls + (f"[{ltk_id}]" if ltk_id else "")
            lines.append("  " * depth + label)
            for child in widget.winfo_children():
                walk(child, depth + 1)

        walk(self.base_frame, 0)
        return "\n".join(lines)
