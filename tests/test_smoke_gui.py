"""Hidden-window smoke tests; skipped when no display is available."""

import os
import sys
import unittest

import lazytkinter as ltk
import lazytkinter.renderer as renderer_mod

_real_create_window = renderer_mod.CTkRenderer.create_window
_real_run = ltk.Application.run


def _has_display():
    if os.name == "nt":
        return True
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no display available")
class SmokeTests(unittest.TestCase):
    def setUp(self):
        orig_create_window = renderer_mod.CTkRenderer.create_window
        orig_run = ltk.Application.run

        def _hidden_create_window(self):
            window = orig_create_window(self)
            window.withdraw()
            return window

        def _auto_run(self):
            self.after(300, self.destroy)
            orig_run(self)

        renderer_mod.CTkRenderer.create_window = _hidden_create_window
        ltk.Application.run = _auto_run

    def tearDown(self):
        renderer_mod.CTkRenderer.create_window = _real_create_window
        ltk.Application.run = _real_run

    def _run_example(self, path):
        import runpy

        sys.argv = [path]
        runpy.run_path(path, run_name="__main__")

    def test_example00(self):
        self._run_example("examples/example00.py")

    def test_example01(self):
        self._run_example("examples/example01.py")

    def test_example02(self):
        self._run_example("examples/example02.py")

    def test_zstack_overlay(self):
        app = ltk.Application()
        app.size((500, 400)).window_title("smoke").center().column(
            ltk.ZStack().width().fill().height().fill().padding(12).add(
                ltk.Button().text("under"),
                ltk.Button().text("over").align("top-right"),
            ),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_spacer_unequal_distribution(self):
        app = ltk.Application()
        app.size((400, 300))
        app.column(
            ltk.Spacer().weight(1),
            ltk.Button().text("middle"),
            ltk.Spacer().weight(2),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_center_shortcut_layout(self):
        app = ltk.Application()
        app.size("small")
        app.column(
            ltk.Column().center().add(
                ltk.Button().text("centered"),
            ),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_application_center_root_with_gap(self):
        app = ltk.Application()
        app.size("small").gap(10).center().column(
            ltk.Label().text("title"),
            ltk.Button().text("centered"),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_row_justify_center_layout(self):
        app = ltk.Application()
        app.size("small")
        app.column(
            ltk.Column().padding(20).add(
                ltk.Row().justify("center").gap(10).add(
                    ltk.Button().text("Login"),
                    ltk.Button().text("Cancel"),
                ),
            ),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_justify_end_layout(self):
        app = ltk.Application()
        app.size("small").justify("end").column(
            ltk.Button().text("bottom"),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_size_chain_and_container_appearance(self):
        app = ltk.Application()
        app.size("small")
        app.column(
            ltk.Column().width().fill().fg_color("#1e1e2e").radius(12).gap(8).padding(10).add(
                ltk.Entry().height(35).width().fill(),
                ltk.Button().width(120).text("ok"),
            ),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_scroll_layout(self):
        app = ltk.Application()
        app.size("small")
        app.column(
            ltk.Scroll(
                ltk.Column().gap(5).add(
                    *[ltk.Button().text(f"Item {i}") for i in range(50)]
                ),
            ).height().fill(),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_invalid_api_raises(self):
        with self.assertRaises(ValueError):
            ltk.Button().width("bogus")
        with self.assertRaises(ValueError):
            ltk.Scroll()
        with self.assertRaises(NotImplementedError):
            ltk.Scroll(ltk.Button()).direction("horizontal")
        with self.assertRaises(ValueError):
            ltk.Column().align("top")
        with self.assertRaises(ValueError):
            ltk.Column().justify("middle")
        with self.assertRaises(ValueError):
            ltk.set_theme("no-such-theme-xyz")

        app = ltk.Application()
        app.column(ltk.Button())
        with self.assertRaises(RuntimeError):
            app.column(ltk.Button())
        app._window.destroy()

        app2 = ltk.Application()
        app2.align("left")
        with self.assertRaises(ValueError):
            app2.row(ltk.Button())
        app2._window.destroy()
