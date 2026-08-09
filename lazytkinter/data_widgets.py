"""Data-oriented widgets for large lists (performance-first, themed native look)."""

from __future__ import annotations
from itertools import count
from tkinter import ttk
from typing import Any

from .base import BaseWidget
from .renderer import get_renderer


_DATA_STYLE_SEQ = count(1)


def _configure_data_styles(
    parent, colors, tree_style=None, heading_style=None, scroll_style=None
) -> None:
    """Apply the CTk-derived palette to one data widget instance's ttk styles.

    Each Treeview/Listbox gets its own style names (like SplitPanel) so
    instances never interfere. Listbox itself is a ``tk`` widget and is colored
    through widget options instead of a ttk style.
    """
    if parent is None:
        return
    style = ttk.Style(parent)
    if tree_style is not None:
        style.configure(
            tree_style,
            background=colors["surface"],
            fieldbackground=colors["surface"],
            foreground=colors["text"],
            bordercolor=colors["border"],
            rowheight=26,
        )
        style.map(
            tree_style,
            background=[("selected", colors["primary"])],
            foreground=[("selected", colors["primary_text"])],
        )
    if heading_style is not None:
        style.configure(
            heading_style,
            background=colors["border"],
            foreground=colors["text"],
            relief="flat",
        )
    if scroll_style is not None:
        style.configure(
            scroll_style,
            background=colors["surface"],
            troughcolor=colors["border"],
            arrowcolor=colors["text"],
            borderwidth=0,
        )


def _new_scroll_frame(wrapper, parent, *, width=None, height=None, scroll_style=None):
    """Create the wrapper frame and its vertical scrollbar (grid-based)."""
    # internal helpers are created directly so they never re-register the
    # widget's id nor overwrite its _built reference (the main native widget)
    frame = get_renderer().create_container("Column", parent, {})
    limit_w = width if width is not None else wrapper._width
    limit_h = height if height is not None else wrapper._height
    if limit_w is not None or limit_h is not None:
        frame.grid_propagate(False)

    scrollbar_kwargs: dict[str, Any] = {"orient": "vertical"}
    if scroll_style is not None:
        scrollbar_kwargs["style"] = scroll_style
    scrollbar = get_renderer().create_widget("Scrollbar", frame, scrollbar_kwargs)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    return frame, scrollbar


def _place_scrollable(frame, scrollbar, native):
    """Wire and grid the native widget plus scrollbar into the wrapper frame."""
    native.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=native.yview)
    native.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    return frame


class Treeview(BaseWidget["Treeview"]):
    """A ``ttk.Treeview`` data widget with a built-in vertical scrollbar.

    Trade-off: native ttk widget (performance-first) instead of one CTk widget
    per row; the per-instance ttk style is themed with the CTk palette.
    """

    def __init__(self) -> None:
        super().__init__()
        self._columns: list[str] = []
        self._rows: list[tuple] = []
        self._command = None
        style_n = next(_DATA_STYLE_SEQ)
        self._tree_style = f"LTkData{style_n}.Treeview"
        self._heading_style = f"LTkData{style_n}.Treeview.Heading"
        self._scroll_style = f"LTkDataScroll{style_n}.Vertical.TScrollbar"

    def columns(self, columns: list) -> Treeview:
        """Set the column headers (each header is used as its column id)."""
        self._columns = list(columns)
        return self

    def rows(self, rows: list) -> Treeview:
        """Set the data rows (list of tuples, one tuple per row)."""
        self._rows = list(rows)
        return self

    def event(self, command=lambda value: None) -> Treeview:
        """Set the selection callback; receives the selected row values."""
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        props: dict[str, Any] = {}
        self._inject_base_args(props, width=width, height=height)
        palette = get_renderer().native_theme_colors()
        _configure_data_styles(
            parent,
            palette,
            tree_style=self._tree_style,
            heading_style=self._heading_style,
            scroll_style=self._scroll_style,
        )
        props["style"] = self._tree_style
        frame, scrollbar = _new_scroll_frame(
            self,
            parent,
            width=width,
            height=height,
            scroll_style=self._scroll_style,
        )
        tree = self._create_widget("Treeview", frame, props)

        columns = self._columns or ["Column"]
        tree.configure(columns=columns, show="headings")
        for column in columns:
            tree.heading(column, text=str(column))

        for row in self._rows:
            tree.insert("", "end", values=tuple(row))

        if self._command is not None:
            user_cmd = self._command
            tree.bind("<<TreeviewSelect>>", lambda _event: self._emit_select(tree, user_cmd))

        return _place_scrollable(frame, scrollbar, tree)

    @staticmethod
    def _emit_select(tree, user_cmd):
        selection = tree.selection()
        if selection:
            user_cmd(tree.item(selection[0], "values"))


class Listbox(BaseWidget["Listbox"]):
    """A ``tk.Listbox`` data widget with a built-in vertical scrollbar."""

    def __init__(self) -> None:
        super().__init__()
        self._items: list = []
        self._command = None
        style_n = next(_DATA_STYLE_SEQ)
        self._scroll_style = f"LTkDataScroll{style_n}.Vertical.TScrollbar"

    def items(self, items: list) -> Listbox:
        """Set the list items."""
        self._items = list(items)
        return self

    def event(self, command=lambda value: None) -> Listbox:
        """Set the selection callback; receives the selected item."""
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        props: dict[str, Any] = {}
        self._inject_base_args(props, width=width, height=height)
        palette = get_renderer().native_theme_colors()
        _configure_data_styles(parent, palette, scroll_style=self._scroll_style)
        props.update(
            {
                "bg": palette["surface"],
                "fg": palette["text"],
                "selectbackground": palette["primary"],
                "selectforeground": palette["primary_text"],
                "highlightbackground": palette["border"],
                "highlightthickness": 1,
                "relief": "flat",
                "bd": 0,
            }
        )
        frame, scrollbar = _new_scroll_frame(
            self,
            parent,
            width=width,
            height=height,
            scroll_style=self._scroll_style,
        )
        listbox = self._create_widget("Listbox", frame, props)

        for item in self._items:
            listbox.insert("end", item)

        if self._command is not None:
            user_cmd = self._command
            listbox.bind("<<ListboxSelect>>", lambda _event: self._emit_select(listbox, user_cmd))

        return _place_scrollable(frame, scrollbar, listbox)

    @staticmethod
    def _emit_select(listbox, user_cmd):
        selection = listbox.curselection()
        if selection:
            user_cmd(listbox.get(selection[0]))
