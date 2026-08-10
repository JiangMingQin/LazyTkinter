"""Hidden-window smoke tests; skipped when no display is available."""

import os
import sys
import unittest

import lazytkinter as ltk
import lazytkinter.renderer as renderer_mod
from lazytkinter import registry

_real_create_window = renderer_mod.CTkRenderer.create_window
_real_run = ltk.Application.run


def _has_display():
    if os.name == "nt":
        return True
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no display available")
class SmokeTests(unittest.TestCase):
    def setUp(self):
        registry.clear()
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
        registry.clear()
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
            ltk.Space().weight(1),
            ltk.Button().text("middle"),
            ltk.Space().weight(2),
        )
        app.build()
        app._window.update_idletasks()

    def test_fixed_space(self):
        app = ltk.Application()
        app.size((400, 120)).window_title("smoke").column(
            ltk.Row().gap(8).padding(8).add(
                ltk.Button().text("left"),
                ltk.Space().width(10),
                ltk.Button().text("right"),
            ),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_fixed_container_height(self):
        app = ltk.Application()
        app.size((300, 200)).column(
            ltk.Row().height(60).add(
                ltk.Label().text("x"),
            ),
        )
        app.build()
        app._window.update_idletasks()
        row = app.base_frame.winfo_children()[0]
        self.assertEqual(row.winfo_reqheight(), 60)
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

    def test_treeview_and_listbox(self):
        app = ltk.Application()
        app.size("small")
        selected = []
        app.column(
            ltk.Treeview()
                .columns(["Item", "Value"])
                .rows([(f"Item {i}", i) for i in range(300)])
                .height().fill()
                .event(selected.append),
            ltk.Listbox()
                .items([f"Item {i}" for i in range(300)])
                .height().fill()
                .event(selected.append),
        )
        app.build()
        app._window.update_idletasks()

        tree_frame, listbox_frame = app.base_frame.winfo_children()
        tree = next(c for c in tree_frame.winfo_children() if c.winfo_class() == "Treeview")
        listbox = next(c for c in listbox_frame.winfo_children() if c.winfo_class() == "Listbox")
        self.assertEqual(len(tree.get_children()), 300)
        self.assertEqual(listbox.size(), 300)

        tree.selection_set(tree.get_children()[0])
        tree.event_generate("<<TreeviewSelect>>")
        app._window.update_idletasks()
        self.assertEqual(len(selected), 1)
        app._window.destroy()

    def test_data_widget_theming(self):
        from tkinter import ttk

        app = ltk.Application()
        app.size((500, 360)).window_title("smoke").column(
            ltk.Treeview().id("t").columns(["A"]).rows([("1",)]),
            ltk.Listbox().id("l").items(["a"]),
        )
        app.build()
        app._window.update_idletasks()

        palette = renderer_mod.get_renderer().native_theme_colors()
        style = ttk.Style(app._window)
        self.assertEqual(style.theme_use(), "clam")
        tree_style = app.native("t").cget("style")
        self.assertTrue(tree_style.startswith("LTkData"))
        self.assertTrue(tree_style.endswith(".Treeview"))
        configured = style.configure(tree_style)
        self.assertEqual(configured["background"], palette["surface"])
        self.assertEqual(style.lookup(tree_style, "background"), palette["surface"])

        scrollbar = next(
            c
            for c in app.native("t").master.winfo_children()
            if c.winfo_class() == "TScrollbar"
        )
        scroll_style = scrollbar.cget("style")
        self.assertTrue(scroll_style.endswith(".Vertical.TScrollbar"))
        self.assertEqual(
            style.configure(scroll_style)["troughcolor"], palette["border"]
        )
        self.assertEqual(app.native("l").cget("bg"), palette["surface"])
        app._window.destroy()

    def test_id_get_and_layout_tree(self):
        app = ltk.Application()
        app.size("small")
        app.column(
            ltk.Column().gap(8).add(
                ltk.Label().id("count").text("0"),
                ltk.Button().id("btn").text("+1"),
            ),
        )
        app.build()
        app._window.update_idletasks()

        app.config(ltk.Label).aim_id("count").text("5")
        self.assertEqual(app.native("count").cget("text"), "5")

        tree = app.layout_tree()
        # CTk widgets are Tk Frames internally; ids are attached to them
        self.assertIn("Frame[count]", tree)
        self.assertIn("Frame[btn]", tree)
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
            ltk.Canvas().draw("not callable")
        with self.assertRaises(ValueError):
            ltk.SplitPanel().orientation("diagonal")
        with self.assertRaises(ValueError):
            ltk.SplitPanel().sash_width(-1)
        with self.assertRaises(ValueError):
            ltk.Divider().line_width(0)
        with self.assertRaises(ValueError):
            ltk.Divider().orientation("diagonal")
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

    def test_canvas(self):
        app = ltk.Application()
        drawn = []
        app.size((500, 360)).window_title("smoke").column(
            ltk.Canvas()
            .width(360)
            .height(220)
            .fg_color("surface_alt")
            .draw(lambda c: drawn.append(c.create_rectangle(10, 10, 120, 90, fill="red"))),
        )
        app.build()
        app._window.update_idletasks()

        self.assertEqual(len(drawn), 1)
        self.assertEqual(len(app._window.winfo_children()), 1)
        app._window.destroy()

    def test_example03(self):
        self._run_example("examples/example03.py")

    def test_split_panel(self):
        app = ltk.Application()
        app.size((600, 420)).window_title("smoke").column(
            ltk.SplitPanel().id("split").vertical()
            .add(ltk.Column().gap(8).padding(8).add(ltk.Label().text("left")))
            .min_width(120).max_width(300)
            .add(ltk.Column().gap(8).padding(8).add(ltk.Label().text("right")))
            .min_width(120),
        )
        app.build()
        app._window.deiconify()
        app._window.update()
        native = app.native("split")
        self.assertGreater(native.winfo_width(), 0)
        # force an out-of-range sash, then let the <Map> clamp snap it back
        native.sashpos(0, 30)
        app._window.update()
        native.event_generate("<Map>")
        app._window.update()
        self.assertGreaterEqual(native.sashpos(0), 100)
        app._window.destroy()

    def test_divider(self):
        app = ltk.Application()
        app.size((500, 360)).window_title("smoke").column(
            ltk.Column().gap(8).padding(8).add(
                ltk.Label().text("above"),
                ltk.Divider(),
                ltk.Label().text("below"),
            ),
            ltk.Row().gap(8).padding(8).add(
                ltk.Label().text("left"),
                ltk.Divider().vertical(),
                ltk.Label().text("right"),
            ),
        )
        app.build()
        app._window.update_idletasks()
        app._window.destroy()

    def test_example04(self):
        self._run_example("examples/example04.py")

    def test_example05(self):
        self._run_example("examples/example05.py")

    def test_example06(self):
        self._run_example("examples/example06.py")

    def test_view(self):
        app = ltk.Application()
        app.size((500, 360)).window_title("smoke").column(
            ltk.View().id("main")
            .add("home", ltk.Column().add(ltk.Label().text("home")))
            .add("settings", ltk.Column().add(ltk.Label().text("settings"))),
        )
        app.build()
        app._window.deiconify()
        app._window.update()

        app.config(ltk.View).aim_id("main").show("settings")
        app._window.update()
        self.assertEqual(app.read("main"), "settings")
        self.assertFalse(app.config(ltk.View).aim_id("main")._frames["home"].winfo_ismapped())
        self.assertTrue(app.config(ltk.View).aim_id("main")._frames["settings"].winfo_ismapped())
        app._window.destroy()

    def test_window_size_constraints(self):
        app = ltk.Application()
        app.size((400, 300)).min_size(300, 200).max_size(800, 600).resizable(False, False)
        # CTk overrides minsize/maxsize/resizable without supporting the no-arg
        # getter form, so query through the underlying wm_* methods.
        self.assertEqual(app._window.wm_minsize(), (300, 200))
        self.assertEqual(app._window.wm_maxsize(), (800, 600))
        self.assertEqual(app._window.wm_resizable(), (0, 0))
        app._window.destroy()

    def test_button_fix_size(self):
        app = ltk.Application()
        app.size((400, 200)).column(
            ltk.Row().gap(8).padding(8).add(
                ltk.Button()
                .text("hello world")
                .width(100).height(30)
                .font(family="Arial", size=28)
                .fix_size()
                .id("fixed"),
                ltk.Button()
                .text("hello world")
                .width(100).height(30)
                .font(family="Arial", size=28)
                .id("free"),
            ),
        )
        app.build()
        app._window.deiconify()
        app._window.update()
        self.assertEqual(app.native("fixed").winfo_width(), 100)
        self.assertGreater(app.native("free").winfo_width(), 100)
        app._window.destroy()

    def test_value_api(self):
        app = ltk.Application()
        app.size((600, 480)).window_title("smoke").column(
            ltk.Entry().id("entry"),
            ltk.Slider().range(0, 100).id("slider"),
            ltk.CheckBox().id("check"),
            ltk.ComboBox().values(["a", "b", "c"]).id("combo"),
            ltk.Textbox().height(60).id("text"),
            ltk.Treeview().columns(["A"]).rows([("1",), ("2",)]).id("tree"),
        )
        app.build()
        app._window.update_idletasks()

        app.config(ltk.Entry).aim_id("entry").set("hello")
        self.assertEqual(app.read("entry"), "hello")
        app.config(ltk.Entry).aim_id("entry").clear()
        self.assertEqual(app.read("entry"), "")

        app.config(ltk.Slider).aim_id("slider").set(40)
        self.assertEqual(app.read("slider"), 40)

        app.config(ltk.CheckBox).aim_id("check").set(True)
        self.assertTrue(app.read("check"))

        app.config(ltk.ComboBox).aim_id("combo").set("b")
        self.assertEqual(app.read("combo"), "b")

        app.config(ltk.Textbox).aim_id("text").set("line1\nline2")
        self.assertEqual(app.read("text"), "line1\nline2")

        app.config(ltk.Treeview).aim_id("tree").set([("3",), ("4",)])
        self.assertEqual(len(app.native("tree").get_children()), 2)
        app._window.destroy()

    def test_window_center_and_visible(self):
        app = ltk.Application()
        app.size((400, 300)).center_window()
        app.column(ltk.Button().text("hide me").id("btn"))
        app.build()
        app._window.deiconify()
        app._window.update()
        screen_w = app._window.winfo_screenwidth()
        screen_h = app._window.winfo_screenheight()
        self.assertGreaterEqual(app._window.winfo_x(), 0)
        self.assertGreaterEqual(app._window.winfo_y(), 0)
        self.assertLess(app._window.winfo_x(), screen_w)
        self.assertLess(app._window.winfo_y(), screen_h)

        app.config(ltk.Button).aim_id("btn").visible(False)
        app._window.update()
        self.assertFalse(app.native("btn").winfo_ismapped())
        app.config(ltk.Button).aim_id("btn").visible(True)
        app._window.update()
        self.assertTrue(app.native("btn").winfo_ismapped())
        app._window.destroy()
