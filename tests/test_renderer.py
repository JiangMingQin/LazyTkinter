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
        self.propagate_calls = []
        self.select_calls = []
        self.deselect_calls = []
        self.deleted = []
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

    def grid_propagate(self, *args):
        self.propagate_calls.append(args)

    def select(self, *args):
        self.select_calls.append(args)

    def deselect(self, *args):
        self.deselect_calls.append(args)

    def delete(self, *args):
        self.deleted.append(args)

    def get_children(self):
        return []

    def curselection(self):
        return []

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
        ltk.Button().text("Login").width(100).height(30).fg_color("#ff0000").build(None)
        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Button")
        self.assertEqual(props["text"], "Login")
        self.assertEqual(props["width"], 100)
        self.assertEqual(props["height"], 30)
        self.assertEqual(props["fg_color"], "#ff0000")
        self.assertNotIn("font", props)

    def test_button_padding_maps_to_border_spacing(self):
        ltk.Button().padding(8).build(None)
        _, props = self.fake.widget_calls[0]
        self.assertEqual(props["border_spacing"], 8)

    def test_button_fix_size_disables_propagate(self):
        ltk.Button().width(100).height(30).fix_size().build(None)
        stub = self.fake.created_widgets[0]
        self.assertEqual(stub.propagate_calls, [(False,)])
        _, props = self.fake.widget_calls[0]
        self.assertEqual(props["width"], 100)

    def test_button_fix_size_requires_size(self):
        with self.assertRaises(ValueError):
            ltk.Button().fix_size().build(None)

    def test_entry_set_applied_at_build(self):
        ltk.Entry().set("hi").build(None)
        stub = self.fake.created_widgets[0]
        self.assertIn((0, "hi"), [args for args, _ in stub.inserted])

    def test_switch_set_applied_at_build(self):
        ltk.Switch().set(True).build(None)
        self.assertTrue(self.fake.created_widgets[0].select_calls)

    def test_checkbox_set_applied_at_build(self):
        ltk.CheckBox().set(False).build(None)
        self.assertTrue(self.fake.created_widgets[0].deselect_calls)

    def test_slider_set_applied_at_build(self):
        ltk.Slider().set(0.5).build(None)
        self.assertEqual(self.fake.created_widgets[0].set_calls, [0.5])

    def test_treeview_set_rebuilds_rows_live(self):
        tree = ltk.Treeview().columns(["A"]).rows([("1",)])
        tree.build(None)
        stub = self.fake.created_widgets[-1]
        stub.inserted.clear()
        tree.set([("2",), ("3",)])
        self.assertTrue(stub.deleted)
        values = [kwargs["values"] for _, kwargs in stub.inserted]
        self.assertEqual(values, [("2",), ("3",)])

    def test_listbox_set_rebuilds_items_live(self):
        box = ltk.Listbox().items(["a"])
        box.build(None)
        stub = self.fake.created_widgets[-1]
        stub.inserted.clear()
        box.set(["x", "y"])
        self.assertTrue(stub.deleted)
        self.assertEqual([args[1] for args, _ in stub.inserted], ["x", "y"])

    def test_fg_color_token_resolved_at_build(self):
        token_mod.set_theme("catppuccin-mocha")
        try:
            ltk.Button().fg_color("primary").build(None)
            self.assertEqual(
                self.fake.widget_calls[0][1]["fg_color"], token_mod.color("primary")
            )
        finally:
            token_mod.set_theme("catppuccin-mocha")

    def test_fg_color_common_color_token_resolved(self):
        token_mod.set_theme("catppuccin-mocha")
        try:
            ltk.Button().fg_color("red").build(None)
            _, props = self.fake.widget_calls[0]
            self.assertEqual(props["fg_color"], token_mod.color("red"))
        finally:
            token_mod.set_theme("catppuccin-mocha")

    def test_container_kinds(self):
        Column().build(None)
        Scroll(ltk.Button().text("x")).build(None)
        ZStack().add(ltk.Button()).build(None)
        ltk.Space().build(None)
        kinds = [call[0] for call in self.fake.container_calls]
        self.assertEqual(kinds, ["Column", "Scroll", "ZStack", "Space"])

    def test_space_build_props(self):
        ltk.Space().build(None)
        _, props = self.fake.container_calls[0]
        self.assertEqual(props, {"fg_color": "transparent", "width": 0, "height": 0})

    def test_fixed_space_build_props(self):
        ltk.Space().width(10).height(20).build(None)
        _, props = self.fake.container_calls[0]
        self.assertEqual(props, {"fg_color": "transparent", "width": 10, "height": 20})

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

    def test_treeview_with_id_registers_main_widget(self):
        registry.clear()
        try:
            tree = ltk.Treeview().id("t").columns(["A"]).rows([(1,)])
            tree.build(None)
            self.assertIs(tree._built, self.fake.created_widgets[-1])
            self.assertIs(registry.get("t"), tree)
        finally:
            registry.clear()

    def test_listbox_with_id_registers_main_widget(self):
        registry.clear()
        try:
            listbox = ltk.Listbox().id("l").items(["a"])
            listbox.build(None)
            self.assertIs(listbox._built, self.fake.created_widgets[-1])
            self.assertIs(registry.get("l"), listbox)
        finally:
            registry.clear()

    def test_treeview_per_instance_styles(self):
        ltk.Treeview().build(None)
        ltk.Treeview().build(None)
        tree_calls = [
            props for kind, props in self.fake.widget_calls if kind == "Treeview"
        ]
        self.assertNotEqual(tree_calls[0]["style"], tree_calls[1]["style"])
        self.assertTrue(tree_calls[0]["style"].startswith("LTkData"))
        self.assertTrue(tree_calls[0]["style"].endswith(".Treeview"))

    def test_data_scrollbar_style(self):
        ltk.Treeview().build(None)
        scroll_calls = [
            props for kind, props in self.fake.widget_calls if kind == "Scrollbar"
        ]
        self.assertTrue(scroll_calls[0]["style"].endswith(".Vertical.TScrollbar"))

    def test_listbox_palette_colors(self):
        ltk.Listbox().items(["a"]).build(None)
        props = [
            p for kind, p in self.fake.widget_calls if kind == "Listbox"
        ][0]
        palette = self.fake.native_theme_colors()
        self.assertEqual(props["bg"], palette["surface"])
        self.assertEqual(props["fg"], palette["text"])
        self.assertEqual(props["selectbackground"], palette["primary"])
        self.assertEqual(props["selectforeground"], palette["primary_text"])
        self.assertEqual(props["highlightbackground"], palette["border"])

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
        space_kinds = [call[0] for call in self.fake.container_calls].count("Space")
        self.assertEqual(space_kinds, 2)
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

    def test_native_theme_palette_cached_and_invalidated(self):
        from lazytkinter.renderer import CTkRenderer

        renderer = CTkRenderer()
        try:
            first = renderer.native_theme_colors()
            second = renderer.native_theme_colors()
            self.assertIs(first, second)

            renderer.set_theme("gruvbox-theme")
            third = renderer.native_theme_colors()
            self.assertIsNot(first, third)

            renderer.set_mode("light")
            fourth = renderer.native_theme_colors()
            self.assertIsNot(third, fourth)
        finally:
            renderer.set_theme("catppuccin-mocha")
            renderer.set_mode("dark")


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
        self.assertTrue(props["style"].startswith("LTkSplitPanel"))
        self.assertTrue(props["style"].endswith(".TPanedwindow"))
        stub = self.fake.created_containers[0]
        self.assertEqual(len(stub.added), 2)

    def test_split_panel_orientation_vertical(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).orientation("vertical").build(None)
        _, props = self.fake.container_calls[0]
        # vertical cut (left/right panes) maps to ttk orient "horizontal"
        self.assertEqual(props["orient"], "horizontal")

    def test_split_panel_horizontal_orient(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).horizontal().build(None)
        _, props = self.fake.container_calls[0]
        # horizontal cut (top/bottom panes) maps to ttk orient "vertical"
        self.assertEqual(props["orient"], "vertical")

    def test_split_panel_requires_two_panes(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel(ltk.Column()).build(None)

    def test_split_panel_per_instance_styles(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).build(None)
        ltk.SplitPanel(ltk.Column(), ltk.Column()).build(None)
        styles = [
            props["style"]
            for kind, props in self.fake.container_calls
            if kind == "SplitPanel"
        ]
        self.assertNotEqual(styles[0], styles[1])

    def test_split_panel_proxy_sash_off_builds(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).proxy_sash(False).build(None)
        kind, props = self.fake.container_calls[0]
        self.assertEqual(kind, "SplitPanel")

    def test_split_panel_orientation_chain(self):
        ltk.SplitPanel(ltk.Column(), ltk.Column()).orientation().vertical().build(None)
        _, props = self.fake.container_calls[0]
        self.assertEqual(props["orient"], "horizontal")

    def test_split_panel_panes_wrapped(self):
        ltk.SplitPanel().add(ltk.Column()).add(ltk.Column()).build(None)
        kinds = [kind for kind, _ in self.fake.container_calls]
        self.assertEqual(kinds[0], "SplitPanel")
        self.assertEqual(kinds.count("SplitPanelPane"), 2)
        self.assertEqual(kinds.count("Column"), 2)

    def test_split_panel_pane_transparent(self):
        ltk.SplitPanel().add(ltk.Column()).transparent().add(ltk.Column()).build(None)
        pane_calls = [
            props
            for kind, props in self.fake.container_calls
            if kind == "SplitPanelPane"
        ]
        self.assertEqual(pane_calls[0]["fg_color"], "transparent")
        self.assertEqual(
            pane_calls[1]["fg_color"], self.fake.native_theme_colors()["surface"]
        )

    def test_split_panel_axis_mismatch_raises(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().add(ltk.Column()).min_height(100).add(ltk.Column()).build(None)
        with self.assertRaises(ValueError):
            ltk.SplitPanel().horizontal().add(ltk.Column()).min_width(100).add(
                ltk.Column()
            ).build(None)

    def test_split_panel_min_exceeds_max_raises(self):
        with self.assertRaises(ValueError):
            ltk.SplitPanel().add(ltk.Column()).min_width(200).max_width(100).add(
                ltk.Column()
            ).build(None)


class DividerFlowTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRenderer()
        set_renderer(self.fake)

    def tearDown(self):
        set_renderer(_real_renderer)

    def test_divider_horizontal_default(self):
        ltk.Divider().build(None)
        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Divider")
        self.assertEqual(props["height"], 1)
        self.assertNotIn("width", props)
        self.assertEqual(props["fg_color"], self.fake.native_theme_colors()["border"])

    def test_divider_vertical(self):
        ltk.Divider().orientation().vertical().build(None)
        kind, props = self.fake.widget_calls[0]
        self.assertEqual(kind, "Divider")
        self.assertEqual(props["width"], 1)
        self.assertNotIn("height", props)

    def test_divider_line_width_and_token_color(self):
        token_mod.set_theme("catppuccin-mocha")
        try:
            ltk.Divider().line_width(3).fg_color("primary").build(None)
            _, props = self.fake.widget_calls[0]
            self.assertEqual(props["height"], 3)
            self.assertEqual(props["fg_color"], token_mod.color("primary"))
        finally:
            token_mod.set_theme("catppuccin-mocha")

    def test_divider_fixed_pixels(self):
        ltk.Divider().width(200).build(None)
        _, props = self.fake.widget_calls[0]
        self.assertEqual(props["width"], 200)
        self.assertEqual(props["height"], 1)

    def test_divider_main_axis_fit_raises(self):
        with self.assertRaises(ValueError):
            ltk.Divider().width().fit().build(None)
        with self.assertRaises(ValueError):
            ltk.Divider().orientation("vertical").height().fit().build(None)


class WindowConstraintTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeRenderer()
        set_renderer(self.fake)

    def tearDown(self):
        set_renderer(_real_renderer)

    def test_resizable_validation(self):
        app = ltk.Application()
        with self.assertRaises(ValueError):
            app.resizable(1, True)

    def test_min_max_size_validation(self):
        app = ltk.Application()
        with self.assertRaises(ValueError):
            app.min_size(0, 100)
        with self.assertRaises(ValueError):
            app.max_size(100, 2.5)
        with self.assertRaises(ValueError):
            app.max_size(True, 100)

    def test_constraint_methods_chainable(self):
        app = ltk.Application()
        self.assertIs(app.resizable(False, False), app)
        self.assertIs(app.min_size(300, 200), app)
        self.assertIs(app.max_size(800, 600), app)
        self.assertIs(app.fixed_size(), app)
