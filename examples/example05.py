"""Example 05: Value API (get / set / clear).

Run with:
    python examples/example05.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()

    def set_and_print(_):
        app.get("entry").set("hello")
        app.get("slider").set(75)
        app.get("check").set(True)
        app.get("combo").set("c")
        app.get("text").set("line1\nline2")
        print("entry:", app.get("entry").get())
        print("slider:", app.get("slider").get())
        print("check:", app.get("check").get())
        print("combo:", app.get("combo").get())
        print("text:", repr(app.get("text").get()))

    def clear_all(_):
        app.get("entry").clear()
        app.get("text").clear()
        print("cleared entry/text")

    app.size("small").window_title("Value API").padding(12).gap(8).column(
        ltk.Entry().id("entry").placeholder_text("entry"),
        ltk.Slider().range(0, 100).id("slider").set(40),
        ltk.CheckBox().id("check").text("check").set(True),
        ltk.ComboBox().id("combo").values(["a", "b", "c"]).set("b"),
        ltk.Textbox().id("text").height(60),
        ltk.Button().text("set & print").event(set_and_print),
        ltk.Button().text("clear").event(clear_all),
    )
    app.run()


if __name__ == "__main__":
    main()
