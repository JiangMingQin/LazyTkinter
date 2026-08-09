from __future__ import annotations
from itertools import count
from tkinter import ttk
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

    Containers use the theme's default frame color unless ``transparent()``
    or an explicit ``fg_color()`` is set; ``radius()`` controls the corner
    radius.
    """
    props: dict[str, Any] = {}
    container._inject_base_args(props, width=width, height=height)
    if container._transparent:
        props["fg_color"] = "transparent"
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
            if child._weight is not None and not main_fill:
                raise ValueError(
                    "fill(weight=...) only works when the child fills the "
                    "container's main axis (fit children or fills downgraded "
                    "by a Spacer cannot use weight)"
                )
            weight = (child._weight if child._weight is not None else 1) if main_fill else 0
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
            if child._weight is not None and not main_fill:
                raise ValueError(
                    "fill(weight=...) only works when the child fills the "
                    "container's main axis (fit children or fills downgraded "
                    "by a Spacer cannot use weight)"
                )
            weight = (child._weight if child._weight is not None else 1) if main_fill else 0
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
        if child._weight is not None:
            raise ValueError("fill(weight=...) is only for Row/Column main-axis fills")
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
        frame = self._create_container("Empty", parent, props)
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
        return self._create_container("Spacer", parent, props)


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
        self._transparent = False
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

    def transparent(self, val: bool = True) -> Column:
        """Opt into a transparent background (default is the theme color)."""
        self._transparent = val
        return self

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
        frame = self._create_container(
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
        self._transparent = False
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

    def transparent(self, val: bool = True) -> Row:
        """Opt into a transparent background (default is the theme color)."""
        self._transparent = val
        return self

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
        frame = self._create_container(
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
        self._transparent = False
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

    def transparent(self, val: bool = True) -> ZStack:
        """Opt into a transparent background (default is the theme color)."""
        self._transparent = val
        return self

    def add(self, *args) -> ZStack:
        """Append child widgets to the container."""
        self._args = self._args + args
        return self

    def build(self, parent, *, width=None, height=None):
        frame = self._create_container(
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
        self._transparent = False
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

    def transparent(self, val: bool = True) -> Scroll:
        """Opt into a transparent background (default is the theme color)."""
        self._transparent = val
        return self

    def build(self, parent, *, width=None, height=None):
        frame = self._create_container(
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


_SPLIT_STYLE_SEQ = count(1)


def _configure_split_panel_style(parent, colors, sash_width, proxysash, style_name) -> None:
    """Apply the CTk-derived palette to this SplitPanel's ttk style.

    Each SplitPanel gets its own ``LTkSplitPanel<N>.TPanedwindow`` style so
    per-instance options (sash width, proxy sash) never leak across panels.
    """
    if parent is None:
        return
    style = ttk.Style(parent)
    opts = {
        "background": colors["border"],
        "sashwidth": sash_width,
        "sashrelief": "flat",
    }
    if proxysash:
        # drag a ghost sash and only split on release, reducing redraw cost
        opts["proxysash"] = 1
    style.configure(style_name, **opts)


def _validate_pane_size(value, name: str) -> int:
    """Validate a per-pane min/max constraint value."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"SplitPanel.{name}() expects a non-negative integer")
    return value


def _resolve_sash_positions(sizes, mins, maxs, total):
    """Compute target sash positions satisfying per-pane min/max constraints.

    Args:
        sizes: current pane sizes along the sash axis.
        mins: per-pane minimum size (None = 0).
        maxs: per-pane maximum size (None = unbounded).
        total: total pane space along the sash axis.

    Returns:
        Target positions for each sash (n-1 values). Each sash is clamped to
        the intersection of the leading pane's [min, max] and the trailing
        panes' aggregate [min, max]; when the intersection is empty, minimum
        constraints take priority.
    """
    n = len(sizes)
    if n < 2:
        return []
    lo = [0 if m is None else m for m in mins]
    hi = [float("inf") if x is None else x for x in maxs]
    pos = []
    acc = 0
    for size in sizes:
        acc += size
        pos.append(acc)
    for i in range(n - 1):
        prev = pos[i - 1] if i > 0 else 0
        trailing_min = sum(lo[i + 1:])
        trailing_max = sum(hi[i + 1:])
        low = max(prev + lo[i], total - trailing_max)
        high = min(prev + hi[i], total - trailing_min)
        if low > high:
            # infeasible: min constraints win over max constraints
            low = prev + lo[i]
            high = min(prev + hi[i], total - trailing_min)
            if high < low:
                high = low
        pos[i] = min(max(pos[i], low), high)
    return pos[:-1]


class SplitPanel(BaseWidget["SplitPanel"]):
    """A resizable split container backed by ``ttk.Panedwindow``.

    Direction follows the cut line: ``.vertical()`` makes a vertical cut
    (left/right panes, width constraints) and ``.horizontal()`` makes a
    horizontal cut (top/bottom panes, height constraints). Panes are added
    with the chainable ``.add(child)`` followed by per-pane attributes::

        ltk.SplitPanel().vertical()
            .add(ltk.Column(...)).min_width(120).max_width(400).transparent()
            .add(ltk.Column(...)).min_width(200)

    Min/max sizes are enforced with a ``sashpos()`` clamp after a drag, because
    ``ttk.Panedwindow`` has no native per-pane size constraints.
    """

    def __init__(self, *children) -> None:
        """Initialize the SplitPanel container.

        Args:
            *children: Optional pane widgets, equivalent to calling add().
        """
        super().__init__()
        self._width_policy = "fill"
        self._height_policy = "fill"
        self._orientation = "vertical"  # cut-line direction: vertical = left/right
        self._sash_width = 5
        self._proxy_sash = True
        self._style_name = f"LTkSplitPanel{next(_SPLIT_STYLE_SEQ)}.TPanedwindow"
        self._panes: list[dict[str, Any]] = []
        for child in children:
            self.add(child)

    @staticmethod
    def _check_child(child) -> None:
        if not hasattr(child, "build"):
            raise TypeError(
                "SplitPanel children must be LazyTkinter widgets with build(), "
                f"got {type(child).__name__}"
            )

    def add(self, *args) -> SplitPanel:
        """Append pane widgets; per-pane attributes apply to the last add."""
        for child in args:
            self._check_child(child)
            self._panes.append(
                {
                    "child": child,
                    "min_width": None,
                    "max_width": None,
                    "min_height": None,
                    "max_height": None,
                    "transparent": False,
                }
            )
        return self

    def _last_pane(self) -> dict[str, Any]:
        if not self._panes:
            raise ValueError(
                "SplitPanel pane attributes must follow add(), e.g. "
                "SplitPanel().vertical().add(child).min_width(120)"
            )
        return self._panes[-1]

    def min_width(self, value: int) -> SplitPanel:
        """Set the last pane's minimum width (vertical cut)."""
        self._last_pane()["min_width"] = _validate_pane_size(value, "min_width")
        return self

    def max_width(self, value: int) -> SplitPanel:
        """Set the last pane's maximum width (vertical cut)."""
        self._last_pane()["max_width"] = _validate_pane_size(value, "max_width")
        return self

    def min_height(self, value: int) -> SplitPanel:
        """Set the last pane's minimum height (horizontal cut)."""
        self._last_pane()["min_height"] = _validate_pane_size(value, "min_height")
        return self

    def max_height(self, value: int) -> SplitPanel:
        """Set the last pane's maximum height (horizontal cut)."""
        self._last_pane()["max_height"] = _validate_pane_size(value, "max_height")
        return self

    def transparent(self, active: bool = True) -> SplitPanel:
        """Make the last pane's wrapper frame transparent."""
        if not isinstance(active, bool):
            raise ValueError("SplitPanel.transparent() expects a bool")
        self._last_pane()["transparent"] = active
        return self

    def orientation(self, orient=None) -> SplitPanel:
        """Set the cut direction.

        ``vertical`` = vertical cut line (left/right panes, width attributes);
        ``horizontal`` = horizontal cut line (top/bottom panes, height
        attributes). Chainable form mirrors ``width().fill()``:
        ``.orientation().vertical()``; the string form is also accepted.
        Calling without an argument is a no-op prefix.
        """
        if orient is None:
            return self
        if orient not in ("vertical", "horizontal"):
            raise ValueError(
                "SplitPanel.orientation() expects 'vertical' or 'horizontal', "
                f"got {orient!r}"
            )
        self._orientation = orient
        return self

    def vertical(self) -> SplitPanel:
        """Cut vertically: left/right panes (width constraints)."""
        self._orientation = "vertical"
        return self

    def horizontal(self) -> SplitPanel:
        """Cut horizontally: top/bottom panes (height constraints)."""
        self._orientation = "horizontal"
        return self

    def sash_width(self, width: int) -> SplitPanel:
        """Set the draggable sash thickness (non-negative integer)."""
        if not isinstance(width, int) or isinstance(width, bool) or width < 0:
            raise ValueError("SplitPanel.sash_width() expects a non-negative integer")
        self._sash_width = width
        return self

    def proxy_sash(self, active: bool = True) -> SplitPanel:
        """Toggle the ghost-sash drag behavior (default True, performance-first)."""
        if not isinstance(active, bool):
            raise ValueError("SplitPanel.proxy_sash() expects a bool")
        self._proxy_sash = active
        return self

    def _validate_panes(self) -> None:
        vertical = self._orientation == "vertical"
        for pane in self._panes:
            if vertical:
                if pane["min_height"] is not None or pane["max_height"] is not None:
                    raise ValueError(
                        "vertical SplitPanel panes use width constraints "
                        "(min_width/max_width), not height"
                    )
                lo, hi = pane["min_width"], pane["max_width"]
            else:
                if pane["min_width"] is not None or pane["max_width"] is not None:
                    raise ValueError(
                        "horizontal SplitPanel panes use height constraints "
                        "(min_height/max_height), not width"
                    )
                lo, hi = pane["min_height"], pane["max_height"]
            if lo is not None and hi is not None and lo > hi:
                raise ValueError("SplitPanel pane min cannot exceed its max")

    def _clamp_sashes(self, paned) -> None:
        """Clamp sash positions so every pane satisfies its min/max constraints."""
        frames = getattr(self, "_pane_frames", None)
        if not frames or len(frames) < 2:
            return
        if self._orientation == "vertical":
            sizes = [frame.winfo_width() for frame in frames]
            mins = [pane["min_width"] for pane in self._panes]
            maxs = [pane["max_width"] for pane in self._panes]
        else:
            sizes = [frame.winfo_height() for frame in frames]
            mins = [pane["min_height"] for pane in self._panes]
            maxs = [pane["max_height"] for pane in self._panes]
        if any(size <= 0 for size in sizes):
            return
        targets = _resolve_sash_positions(sizes, mins, maxs, sum(sizes))
        for index, target in enumerate(targets):
            paned.sashpos(index, target)

    def build(self, parent, *, width=None, height=None):
        if len(self._panes) < 2:
            raise ValueError(
                "SplitPanel needs at least two panes, e.g. "
                "SplitPanel().vertical().add(...).add(...)"
            )
        self._validate_panes()
        palette = get_renderer().native_theme_colors()
        _configure_split_panel_style(
            parent,
            palette,
            self._sash_width,
            self._proxy_sash,
            self._style_name,
        )
        ttk_orient = "horizontal" if self._orientation == "vertical" else "vertical"
        paned = self._create_container(
            "SplitPanel",
            parent,
            {"orient": ttk_orient, "style": self._style_name},
        )
        pane_frames = []
        for pane in self._panes:
            fg = "transparent" if pane["transparent"] else palette["surface"]
            # internal pane wrapper: created directly so it does not re-register
            # the SplitPanel's id nor overwrite self._built (the paned window)
            frame = get_renderer().create_container(
                "SplitPanelPane", paned, {"fg_color": fg}
            )
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
            the_ele = pane["child"].build(frame)
            the_ele.grid(row=0, column=0, sticky="nsew")
            paned.add(frame, weight=1)
            pane_frames.append(frame)
        self._pane_frames = pane_frames
        paned.bind(
            "<Map>",
            lambda _event: paned.after_idle(lambda: self._clamp_sashes(paned)),
        )
        paned.bind(
            "<ButtonRelease-1>",
            lambda _event: paned.after_idle(lambda: self._clamp_sashes(paned)),
        )
        return paned
