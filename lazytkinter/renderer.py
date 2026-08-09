"""Renderer protocol and the default CustomTkinter implementation.

This module is the package's only bridge to ``customtkinter``. Widget
descriptions in ``base``, ``widgets`` and ``containers`` and the
``Application`` wrapper never import it directly, so a different Tk-based
backend can be plugged in later by implementing the ``Renderer`` protocol.
"""

from __future__ import annotations

import logging
import os
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Type

import customtkinter as ctk

from .tokens import color as _token_color

logger = logging.getLogger(__name__)

THEME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")

# Re-exports so the rest of the package never has to import customtkinter.
StringVar = ctk.StringVar
IntVar = ctk.IntVar
DoubleVar = ctk.DoubleVar
BooleanVar = ctk.BooleanVar
Image = ctk.CTkImage
Font = ctk.CTkFont


class Renderer:
    """Contract between widget descriptions and a concrete Tk backend."""

    def create_window(self):
        raise NotImplementedError

    def create_widget(self, kind: str, parent, props: Dict[str, Any]):
        raise NotImplementedError

    def create_container(self, kind: str, parent, props: Dict[str, Any]):
        raise NotImplementedError

    def native_theme_colors(self) -> Dict[str, str]:
        """Return a palette of the current theme's colors for native widgets."""
        raise NotImplementedError

    def set_theme(self, theme_name: str) -> None:
        raise NotImplementedError

    def set_mode(self, mode: str) -> None:
        raise NotImplementedError


class CTkRenderer(Renderer):
    """Default renderer backed by CustomTkinter."""

    def __init__(self) -> None:
        self._widget_classes: Dict[str, Type] = {
            "Button": ctk.CTkButton,
            "Label": ctk.CTkLabel,
            "Entry": ctk.CTkEntry,
            "Switch": ctk.CTkSwitch,
            "CheckBox": ctk.CTkCheckBox,
            "RadioButton": ctk.CTkRadioButton,
            "Slider": ctk.CTkSlider,
            "ProgressBar": ctk.CTkProgressBar,
            "SegmentedButton": ctk.CTkSegmentedButton,
            "ComboBox": ctk.CTkComboBox,
            "OptionMenu": ctk.CTkOptionMenu,
            "Textbox": ctk.CTkTextbox,
            "Canvas": ctk.CTkCanvas,
            "Treeview": ttk.Treeview,
            "Listbox": tk.Listbox,
            "Scrollbar": ttk.Scrollbar,
        }
        self._container_classes: Dict[str, Type] = {
            "RootFrame": ctk.CTkFrame,
            "Empty": ctk.CTkFrame,
            "Spacer": ctk.CTkFrame,
            "Column": ctk.CTkFrame,
            "Row": ctk.CTkFrame,
            "ZStack": ctk.CTkFrame,
            "Scroll": ctk.CTkScrollableFrame,
            "SplitPanel": ttk.Panedwindow,
        }
        self._palette_cache: Dict[str, str] | None = None

    def create_window(self):
        return ctk.CTk()

    def create_widget(self, kind: str, parent, props: Dict[str, Any]):
        try:
            widget_cls = self._widget_classes[kind]
        except KeyError:
            raise ValueError(f"Unknown widget kind: {kind!r}") from None
        return widget_cls(parent, **props)

    def create_container(self, kind: str, parent, props: Dict[str, Any]):
        try:
            container_cls = self._container_classes[kind]
        except KeyError:
            raise ValueError(f"Unknown container kind: {kind!r}") from None
        return container_cls(parent, **props)

    def native_theme_colors(self) -> Dict[str, str]:
        if self._palette_cache is None:
            self._palette_cache = _native_theme_palette()
        return self._palette_cache

    def set_theme(self, theme_name: str) -> None:
        self._palette_cache = None
        filename = theme_name if theme_name.endswith(".json") else f"{theme_name}.json"
        internal_path = os.path.join(THEME_DIR, filename)
        if os.path.exists(internal_path):
            ctk.set_default_color_theme(internal_path)
            logger.info("Loaded built-in theme: %s", theme_name)
            return
        try:
            ctk.set_default_color_theme(theme_name)
        except FileNotFoundError:
            raise ValueError(
                f"Theme {theme_name!r} not found in built-in themes or system paths."
            ) from None

    def set_mode(self, mode: str) -> None:
        self._palette_cache = None
        ctk.set_appearance_mode(mode)


def _pick_theme_color(widget: str, option: str, fallback: str) -> str:
    """Read a color from the active CTk theme, resolving [light, dark] pairs."""
    try:
        value = ctk.ThemeManager.theme[widget][option]
    except (KeyError, AttributeError, TypeError):
        return fallback
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return value[1] if ctk.get_appearance_mode() == "Dark" else value[0]
    return value


def _native_theme_palette() -> Dict[str, str]:
    """Build the native-widget palette from the active CTk theme.

    Falls back to semantic tokens when a widget class/option is missing, so
    native widgets stay consistent with the application theme.
    """
    fallback = {
        "surface": _token_color("surface"),
        "text": _token_color("text"),
        "border": _token_color("border"),
        "primary": _token_color("primary"),
        "primary_text": _token_color("text"),
        "field_bg": _token_color("surface"),
        "field_text": _token_color("text"),
        "field_border": _token_color("border"),
    }
    return {
        "surface": _pick_theme_color("CTkFrame", "fg_color", fallback["surface"]),
        "text": _pick_theme_color("CTkLabel", "text_color", fallback["text"]),
        "border": _pick_theme_color("CTkFrame", "border_color", fallback["border"]),
        "primary": _pick_theme_color("CTkButton", "fg_color", fallback["primary"]),
        "primary_text": _pick_theme_color("CTkButton", "text_color", fallback["primary_text"]),
        "field_bg": _pick_theme_color("CTkEntry", "fg_color", fallback["field_bg"]),
        "field_text": _pick_theme_color("CTkEntry", "text_color", fallback["field_text"]),
        "field_border": _pick_theme_color("CTkEntry", "border_color", fallback["field_border"]),
    }


_renderer: Renderer = CTkRenderer()


def get_renderer() -> Renderer:
    """Return the active renderer (internal API)."""
    return _renderer


def set_renderer(renderer: Renderer) -> None:
    """Replace the active renderer (internal API, mainly used by tests)."""
    global _renderer
    _renderer = renderer
