"""Build-flow tests using a fake renderer (no Tk window needed)."""

import unittest

import lazytkinter as ltk
from lazytkinter.containers import Column, Scroll, ZStack
from lazytkinter.renderer import Renderer, get_renderer, set_renderer

_real_renderer = get_renderer()


class Stub:
    """Duck-typed stand-in for any native Tk widget."""

    def __init__(self):
        self.configured = {}
        self.set_calls = []
        self.value = 1

    def get(self):
        return self.value

    def configure(self, **kwargs):
        self.configured.update(kwargs)

    def set(self, value):
        self.set_calls.append(value)

    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None

        return _noop


class FakeRenderer(Renderer):
    def __init__(self):
        self.widget_calls = []
        self.container_calls = []
        self.window = Stub()

    def create_window(self):
        return self.window

    def create_widget(self, kind, parent, props):
        self.widget_calls.append((kind, dict(props)))
        return Stub()

    def create_container(self, kind, parent, props):
        self.container_calls.append((kind, dict(props)))
        return Stub()

    def set_theme(self, theme_name):
        pass

    def set_mode(self, mode):
        pass


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


class ThemeTests(unittest.TestCase):
    def test_missing_theme_raises_value_error(self):
        from lazytkinter.renderer import CTkRenderer

        with self.assertRaises(ValueError):
            CTkRenderer().set_theme("no-such-theme-xyz")

    def test_native_theme_passes_through(self):
        from lazytkinter.renderer import CTkRenderer

        CTkRenderer().set_theme("blue")
