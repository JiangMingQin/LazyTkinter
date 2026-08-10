from __future__ import annotations
from tkinter import TclError
from typing import TypeVar, Generic, Literal, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .app import Application

from .registry import register as _register_id
from .renderer import get_renderer
from .tokens import resolve as _resolve_token

T = TypeVar('T', bound='BaseWidget')

_SIZE_POLICIES = ("fit", "fill")

_ALIGNMENTS = (
    "left", "center", "right",
    "top", "bottom",
    "top-left", "top-right", "bottom-left", "bottom-right",
)

_FONT_KEYS = ("family", "size", "weight", "slant", "underline", "overstrike")
_FONT_WEIGHTS = ("normal", "bold")
_FONT_SLANTS = ("roman", "italic")


def _tuple_to_font_config(font_tuple):
    """Convert a legacy tkinter-style font tuple to a config dict."""
    config = {}
    if not font_tuple:
        return config
    config["family"] = font_tuple[0]
    if len(font_tuple) > 1 and isinstance(font_tuple[1], (int, float)):
        config["size"] = font_tuple[1]
        styles = font_tuple[2:]
    else:
        styles = font_tuple[1:]
    style_text = " ".join(str(part) for part in styles).lower()
    for token in style_text.split():
        if token == "bold":
            config["weight"] = "bold"
        elif token == "italic":
            config["slant"] = "italic"
        elif token == "underline":
            config["underline"] = True
        elif token == "overstrike":
            config["overstrike"] = True
    return config


def _build_font_tuple(config):
    """Build a tkinter-compatible font tuple from a config dict."""
    family = config.get("family") or "Roboto"
    size = config.get("size")
    parts = [family]
    if size is not None:
        parts.append(size)
    styles = []
    if config.get("weight") == "bold":
        styles.append("bold")
    if config.get("slant") == "italic":
        styles.append("italic")
    if config.get("underline"):
        styles.append("underline")
    if config.get("overstrike"):
        styles.append("overstrike")
    if styles:
        parts.append(" ".join(styles))
    return tuple(parts)


class BaseWidget(Generic[T]):
    """Base class for custom Tkinter widgets providing common properties and methods.

    Attributes:
        _width (int | None): Fixed pixel width (size policy is 'fit' then).
        _height (int | None): Fixed pixel height (size policy is 'fit' then).
        _width_policy (str): "fit" (wrap content) or "fill" (stretch to parent).
        _height_policy (str): Same as _width_policy for the height axis.
        _radius (int | None): Corner radius.
        _fg_color (str | None): Foreground color.
        _bg_color (str | None): Background color.
        _text_color (str | None): Text color.
        _font (tuple | Any | None): Font settings.
        _cursor (str | None): Cursor style.
        _state (str | None): Widget state ("normal" or "disabled").
        _align (str | None): Per-widget placement override for the parent container.
        _pending_size_axis (str | None): Axis being configured by a no-arg
            width()/height() call, completed by the following fill()/fit().
    """
    def __init__(self) -> None:
        """Initialize base widget properties."""
        # Dimensions/appearance
        self._width = None
        self._height = None
        self._width_policy = "fit"
        self._height_policy = "fit"
        self._radius = None

        # Colors
        self._fg_color = None
        self._bg_color = None
        self._text_color = None
        self._font = None
        self._cursor = None

        # State
        self._state = None  # "normal" or "disabled"

        # Layout
        self._align = None  # per-widget override, resolved by the parent container
        self._pending_size_axis = None  # "width" / "height" / None
        self._weight = None  # fill(weight=...), None means the default 1
        self._id = None  # registered via .id("name"), retrievable with app.config()
        self._built = None  # native widget after build(), enables live updates

    def id(self, name: str) -> T:
        """Give this widget a name so it is retrievable via app.config()."""
        self._id = name
        return self  # type: ignore

    def _create_widget(self, kind, parent, kwargs):
        """Create a native widget through the renderer and register its id."""
        widget = get_renderer().create_widget(kind, parent, kwargs)
        self._built = widget
        if self._id is not None:
            _register_id(self._id, self, widget)
        return widget

    def _create_container(self, kind, parent, kwargs):
        """Create a native container through the renderer and register its id."""
        widget = get_renderer().create_container(kind, parent, kwargs)
        self._built = widget
        if self._id is not None:
            _register_id(self._id, self, widget)
        return widget

    def _apply(self, key: str, value) -> None:
        """Push a property to the built native widget (no-op before build).

        Runtime updates apply only when the native widget supports the option;
        unsupported ones are skipped so build-time configuration stays the
        source of truth.
        """
        if self._built is not None and value is not None:
            try:
                self._built.configure(**{key: value})
            except TclError:
                pass

    def _inject_base_args(
        self, kwargs: dict[str, Any], *, width=None, height=None
    ) -> None:
        """Inject non-null common properties into kwargs dictionary.

        Args:
            kwargs (dict[str, Any]): Target dictionary to be injected with properties.
            width: Optional build-time width override (used by containers to clamp
                child sizes without mutating the child configuration).
            height: Optional build-time height override (same purpose as width).
        """
        effective_width = width if width is not None else self._width
        effective_height = height if height is not None else self._height
        if effective_width is not None: kwargs['width'] = effective_width
        if effective_height is not None: kwargs['height'] = effective_height
        if self._radius is not None: kwargs['corner_radius'] = self._radius

        if self._fg_color is not None: kwargs['fg_color'] = _resolve_token(self._fg_color)
        if self._bg_color is not None: kwargs['bg_color'] = _resolve_token(self._bg_color)
        if self._text_color is not None: kwargs['text_color'] = _resolve_token(self._text_color)

        if self._font is not None: kwargs['font'] = self._font
        if self._state is not None: kwargs['state'] = self._state
        if self._cursor is not None: kwargs['cursor'] = self._cursor

    # Dimensions
    def width(self, w: int | str | None = None) -> T:
        """Set widget width.

        Accepts a fixed pixel int, or a size policy: "fit" (wrap content) or
        "fill" (stretch to parent). Calling without an argument marks the width
        axis so the following ``.fill()`` / ``.fit()`` applies to width only:
        ``widget.width().fill()``.

        Args:
            w (int | str | None): Width value; None marks the width axis.

        Returns:
            T: Returns self for method chaining.
        """
        if w is None:
            self._pending_size_axis = "width"
            return self  # type: ignore
        if isinstance(w, int):
            if w < 0:
                raise ValueError(
                    f"width() expects a non-negative int or one of {_SIZE_POLICIES!r}, got {w!r}"
                )
            self._width = w
            self._width_policy = "fit"
        elif w in _SIZE_POLICIES:
            self._width = None
            self._width_policy = w
        else:
            raise ValueError(
                f"width() expects an int or one of {_SIZE_POLICIES!r}, got {w!r}"
            )
        self._pending_size_axis = None
        return self  # type: ignore

    def height(self, h: int | str | None = None) -> T:
        """Set widget height.

        Accepts a fixed pixel int, or a size policy: "fit" (wrap content) or
        "fill" (stretch to parent). Calling without an argument marks the
        height axis so the following ``.fill()`` / ``.fit()`` applies to height
        only: ``widget.height().fit()``.

        Args:
            h (int | str | None): Height value; None marks the height axis.

        Returns:
            T: Returns self for method chaining.
        """
        if h is None:
            self._pending_size_axis = "height"
            return self  # type: ignore
        if isinstance(h, int):
            if h < 0:
                raise ValueError(
                    f"height() expects a non-negative int or one of {_SIZE_POLICIES!r}, got {h!r}"
                )
            self._height = h
            self._height_policy = "fit"
        elif h in _SIZE_POLICIES:
            self._height = None
            self._height_policy = h
        else:
            raise ValueError(
                f"height() expects an int or one of {_SIZE_POLICIES!r}, got {h!r}"
            )
        self._pending_size_axis = None
        return self  # type: ignore

    def fill(self, weight: int | None = None) -> T:
        """Set the size policy to "fill" on the pending axis, or both axes.

        Use after a no-arg ``width()`` / ``height()`` to target one axis
        (``widget.width().fill()``), or standalone to fill both axes.

        ``weight`` (positive int) controls how this child shares the parent's
        remaining main-axis space with other fill children: fills with weights
        1 and 2 split the leftover space 1:2. The default is 1.
        """
        if weight is not None:
            if not isinstance(weight, int) or isinstance(weight, bool) or weight < 1:
                raise ValueError("fill() weight expects a positive integer")
            self._weight = weight
        self._apply_size_policy("fill")
        return self  # type: ignore

    def fit(self) -> T:
        """Set the size policy to "fit" on the pending axis, or both axes.

        Use after a no-arg ``width()`` / ``height()`` to target one axis
        (``widget.height().fit()``), or standalone to fit both axes.
        """
        self._apply_size_policy("fit")
        return self  # type: ignore

    def _apply_size_policy(self, policy: str) -> None:
        if self._pending_size_axis == "width":
            self._width = None
            self._width_policy = policy
        elif self._pending_size_axis == "height":
            self._height = None
            self._height_policy = policy
        else:
            self._width = None
            self._height = None
            self._width_policy = policy
            self._height_policy = policy
        self._pending_size_axis = None

    def radius(self, r: int) -> T:
        """Set corner radius.

        Args:
            r (int): Radius value.

        Returns:
            T: Returns self for method chaining.
        """
        self._radius = r
        self._apply("corner_radius", r)
        return self  # type: ignore

    # Colors
    def fg_color(self, color: str) -> T:
        """Set foreground color."""
        self._fg_color = color
        self._apply("fg_color", color)
        return self  # type: ignore

    def bg_color(self, color: str) -> T:
        """Set background color."""
        self._bg_color = color
        self._apply("bg_color", color)
        return self  # type: ignore

    def text_color(self, color: str) -> T:
        """Set text color."""
        self._text_color = color
        self._apply("text_color", color)
        return self  # type: ignore

    # Font
    def font(
        self,
        *args,
        family=None,
        size=None,
        weight=None,
        slant=None,
        underline=None,
        overstrike=None,
        **kwargs,
    ) -> T:
        """Set the widget font with keyword arguments or a dict.

        Preferred forms (IDE autocompletion friendly):
            .font(family="Arial", size=20, weight="bold")
            .font({"family": "Arial", "size": 20})

        The legacy tuple form .font(("Arial", 20, "bold")) and a single font
        object (e.g. a CTkFont) are still accepted.

        Supported keys: family, size, weight ("normal"/"bold"),
        slant ("roman"/"italic"), underline (bool), overstrike (bool).
        """
        if args:
            if len(args) == 1 and isinstance(args[0], dict):
                config = dict(args[0])
            elif len(args) == 1 and isinstance(args[0], tuple):
                config = _tuple_to_font_config(args[0])
            elif len(args) == 1 and not isinstance(args[0], (str, int, float)):
                # pass-through of a font object (e.g. ctk.CTkFont)
                if (
                    family is not None
                    or size is not None
                    or weight is not None
                    or slant is not None
                    or underline is not None
                    or overstrike is not None
                    or kwargs
                ):
                    raise TypeError(
                        "font() cannot combine a font object with other arguments"
                    )
                self._font = args[0]
                return self  # type: ignore
            else:
                config = _tuple_to_font_config(tuple(args))
        else:
            config = {}

        named = {
            "family": family,
            "size": size,
            "weight": weight,
            "slant": slant,
            "underline": underline,
            "overstrike": overstrike,
        }
        for key, value in named.items():
            if value is not None:
                config[key] = value
        config.update(kwargs)

        for key in config:
            if key not in _FONT_KEYS:
                raise ValueError(
                    f"font() got unsupported key {key!r}; supported keys: {_FONT_KEYS}"
                )
        if config.get("weight") not in (None,) + _FONT_WEIGHTS:
            raise ValueError(f"font() weight must be one of {_FONT_WEIGHTS}")
        if config.get("slant") not in (None,) + _FONT_SLANTS:
            raise ValueError(f"font() slant must be one of {_FONT_SLANTS}")
        if config.get("underline") not in (None, True, False):
            raise ValueError("font() underline must be a bool")
        if config.get("overstrike") not in (None, True, False):
            raise ValueError("font() overstrike must be a bool")

        self._font = _build_font_tuple(config) if config else None
        self._apply("font", self._font)
        return self  # type: ignore

    # Interaction
    def state(self, state: Literal["normal", "disabled"]) -> T:
        """Set widget state."""
        self._state = state
        self._apply("state", state)
        return self  # type: ignore

    def cursor(self, cursor: str) -> T:
        """Set cursor style."""
        self._cursor = cursor
        self._apply("cursor", cursor)
        return self  # type: ignore

    def visible(self, active: bool = True) -> T:
        """Show or hide the built widget (grid_remove/grid).

        Requires the widget to be built; call it after the layout is built,
        e.g. ``app.config(type).aim_id("id").visible(False)``. Declarative "hidden by
        default" is not supported yet.
        """
        if not isinstance(active, bool):
            raise ValueError("visible() expects a bool")
        if self._built is None:
            raise ValueError(
                "visible() requires the widget to be built; "
                "call it after the layout is built, e.g. "
                "app.config(type).aim_id('id').visible(False)"
            )
        if active:
            self._built.grid()
        else:
            self._built.grid_remove()
        return self  # type: ignore

    # Layout
    def align(self, a: str) -> T:
        """Set per-widget alignment override used by the parent container.

        Column children accept "left"/"center"/"right"; Row children accept
        "top"/"center"/"bottom"; ZStack children accept any anchor such as
        "top-left" or "bottom-right". Invalid axis values are rejected by the
        parent container at build time.
        """
        if a not in _ALIGNMENTS:
            raise ValueError(
                f"align() expects one of {_ALIGNMENTS!r}, got {a!r}"
            )
        self._align = a
        return self  # type: ignore

    def build(self, parent, *, width=None, height=None):
        """Build the widget (to be implemented in subclasses).

        Args:
            parent: Parent widget.
            width: Optional build-time width override (internal use).
            height: Optional build-time height override (internal use).
        """
        ...
