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
    _resolve_sash_positions,
    _resolve_zstack_slots,
)
from lazytkinter import registry
from lazytkinter import tokens as token_mod


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


class SizePolicyChainTests(unittest.TestCase):
    def test_width_chain_only_changes_width(self):
        widget = ltk.Button().width().fill()
        self.assertEqual(widget._width_policy, "fill")
        self.assertEqual(widget._height_policy, "fit")
        self.assertIsNone(widget._width)

    def test_height_chain_only_changes_height(self):
        widget = ltk.Button().width("fill").height().fit()
        self.assertEqual(widget._width_policy, "fill")
        self.assertEqual(widget._height_policy, "fit")

    def test_bare_fill_applies_to_both_axes(self):
        widget = ltk.Button().width(120).height(60).fill()
        self.assertEqual(widget._width_policy, "fill")
        self.assertEqual(widget._height_policy, "fill")
        self.assertIsNone(widget._width)
        self.assertIsNone(widget._height)

    def test_bare_fit_applies_to_both_axes(self):
        widget = ltk.Button().fill().fit()
        self.assertEqual(widget._width_policy, "fit")
        self.assertEqual(widget._height_policy, "fit")

    def test_policy_clears_fixed_pixels(self):
        widget = ltk.Button().width(120)
        widget.width().fill()
        self.assertIsNone(widget._width)
        self.assertEqual(widget._width_policy, "fill")

    def test_argument_call_clears_pending_axis(self):
        widget = ltk.Button()
        widget.width(120)
        self.assertIsNone(widget._pending_size_axis)
        widget.height("fill")
        self.assertIsNone(widget._pending_size_axis)


class FillWeightTests(unittest.TestCase):
    def test_fill_with_weight(self):
        widget = ltk.Button().fill(weight=2)
        self.assertEqual(widget._weight, 2)
        self.assertEqual((widget._width_policy, widget._height_policy), ("fill", "fill"))

    def test_fill_without_weight_defaults_none(self):
        self.assertIsNone(ltk.Button().fill()._weight)

    def test_invalid_weight_raises(self):
        with self.assertRaises(ValueError):
            ltk.Button().fill(weight=0)
        with self.assertRaises(ValueError):
            ltk.Button().fill(weight=-1)
        with self.assertRaises(ValueError):
            ltk.Button().fill(weight="x")

    def test_column_weights_are_proportional(self):
        slots = _resolve_column_slots(
            [
                ltk.Button().height().fill(weight=1),
                ltk.Button().height().fill(weight=2),
            ],
            default_align="left",
            gap=0,
            padding=0,
        )
        self.assertEqual([slot["weight"] for slot in slots], [1, 2])

    def test_row_weights_are_proportional(self):
        slots = _resolve_row_slots(
            [
                ltk.Button().width().fill(weight=2),
                ltk.Button().width().fill(weight=3),
            ],
            default_align="top",
            gap=0,
            padding=0,
        )
        self.assertEqual([slot["weight"] for slot in slots], [2, 3])

    def test_default_fills_split_equally(self):
        slots = _resolve_column_slots(
            [ltk.Button().height().fill(), ltk.Button().height().fill()],
            default_align="left",
            gap=0,
            padding=0,
        )
        self.assertEqual([slot["weight"] for slot in slots], [1, 1])

    def test_weight_on_non_main_axis_raises(self):
        with self.assertRaises(ValueError):
            _resolve_column_slots(
                [ltk.Button().width().fill(weight=2)],
                default_align="left",
                gap=0,
                padding=0,
            )

    def test_weight_downgraded_by_spacer_raises(self):
        with self.assertRaises(ValueError):
            _resolve_column_slots(
                [ltk.Button().height().fill(weight=2), ltk.Spacer()],
                default_align="left",
                gap=0,
                padding=0,
            )

    def test_zstack_weight_raises(self):
        with self.assertRaises(ValueError):
            _resolve_zstack_slots(
                [ltk.Button().fill(weight=2)], default_align="center", padding=0
            )


class ContainerSizeChainTests(unittest.TestCase):
    def test_column_width_chain_overrides_default(self):
        column = ltk.Column().width().fit()
        self.assertEqual(column._width_policy, "fit")
        self.assertEqual(column._height_policy, "fit")

    def test_row_height_chain(self):
        row = ltk.Row().height().fill()
        self.assertEqual(row._height_policy, "fill")
        self.assertEqual(row._width_policy, "fit")

    def test_chained_and_string_forms_resolve_identically(self):
        from lazytkinter.containers import _resolve_column_slots, _resolve_row_slots

        chained_row = _resolve_row_slots(
            [ltk.Button().width().fill()], default_align="top", gap=0, padding=0
        )[0]
        string_row = _resolve_row_slots(
            [ltk.Button().width("fill")], default_align="top", gap=0, padding=0
        )[0]
        self.assertEqual(chained_row["weight"], string_row["weight"])
        self.assertEqual(chained_row["sticky"], string_row["sticky"])

        chained_col = _resolve_column_slots(
            [ltk.Button().height().fill()], default_align="left", gap=0, padding=0
        )[0]
        string_col = _resolve_column_slots(
            [ltk.Button().height("fill")], default_align="left", gap=0, padding=0
        )[0]
        self.assertEqual(chained_col["weight"], string_col["weight"])
        self.assertEqual(chained_col["sticky"], string_col["sticky"])

        chained_container = _resolve_row_slots(
            [ltk.Column().width().fit()], default_align="top", gap=0, padding=0
        )[0]
        string_container = _resolve_row_slots(
            [ltk.Column().width("fit")], default_align="top", gap=0, padding=0
        )[0]
        self.assertEqual(chained_container["weight"], string_container["weight"])
        self.assertEqual(chained_container["sticky"], string_container["sticky"])


class JustifyTests(unittest.TestCase):
    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            ltk.Column().justify("middle")
        with self.assertRaises(ValueError):
            ltk.Row().justify("middle")

    def test_column_center_auto_fills_height(self):
        column = ltk.Column().justify("center")
        self.assertEqual(column._justify, "center")
        self.assertEqual(column._height_policy, "fill")

    def test_row_center_auto_fills_width(self):
        row = ltk.Row().justify("center")
        self.assertEqual(row._justify, "center")
        self.assertEqual(row._width_policy, "fill")

    def test_fixed_size_not_overridden(self):
        column = ltk.Column().height(300).justify("center")
        self.assertEqual(column._height, 300)
        self.assertEqual(column._height_policy, "fit")

    def test_start_does_not_autofill(self):
        self.assertEqual(ltk.Column().justify("start")._height_policy, "fit")

    def test_column_center_insets_implicit_spacers(self):
        slots = _resolve_column_slots(
            [ltk.Button()], default_align="left", gap=0, padding=0, justify="center"
        )
        self.assertEqual(len(slots), 3)
        self.assertIsInstance(slots[0]["child"], ltk.Spacer)
        self.assertIsInstance(slots[2]["child"], ltk.Spacer)
        self.assertEqual(slots[0]["weight"], 1)
        self.assertEqual(slots[1]["weight"], 0)
        self.assertEqual(slots[2]["weight"], 1)

    def test_column_end_insets_leading_spacer(self):
        slots = _resolve_column_slots(
            [ltk.Button()], default_align="left", gap=0, padding=0, justify="end"
        )
        self.assertEqual(len(slots), 2)
        self.assertIsInstance(slots[0]["child"], ltk.Spacer)
        self.assertEqual(slots[0]["weight"], 1)

    def test_fill_downgraded_with_implicit_spacer(self):
        slots = _resolve_column_slots(
            [ltk.Button().height("fill")],
            default_align="left",
            gap=0,
            padding=0,
            justify="center",
        )
        self.assertEqual(slots[1]["weight"], 0)

    def test_row_center_insets_implicit_spacers(self):
        slots = _resolve_row_slots(
            [ltk.Button()], default_align="top", gap=0, padding=0, justify="center"
        )
        self.assertEqual(len(slots), 3)
        self.assertEqual(slots[0]["weight"], 1)
        self.assertEqual(slots[2]["weight"], 1)
        self.assertIsInstance(slots[0]["child"], ltk.Spacer)


class CenterShortcutTests(unittest.TestCase):
    def test_column_center_shortcut(self):
        column = ltk.Column().center()
        self.assertEqual(column._justify, "center")
        self.assertEqual(column._default_align, "center")
        self.assertEqual(column._height_policy, "fill")

    def test_row_center_shortcut(self):
        row = ltk.Row().center()
        self.assertEqual(row._justify, "center")
        self.assertEqual(row._default_align, "center")
        self.assertEqual(row._width_policy, "fill")


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


class FontTests(unittest.TestCase):
    def test_keyword_config(self):
        widget = ltk.Label().font(family="Arial", size=20, weight="bold")
        self.assertEqual(widget._font, ("Arial", 20, "bold"))

    def test_dict_config(self):
        widget = ltk.Label().font({"family": "Arial", "size": 20})
        self.assertEqual(widget._font, ("Arial", 20))

    def test_legacy_tuple_still_works(self):
        widget = ltk.Label().font(("Arial", 20, "bold"))
        self.assertEqual(widget._font, ("Arial", 20, "bold"))

    def test_flattened_positional_still_works(self):
        widget = ltk.Label().font("Arial", 20, "bold")
        self.assertEqual(widget._font, ("Arial", 20, "bold"))

    def test_size_only_defaults_family(self):
        widget = ltk.Label().font(size=20)
        self.assertEqual(widget._font, ("Roboto", 20))

    def test_style_combination(self):
        widget = ltk.Label().font(
            family="Arial", size=12, weight="bold", slant="italic", underline=True
        )
        self.assertEqual(widget._font, ("Arial", 12, "bold italic underline"))

    def test_no_args_is_noop(self):
        self.assertIsNone(ltk.Label().font()._font)

    def test_unsupported_key_raises(self):
        with self.assertRaises(ValueError):
            ltk.Label().font(color="red")

    def test_invalid_weight_raises(self):
        with self.assertRaises(ValueError):
            ltk.Label().font(weight="heavy")


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


class ComponentConsistencyTests(unittest.TestCase):
    def test_set_value_empty_string_works(self):
        self.assertEqual(ltk.ComboBox().set_value("")._default_value, "")
        self.assertEqual(ltk.SegmentedButton().set_value("")._default_value, "")
        self.assertEqual(ltk.OptionMenu().set_value("")._default_value, "")

    def test_values_are_copied(self):
        items = ["a", "b"]
        combo = ltk.ComboBox().values(items)
        items.append("c")
        self.assertEqual(combo._values, ["a", "b"])

        seg_items = ["x"]
        seg = ltk.SegmentedButton().values(seg_items)
        seg_items.append("y")
        self.assertEqual(seg._values, ["x"])

    def test_progressbar_value_validation(self):
        with self.assertRaises(ValueError):
            ltk.ProgressBar().value(1.5)
        with self.assertRaises(ValueError):
            ltk.ProgressBar().value(-0.1)
        ltk.ProgressBar().value(0.7)


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

    def test_default_fg_color_is_theme_color(self):
        props = _frame_props(Column())
        self.assertNotIn("fg_color", props)  # theme default is used

    def test_explicit_fg_color_wins(self):
        props = _frame_props(Column().fg_color("blue"))
        self.assertEqual(props["fg_color"], "blue")

    def test_transparent_opt_in(self):
        props = _frame_props(Column().transparent())
        self.assertEqual(props["fg_color"], "transparent")


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


class RegistryTests(unittest.TestCase):
    def setUp(self):
        registry.clear()

    def tearDown(self):
        registry.clear()

    def test_register_and_get(self):
        wrapper = object()
        registry.register("btn", wrapper, object())
        self.assertIs(registry.get("btn"), wrapper)

    def test_duplicate_raises(self):
        registry.register("btn", object(), object())
        with self.assertRaises(ValueError):
            registry.register("btn", object(), object())

    def test_ids_and_clear(self):
        registry.register("a", object(), object())
        registry.register("b", object(), object())
        self.assertEqual(set(registry.ids()), {"a", "b"})
        registry.clear()
        self.assertEqual(registry.ids(), [])


class TokenTests(unittest.TestCase):
    def setUp(self):
        self._saved = token_mod._current

    def tearDown(self):
        token_mod._current = self._saved

    def test_color_and_tokens_export(self):
        self.assertTrue(token_mod.color("primary").startswith("#"))
        self.assertEqual(ltk.color("primary"), token_mod.color("primary"))
        self.assertEqual(ltk.Tokens.radius, token_mod.Tokens.radius)

    def test_unknown_token_raises(self):
        with self.assertRaises(ValueError):
            token_mod.color("nope")

    def test_theme_switch_changes_tokens(self):
        before = token_mod.color("primary")
        token_mod.set_theme("gruvbox-theme")
        after = token_mod.color("primary")
        self.assertNotEqual(before, after)

    def test_resolve_token_and_pass_through(self):
        primary = token_mod.color("primary")
        self.assertEqual(token_mod.resolve("primary"), primary)
        self.assertEqual(token_mod.resolve("#123456"), "#123456")

    def test_set_theme_syncs_tokens(self):
        ltk.set_theme("gruvbox-theme")
        self.assertEqual(token_mod._current, "gruvbox-theme")
        ltk.set_theme("catppuccin-mocha")


class ConfigNarrowingTests(unittest.TestCase):
    def test_config_returns_same_wrapper(self):
        label = ltk.Label()
        self.assertIs(label.config(ltk.Label), label)

    def test_config_mismatch_raises(self):
        button = ltk.Button().id("btn")
        with self.assertRaises(TypeError):
            button.config(ltk.Label)


class CanvasLogicTests(unittest.TestCase):
    def test_canvas_collects_draw_callbacks(self):
        def one(c):
            pass

        def two(c):
            pass

        canvas = ltk.Canvas().draw(one).draw(two)
        self.assertEqual(canvas._draws, [one, two])

    def test_canvas_rejects_non_callable_draw(self):
        with self.assertRaises(ValueError):
            ltk.Canvas().draw("not callable")


class SplitPanelLogicTests(unittest.TestCase):
    def test_constructor_and_add(self):
        paned = ltk.SplitPanel(Column(), Column())
        self.assertEqual(len(paned._panes), 2)
        paned.add(Column())
        self.assertEqual(len(paned._panes), 3)

    def test_orientation_validation(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().orientation("diagonal")

    def test_orientation_chain_and_string(self):
        panel = ltk.SplitPanel()
        panel.orientation().vertical()
        self.assertEqual(panel._orientation, "vertical")
        panel.horizontal()
        self.assertEqual(panel._orientation, "horizontal")
        self.assertEqual(
            ltk.SplitPanel().orientation("vertical")._orientation, "vertical"
        )
        self.assertEqual(ltk.SplitPanel().vertical()._orientation, "vertical")

    def test_no_arg_orientation_is_noop(self):
        panel = ltk.SplitPanel()
        self.assertIs(panel.orientation(), panel)
        self.assertEqual(panel._orientation, "vertical")

    def test_sash_width_validation(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().sash_width(-1)
        with self.assertRaises(ValueError):
            ltk.SplitPanel().sash_width(2.5)
        with self.assertRaises(ValueError):
            ltk.SplitPanel().sash_width(True)

    def test_proxy_sash_validation(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().proxy_sash("yes")

    def test_style_name_unique_per_instance(self):
        first = ltk.SplitPanel()
        second = ltk.SplitPanel()
        self.assertNotEqual(first._style_name, second._style_name)

    def test_non_widget_child_raises(self):
        with self.assertRaises(TypeError):
            ltk.SplitPanel(object())
        with self.assertRaises(TypeError):
            ltk.SplitPanel().add(object())

    def test_chain_add_and_pane_attributes(self):
        panel = ltk.SplitPanel()
        panel.add(Column()).min_width(120).max_width(400)
        panel.add(Column()).min_width(200).transparent()
        first, second = panel._panes
        self.assertEqual(first["min_width"], 120)
        self.assertEqual(first["max_width"], 400)
        self.assertFalse(first["transparent"])
        self.assertEqual(second["min_width"], 200)
        self.assertTrue(second["transparent"])

    def test_pane_attribute_before_add_raises(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().min_width(100)

    def test_pane_size_validation(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().add(Column()).min_width(-1)
        with self.assertRaises(ValueError):
            ltk.SplitPanel().add(Column()).max_width(True)
        with self.assertRaises(ValueError):
            ltk.SplitPanel().add(Column()).min_height(2.5)
        with self.assertRaises(ValueError):
            ltk.SplitPanel().add(Column()).transparent("yes")


class SashSolverTests(unittest.TestCase):
    def test_unbounded_keeps_positions(self):
        targets = _resolve_sash_positions([200, 200], [None, None], [None, None], 400)
        self.assertEqual(targets, [200])

    def test_min_clamps_up(self):
        targets = _resolve_sash_positions([100, 300], [250, None], [None, None], 400)
        self.assertEqual(targets, [250])

    def test_max_clamps_down(self):
        targets = _resolve_sash_positions([150, 250], [None, None], [150, None], 400)
        self.assertEqual(targets, [150])

    def test_two_mins_intersection(self):
        targets = _resolve_sash_positions([200, 200], [250, 100], [None, None], 400)
        self.assertEqual(targets, [250])

    def test_conflict_prefers_min(self):
        targets = _resolve_sash_positions([200, 200], [350, 100], [None, None], 400)
        self.assertEqual(targets, [350])

    def test_three_panes_sequential(self):
        targets = _resolve_sash_positions(
            [100, 100, 200],
            [150, 80, None],
            [None, None, None],
            400,
        )
        self.assertEqual(targets, [150, 230])


class DividerLogicTests(unittest.TestCase):
    def test_default_horizontal(self):
        divider = ltk.Divider()
        self.assertEqual(divider._orientation, "horizontal")
        self.assertEqual(divider._thickness, 1)
        self.assertEqual(divider._width_policy, "fill")

    def test_orientation_chain_and_string(self):
        divider = ltk.Divider()
        divider.orientation().vertical()
        self.assertEqual(divider._orientation, "vertical")
        self.assertEqual(divider._height_policy, "fill")
        divider.horizontal()
        self.assertEqual(divider._orientation, "horizontal")
        self.assertEqual(divider._width_policy, "fill")
        self.assertEqual(
            ltk.Divider().orientation("vertical")._orientation, "vertical"
        )
        self.assertEqual(ltk.Divider().vertical()._orientation, "vertical")

    def test_no_arg_orientation_is_noop(self):
        divider = ltk.Divider()
        self.assertIs(divider.orientation(), divider)
        self.assertEqual(divider._orientation, "horizontal")

    def test_orientation_validation(self):
        with self.assertRaises(ValueError):
            ltk.Divider().orientation("diagonal")

    def test_thickness_validation(self):
        with self.assertRaises(ValueError):
            ltk.Divider().thickness(0)
        with self.assertRaises(ValueError):
            ltk.Divider().thickness(-1)
        with self.assertRaises(ValueError):
            ltk.Divider().thickness(2.5)
        with self.assertRaises(ValueError):
            ltk.Divider().thickness(True)
