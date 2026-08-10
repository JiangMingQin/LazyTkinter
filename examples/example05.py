"""Example 05: Window & widget details.

Run with:
    python examples/example05.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()

    def on_close():
        print("window closing")
        app.destroy()

    # icon / compound need an image asset (PIL for CTkImage, .ico for iconbitmap):
    #   app.icon("app.ico")
    #   ltk.Button().image(ltk.Image(light_image=..., size=(16, 16))).compound("left")

    app.size("medium").window_title("Window & Widget Details").center_window().on_close(on_close)

    app.padding(12).gap(8).column(
        ltk.Label().text("This label is left-aligned (anchor='w').").anchor("w"),
        ltk.Label().id("toggle").text("I can be hidden at runtime."),
        ltk.Button().text("hide label").event(lambda _: app.get("toggle").visible(False)),
        ltk.Button().text("show label").event(lambda _: app.get("toggle").visible(True)),
    )
    app.run()


if __name__ == "__main__":
    main()
