"""Pure-logic unit tests that never create a Tk window."""

import unittest

from lazytkinter.app import Application
from lazytkinter.base import BaseWidget
from lazytkinter.containers import (
    Column,
    Row,
    ScrollableColumn,
    _clamp,
    _frame_props,
)


class MarginTests(unittest.TestCase):
    def test_uniform_margin(self):
        widget = BaseWidget()
        widget.margin(10)
        self.assertEqual((widget._margin_x, widget._margin_y), (10, 10))

    def test_tuple_margin_is_horizontal_vertical(self):
        widget = BaseWidget()
        widget.margin((20, 30))
        self.assertEqual((widget._margin_x, widget._margin_y), (20, 30))


class PaddingParsingTests(unittest.TestCase):
    def test_column_uniform_padding(self):
        column = Column().padding(8)
        self.assertEqual((column._pad_x, column._pad_y), (8, 8))

    def test_column_tuple_padding(self):
        column = Column().padding((5, 10))
        self.assertEqual((column._pad_x, column._pad_y), (5, 10))

    def test_row_tuple_padding(self):
        row = Row().padding((3, 7))
        self.assertEqual((row._pad_x, row._pad_y), (3, 7))


class ClampTests(unittest.TestCase):
    def test_clamps_to_container(self):
        self.assertEqual(_clamp(300, 200), 200)

    def test_passes_through_when_unset(self):
        self.assertIsNone(_clamp(None, 200))
        self.assertEqual(_clamp(100, None), 100)


class FramePropsTests(unittest.TestCase):
    def test_unsupported_keys_are_removed(self):
        column = (
            Column()
            .font(("Arial", 12))
            .text_color("red")
            .state("disabled")
            .cursor("hand2")
        )
        props = _frame_props(column)
        for key in ("font", "text_color", "state", "cursor"):
            self.assertNotIn(key, props)

    def test_keeps_supported_keys(self):
        column = Column().width(120).height(40).radius(8).fg_color("blue")
        props = _frame_props(column)
        self.assertEqual(props["width"], 120)
        self.assertEqual(props["height"], 40)
        self.assertEqual(props["corner_radius"], 8)
        self.assertEqual(props["fg_color"], "blue")


class ChildrenApiTests(unittest.TestCase):
    def test_constructor_children(self):
        a, b, c = object(), object(), object()
        self.assertEqual(Column(a, b)._args, (a, b))
        self.assertEqual(Row(c)._args, (c,))
        self.assertEqual(ScrollableColumn(a, c)._args, (a, c))

    def test_add_appends(self):
        a, b, c = object(), object(), object()
        column = Column(a)
        column.add(b).add(c)
        self.assertEqual(column._args, (a, b, c))


class SingleLayoutGuardTests(unittest.TestCase):
    def test_second_layout_call_raises(self):
        app = object.__new__(Application)
        app._layout_set = True  # simulate an already-built root layout
        with self.assertRaises(RuntimeError):
            app.column()
        with self.assertRaises(RuntimeError):
            app.row()
