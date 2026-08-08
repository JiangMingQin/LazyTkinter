from __future__ import annotations
from typing import TypeVar, Generic, Literal, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .app import Application

T = TypeVar('T', bound='BaseWidget')

_SIZE_POLICIES = ("fit", "fill")

_ALIGNMENTS = (
    "left", "center", "right",
    "top", "bottom",
    "top-left", "top-right", "bottom-left", "bottom-right",
)


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

        if self._fg_color is not None: kwargs['fg_color'] = self._fg_color
        if self._bg_color is not None: kwargs['bg_color'] = self._bg_color
        if self._text_color is not None: kwargs['text_color'] = self._text_color

        if self._font is not None: kwargs['font'] = self._font
        if self._state is not None: kwargs['state'] = self._state
        if self._cursor is not None: kwargs['cursor'] = self._cursor

    # Dimensions
    def width(self, w: int | str) -> T:
        """Set widget width: a fixed pixel int, "fit" (wrap content) or "fill".

        Args:
            w (int | str): Width value.

        Returns:
            T: Returns self for method chaining.
        """
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
        return self  # type: ignore

    def height(self, h: int | str) -> T:
        """Set widget height: a fixed pixel int, "fit" (wrap content) or "fill".

        Args:
            h (int | str): Height value.

        Returns:
            T: Returns self for method chaining.
        """
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
        return self  # type: ignore

    def radius(self, r: int) -> T:
        """Set corner radius.

        Args:
            r (int): Radius value.

        Returns:
            T: Returns self for method chaining.
        """
        self._radius = r
        return self  # type: ignore

    # Colors
    def fg_color(self, color: str) -> T:
        """Set foreground color."""
        self._fg_color = color
        return self  # type: ignore

    def bg_color(self, color: str) -> T:
        """Set background color."""
        self._bg_color = color
        return self  # type: ignore

    def text_color(self, color: str) -> T:
        """Set text color."""
        self._text_color = color
        return self  # type: ignore

    # Font (supports tuple ("Roboto", 12) or ctk.CTkFont)
    def font(self, font: tuple | Any) -> T:
        """Set font."""
        self._font = font
        return self  # type: ignore

    # Interaction
    def state(self, state: Literal["normal", "disabled"]) -> T:
        """Set widget state."""
        self._state = state
        return self  # type: ignore

    def cursor(self, cursor: str) -> T:
        """Set cursor style."""
        self._cursor = cursor
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
