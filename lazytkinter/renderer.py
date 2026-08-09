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
        }

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

    def set_theme(self, theme_name: str) -> None:
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
        ctk.set_appearance_mode(mode)


_renderer: Renderer = CTkRenderer()


def get_renderer() -> Renderer:
    """Return the active renderer (internal API)."""
    return _renderer


def set_renderer(renderer: Renderer) -> None:
    """Replace the active renderer (internal API, mainly used by tests)."""
    global _renderer
    _renderer = renderer
