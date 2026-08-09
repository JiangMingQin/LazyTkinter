from __future__ import annotations
from typing import Any, Literal

from .base import BaseWidget
from .renderer import get_renderer
from .tokens import resolve as _resolve_token


class Button(BaseWidget["Button"]):
    """
    Button Widget

    A wrapper based on `customtkinter.CTkButton`, supporting fluent interface (method chaining).
    Used to trigger immediate actions.

    Usage Example:
        # Create a button with red border, click to trigger login function
        btn = ltk.Button() \
            .text("Login") \
            .text_color("white") \
            .border(2, "red") \
            .event(self.login_action)
    """
    def __init__(self) -> None:
        super().__init__()
        # [Implementation Detail]:
        # All private properties are initialized as None, instead of default values.
        # Reason: We want to preserve CustomTkinter's native default values.
        # Only when users explicitly call methods (e.g., .text("OK")), we override the native defaults during build.
        self._text = None
        self._command = None
        self._hover_color = None
        self._border_width = None
        self._border_color = None
        self._image = None

    def text(self, text: str = "Button") -> Button:
        # [Design Pattern - Fluent Interface]:
        # Must return self, which is the core of implementing chainable methods.
        # Allows users to write fluent code like btn.text("A").event(func).
        self._text = text
        self._apply("text", text)
        return self

    def event(self, command=lambda value: None) -> Button:
        self._command = command
        return self

    def hover_color(self, color: str) -> Button:
        self._hover_color = color
        self._apply("hover_color", color)
        return self

    def border(self, width: int, color: str | None = None) -> Button:
        self._border_width = width
        self._apply("border_width", width)
        if color:
            self._border_color = color
            self._apply("border_color", color)
        return self

    def image(self, img: Any) -> Button:
        self._image = img
        return self

    def build(self, parent, *, width=None, height=None):
        """
        [Internal Method] Build the underlying native button through the renderer.
        Usually not called manually by users, automatically called by containers.
        """
        kwargs: dict[str, Any] = {}
        # [Logic]: Only include properties in kwargs if they are explicitly set (not None).
        # If not set (is None), we don't pass this parameter,
        # so the native widget uses its own default styles.
        if self._text is not None: kwargs["text"] = self._text
        if self._hover_color is not None: kwargs["hover_color"] = _resolve_token(self._hover_color)
        if self._border_width is not None: kwargs["border_width"] = self._border_width
        if self._border_color is not None: kwargs["border_color"] = _resolve_token(self._border_color)
        if self._image is not None: kwargs["image"] = self._image

        # [Code Reuse]:
        # The handling logic for generic properties like width, height, font, fg_color
        # is extracted to the _inject_base_args method in BaseWidget.
        self._inject_base_args(kwargs, width=width, height=height)

        btn = self._create_widget("Button", parent, kwargs)
        if self._command is not None:
            user_cmd = self._command
            btn.configure(command=lambda: user_cmd(None))
        return btn


class Label(BaseWidget["Label"]):
    def __init__(self) -> None:
        super().__init__()
        self._text = None
        self._justify = None
        self._wraplength = None
        self._image = None
        self._variable = None

    def text(self, text: str = "Label") -> Label:
        self._text = text
        self._apply("text", text)
        return self

    def variable(self, var: Any) -> Label:
        self._variable = var
        return self

    # Layout Control
    def justify(self, mode: Literal["left", "center", "right"]) -> Label:
        self._justify = mode
        self._apply("justify", mode)
        return self

    def wrap_length(self, length: int) -> Label:
        self._wraplength = length
        self._apply("wraplength", length)
        return self

    def image(self, img: Any) -> Label:
        self._image = img
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._justify is not None: kwargs["justify"] = self._justify
        if self._wraplength is not None: kwargs["wraplength"] = self._wraplength
        if self._image is not None: kwargs["image"] = self._image  # Label supports images
        if self._variable is not None: kwargs["textvariable"] = self._variable

        self._inject_base_args(kwargs, width=width, height=height)
        return self._create_widget("Label", parent, kwargs)


class Entry(BaseWidget["Entry"]):
    def __init__(self) -> None:
        super().__init__()
        self._placeholder_text = None
        self._show = None
        self._border_width = None
        self._border_color = None
        self._variable = None

    def placeholder_text(self, text: str = "Entry") -> Entry:
        self._placeholder_text = text
        self._apply("placeholder_text", text)
        return self

    # Used for password fields e.g. show("*")
    def show(self, char: str) -> Entry:
        self._show = char
        self._apply("show", char)
        return self

    def border(self, width: int, color: str | None = None) -> Entry:
        self._border_width = width
        self._apply("border_width", width)
        if color:
            self._border_color = color
            self._apply("border_color", color)
        return self

    def variable(self, var: Any) -> Entry:
        self._variable = var
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._placeholder_text is not None: kwargs["placeholder_text"] = self._placeholder_text
        if self._show is not None: kwargs["show"] = self._show
        if self._border_width is not None: kwargs["border_width"] = self._border_width
        if self._border_color is not None: kwargs["border_color"] = _resolve_token(self._border_color)
        if self._variable is not None: kwargs["textvariable"] = self._variable

        self._inject_base_args(kwargs, width=width, height=height)
        return self._create_widget("Entry", parent, kwargs)


class Switch(BaseWidget["Switch"]):
    def __init__(self) -> None:
        super().__init__()
        self._text = None
        self._command = None
        self._on_value = None
        self._off_value = None
        self._variable = None
        self._progress_color = None

    def text(self, text: str = "") -> Switch:
        self._text = text
        self._apply("text", text)
        return self

    def event(self, command=lambda value: None) -> Switch:
        self._command = command
        return self

    def values(self, on_val: Any, off_val: Any) -> Switch:
        self._on_value = on_val
        self._off_value = off_val
        self._apply("onvalue", on_val)
        self._apply("offvalue", off_val)
        return self

    def variable(self, var: Any) -> Switch:
        self._variable = var
        return self

    def progress_color(self, color: str) -> Switch:
        self._progress_color = color
        self._apply("progress_color", color)
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._on_value is not None: kwargs["onvalue"] = self._on_value
        if self._off_value is not None: kwargs["offvalue"] = self._off_value
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._progress_color is not None: kwargs["progress_color"] = _resolve_token(self._progress_color)

        self._inject_base_args(kwargs, width=width, height=height)
        switch = self._create_widget("Switch", parent, kwargs)

        # Event wrapping logic (for passing arguments)
        if self._command is not None:
            user_cmd = self._command
            switch.configure(command=lambda: user_cmd(switch.get()))

        return switch


class CheckBox(BaseWidget["CheckBox"]):
    def __init__(self) -> None:
        super().__init__()
        self._text = None
        self._command = None
        self._variable = None
        self._on_value = None
        self._off_value = None

    def text(self, text: str) -> CheckBox:
        self._text = text
        self._apply("text", text)
        return self

    def event(self, command=lambda value: None) -> CheckBox:
        self._command = command
        return self

    def variable(self, var: Any) -> CheckBox:
        self._variable = var
        return self

    def values(self, on_val: Any, off_val: Any) -> CheckBox:
        self._on_value = on_val
        self._off_value = off_val
        self._apply("onvalue", on_val)
        self._apply("offvalue", off_val)
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._on_value is not None: kwargs["onvalue"] = self._on_value
        if self._off_value is not None: kwargs["offvalue"] = self._off_value

        self._inject_base_args(kwargs, width=width, height=height)
        check_box = self._create_widget("CheckBox", parent, kwargs)
        if self._command is not None:
            user_cmd = self._command
            check_box.configure(command=lambda: user_cmd(check_box.get()))
        return check_box


class RadioButton(BaseWidget["RadioButton"]):
    def __init__(self) -> None:
        super().__init__()
        self._text = None
        self._value = None
        self._variable = None
        self._command = None
        self._radiobutton_width = None
        self._radiobutton_height = None

    def text(self, text: str) -> RadioButton:
        self._text = text
        self._apply("text", text)
        return self

    def value(self, val: Any) -> RadioButton:
        self._value = val
        self._apply("value", val)
        return self

    def variable(self, var: Any) -> RadioButton:
        self._variable = var
        return self

    def event(self, command=lambda value: None) -> RadioButton:
        self._command = command
        return self

    def radiobutton_width(self, rw: int = 20) -> RadioButton:
        self._radiobutton_width = rw
        self._apply("radiobutton_width", rw)
        return self

    def radiobutton_height(self, rh: int = 20) -> RadioButton:
        self._radiobutton_height = rh
        self._apply("radiobutton_height", rh)
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._value is not None: kwargs["value"] = self._value
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._radiobutton_width is not None: kwargs["radiobutton_width"] = self._radiobutton_width
        if self._radiobutton_height is not None: kwargs["radiobutton_height"] = self._radiobutton_height

        self._inject_base_args(kwargs, width=width, height=height)
        radio_button = self._create_widget("RadioButton", parent, kwargs)
        if self._command is not None:
            user_cmd = self._command
            radio_button.configure(command=lambda: user_cmd(radio_button.get()))
        return radio_button


class Textbox(BaseWidget["Textbox"]):
    def __init__(self) -> None:
        super().__init__()
        self._border_width = None
        self._border_spacing = None
        self._wrap = None  # "char", "word", "none"
        self._activate_scrollbars = True

    def border(self, width: int, spacing: int | None = None) -> Textbox:
        self._border_width = width
        self._apply("border_width", width)
        if spacing is not None:
            self._border_spacing = spacing
            self._apply("border_spacing", spacing)
        return self

    def wrap(self, mode: Literal["char", "word", "none"]) -> Textbox:
        self._wrap = mode
        self._apply("wrap", mode)
        return self

    def scrollbar(self, active: bool) -> Textbox:
        self._activate_scrollbars = active
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._border_width is not None: kwargs["border_width"] = self._border_width
        if self._border_spacing is not None: kwargs["border_spacing"] = self._border_spacing
        if self._wrap is not None: kwargs["wrap"] = self._wrap
        kwargs["activate_scrollbars"] = self._activate_scrollbars

        self._inject_base_args(kwargs, width=width, height=height)
        return self._create_widget("Textbox", parent, kwargs)


class Slider(BaseWidget["Slider"]):
    def __init__(self) -> None:
        super().__init__()
        self._from_ = 0
        self._to = 1
        self._number_of_steps = None
        self._command = None
        self._variable = None
        self._orientation = "horizontal"

        # style attributes
        self._button_color = None
        self._progress_color = None
        self._button_hover_color = None

    def range(self, start: float, end: float) -> Slider:
        """set the range of the slider, default is 0 to 1"""
        self._from_ = start
        self._to = end
        self._apply("from_", start)
        self._apply("to", end)
        return self

    def steps(self, steps: int) -> Slider:
        """set the step size (if not set, it will be a smooth slide)"""
        self._number_of_steps = steps
        self._apply("number_of_steps", steps)
        return self

    def variable(self, var: Any) -> Slider:
        """set the variable to link to the slider"""
        self._variable = var
        return self

    def event(self, command=lambda value: None) -> Slider:
        """set the callback function for the slider"""
        self._command = command
        return self

    def orientation(self, orient: Literal["horizontal", "vertical"]) -> Slider:
        """set the orientation of the slider"""
        self._orientation = orient
        self._apply("orientation", orient)
        return self

    def button_color(self, color: str) -> Slider:
        self._button_color = color
        self._apply("button_color", color)
        return self

    def progress_color(self, color: str) -> Slider:
        self._progress_color = color
        self._apply("progress_color", color)
        return self

    def button_hover_color(self, color: str) -> Slider:
        self._button_hover_color = color
        self._apply("button_hover_color", color)
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}

        # slider parameters
        kwargs["from_"] = self._from_
        kwargs["to"] = self._to
        kwargs["orientation"] = self._orientation

        if self._number_of_steps is not None: kwargs["number_of_steps"] = self._number_of_steps
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._command is not None: kwargs["command"] = self._command

        # color style parameters
        if self._button_color is not None: kwargs["button_color"] = _resolve_token(self._button_color)
        if self._progress_color is not None: kwargs["progress_color"] = _resolve_token(self._progress_color)
        if self._button_hover_color is not None: kwargs["button_hover_color"] = _resolve_token(self._button_hover_color)

        self._inject_base_args(kwargs, width=width, height=height)
        return self._create_widget("Slider", parent, kwargs)


class ProgressBar(BaseWidget["ProgressBar"]):
    def __init__(self) -> None:
        super().__init__()
        self._orientation = "horizontal"
        self._mode = "determinate"
        self._value = 0.5  # default value

    def orientation(self, orient: Literal["horizontal", "vertical"]) -> ProgressBar:
        self._orientation = orient
        self._apply("orientation", orient)
        return self

    def mode(self, mode: Literal["determinate", "indeterminate"]) -> ProgressBar:
        self._mode = mode
        self._apply("mode", mode)
        return self

    def value(self, val: float) -> ProgressBar:
        if isinstance(val, bool) or not isinstance(val, (int, float)) or not (0 <= val <= 1):
            raise ValueError("ProgressBar.value() expects a number between 0 and 1")
        self._value = val
        if self._built is not None:
            self._built.set(val)
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        # progressbar parameters
        kwargs["orientation"] = self._orientation
        kwargs["mode"] = self._mode

        progress = self._create_widget("ProgressBar", parent, kwargs)
        progress.set(self._value)  # set default value
        return progress


class SegmentedButton(BaseWidget["SegmentedButton"]):
    def __init__(self) -> None:
        super().__init__()
        self._values = []
        self._command = None
        self._default_value = None

    def values(self, values: list) -> SegmentedButton:
        self._values = list(values)
        self._apply("values", self._values)
        return self

    def set_value(self, val: str) -> SegmentedButton:
        self._default_value = val
        if self._built is not None:
            self._built.set(val)
        return self

    def event(self, command=lambda value: None) -> SegmentedButton:
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        if self._values: kwargs["values"] = self._values
        if self._command: kwargs["command"] = self._command

        seg_btn = self._create_widget("SegmentedButton", parent, kwargs)
        if self._default_value is not None:
            seg_btn.set(self._default_value)
        elif self._values:
            seg_btn.set(self._values[0])  # default value is the first one

        return seg_btn


class ComboBox(BaseWidget["ComboBox"]):
    def __init__(self) -> None:
        super().__init__()
        self._values = []
        self._command = None
        self._default_value = None

    def values(self, values: list) -> ComboBox:
        self._values = list(values)
        self._apply("values", self._values)
        return self

    def set_value(self, val: str) -> ComboBox:
        self._default_value = val
        if self._built is not None:
            self._built.set(val)
        return self

    def event(self, command=lambda value: None) -> ComboBox:
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        if self._values: kwargs["values"] = self._values
        if self._command: kwargs["command"] = self._command

        combo = self._create_widget("ComboBox", parent, kwargs)
        if self._default_value is not None:
            combo.set(self._default_value)
        return combo


class OptionMenu(BaseWidget["OptionMenu"]):
    def __init__(self) -> None:
        super().__init__()
        self._values = []
        self._command = None
        self._default_value = None

    def values(self, values: list) -> OptionMenu:
        self._values = list(values)
        self._apply("values", self._values)
        return self

    def set_value(self, val: str) -> OptionMenu:
        self._default_value = val
        if self._built is not None:
            self._built.set(val)
        return self

    def event(self, command=lambda value: None) -> OptionMenu:
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        if self._values: kwargs["values"] = self._values
        if self._command: kwargs["command"] = self._command

        opt = self._create_widget("OptionMenu", parent, kwargs)
        if self._default_value is not None:
            opt.set(self._default_value)
        return opt


class Canvas(BaseWidget["Canvas"]):
    """A drawing surface backed by ``ctk.CTkCanvas`` (a ``tk.Canvas`` subclass).

    The drawing background is controlled with ``.fg_color()`` (mapped to the
    tk canvas ``bg`` option); ``.draw(func)`` registers callbacks that receive
    the native canvas after build, so arbitrary tk canvas drawing is possible.
    Interaction (clicks, drags, ...) is done through ``.id()`` +
    ``app.native(id).bind(...)``.

    Usage Example:
        canvas = ltk.Canvas() \
            .width(400).height(300) \
            .fg_color("surface_alt") \
            .draw(lambda c: c.create_rectangle(10, 10, 100, 100, fill="primary"))
    """

    def __init__(self) -> None:
        super().__init__()
        self._draws: list = []

    def draw(self, func) -> Canvas:
        """Register a drawing callback; run in order with the native canvas."""
        if not callable(func):
            raise ValueError(
                "Canvas.draw() expects a callable, e.g. "
                "lambda c: c.create_line(0, 0, 100, 100)"
            )
        self._draws.append(func)
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        effective_width = width if width is not None else self._width
        effective_height = height if height is not None else self._height
        if effective_width is not None:
            kwargs["width"] = effective_width
        if effective_height is not None:
            kwargs["height"] = effective_height
        if self._fg_color is not None:
            kwargs["bg"] = _resolve_token(self._fg_color)
        if self._cursor is not None:
            kwargs["cursor"] = self._cursor

        canvas = self._create_widget("Canvas", parent, kwargs)
        for func in self._draws:
            func(canvas)
        return canvas


class Divider(BaseWidget["Divider"]):
    """A thin themed separator line backed by a CTkFrame.

    Horizontal by default (spans the container width at a fixed height); use
    ``.orientation().vertical()`` for a vertical line. The color comes from the
    active CTk theme's border color unless overridden with ``.fg_color()``.

    Usage Example:
        ltk.Column().gap(8).add(
            ltk.Label().text("above"),
            ltk.Divider(),
            ltk.Label().text("below"),
        )
    """

    def __init__(self) -> None:
        super().__init__()
        self._orientation = "horizontal"
        self._thickness = 1
        self._width_policy = "fill"

    def orientation(self, orient=None) -> Divider:
        """Set the direction; chainable via ``.orientation().horizontal()``."""
        if orient is None:
            return self
        if orient not in ("horizontal", "vertical"):
            raise ValueError(
                "Divider.orientation() expects 'horizontal' or 'vertical', "
                f"got {orient!r}"
            )
        self._orientation = orient
        # the main axis spans the container; the cross axis stays at thickness
        if orient == "horizontal":
            self._width_policy = "fill"
        else:
            self._height_policy = "fill"
        return self

    def horizontal(self) -> Divider:
        """Set the divider horizontal (default)."""
        return self.orientation("horizontal")

    def vertical(self) -> Divider:
        """Set the divider vertical."""
        return self.orientation("vertical")

    def thickness(self, n: int) -> Divider:
        """Set the cross-axis thickness in pixels (positive integer)."""
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError("Divider.thickness() expects a positive integer")
        self._thickness = n
        return self

    def build(self, parent, *, width=None, height=None):
        palette = get_renderer().native_theme_colors()
        color = (
            _resolve_token(self._fg_color)
            if self._fg_color is not None
            else palette["border"]
        )
        props: dict[str, Any] = {"fg_color": color}
        if self._orientation == "horizontal":
            if self._width is None and self._width_policy == "fit":
                raise ValueError(
                    "Divider's main axis cannot be fit; use fill() or a fixed width"
                )
            props["height"] = self._thickness
            if self._width is not None:
                props["width"] = self._width
        else:
            if self._height is None and self._height_policy == "fit":
                raise ValueError(
                    "Divider's main axis cannot be fit; use fill() or a fixed height"
                )
            props["width"] = self._thickness
            if self._height is not None:
                props["height"] = self._height
        return self._create_widget("Divider", parent, props)
