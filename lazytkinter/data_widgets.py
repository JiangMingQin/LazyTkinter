"""Data-oriented widgets for large lists (performance-first, native look)."""

from __future__ import annotations
from typing import Any

from .base import BaseWidget
from .renderer import get_renderer


def _new_scroll_frame(wrapper, parent, *, width=None, height=None):
    """Create the wrapper frame and its vertical scrollbar (grid-based)."""
    # internal helpers are created directly so they never re-register the
    # widget's id nor overwrite its _built reference (the main native widget)
    frame = get_renderer().create_container("Column", parent, {})
    limit_w = width if width is not None else wrapper._width
    limit_h = height if height is not None else wrapper._height
    if limit_w is not None or limit_h is not None:
        frame.grid_propagate(False)

    scrollbar = get_renderer().create_widget("Scrollbar", frame, {"orient": "vertical"})
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

    Trade-off: native ttk appearance (performance-first) instead of CTk
    styling; one widget plus data instead of one widget per row.
    """

    def __init__(self) -> None:
        super().__init__()
        self._columns: list[str] = []
        self._rows: list[tuple] = []
        self._command = None

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
        frame, scrollbar = _new_scroll_frame(self, parent, width=width, height=height)
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
        frame, scrollbar = _new_scroll_frame(self, parent, width=width, height=height)
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
