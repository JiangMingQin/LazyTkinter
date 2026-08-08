from __future__ import annotations
from typing import Any, Tuple

from .base import BaseWidget
from .renderer import get_renderer

# Keys that the container frames do NOT support. Row/Column/ScrollableColumn
# share this filter so no container accidentally forwards widget-only options
# (font/text_color/state/cursor) to CTkFrame or CTkScrollableFrame.
_FRAME_UNSUPPORTED_KEYS = ("text_color", "font", "state", "cursor")


def _clamp(value, limit):
    """Return ``value`` clamped to ``limit``; ``None`` passes through unchanged."""
    if value is not None and limit is not None:
        return min(value, limit)
    return value


def _frame_props(container, *, width=None, height=None) -> dict[str, Any]:
    """Collect frame constructor props shared by Row/Column/ScrollableColumn."""
    props: dict[str, Any] = {
        "fg_color": "transparent" if container._transparent else None
    }
    container._inject_base_args(props, width=width, height=height)
    for key in _FRAME_UNSUPPORTED_KEYS:
        props.pop(key, None)
    return props


class Empty(BaseWidget["Empty"]):
    """An empty container widget used for spacing and alignment.

    Inherits from BaseWidget and creates a transparent frame with optional dimensions.
    """

    def __init__(self) -> None:
        super().__init__()

    def build(self, parent, *, width=None, height=None):
        """Builds the empty container widget.

        Args:
            parent: The parent widget.
            width: Optional build-time width override (internal use).
            height: Optional build-time height override (internal use).

        Returns:
            A CTkFrame configured as an empty container.
        """
        effective_width = width if width is not None else self._width
        effective_height = height if height is not None else self._height
        props = {
            "fg_color": "transparent",
            "width": effective_width if effective_width else 0,
            "height": effective_height if effective_height else 0,
        }

        frame = get_renderer().create_container("Empty", parent, props)
        frame.pack_propagate(False)
        frame.grid_propagate(False)

        return frame


class Column(BaseWidget["Column"]):
    """A vertical container that arranges widgets in a single column.

    Attributes:
        _spacing (int): Vertical spacing between child widgets.
        _transparent (bool): Whether the container has transparent background.
        _args (tuple): Child widgets to be added.
        _pad_x (int): Horizontal internal padding.
        _pad_y (int): Vertical internal padding.
    """

    def __init__(self, *children) -> None:
        """Initializes the Column container.

        Args:
            *children: Optional child widgets, equivalent to calling add().
        """
        super().__init__()
        self._spacing = 0
        self._transparent = False
        self._args = children

        # Container-specific padding properties
        self._pad_x = 0
        self._pad_y = 0

    def padding(self, pad: int | Tuple[int, int]) -> Column:
        """Sets internal padding for the container.

        Args:
            pad: Padding value, either uniform (int) or (horizontal, vertical) tuple.

        Returns:
            Column: Returns self for method chaining.
        """
        if isinstance(pad, int):
            self._pad_x, self._pad_y = pad, pad
        elif isinstance(pad, tuple):
            self._pad_x, self._pad_y = pad[0], pad[1]
        return self

    def spacing(self, space: int) -> Column:
        """Sets vertical spacing between child widgets.

        Args:
            space: Spacing value in pixels.

        Returns:
            Column: Returns self for method chaining.
        """
        self._spacing = space
        return self

    def transparent(self, val: bool) -> Column:
        """Sets whether the container has transparent background.

        Args:
            val: True for transparent, False for default background.

        Returns:
            Column: Returns self for method chaining.
        """
        self._transparent = val
        return self

    def add(self, *args) -> Column:
        """Adds child widgets to the container (appends to existing children).

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Column: Returns self for method chaining.
        """
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        """Builds the column container with all child widgets.

        Args:
            parent: The parent widget.
            width: Optional build-time width override (internal use).
            height: Optional build-time height override (internal use).

        Returns:
            A configured CTkFrame containing all child widgets in vertical layout.
        """
        frame = get_renderer().create_container(
            "Column", parent, _frame_props(self, width=width, height=height)
        )

        limit_w = width if width is not None else self._width
        limit_h = height if height is not None else self._height
        if limit_w is not None or limit_h is not None:
            frame.pack_propagate(False)

        # Layout in parent container
        grid_args = {
            "sticky": self._sticky,
            "rowspan": self._row_span,
            "columnspan": self._col_span,
            "padx": self._margin_x,
            "pady": self._margin_y,
        }
        frame.grid(**grid_args)

        # Single column configuration
        frame.columnconfigure(0, weight=1)

        # Stack child widgets vertically
        total = len(self._args)
        for i, ele in enumerate(self._args):
            # Clamp child sizes locally; the child's own config is never mutated.
            effective_w = _clamp(ele._width, limit_w)
            effective_h = _clamp(ele._height, limit_h)

            frame.rowconfigure(i, weight=ele._weight)
            the_ele = ele.build(frame, width=effective_w, height=effective_h)

            m_top = ele._margin_y
            m_bottom = ele._margin_y
            if i == 0:
                m_top += self._pad_y
            if i == total - 1:
                m_bottom += self._pad_y
            if i != total - 1:
                m_bottom += self._spacing

            the_ele.grid(
                row=i,
                column=0,
                sticky="nsew",
                padx=ele._margin_x + self._pad_x,
                pady=(m_top, m_bottom),
            )

        return frame


class Row(BaseWidget["Row"]):
    """A horizontal container that arranges widgets in a single row.

    Attributes:
        _spacing (int): Horizontal spacing between child widgets.
        _transparent (bool): Whether the container has transparent background.
        _args (tuple): Child widgets to be added.
        _pad_x (int): Horizontal internal padding.
        _pad_y (int): Vertical internal padding.
    """

    def __init__(self, *children) -> None:
        """Initializes the Row container.

        Args:
            *children: Optional child widgets, equivalent to calling add().
        """
        super().__init__()
        self._spacing = 0
        self._transparent = False
        self._args = children
        self._pad_x = 0
        self._pad_y = 0

    def padding(self, pad: int | Tuple[int, int]) -> Row:
        """Sets internal padding for the container.

        Args:
            pad: Padding value, either uniform (int) or (horizontal, vertical) tuple.

        Returns:
            Row: Returns self for method chaining.
        """
        if isinstance(pad, int):
            self._pad_x, self._pad_y = pad, pad
        elif isinstance(pad, tuple):
            self._pad_x, self._pad_y = pad[0], pad[1]
        return self

    def spacing(self, space: int) -> Row:
        """Sets horizontal spacing between child widgets.

        Args:
            space: Spacing value in pixels.

        Returns:
            Row: Returns self for method chaining.
        """
        self._spacing = space
        return self

    def transparent(self, val: bool) -> Row:
        """Sets whether the container has transparent background.

        Args:
            val: True for transparent, False for default background.

        Returns:
            Row: Returns self for method chaining.
        """
        self._transparent = val
        return self

    def add(self, *args) -> Row:
        """Adds child widgets to the container (appends to existing children).

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Row: Returns self for method chaining.
        """
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        """Builds the row container with all child widgets.

        Args:
            parent: The parent widget.
            width: Optional build-time width override (internal use).
            height: Optional build-time height override (internal use).

        Returns:
            A configured CTkFrame containing all child widgets in horizontal layout.
        """
        frame = get_renderer().create_container(
            "Row", parent, _frame_props(self, width=width, height=height)
        )

        limit_w = width if width is not None else self._width
        limit_h = height if height is not None else self._height
        if limit_w is not None or limit_h is not None:
            frame.pack_propagate(False)

        # Layout in parent container
        grid_args = {
            "sticky": self._sticky,
            "rowspan": self._row_span,
            "columnspan": self._col_span,
            "padx": self._margin_x,
            "pady": self._margin_y,
        }
        frame.grid(**grid_args)

        # Single row configuration
        frame.rowconfigure(0, weight=1)

        # Stack child widgets horizontally
        total = len(self._args)
        for i, ele in enumerate(self._args):
            # Clamp child sizes locally; the child's own config is never mutated.
            effective_w = _clamp(ele._width, limit_w)
            effective_h = _clamp(ele._height, limit_h)

            frame.columnconfigure(i, weight=ele._weight)
            the_ele = ele.build(frame, width=effective_w, height=effective_h)

            m_left = ele._margin_x
            m_right = ele._margin_x
            if i == 0:
                m_left += self._pad_x
            if i == total - 1:
                m_right += self._pad_x
            if i != total - 1:
                m_right += self._spacing

            the_ele.grid(
                row=0,
                column=i,
                sticky="nsew",
                padx=(m_left, m_right),
                pady=ele._margin_y + self._pad_y,
            )

        return frame


class ScrollableColumn(BaseWidget["ScrollableColumn"]):
    """A vertically scrollable container based on CTkScrollableFrame.

    Attributes:
        _spacing (int): Vertical spacing between child widgets.
        _transparent (bool): Whether the container has transparent background.
        _args (tuple): Child widgets to be added.
        _pad_x (int): Horizontal internal padding.
        _pad_y (int): Vertical internal padding.
        _label_text (str): Optional label text for the scrollable frame.
    """

    def __init__(self, *children) -> None:
        """Initializes the ScrollableColumn container.

        Args:
            *children: Optional child widgets, equivalent to calling add().
        """
        super().__init__()
        self._spacing = 0
        self._transparent = False
        self._args = children
        self._pad_x = 0
        self._pad_y = 0
        self._label_text = None

    def padding(self, pad: int | Tuple[int, int]) -> ScrollableColumn:
        """Sets internal padding for the container.

        Args:
            pad: Padding value, either uniform (int) or (horizontal, vertical) tuple.

        Returns:
            ScrollableColumn: Returns self for method chaining.
        """
        if isinstance(pad, int):
            self._pad_x, self._pad_y = pad, pad
        elif isinstance(pad, tuple):
            self._pad_x, self._pad_y = pad[0], pad[1]
        return self

    def spacing(self, space: int) -> ScrollableColumn:
        """Sets vertical spacing between child widgets.

        Args:
            space: Spacing value in pixels.

        Returns:
            ScrollableColumn: Returns self for method chaining.
        """
        self._spacing = space
        return self

    def label(self, text: str) -> ScrollableColumn:
        """Sets an optional label for the scrollable frame.

        Args:
            text: The label text.

        Returns:
            ScrollableColumn: Returns self for method chaining.
        """
        self._label_text = text
        return self

    def transparent(self, val: bool) -> ScrollableColumn:
        """Sets whether the container has transparent background.

        Args:
            val: True for transparent, False for default background.

        Returns:
            ScrollableColumn: Returns self for method chaining.
        """
        self._transparent = val
        return self

    def add(self, *args) -> ScrollableColumn:
        """Adds child widgets to the container (appends to existing children).

        Args:
            *args: Variable number of widgets to add.

        Returns:
            ScrollableColumn: Returns self for method chaining.
        """
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        """Builds the scrollable column container with all child widgets.

        Args:
            parent: The parent widget.
            width: Optional build-time width override (internal use).
            height: Optional build-time height override (internal use).

        Returns:
            A configured CTkScrollableFrame containing all child widgets.
        """
        props = _frame_props(self, width=width, height=height)
        if self._label_text:
            props["label_text"] = self._label_text

        frame = get_renderer().create_container("ScrollableColumn", parent, props)

        limit_w = width if width is not None else self._width

        # Configure single column layout
        frame.columnconfigure(0, weight=1)

        # Add child widgets with spacing
        total = len(self._args)
        for i, ele in enumerate(self._args):
            # Prevent width overflow (height is scrollable)
            effective_w = _clamp(ele._width, limit_w)

            frame.rowconfigure(i, weight=ele._weight)
            the_ele = ele.build(frame, width=effective_w)

            m_top = ele._margin_y
            m_bottom = ele._margin_y
            if i == 0:
                m_top += self._pad_y
            if i == total - 1:
                m_bottom += self._pad_y
            if i != total - 1:
                m_bottom += self._spacing

            the_ele.grid(
                row=i,
                column=0,
                sticky="nsew",
                padx=ele._margin_x + self._pad_x,
                pady=(m_top, m_bottom),
            )

        return frame
