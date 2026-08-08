from __future__ import annotations
from typing import Any

from .base import BaseWidget
from .renderer import get_renderer

# Keys that the container frames do NOT support. All containers share this
# filter so no container accidentally forwards widget-only options
# (font/text_color/state/cursor) to CTkFrame or CTkScrollableFrame.
_FRAME_UNSUPPORTED_KEYS = ("text_color", "font", "state", "cursor")

# align value -> sticky characters on the container's cross axis
_COLUMN_ALIGN_STICKY = {"left": "w", "center": "", "right": "e"}
_ROW_ALIGN_STICKY = {"top": "n", "center": "", "bottom": "s"}
_ZSTACK_ANCHOR_STICKY = {
    "center": "",
    "top": "n",
    "bottom": "s",
    "left": "w",
    "right": "e",
    "top-left": "nw",
    "top-right": "ne",
    "bottom-left": "sw",
    "bottom-right": "se",
}


def _clamp(value, limit):
    """Return ``value`` clamped to ``limit``; ``None`` passes through unchanged."""
    if value is not None and limit is not None:
        return min(value, limit)
    return value


def _compose_sticky(axis_sticky: str, horizontal_fill: bool, vertical_fill: bool) -> str:
    """Combine the cross-axis align sticky with fill stretching on both axes."""
    chars = set(axis_sticky)
    if horizontal_fill:
        chars.update("ew")
    if vertical_fill:
        chars.update("ns")
    return "".join(c for c in "nsew" if c in chars)


def _frame_props(container, *, width=None, height=None) -> dict[str, Any]:
    """Collect frame constructor props shared by all containers.

    Containers are transparent by default; a background color is opt-in via
    ``fg_color()`` (which maps to the frame's fill color), and ``radius()``
    controls the corner radius.
    """
    props: dict[str, Any] = {}
    container._inject_base_args(props, width=width, height=height)
    props.setdefault("fg_color", "transparent")
    for key in _FRAME_UNSUPPORTED_KEYS:
        props.pop(key, None)
    return props


def _resolve_column_slots(children, default_align, gap, padding, justify="start"):
    """Resolve each Column child to (row, weight, sticky, padx, pady).

    Rules:
    - fit children get weight 0; fill children get weight 1 (multiple fills
      split remaining space equally);
    - if any Spacer exists, fill children lose their main-axis stretch and
      Spacers consume the remaining space by their weight;
    - padding applies on the container edges, gap applies between children;
    - the cross axis follows the child's align (or the container default).
    - ``justify="center"`` insets one implicit weight-1 Spacer on each end,
      ``justify="end"`` insets one on the leading end only; implicit spacers
      participate in the "Spacer present -> fill downgrades" rule.
    """
    if justify == "center":
        children = [Spacer()] + list(children) + [Spacer()]
    elif justify == "end":
        children = [Spacer()] + list(children)
    has_spacer = any(isinstance(child, Spacer) for child in children)
    total = len(children)
    slots = []
    for i, child in enumerate(children):
        align = child._align if child._align is not None else default_align
        if align not in _COLUMN_ALIGN_STICKY:
            raise ValueError(
                f"Column child uses invalid align {align!r}; "
                f"expected one of {list(_COLUMN_ALIGN_STICKY)}"
            )
        if isinstance(child, Spacer):
            weight = child._weight
            sticky = ""
        else:
            main_fill = child._height_policy == "fill" and not has_spacer
            cross_fill = child._width_policy == "fill"
            weight = 1 if main_fill else 0
            sticky = _compose_sticky(
                _COLUMN_ALIGN_STICKY[align],
                horizontal_fill=cross_fill,
                vertical_fill=main_fill,
            )
        m_top = padding if i == 0 else 0
        m_bottom = padding if i == total - 1 else 0
        if i != total - 1:
            m_bottom += gap
        slots.append({
            "child": child,
            "row": i,
            "weight": weight,
            "sticky": sticky,
            "padx": padding,
            "pady": (m_top, m_bottom),
        })
    return slots


def _resolve_row_slots(children, default_align, gap, padding, justify="start"):
    """Resolve each Row child to (column, weight, sticky, padx, pady).

    Rules mirror ``_resolve_column_slots`` (including ``justify``) with the main
    axis horizontal.
    """
    if justify == "center":
        children = [Spacer()] + list(children) + [Spacer()]
    elif justify == "end":
        children = [Spacer()] + list(children)
    has_spacer = any(isinstance(child, Spacer) for child in children)
    total = len(children)
    slots = []
    for i, child in enumerate(children):
        align = child._align if child._align is not None else default_align
        if align not in _ROW_ALIGN_STICKY:
            raise ValueError(
                f"Row child uses invalid align {align!r}; "
                f"expected one of {list(_ROW_ALIGN_STICKY)}"
            )
        if isinstance(child, Spacer):
            weight = child._weight
            sticky = ""
        else:
            main_fill = child._width_policy == "fill" and not has_spacer
            cross_fill = child._height_policy == "fill"
            weight = 1 if main_fill else 0
            sticky = _compose_sticky(
                _ROW_ALIGN_STICKY[align],
                horizontal_fill=main_fill,
                vertical_fill=cross_fill,
            )
        m_left = padding if i == 0 else 0
        m_right = padding if i == total - 1 else 0
        if i != total - 1:
            m_right += gap
        slots.append({
            "child": child,
            "column": i,
            "weight": weight,
            "sticky": sticky,
            "padx": (m_left, m_right),
            "pady": padding,
        })
    return slots


def _resolve_zstack_slots(children, default_align, padding):
    """Resolve each ZStack child to (sticky, padx, pady) in the shared cell."""
    slots = []
    for child in children:
        align = child._align if child._align is not None else default_align
        if align not in _ZSTACK_ANCHOR_STICKY:
            raise ValueError(
                f"ZStack child uses invalid align {align!r}; "
                f"expected one of {list(_ZSTACK_ANCHOR_STICKY)}"
            )
        sticky = _compose_sticky(
            _ZSTACK_ANCHOR_STICKY[align],
            horizontal_fill=child._width_policy == "fill",
            vertical_fill=child._height_policy == "fill",
        )
        slots.append({
            "child": child,
            "sticky": sticky,
            "padx": padding,
            "pady": padding,
        })
    return slots


class Empty(BaseWidget["Empty"]):
    """A fixed-size transparent placeholder used for spacing."""

    def __init__(self) -> None:
        super().__init__()

    def build(self, parent, *, width=None, height=None):
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


class Spacer(BaseWidget["Spacer"]):
    """An elastic spring that consumes the container's remaining main-axis space.

    When multiple Spacers share a container, they split the leftover space by
    their ``weight`` ratio.
    """

    def __init__(self) -> None:
        super().__init__()
        self._weight = 1

    def weight(self, w: int) -> Spacer:
        """Set the space-sharing weight (positive integer, default 1)."""
        if isinstance(w, int) and w >= 1:
            self._weight = w
        else:
            raise ValueError("Spacer.weight() expects a positive integer")
        return self

    def build(self, parent, *, width=None, height=None):
        props = {"fg_color": "transparent", "width": 0, "height": 0}
        return get_renderer().create_container("Spacer", parent, props)


class Column(BaseWidget["Column"]):
    """A vertical container that stacks children from top to bottom.

    Attributes:
        _args (tuple): Child widgets.
        _gap (int): Vertical spacing between children.
        _padding (int): Inner padding on the container edges.
        _default_align (str): Default cross-axis alignment ("left"/"center"/"right").
    """

    def __init__(self, *children) -> None:
        """Initialize the Column container.

        Args:
            *children: Optional child widgets, equivalent to calling add().
        """
        super().__init__()
        self._width_policy = "fill"  # Columns stretch across the parent by default
        self._default_align = "left"
        self._justify = "start"
        self._args = children
        self._gap = 0
        self._padding = 0

    def align(self, a: str) -> Column:
        """Set the default cross-axis alignment for children."""
        if a not in _COLUMN_ALIGN_STICKY:
            raise ValueError(
                f"Column.align() expects one of {list(_COLUMN_ALIGN_STICKY)}, got {a!r}"
            )
        self._default_align = a
        return self

    def justify(self, value: str) -> Column:
        """Set the main-axis distribution: "start" (default), "center" or "end".

        "center" / "end" automatically turn the main axis into "fill" (when no
        fixed height is set) so there is space to distribute.
        """
        if value not in ("start", "center", "end"):
            raise ValueError(
                f"Column.justify() expects one of ('start', 'center', 'end'), got {value!r}"
            )
        self._justify = value
        if value != "start" and self._height is None and self._height_policy == "fit":
            self._height_policy = "fill"
        return self

    def center(self) -> Column:
        """Center children on both axes: justify("center") + align("center")."""
        return self.justify("center").align("center")

    def gap(self, space: int) -> Column:
        """Set the vertical spacing between children (integer pixels)."""
        if isinstance(space, int) and space >= 0:
            self._gap = space
        else:
            raise ValueError("gap() expects a non-negative integer")
        return self

    def padding(self, pad: int) -> Column:
        """Set the inner padding (integer pixels)."""
        if isinstance(pad, int) and pad >= 0:
            self._padding = pad
        else:
            raise ValueError("padding() expects a non-negative integer")
        return self

    def add(self, *args) -> Column:
        """Append child widgets to the container."""
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        frame = get_renderer().create_container(
            "Column", parent, _frame_props(self, width=width, height=height)
        )
        limit_w = width if width is not None else self._width
        limit_h = height if height is not None else self._height
        if limit_w is not None or limit_h is not None:
            frame.grid_propagate(False)

        frame.columnconfigure(0, weight=1)
        slots = _resolve_column_slots(
            self._args, self._default_align, self._gap, self._padding, self._justify
        )
        for slot in slots:
            child = slot["child"]
            effective_w = _clamp(child._width, limit_w)
            effective_h = _clamp(child._height, limit_h)
            the_ele = child.build(frame, width=effective_w, height=effective_h)
            frame.rowconfigure(slot["row"], weight=slot["weight"])
            the_ele.grid(
                row=slot["row"],
                column=0,
                sticky=slot["sticky"],
                padx=slot["padx"],
                pady=slot["pady"],
            )
        return frame


class Row(BaseWidget["Row"]):
    """A horizontal container that arranges children from left to right.

    Attributes:
        _args (tuple): Child widgets.
        _gap (int): Horizontal spacing between children.
        _padding (int): Inner padding on the container edges.
        _default_align (str): Default cross-axis alignment ("top"/"center"/"bottom").
    """

    def __init__(self, *children) -> None:
        """Initialize the Row container.

        Args:
            *children: Optional child widgets, equivalent to calling add().
        """
        super().__init__()
        self._default_align = "top"
        self._justify = "start"
        self._args = children
        self._gap = 0
        self._padding = 0

    def align(self, a: str) -> Row:
        """Set the default cross-axis alignment for children."""
        if a not in _ROW_ALIGN_STICKY:
            raise ValueError(
                f"Row.align() expects one of {list(_ROW_ALIGN_STICKY)}, got {a!r}"
            )
        self._default_align = a
        return self

    def justify(self, value: str) -> Row:
        """Set the main-axis distribution: "start" (default), "center" or "end".

        "center" / "end" automatically turn the main axis into "fill" (when no
        fixed width is set) so there is space to distribute.
        """
        if value not in ("start", "center", "end"):
            raise ValueError(
                f"Row.justify() expects one of ('start', 'center', 'end'), got {value!r}"
            )
        self._justify = value
        if value != "start" and self._width is None and self._width_policy == "fit":
            self._width_policy = "fill"
        return self

    def center(self) -> Row:
        """Center children on both axes: justify("center") + align("center")."""
        return self.justify("center").align("center")

    def gap(self, space: int) -> Row:
        """Set the horizontal spacing between children (integer pixels)."""
        if isinstance(space, int) and space >= 0:
            self._gap = space
        else:
            raise ValueError("gap() expects a non-negative integer")
        return self

    def padding(self, pad: int) -> Row:
        """Set the inner padding (integer pixels)."""
        if isinstance(pad, int) and pad >= 0:
            self._padding = pad
        else:
            raise ValueError("padding() expects a non-negative integer")
        return self

    def add(self, *args) -> Row:
        """Append child widgets to the container."""
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        frame = get_renderer().create_container(
            "Row", parent, _frame_props(self, width=width, height=height)
        )
        limit_w = width if width is not None else self._width
        limit_h = height if height is not None else self._height
        if limit_w is not None or limit_h is not None:
            frame.grid_propagate(False)

        frame.rowconfigure(0, weight=1)
        slots = _resolve_row_slots(
            self._args, self._default_align, self._gap, self._padding, self._justify
        )
        for slot in slots:
            child = slot["child"]
            effective_w = _clamp(child._width, limit_w)
            effective_h = _clamp(child._height, limit_h)
            the_ele = child.build(frame, width=effective_w, height=effective_h)
            frame.columnconfigure(slot["column"], weight=slot["weight"])
            the_ele.grid(
                row=0,
                column=slot["column"],
                sticky=slot["sticky"],
                padx=slot["padx"],
                pady=slot["pady"],
            )
        return frame


class ZStack(BaseWidget["ZStack"]):
    """A container that overlaps all children in the same area.

    Children are anchored by their own ``align`` value, falling back to the
    container's default anchor ("center").
    """

    def __init__(self, *children) -> None:
        """Initialize the ZStack container.

        Args:
            *children: Optional child widgets, equivalent to calling add().
        """
        super().__init__()
        self._width_policy = "fill"
        self._height_policy = "fill"
        self._default_align = "center"
        self._args = children
        self._padding = 0

    def align(self, a: str) -> ZStack:
        """Set the default anchor for children."""
        if a not in _ZSTACK_ANCHOR_STICKY:
            raise ValueError(
                f"ZStack.align() expects one of {list(_ZSTACK_ANCHOR_STICKY)}, got {a!r}"
            )
        self._default_align = a
        return self

    def padding(self, pad: int) -> ZStack:
        """Set the inner padding (integer pixels)."""
        if isinstance(pad, int) and pad >= 0:
            self._padding = pad
        else:
            raise ValueError("padding() expects a non-negative integer")
        return self

    def add(self, *args) -> ZStack:
        """Append child widgets to the container."""
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        frame = get_renderer().create_container(
            "ZStack", parent, _frame_props(self, width=width, height=height)
        )
        limit_w = width if width is not None else self._width
        limit_h = height if height is not None else self._height
        if limit_w is not None or limit_h is not None:
            frame.grid_propagate(False)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        slots = _resolve_zstack_slots(self._args, self._default_align, self._padding)
        for slot in slots:
            child = slot["child"]
            effective_w = _clamp(child._width, limit_w)
            effective_h = _clamp(child._height, limit_h)
            the_ele = child.build(frame, width=effective_w, height=effective_h)
            the_ele.grid(
                row=0,
                column=0,
                sticky=slot["sticky"],
                padx=slot["padx"],
                pady=slot["pady"],
            )
        return frame


class Scroll(BaseWidget["Scroll"]):
    """A scrollable wrapper around a single child.

    v1 only supports ``direction='vertical'`` (backed by CTkScrollableFrame);
    horizontal / both directions require a canvas-based renderer and are not
    implemented yet.
    """

    def __init__(self, *children) -> None:
        """Initialize the Scroll wrapper.

        Args:
            *children: Exactly one child widget.
        """
        super().__init__()
        if len(children) != 1:
            raise ValueError("Scroll expects exactly one child, e.g. Scroll(Column(...))")
        self._width_policy = "fill"
        self._height_policy = "fill"
        self._child = children[0]
        self._direction = "vertical"

    def direction(self, d: str) -> Scroll:
        """Set the scroll direction ("vertical" for now)."""
        if d != "vertical":
            raise NotImplementedError(
                "Scroll only supports direction='vertical' for now; "
                "horizontal/both need a canvas-based renderer"
            )
        self._direction = d
        return self

    def build(self, parent, *, width=None, height=None):
        frame = get_renderer().create_container(
            "Scroll", parent, _frame_props(self, width=width, height=height)
        )
        limit_w = width if width is not None else self._width
        limit_h = height if height is not None else self._height

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        effective_w = _clamp(self._child._width, limit_w)
        effective_h = _clamp(self._child._height, limit_h)
        the_ele = self._child.build(frame, width=effective_w, height=effective_h)
        the_ele.grid(row=0, column=0, sticky="nsew")
        return frame
