"""轻量压力/规模测试：隐藏窗口验证批量构建、大数据、重建循环、高频更新与深嵌套。

规模刻意控制在 CI 可接受的范围内；无显示环境时自动跳过（与 test_smoke_gui 一致）。
"""

import os
import unittest

import lazytkinter as ltk
from lazytkinter import registry


def _has_display():
    if os.name == "nt":
        return True
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no display available")
class StressTests(unittest.TestCase):
    def setUp(self):
        registry.clear()

    def tearDown(self):
        registry.clear()

    def _make_app(self):
        app = ltk.Application()
        app.withdraw()
        return app

    def test_many_widgets_build_and_live_update(self):
        app = self._make_app()
        col = ltk.Column()
        for i in range(100):
            col.add(ltk.Button().text(f"b{i}").id(f"b{i}"))
            if i % 3 == 0:
                col.add(ltk.Label().text(f"l{i}"))
        app.column(col)
        app.build()
        app.update()
        for i in range(0, 100, 10):
            app.config(ltk.Button).aim_id(f"b{i}").text(f"x{i}")
        self.assertEqual(len(app.ids()), 100)
        app.destroy()

    def test_data_widgets_large_dataset_and_replace(self):
        app = self._make_app()
        rows = [(f"row {i}", f"col{i}", i % 7) for i in range(1000)]
        tv = (
            ltk.Treeview()
            .id("tv")
            .columns(["A", "B", "C"])
            .rows(rows)
            .width().fill()
            .height().fill()
        )
        lb = (
            ltk.Listbox()
            .id("lb")
            .items([f"item {i}" for i in range(1000)])
            .width().fill()
            .height().fill()
        )
        app.column(ltk.Row().width().fill().height().fill().add(tv, lb))
        app.build()
        app.update()
        app.config(ltk.Treeview).aim_id("tv").set(
            [(f"new {i}", "x", 1) for i in range(500)]
        )
        app.config(ltk.Listbox).aim_id("lb").set([f"n{i}" for i in range(500)])
        app.update()
        app.destroy()

    def test_application_rebuild_cycles(self):
        for _ in range(5):
            app = self._make_app()
            app.column(ltk.Button().text("t").id("btn"))
            app.build()
            app.update()
            app.destroy()

    def test_rapid_live_updates(self):
        app = self._make_app()
        app.column(
            ltk.Entry().id("e").set("0"),
            ltk.Slider().id("s").range(0, 100),
            ltk.ProgressBar().id("p"),
        )
        app.build()
        app.update()
        for i in range(500):
            app.config(ltk.Entry).aim_id("e").set(str(i))
            app.config(ltk.Slider).aim_id("s").set(i % 100)
            app.config(ltk.ProgressBar).aim_id("p").set((i % 100) / 100)
        app.update()
        app.destroy()

    def test_deep_nesting(self):
        app = self._make_app()
        inner = ltk.Button().text("deep")
        for _ in range(15):
            inner = ltk.Column().add(inner)
        app.column(inner)
        app.build()
        app.update()
        app.destroy()


if __name__ == "__main__":
    unittest.main()
