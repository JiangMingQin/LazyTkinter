"""Build-flow tests using a fake renderer (no Tk window needed)."""

import unittest

import lazytkinter as ltk
from lazytkinter import registry
from lazytkinter import tokens as token_mod
from lazytkinter.containers import Column, Scroll, ZStack
from lazytkinter.renderer import Renderer, get_renderer, set_renderer

_real_renderer = get_renderer()


class Stub:
    """Duck-typed stand-in for any native Tk widget."""

    def __init__(self):
        self.configured = {}
        self.set_calls = []
        self.inserted = []
        self.added = []
        self.value = 1

    def get(self):
        return self.value

    def configure(self, **kwargs):
        self.configured.update(kwargs)

    def set(self, value):
        self.set_calls.append(value)

    def insert(self, *args, **kwargs):
        self.inserted.append((args, kwargs))

    def add(self, *args, **kwargs):
        """Mimic ttk.Panedwindow.add(): return a pane stub."""
        self.added.append((args, kwargs))
        return Stub()

    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None

        return _noop


class FakeRenderer(Renderer):
    def __init__(self):
        self.widget_calls = []
        self.container_calls = []
        self.created_widgets = []
        self.created_containers = []
        self.window = Stub()

    def create_window(self):
        return self.window

    def create_widget(self, kind, parent, props):
        stub = Stub()
        self.widget_calls.append((kind, dict(props)))
        self.created_widgets.append(stub)
        return stub

    def create_container(self, kind, parent, props):
        stub = Stub()
        self.container_calls.append((kind, dict(props)))
        self.created_containers.append(stub)
        return stub

    def set_theme(self, theme_name):
        pass

    def set_mode(self, mode):
        pass

    def native_theme_colors(self):
        return {
            "surface": "#101010",
            "text": "#eeeeee",
            "border": "#333333",
            "primary": "#3355aa",
            "primary_text": "#ffffff",
            "field_bg": "#202020",
            "field_text": "#eeeeee",
            "field_border": "#333333",
        }


class RendererFlowTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRenderer()
        set_renderer(self.fake)

    def tearDown(self):
        set_renderer(_real_renderer)

    def test_button_collects_configured_props_only(self):
        ltk.Button().text("Login").width(100).height(30).fg_color("red").build(None)
        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Button")
        self.assertEqual(props["text"], "Login")
        self.assertEqual(props["width"], 100)
        self.assertEqual(props["height"], 30)
        self.assertEqual(props["fg_color"], "red")
        self.assertNotIn("font", props)

    def test_fg_color_token_resolved_at_build(self):
        token_mod.set_theme("catppuccin-mocha")
        try:
            ltk.Button().fg_color("primary").build(None)
            self.assertEqual(
                self.fake.widget_calls[0][1]["fg_color"], token_mod.color("primary")
            )
        finally:
            token_mod.set_theme("catppuccin-mocha")

    def test_container_kinds(self):
        Column().build(None)
        Scroll(ltk.Button().text("x")).build(None)
        ZStack().add(ltk.Button()).build(None)
        ltk.Spacer().build(None)
        kinds = [call[0] for call in self.fake.container_calls]
        self.assertEqual(kinds, ["Column", "Scroll", "ZStack", "Spacer"])

    def test_column_clamps_child_without_mutating(self):
        child = ltk.Button().width(300).height(60)
        Column().width(200).height(50).add(child).build(None)
        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Button")
        self.assertEqual(props["width"], 200)
        self.assertEqual(props["height"], 50)
        self.assertEqual(child._width, 300)
        self.assertEqual(child._height, 60)

    def test_nested_container_receives_size_overrides(self):
        inner = Column().width(300).add(ltk.Button().width(500))
        outer = Column().width(200).add(inner)
        outer.build(None)

        self.assertEqual(self.fake.container_calls[0][0], "Column")
        self.assertEqual(self.fake.container_calls[0][1]["width"], 200)
        self.assertEqual(self.fake.container_calls[1][0], "Column")
        self.assertEqual(self.fake.container_calls[1][1]["width"], 200)  # clamped

        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Button")
        self.assertEqual(props["width"], 200)  # clamped through the nested chain
        self.assertEqual(inner._width, 300)  # config untouched

    def test_switch_event_receives_value(self):
        received = []
        switch = ltk.Switch().event(received.append)
        widget = switch.build(None)
        command = widget.configured.get("command")
        self.assertIsNotNone(command)
        command()
        self.assertEqual(received, [widget.value])

    def test_button_event_receives_none(self):
        received = []
        widget = ltk.Button().event(received.append).build(None)
        widget.configured["command"]()
        self.assertEqual(received, [None])

    def test_checkbox_event_receives_value(self):
        received = []
        widget = ltk.CheckBox().event(received.append).build(None)
        widget.configured["command"]()
        self.assertEqual(received, [widget.value])

    def test_radiobutton_event_receives_value(self):
        received = []
        widget = ltk.RadioButton().event(received.append).build(None)
        widget.configured["command"]()
        self.assertEqual(received, [widget.value])

    def test_empty_default_value_is_set(self):
        widget = ltk.ComboBox().values(["a", "b"]).set_value("").build(None)
        self.assertEqual(widget.set_calls, [""])

    def test_id_registers_built_widget(self):
        registry.clear()
        try:
            wrapper = ltk.Button().id("btn")
            built = wrapper.build(None)
            self.assertIs(registry.get("btn"), wrapper)
            self.assertIs(wrapper._built, built)
            self.assertEqual(built._ltk_id, "btn")
        finally:
            registry.clear()

    def test_live_setter_updates_built_widget(self):
        registry.clear()
        try:
            wrapper = ltk.Label().id("label")
            built = wrapper.build(None)
            wrapper.config(ltk.Label).text("hi")
            self.assertEqual(built.configured.get("text"), "hi")
        finally:
            registry.clear()

    def test_treeview_build_inserts_rows(self):
        ltk.Treeview().columns(["A", "B"]).rows([("1", "2"), ("3", "4")]).build(None)
        kinds = [call[0] for call in self.fake.widget_calls]
        self.assertIn("Treeview", kinds)
        self.assertIn("Scrollbar", kinds)
        self.assertEqual(self.fake.container_calls[0][0], "Column")
        tree = self.fake.created_widgets[kinds.index("Treeview")]
        self.assertEqual(
            tree.inserted,
            [(("", "end"), {"values": ("1", "2")}), (("", "end"), {"values": ("3", "4")})],
        )

    def test_listbox_build_inserts_items(self):
        ltk.Listbox().items(["x", "y"]).build(None)
        kinds = [call[0] for call in self.fake.widget_calls]
        self.assertIn("Listbox", kinds)
        listbox = self.fake.created_widgets[kinds.index("Listbox")]
        self.assertEqual(listbox.inserted, [(("end", "x"), {}), (("end", "y"), {})])

    def test_progressbar_sets_initial_value(self):
        widget = ltk.ProgressBar().value(0.7).build(None)
        self.assertEqual(widget.set_calls, [0.7])

    def test_application_single_layout_guard(self):
        app = ltk.Application()
        app.column(ltk.Button().text("x"))
        with self.assertRaises(RuntimeError):
            app.column(ltk.Button())
        with self.assertRaises(RuntimeError):
            app.row(ltk.Button())


class ApplicationLayoutTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRenderer()
        set_renderer(self.fake)

    def tearDown(self):
        set_renderer(_real_renderer)

    def test_center_shortcut_builds(self):
        app = ltk.Application()
        app.center().column(ltk.Button().text("x"))
        self.assertTrue(app._layout_set)

    def test_gap_align_justify_state(self):
        app = ltk.Application()
        app.gap(10).align("center").justify("end")
        self.assertEqual(app._layout_gap, 10)
        self.assertEqual(app._layout_align, "center")
        self.assertEqual(app._layout_justify, "end")

    def test_invalid_values_raise(self):
        app = ltk.Application()
        with self.assertRaises(ValueError):
            app.justify("middle")
        with self.assertRaises(ValueError):
            app.align("top-left")
        with self.assertRaises(ValueError):
            app.gap(-1)

    def test_align_axis_validated_at_root_call(self):
        app = ltk.Application()
        app.align("left")
        with self.assertRaises(ValueError):
            app.row(ltk.Button())

        app2 = ltk.Application()
        app2.align("top")
        with self.assertRaises(ValueError):
            app2.column(ltk.Button())

    def test_justify_center_insets_implicit_spacers_at_root(self):
        app = ltk.Application()
        app.justify("center").column(ltk.Button().text("x"))
        spacer_kinds = [call[0] for call in self.fake.container_calls].count("Spacer")
        self.assertEqual(spacer_kinds, 2)
        self.assertEqual(len(self.fake.widget_calls), 1)

    def test_application_get_and_ids(self):
        registry.clear()
        try:
            app = ltk.Application()
            app.column(ltk.Button().id("btn").text("x"))
            app.build()
            self.assertIn("btn", app.ids())
            self.assertIsNotNone(app.get("btn"))
            self.assertIsNotNone(app.native("btn"))
        finally:
            registry.clear()


class ThemeTests(unittest.TestCase):
    def test_missing_theme_raises_value_error(self):
        from lazytkinter.renderer import CTkRenderer

        with self.assertRaises(ValueError):
            CTkRenderer().set_theme("no-such-theme-xyz")

    def test_native_theme_passes_through(self):
        from lazytkinter.renderer import CTkRenderer

        CTkRenderer().set_theme("blue")

    def test_native_theme_palette_keys(self):
        from lazytkinter.renderer import CTkRenderer

        colors = CTkRenderer().native_theme_colors()
        for key in (
            "surface",
            "text",
            "border",
            "primary",
            "primary_text",
            "field_bg",
            "field_text",
            "field_border",
        ):
            self.assertIn(key, colors)
            self.assertIsInstance(colors[key], str)


class CanvasFlowTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRenderer()
        set_renderer(self.fake)

    def tearDown(self):
        set_renderer(_real_renderer)

    def test_canvas_creates_widget_and_runs_draw(self):
        token_mod.set_theme("catppuccin-mocha")
        drawn = []
        try:
            ltk.Canvas().width(200).height(100).fg_color("primary").draw(
                lambda c: drawn.append(c)
            ).build(None)
        finally:
            token_mod.set_theme("catppuccin-mocha")

        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Canvas")
        self.assertEqual(props["width"], 200)
        self.assertEqual(props["height"], 100)
        self.assertEqual(props["bg"], token_mod.color("primary"))
        self.assertNotIn("fg_color", props)
        self.assertEqual(len(drawn), 1)
        self.assertIs(drawn[0], self.fake.created_widgets[0])

    def test_canvas_draws_in_order(self):
        order = []
        canvas = (
            ltk.Canvas()
            .draw(lambda c: order.append("first"))
            .draw(lambda c: order.append("second"))
        )
        canvas.build(None)
        self.assertEqual(order, ["first", "second"])

    def test_canvas_rejects_non_callable_draw(self):
        with self.assertRaises(ValueError):
            ltk.Canvas().draw("not callable")


class SplitPanelFlowTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRenderer()
        set_renderer(self.fake)

    def tearDown(self):
        set_renderer(_real_renderer)

    def test_split_panel_creates_container_and_panes(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).build(None)
        kind, props = self.fake.container_calls[0]
        self.assertEqual(kind, "SplitPanel")
        self.assertEqual(props["orient"], "horizontal")
        self.assertEqual(props["style"], "LTk.TPanedwindow")
        stub = self.fake.created_containers[0]
        self.assertEqual(len(stub.added), 2)

    def test_split_panel_orientation_vertical(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).orientation("vertical").build(None)
        _, props = self.fake.container_calls[0]
        self.assertEqual(props["orient"], "vertical")

    def test_split_panel_requires_two_panes(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel(ltk.Column()).build(None)
