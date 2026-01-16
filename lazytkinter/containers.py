from __future__ import annotations
from typing import Tuple, Any
import customtkinter as ctk

from .base import BaseWidget

class Empty(BaseWidget["Empty"]):
    """An empty container widget used for spacing and alignment.
    
    Inherits from BaseWidget and creates a transparent frame with optional dimensions.
    """

    def __init__(self) -> None:
        """Initializes the Empty container."""
        super().__init__()

    def build(self, parent):
        """Builds the empty container widget.

        Args:
            parent: The parent widget.

        Returns:
            A CTkFrame configured as an empty container.
        """
        kwargs = {
            "fg_color": "transparent", 
            "width": self._width if self._width else 0,
            "height": self._height if self._height else 0
        }
        
        frame = ctk.CTkFrame(parent, **kwargs)
        
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

    def __init__(self) -> None:
        """Initializes the Column container."""
        super().__init__()
        self._spacing = 0
        self._transparent = False
        self._args = ()
        
        # Container-specific padding properties
        self._pad_x = 0
        self._pad_y = 0

    def padding(self, pad: int|Tuple[int, int]) -> Column:
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
        """Adds child widgets to the container.

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Column: Returns self for method chaining.
        """
        self._args = args
        return self

    def build(self, parent):
        """Builds the column container with all child widgets.

        Args:
            parent: The parent widget.

        Returns:
            A configured CTkFrame containing all child widgets in vertical layout.
        """
        # Outer Frame configuration
        outer_kwargs: dict[str, Any] = {"fg_color": "transparent" if self._transparent else None}
        self._inject_base_args(outer_kwargs)
        for k in ['text_color', 'font', 'state', 'cursor']: 
            outer_kwargs.pop(k, None)

        outer_frame = ctk.CTkFrame(parent, **outer_kwargs)

        if self._width is not None or self._height is not None:
            outer_frame.pack_propagate(False)

        # Layout in parent container
        grid_args = {
            "sticky": self._sticky, 
            "rowspan": self._row_span, 
            "columnspan": self._col_span,
            "padx": self._margin_x,  # Container margin
            "pady": self._margin_y
        }
        outer_frame.grid(**grid_args)
        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)
        
        # Inner frame for actual content
        inner_frame = ctk.CTkFrame(outer_frame, corner_radius=0, fg_color="transparent")
        inner_frame.pack(
            expand=True, 
            fill="both", 
            padx=self._pad_x, 
            pady=self._pad_y 
        )
        
        # Single column configuration
        inner_frame.columnconfigure(0, weight=1)

        # Stack child widgets vertically
        total = len(self._args)
        for i, ele in enumerate(self._args):
            # Prevent overflow
            if self._height is not None and ele._height is not None:
                if ele._height > self._height: 
                    ele.height(self._height)
            if self._width is not None and ele._width is not None:
                if ele._width > self._width: 
                    ele.width(self._width)
            
            # Configure row weight
            inner_frame.rowconfigure(i, weight=ele._weight)
            the_ele = ele.build(inner_frame)
            
            # Handle child margins (compatible with int and tuple)
            m_top = ele._margin_y[0] if isinstance(ele._margin_y, tuple) else ele._margin_y
            m_bottom = ele._margin_y[1] if isinstance(ele._margin_y, tuple) else ele._margin_y
            
            # Add spacing to all but last child
            m_bottom += (self._spacing if i != total - 1 else 0)

            # Stack with combined margins
            the_ele.grid(
                row=i, 
                column=0, 
                sticky="nsew", 
                padx=ele._margin_x,
                pady=(m_top, m_bottom)
            )

        return outer_frame

class Row(BaseWidget["Row"]):
    """A horizontal container that arranges widgets in a single row.

    Attributes:
        _spacing (int): Horizontal spacing between child widgets.
        _transparent (bool): Whether the container has transparent background.
        _args (tuple): Child widgets to be added.
        _pad_x (int): Horizontal internal padding.
        _pad_y (int): Vertical internal padding.
    """

    def __init__(self) -> None:
        """Initializes the Row container."""
        super().__init__()
        self._spacing = 0
        self._transparent = False
        self._args = ()
        self._pad_x = 0
        self._pad_y = 0

    def padding(self, pad: int|Tuple[int, int]) -> Row:
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
        """Adds child widgets to the container.

        Args:
            *args: Variable number of widgets to add.

        Returns:
            Row: Returns self for method chaining.
        """
        self._args = args
        return self

    def build(self, parent):
        """Builds the row container with all child widgets.

        Args:
            parent: The parent widget.

        Returns:
            A configured CTkFrame containing all child widgets in horizontal layout.
        """
        # Outer Frame configuration
        outer_kwargs: dict[str, Any] = {"fg_color": "transparent" if self._transparent else None}
        self._inject_base_args(outer_kwargs)
        for k in ['text_color', 'font', 'state', 'cursor']: 
            outer_kwargs.pop(k, None)

        outer_frame = ctk.CTkFrame(parent, **outer_kwargs)

        if self._width is not None or self._height is not None:
            outer_frame.pack_propagate(False)

        # Layout in parent container
        grid_args = {
            "sticky": self._sticky, 
            "rowspan": self._row_span, 
            "columnspan": self._col_span,
            "padx": self._margin_x,
            "pady": self._margin_y
        }
        outer_frame.grid(**grid_args)

        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)
        
        # Inner frame for actual content
        inner_frame = ctk.CTkFrame(outer_frame, corner_radius=0, fg_color="transparent")
        inner_frame.pack(expand=True, fill="both", padx=self._pad_x, pady=self._pad_y)
        
        # Single row configuration
        inner_frame.rowconfigure(0, weight=1)

        # Stack child widgets horizontally
        total = len(self._args)
        for i, ele in enumerate(self._args):
            # Prevent overflow
            if self._height is not None and ele._height is not None:
                if ele._height > self._height: 
                    ele.height(self._height)
            if self._width is not None and ele._width is not None:
                if ele._width > self._width: 
                    ele.width(self._width)
            
            # Configure column weight
            inner_frame.columnconfigure(i, weight=ele._weight)
            the_ele = ele.build(inner_frame)
            
            # Handle child margins (compatible with int and tuple)
            m_left = ele._margin_x[0] if isinstance(ele._margin_x, tuple) else ele._margin_x
            m_right = ele._margin_x[1] if isinstance(ele._margin_x, tuple) else ele._margin_x
            
            # Add spacing to all but last child
            m_right += (self._spacing if i != total - 1 else 0)

            # Stack with combined margins
            the_ele.grid(
                row=0, 
                column=i, 
                sticky="nsew",
                padx=(m_left, m_right),
                pady=ele._margin_y
            )

        return outer_frame
    
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

    def __init__(self) -> None:
        """Initializes the ScrollableColumn container."""
        super().__init__()
        self._spacing = 0
        self._transparent = False
        self._args = ()
        self._pad_x = 0
        self._pad_y = 0
        self._label_text = None

    def padding(self, pad: int|Tuple[int, int]) -> ScrollableColumn:
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
        """Adds child widgets to the container.

        Args:
            *args: Variable number of widgets to add.

        Returns:
            ScrollableColumn: Returns self for method chaining.
        """
        self._args = args
        return self

    def build(self, parent):
        """Builds the scrollable column container with all child widgets.

        Args:
            parent: The parent widget.

        Returns:
            A configured CTkScrollableFrame containing all child widgets.
        """
        # Prepare CTkScrollableFrame arguments
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs)
        
        # Handle transparent background
        if self._transparent:
            kwargs["fg_color"] = "transparent"
            
        if self._label_text:
            kwargs["label_text"] = self._label_text

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, **kwargs)
        
        # Configure single column layout
        scroll_frame.columnconfigure(0, weight=1)

        # Add child widgets with spacing
        total = len(self._args)
        for i, ele in enumerate(self._args):
            # Prevent width overflow (height is scrollable)
            if self._width is not None and ele._width is not None:
                if ele._width > self._width: 
                    ele.width(self._width)
            
            # Configure row weight
            scroll_frame.rowconfigure(i, weight=ele._weight)
            
            # Build child element
            the_ele = ele.build(scroll_frame)
            
            # Handle child margins (compatible with int and tuple)
            m_top = ele._margin_y[0] if isinstance(ele._margin_y, tuple) else ele._margin_y
            m_bottom = ele._margin_y[1] if isinstance(ele._margin_y, tuple) else ele._margin_y
            
            # Add spacing to all but last child
            m_bottom += (self._spacing if i != total - 1 else 0)

            # Stack with combined margins
            the_ele.grid(
                row=i, 
                column=0, 
                sticky="nsew", 
                padx=ele._margin_x,
                pady=(m_top, m_bottom)
            )

        return scroll_frame
