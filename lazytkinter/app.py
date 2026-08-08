from __future__ import annotations

from .renderer import get_renderer


def set_mode(mode: str) -> None:
    """Sets the application appearance mode.

    Args:
        mode (str): Appearance mode, can be "light", "dark" or "system".
    """
    get_renderer().set_mode(mode)


def set_theme(theme_name: str) -> None:
    """Sets the application theme.

    First tries to find theme file in built-in themes directory; if not found,
    attempts to load directly through customtkinter.

    Args:
        theme_name (str): Theme name, can be either built-in theme name or system path.

    Raises:
        ValueError: When theme file cannot be found.
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
    # CustomTkinter native themes
    Blue = "blue"
    DarkBlue = "dark-blue"
    Green = "green"

    # Additional themes
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
        """Forward unknown attributes to the native root window.

        Keeps compatibility with the previous CTk subclass: native window
        methods like ``after``, ``protocol`` or ``minsize`` still work on
        ``Application`` instances.
        """
        return getattr(self._window, name)

    def _check_single_layout(self) -> None:
        if self._layout_set:
            raise RuntimeError(
                "Application layout is already set: call column()/row() exactly once. "
                "Use Row/Column containers to build more complex layouts."
            )

    def window_title(self, title: str) -> Application:
        """Sets window title.

        Args:
            title (str): Window title text.

        Returns:
            Application: Returns self for method chaining.
        """
        self._window.title(title)
        return self

    def window_size(self, size) -> Application:
        """Sets window size.

        Args:
            size: Window dimensions, either "400x300" or a (width, height) tuple/list.

        Returns:
            Application: Returns self for method chaining.
        """
        if isinstance(size, str):
            self._window.geometry(size)
        else:
            self._window.geometry(f"{size[0]}x{size[1]}")
        return self

    def padding(self, pad) -> Application:
        """Sets internal padding.

        Args:
            pad: Padding value, can be uniform (int) or (horizontal, vertical) tuple.

        Returns:
            Application: Returns self for method chaining.
        """
        if isinstance(pad, int):
            self._ipadx, self._ipady = pad, pad
        elif isinstance(pad, tuple):
            self._ipadx, self._ipady = pad[0], pad[1]
        else:
            raise TypeError("padding() expects an int or a (horizontal, vertical) tuple")

        self.base_frame.grid_configure(padx=self._ipadx, pady=self._ipady)
        return self

    def column(self, *args) -> Application:
        """Adds widgets in column layout (single root layout call).

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Application: Returns self for method chaining.
        """
        self._check_single_layout()
        num = 0
        self.base_frame.columnconfigure(0, weight=1)
        for ele in args:
            self.base_frame.rowconfigure(num, weight=ele._weight)
            the_ele = ele.build(self.base_frame)
            grid_args = {
                "row": num,
                "column": 0,
                "sticky": ele._sticky,
                "padx": ele._margin_x,
                "pady": ele._margin_y,
                "rowspan": ele._row_span,
                "columnspan": ele._col_span,
            }
            the_ele.grid(**grid_args)
            num += 1

        self._layout_set = True
        return self

    def row(self, *args) -> Application:
        """Adds widgets in row layout (single root layout call).

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Application: Returns self for method chaining.
        """
        self._check_single_layout()
        num = 0
        self.base_frame.rowconfigure(0, weight=1)
        for ele in args:
            self.base_frame.columnconfigure(num, weight=ele._weight)
            the_ele = ele.build(self.base_frame)
            grid_args = {
                "row": 0,
                "column": num,
                "sticky": ele._sticky,
                "padx": ele._margin_x,
                "pady": ele._margin_y,
                "rowspan": ele._row_span,
                "columnspan": ele._col_span,
            }
            the_ele.grid(**grid_args)
            num += 1

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
