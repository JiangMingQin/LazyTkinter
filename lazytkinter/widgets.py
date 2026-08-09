from __future__ import annotations
from typing import Any, Literal

from .base import BaseWidget
from .renderer import get_renderer


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
        return self

    def event(self, command=lambda value: None) -> Button:
        self._command = command
        return self

    def hover_color(self, color: str) -> Button:
        self._hover_color = color
        return self

    def border(self, width: int, color: str | None = None) -> Button:
        self._border_width = width
        if color:
            self._border_color = color
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
        if self._hover_color is not None: kwargs["hover_color"] = self._hover_color
        if self._border_width is not None: kwargs["border_width"] = self._border_width
        if self._border_color is not None: kwargs["border_color"] = self._border_color
        if self._image is not None: kwargs["image"] = self._image

        # [Code Reuse]:
        # The handling logic for generic properties like width, height, font, fg_color
        # is extracted to the _inject_base_args method in BaseWidget.
        self._inject_base_args(kwargs, width=width, height=height)

        btn = get_renderer().create_widget("Button", parent, kwargs)
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
        return self

    def variable(self, var: Any) -> Label:
        self._variable = var
        return self

    # Layout Control
    def justify(self, mode: Literal["left", "center", "right"]) -> Label:
        self._justify = mode
        return self

    def wrap_length(self, length: int) -> Label:
        self._wraplength = length
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
        return get_renderer().create_widget("Label", parent, kwargs)


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
        return self

    # Used for password fields e.g. show("*")
    def show(self, char: str) -> Entry:
        self._show = char
        return self

    def border(self, width: int, color: str | None = None) -> Entry:
        self._border_width = width
        if color:
            self._border_color = color
        return self

    def variable(self, var: Any) -> Entry:
        self._variable = var
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._placeholder_text is not None: kwargs["placeholder_text"] = self._placeholder_text
        if self._show is not None: kwargs["show"] = self._show
        if self._border_width is not None: kwargs["border_width"] = self._border_width
        if self._border_color is not None: kwargs["border_color"] = self._border_color
        if self._variable is not None: kwargs["textvariable"] = self._variable

        self._inject_base_args(kwargs, width=width, height=height)
        return get_renderer().create_widget("Entry", parent, kwargs)


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
        return self

    def event(self, command=lambda value: None) -> Switch:
        self._command = command
        return self

    def values(self, on_val: Any, off_val: Any) -> Switch:
        self._on_value = on_val
        self._off_value = off_val
        return self

    def variable(self, var: Any) -> Switch:
        self._variable = var
        return self

    def progress_color(self, color: str) -> Switch:
        self._progress_color = color
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._on_value is not None: kwargs["onvalue"] = self._on_value
        if self._off_value is not None: kwargs["offvalue"] = self._off_value
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._progress_color is not None: kwargs["progress_color"] = self._progress_color

        self._inject_base_args(kwargs, width=width, height=height)
        switch = get_renderer().create_widget("Switch", parent, kwargs)

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
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._on_value is not None: kwargs["onvalue"] = self._on_value
        if self._off_value is not None: kwargs["offvalue"] = self._off_value

        self._inject_base_args(kwargs, width=width, height=height)
        check_box = get_renderer().create_widget("CheckBox", parent, kwargs)
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
        return self

    def value(self, val: Any) -> RadioButton:
        self._value = val
        return self

    def variable(self, var: Any) -> RadioButton:
        self._variable = var
        return self

    def event(self, command=lambda value: None) -> RadioButton:
        self._command = command
        return self

    def radiobutton_width(self, rw: int = 20) -> RadioButton:
        self._radiobutton_width = rw
        return self

    def radiobutton_height(self, rh: int = 20) -> RadioButton:
        self._radiobutton_height = rh
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        if self._text is not None: kwargs["text"] = self._text
        if self._value is not None: kwargs["value"] = self._value
        if self._variable is not None: kwargs["variable"] = self._variable
        if self._radiobutton_width is not None: kwargs["radiobutton_width"] = self._radiobutton_width
        if self._radiobutton_height is not None: kwargs["radiobutton_height"] = self._radiobutton_height

        self._inject_base_args(kwargs, width=width, height=height)
        radio_button = get_renderer().create_widget("RadioButton", parent, kwargs)
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
        if spacing is not None:
            self._border_spacing = spacing
        return self

    def wrap(self, mode: Literal["char", "word", "none"]) -> Textbox:
        self._wrap = mode
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
        return get_renderer().create_widget("Textbox", parent, kwargs)


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
        return self

    def steps(self, steps: int) -> Slider:
        """set the step size (if not set, it will be a smooth slide)"""
        self._number_of_steps = steps
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
        return self

    def button_color(self, color: str) -> Slider:
        self._button_color = color
        return self

    def progress_color(self, color: str) -> Slider:
        self._progress_color = color
        return self

    def button_hover_color(self, color: str) -> Slider:
        self._button_hover_color = color
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
        if self._button_color is not None: kwargs["button_color"] = self._button_color
        if self._progress_color is not None: kwargs["progress_color"] = self._progress_color
        if self._button_hover_color is not None: kwargs["button_hover_color"] = self._button_hover_color

        self._inject_base_args(kwargs, width=width, height=height)
        return get_renderer().create_widget("Slider", parent, kwargs)


class ProgressBar(BaseWidget["ProgressBar"]):
    def __init__(self) -> None:
        super().__init__()
        self._orientation = "horizontal"
        self._mode = "determinate"
        self._value = 0.5  # default value

    def orientation(self, orient: Literal["horizontal", "vertical"]) -> ProgressBar:
        self._orientation = orient
        return self

    def mode(self, mode: Literal["determinate", "indeterminate"]) -> ProgressBar:
        self._mode = mode
        return self

    def value(self, val: float) -> ProgressBar:
        if isinstance(val, bool) or not isinstance(val, (int, float)) or not (0 <= val <= 1):
            raise ValueError("ProgressBar.value() expects a number between 0 and 1")
        self._value = val
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        # progressbar parameters
        kwargs["orientation"] = self._orientation
        kwargs["mode"] = self._mode

        progress = get_renderer().create_widget("ProgressBar", parent, kwargs)
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
        return self

    def set_value(self, val: str) -> SegmentedButton:
        self._default_value = val
        return self

    def event(self, command=lambda value: None) -> SegmentedButton:
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        if self._values: kwargs["values"] = self._values
        if self._command: kwargs["command"] = self._command

        seg_btn = get_renderer().create_widget("SegmentedButton", parent, kwargs)
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
        return self

    def set_value(self, val: str) -> ComboBox:
        self._default_value = val
        return self

    def event(self, command=lambda value: None) -> ComboBox:
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        if self._values: kwargs["values"] = self._values
        if self._command: kwargs["command"] = self._command

        combo = get_renderer().create_widget("ComboBox", parent, kwargs)
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
        return self

    def set_value(self, val: str) -> OptionMenu:
        self._default_value = val
        return self

    def event(self, command=lambda value: None) -> OptionMenu:
        self._command = command
        return self

    def build(self, parent, *, width=None, height=None):
        kwargs: dict[str, Any] = {}
        self._inject_base_args(kwargs, width=width, height=height)

        if self._values: kwargs["values"] = self._values
        if self._command: kwargs["command"] = self._command

        opt = get_renderer().create_widget("OptionMenu", parent, kwargs)
        if self._default_value is not None:
            opt.set(self._default_value)
        return opt
