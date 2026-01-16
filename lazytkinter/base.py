from __future__ import annotations
import customtkinter as ctk
from typing import TypeVar, Generic, Literal, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .app import Application

T = TypeVar('T', bound='BaseWidget')

class BaseWidget(Generic[T]):
    """Base class for custom Tkinter widgets providing common properties and methods.

    Attributes:
        _width (int | None): Widget width.
        _height (int | None): Widget height.
        _radius (int | None): Corner radius.
        _fg_color (str | None): Foreground color.
        _bg_color (str | None): Background color.
        _text_color (str | None): Text color.
        _font (tuple | Any | None): Font settings.
        _cursor (str | None): Cursor style.
        _state (str | None): Widget state ("normal" or "disabled").
        _weight (int): Layout weight.
        _row_span (int): Row span.
        _col_span (int): Column span.
        _margin_x (int): Horizontal margin.
        _margin_y (int): Vertical margin.
        _sticky (str): Alignment, defaults to "nsew" (fill).
        _padx (int | None): Horizontal padding.
        _pady (int | None): Vertical padding.
    """
    def __init__(self) -> None:
        """Initialize base widget properties."""
        # Dimensions/appearance
        self._width = None
        self._height = None
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
        self._weight = 1
        self._row_span = 1
        self._col_span = 1
        self._margin_x = 0
        self._margin_y = 0
        self._sticky = "nsew"  # Default fill

    def _inject_base_args(self, kwargs: dict[str, Any]) -> None:
        """Inject non-null common properties into kwargs dictionary.

        Used for widget constructors (CTkButton, CTkFrame, etc.).

        Args:
            kwargs (dict[str, Any]): Target dictionary to be injected with properties.
        """
        if self._width is not None: kwargs['width'] = self._width
        if self._height is not None: kwargs['height'] = self._height
        if self._radius is not None: kwargs['corner_radius'] = self._radius
        
        if self._fg_color is not None: kwargs['fg_color'] = self._fg_color
        if self._bg_color is not None: kwargs['bg_color'] = self._bg_color
        if self._text_color is not None: kwargs['text_color'] = self._text_color
        
        if self._font is not None: kwargs['font'] = self._font
        if self._state is not None: kwargs['state'] = self._state
        if self._cursor is not None: kwargs['cursor'] = self._cursor

    def _inject_grid_args(self, kwargs: dict[str, Any]) -> None:
        """Inject layout properties into kwargs dictionary.

        Used for .grid() method.

        Args:
            kwargs (dict[str, Any]): Target dictionary to be injected with layout properties.
        """
        # Note: weight is for rowconfigure/columnconfigure, not for grid
        # So weight is handled in Application or Layout containers
        
        kwargs['rowspan'] = self._row_span
        kwargs['columnspan'] = self._col_span
        kwargs['padx'] = self._margin_x
        kwargs['pady'] = self._margin_y
        kwargs['sticky'] = self._sticky

    # Dimensions
    def width(self, w: int) -> T:
        """Set widget width.

        Args:
            w (int): Width value.

        Returns:
            T: Returns self for method chaining.
        """
        self._width = w; return self # type: ignore
    
    def height(self, h: int) -> T:
        """Set widget height.

        Args:
            h (int): Height value.

        Returns:
            T: Returns self for method chaining.
        """
        self._height = h; return self # type: ignore
    
    def radius(self, r: int) -> T:
        """Set corner radius.

        Args:
            r (int): Radius value.

        Returns:
            T: Returns self for method chaining.
        """
        self._radius = r; return self # type: ignore
    
    # Colors
    def fg_color(self, color: str) -> T:
        """Set foreground color.

        Args:
            color (str): Color value.

        Returns:
            T: Returns self for method chaining.
        """
        self._fg_color = color; return self # type: ignore
    
    def bg_color(self, color: str) -> T:
        """Set background color.

        Args:
            color (str): Color value.

        Returns:
            T: Returns self for method chaining.
        """
        self._bg_color = color; return self # type: ignore
    
    def text_color(self, color: str) -> T:
        """Set text color.

        Args:
            color (str): Color value.

        Returns:
            T: Returns self for method chaining.
        """
        self._text_color = color; return self # type: ignore
    
    # Font (supports tuple ("Roboto", 12) or ctk.CTkFont)
    def font(self, font: tuple | Any) -> T:
        """Set font.

        Args:
            font (tuple | Any): Font settings, either as tuple like ("Roboto", 12) or CTkFont object.

        Returns:
            T: Returns self for method chaining.
        """
        self._font = font; return self # type: ignore
    
    # Interaction
    def state(self, state: Literal["normal", "disabled"]) -> T:
        """Set widget state.

        Args:
            state (Literal["normal", "disabled"]): Widget state.

        Returns:
            T: Returns self for method chaining.
        """
        self._state = state; return self # type: ignore
    
    def cursor(self, cursor: str) -> T:
        """Set cursor style.

        Args:
            cursor (str): Cursor style name.

        Returns:
            T: Returns self for method chaining.
        """
        self._cursor = cursor; return self # type: ignore

    # Layout
    def weight(self, w: int) -> T:
        """Set layout weight.

        Args:
            w (int): Weight value.

        Returns:
            T: Returns self for method chaining.
        """
        self._weight = w; return self # type: ignore
    
    def row_span(self, span: int) -> T:
        """Set row span.

        Args:
            span (int): Row span value.

        Returns:
            T: Returns self for method chaining.
        """
        self._row_span = span; return self # type: ignore
    
    def col_span(self, span: int) -> T:
        """Set column span.

        Args:
            span (int): Column span value.

        Returns:
            T: Returns self for method chaining.
        """
        self._col_span = span; return self # type: ignore
    
    def sticky(self, s: str) -> T:
        """Set widget alignment.

        Args:
            s (str): Alignment string like "nsew".

        Returns:
            T: Returns self for method chaining.
        """
        self._sticky = s; return self # type: ignore
    
    def margin(self, mar: int | Tuple[int, int]) -> T:
        """Set margins.

        Args:
            mar (int | Tuple[int, int]): Margin value, either uniform or (horizontal, vertical).

        Returns:
            T: Returns self for method chaining.
        """
        if isinstance(mar, int):
            self._margin_x, self._margin_y = mar, mar
        elif isinstance(mar, tuple):
            self._margin_x, self._margin_y = mar[0], mar[1]
        return self # type: ignore
    
    def margin_x(self, x: int) -> T:
        """Set horizontal margin.

        Args:
            x (int): Horizontal margin value.

        Returns:
            T: Returns self for method chaining.
        """
        self._margin_x = x; return self # type: ignore
    
    def margin_y(self, y: int) -> T:
        """Set vertical margin.

        Args:
            y (int): Vertical margin value.

        Returns:
            T: Returns self for method chaining.
        """
        self._margin_y = y; return self # type: ignore

    def padding(self, pad: int | Tuple[int, int]) -> T: 
        """Set padding.

        Args:
            pad (int | Tuple[int, int]): Padding value, either uniform or (horizontal, vertical).

        Returns:
            T: Returns self for method chaining.
        """
        if isinstance(pad, int):
            self._padx, self._pady = pad, pad
        elif isinstance(pad, tuple):
            self._padx, self._pady = pad[0], pad[1]
        return self # type: ignore

    def build(self, parent):
        """Build the widget (to be implemented in subclasses).

        Args:
            parent: Parent widget.
        """
        ...
