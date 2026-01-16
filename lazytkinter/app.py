from __future__ import annotations
from typing import Tuple, List
import customtkinter as ctk
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_DIR = os.path.join(BASE_DIR, "themes")

def set_mode(mode: str):
    """Sets the application appearance mode.

    Args:
        mode (str): Appearance mode, can be "light", "dark" or "system".
    """
    ctk.set_appearance_mode(mode)

def set_theme(theme_name: str):
    """Sets the application theme.

    First tries to find theme file in built-in themes directory, if not found,
    attempts to load directly through customtkinter.

    Args:
        theme_name (str): Theme name, can be either built-in theme name or system path.

    Raises:
        FileNotFoundError: When theme file cannot be found.
    """
    # Try to find in built-in themes directory
    filename = theme_name if theme_name.endswith(".json") else f"{theme_name}.json"
    internal_path = os.path.join(THEME_DIR, filename)

    if os.path.exists(internal_path):
        # Load using absolute path
        ctk.set_default_color_theme(internal_path)
        print(f"Loaded built-in theme: {theme_name}")
        return

    # If not found in built-in, try passing directly to customtkinter
    # (allows loading JSON from other locations or using default themes like "blue")
    try:
        ctk.set_default_color_theme(theme_name)
    except FileNotFoundError:
        print(f"Error: Theme '{theme_name}' not found in built-in themes or system paths.")

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

class Application(ctk.CTk):
    """Custom Tkinter application base class.

    Attributes:
        _ipadx (int): Horizontal internal padding.
        _ipady (int): Vertical internal padding.
        base_frame (CTkFrame): Base frame container.
    """
    def __init__(self) -> None:
        """Initializes the application."""
        super().__init__() 
        self._ipadx = 0
        self._ipady = 0
        self.base_frame = ctk.CTkFrame(self, corner_radius=0)
        self.base_frame.grid(row=0, column=0, sticky="nsew")

    def window_title(self, title: str) -> Application:
        """Sets window title.

        Args:
            title (str): Window title text.

        Returns:
            Application: Returns self for method chaining.
        """
        self.title(title)
        return self

    def window_size(self, size: str | Tuple | List) -> Application:
        """Sets window size.

        Args:
            size (str | Tuple | List): Window dimensions, can be string format like "400x300"
                or tuple/list containing (width, height).

        Returns:
            Application: Returns self for method chaining.
        """
        if type(size) is str:
            self.geometry(size)
        else:
            self.geometry(f"{size[0]}x{size[1]}")
        return self
    
    def padding(self, pad: int|Tuple[int, int]) -> Application: 
        """Sets internal padding.

        Args:
            pad (int | Tuple[int, int]): Padding value, can be uniform or (horizontal, vertical).

        Returns:
            Application: Returns self for method chaining.
        """
        if type(pad) is int:
            self._ipadx, self._ipady = pad, pad
        elif type(pad) is Tuple:
            self._ipadx, self._ipady = pad[0], pad[1]

        self.base_frame.grid_configure(padx=self._ipadx, pady=self._ipady)
        return self

    def column(self, *args) -> Application:
        """Adds widgets in column layout.

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Application: Returns self for method chaining.
        """
        num = 0
        self.base_frame.columnconfigure(0, weight=1)
        for ele in args:
            self.base_frame.rowconfigure(num, weight=ele._weight)
            the_ele = ele.build(self.base_frame)
            grid_args = {
                "row": num, 
                "column": 0, 
                "sticky": ele._sticky,  # Use child widget's sticky setting
                "padx": ele._margin_x,  # Use child widget's margin settings
                "pady": ele._margin_y,
                "rowspan": ele._row_span,
                "columnspan": ele._col_span
            }
            the_ele.grid(**grid_args)
            num += 1

        return self
    
    def row(self, *args) -> Application:
        """Adds widgets in row layout.

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Application: Returns self for method chaining.
        """
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
                "columnspan": ele._col_span
            }
            the_ele.grid(**grid_args)
            num += 1

        return self
        
    def build(self):
        """Builds the application layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def run(self):
        """Runs the application main loop."""
        self.build()
        self.mainloop()
