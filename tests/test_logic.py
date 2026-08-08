"""Pure-logic unit tests that never create a Tk window."""

import unittest

import lazytkinter as ltk
from lazytkinter.app import Application, _resolve_window_size
from lazytkinter.base import BaseWidget
from lazytkinter.containers import (
    Column,
    Row,
    Scroll,
    Spacer,
    ZStack,
    _frame_props,
    _resolve_column_slots,
    _resolve_row_slots,
    _resolve_zstack_slots,
)


class SizePolicyTests(unittest.TestCase):
    def test_default_policy_is_fit(self):
        widget = BaseWidget()
        self.assertEqual((widget._width_policy, widget._height_policy), ("fit", "fit"))

    def test_fixed_int_size(self):
        widget = ltk.Button().width(120).height(30)
        self.assertEqual(widget._width, 120)
        self.assertEqual(widget._height, 30)
        self.assertEqual(widget._width_policy, "fit")

    def test_policy_size(self):
        widget = ltk.Button().width("fill").height("fit")
        self.assertEqual(widget._width_policy, "fill")
        self.assertEqual(widget._height_policy, "fit")
        self.assertIsNone(widget._width)

    def test_invalid_size_raises(self):
        with self.assertRaises(ValueError):
            ltk.Button().width("bogus")
        with self.assertRaises(ValueError):
            ltk.Button().height(-5)


class AlignTests(unittest.TestCase):
    def test_widget_align_stores_override(self):
        widget = ltk.Button().align("top-right")
        self.assertEqual(widget._align, "top-right")

    def test_invalid_align_raises(self):
        with self.assertRaises(ValueError):
            ltk.Button().align("bogus")

    def test_column_align_validates_axis(self):
        ltk.Column().align("center")
        with self.assertRaises(ValueError):
            ltk.Column().align("top")

    def test_row_align_validates_axis(self):
        ltk.Row().align("bottom")
        with self.assertRaises(ValueError):
            ltk.Row().align("left")

    def test_zstack_align_accepts_anchors(self):
        ltk.ZStack().align("bottom-right")
        with self.assertRaises(ValueError):
            ltk.ZStack().align("bogus")


class ColumnSlotTests(unittest.TestCase):
    def test_fit_and_fill_weights(self):
        fit = ltk.Button()
        fill = ltk.Button().height("fill")
        slots = _resolve_column_slots([fit, fill], default_align="left", gap=0, padding=0)
        self.assertEqual(slots[0]["weight"], 0)
        self.assertEqual(slots[0]["sticky"], "w")
        self.assertEqual(slots[1]["weight"], 1)
        self.assertEqual(slots[1]["sticky"], "nsw")

    def test_multiple_fills_split_equally(self):
        slots = _resolve_column_slots(
            [ltk.Button().height("fill"), ltk.Button().height("fill")],
            default_align="left",
            gap=0,
            padding=0,
        )
        self.assertEqual([slot["weight"] for slot in slots], [1, 1])

    def test_spacer_takes_priority_over_fill(self):
        slots = _resolve_column_slots(
            [
                ltk.Button().height("fill"),
                ltk.Spacer().weight(2),
                ltk.Button().height("fill"),
            ],
            default_align="left",
            gap=0,
            padding=0,
        )
        self.assertEqual(slots[0]["weight"], 0)
        self.assertEqual(slots[1]["weight"], 2)
        self.assertEqual(slots[2]["weight"], 0)

    def test_gap_and_padding(self):
        slots = _resolve_column_slots(
            [ltk.Button(), ltk.Button(), ltk.Button()],
            default_align="left",
            gap=10,
            padding=8,
        )
        self.assertEqual(slots[0]["pady"], (8, 10))
        self.assertEqual(slots[1]["pady"], (0, 10))
        self.assertEqual(slots[2]["pady"], (0, 8))
        for slot in slots:
            self.assertEqual(slot["padx"], 8)

    def test_invalid_child_align_raises(self):
        with self.assertRaises(ValueError):
            _resolve_column_slots(
                [ltk.Button().align("top")], default_align="left", gap=0, padding=0
            )


class RowSlotTests(unittest.TestCase):
    def test_gap_and_padding(self):
        slots = _resolve_row_slots(
            [ltk.Button(), ltk.Button()],
            default_align="top",
            gap=5,
            padding=4,
        )
        self.assertEqual(slots[0]["padx"], (4, 5))
        self.assertEqual(slots[1]["padx"], (0, 4))
        self.assertEqual(slots[0]["pady"], 4)
        self.assertEqual(slots[1]["pady"], 4)

    def test_width_fill_gets_weight(self):
        slots = _resolve_row_slots(
            [ltk.Button().width("fill"), ltk.Button()],
            default_align="top",
            gap=0,
            padding=0,
        )
        self.assertEqual(slots[0]["weight"], 1)
        self.assertEqual(slots[0]["sticky"], "new")
        self.assertEqual(slots[1]["weight"], 0)

    def test_invalid_child_align_raises(self):
        with self.assertRaises(ValueError):
            _resolve_row_slots(
                [ltk.Button().align("left")], default_align="top", gap=0, padding=0
            )


class ZStackSlotTests(unittest.TestCase):
    def test_anchor_and_fill(self):
        slots = _resolve_zstack_slots(
            [
                ltk.Button().align("top-right"),
                ltk.Button().width("fill").height("fill"),
            ],
            default_align="center",
            padding=6,
        )
        self.assertEqual(slots[0]["sticky"], "ne")
        self.assertEqual(slots[1]["sticky"], "nsew")
        self.assertEqual(slots[0]["padx"], 6)

    def test_child_override_wins(self):
        slots = _resolve_zstack_slots(
            [ltk.Button().align("bottom-left")],
            default_align="center",
            padding=0,
        )
        self.assertEqual(slots[0]["sticky"], "sw")


class WindowSizeTests(unittest.TestCase):
    def test_presets(self):
        self.assertEqual(_resolve_window_size("fill"), ("zoom", None))
        self.assertEqual(_resolve_window_size("large"), ("geometry", "1200x800"))
        self.assertEqual(_resolve_window_size("medium"), ("geometry", "900x600"))
        self.assertEqual(_resolve_window_size("small"), ("geometry", "600x400"))

    def test_tuple(self):
        self.assertEqual(_resolve_window_size((400, 300)), ("geometry", "400x300"))

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            _resolve_window_size("huge")
        with self.assertRaises(ValueError):
            _resolve_window_size((0, 300))
        with self.assertRaises(ValueError):
            _resolve_window_size(123)


class ScrollTests(unittest.TestCase):
    def test_single_child_required(self):
        with self.assertRaises(ValueError):
            Scroll()
        with self.assertRaises(ValueError):
            Scroll(ltk.Button(), ltk.Button())
        scroll = Scroll(ltk.Button())
        self.assertIsNone(scroll._child._width)

    def test_direction_validation(self):
        Scroll(ltk.Button()).direction("vertical")
        with self.assertRaises(NotImplementedError):
            Scroll(ltk.Button()).direction("horizontal")
        with self.assertRaises(NotImplementedError):
            Scroll(ltk.Button()).direction("both")


class SpacerTests(unittest.TestCase):
    def test_default_weight(self):
        self.assertEqual(Spacer()._weight, 1)

    def test_weight_setter(self):
        self.assertEqual(Spacer().weight(3)._weight, 3)
        with self.assertRaises(ValueError):
            Spacer().weight(0)
        with self.assertRaises(ValueError):
            Spacer().weight("x")


class ChildrenApiTests(unittest.TestCase):
    def test_constructor_children(self):
        a, b, c = object(), object(), object()
        self.assertEqual(Column(a, b)._args, (a, b))
        self.assertEqual(Row(c)._args, (c,))
        self.assertEqual(ZStack(a, c)._args, (a, c))

    def test_add_appends(self):
        a, b, c = object(), object(), object()
        column = Column(a)
        column.add(b).add(c)
        self.assertEqual(column._args, (a, b, c))


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

    def test_default_fg_color_is_transparent(self):
        props = _frame_props(Column())
        self.assertEqual(props["fg_color"], "transparent")

    def test_explicit_fg_color_wins(self):
        props = _frame_props(Column().fg_color("blue"))
        self.assertEqual(props["fg_color"], "blue")


class ContainerPaddingTests(unittest.TestCase):
    def test_padding_must_be_int(self):
        with self.assertRaises(ValueError):
            Column().padding((10, 20))
        with self.assertRaises(ValueError):
            Row().padding("x")
        with self.assertRaises(ValueError):
            ZStack().padding(-1)
        Column().padding(10)


class SingleLayoutGuardTests(unittest.TestCase):
    def test_second_layout_call_raises(self):
        app = object.__new__(Application)
        app._layout_set = True  # simulate an already-built root layout
        with self.assertRaises(RuntimeError):
            app.column()
        with self.assertRaises(RuntimeError):
            app.row()
