"""Example 03: Canvas.

Run with:
    python examples/example03.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()
    app.size("medium").window_title("Canvas").padding(16).gap(12).column(
        ltk.Label().text("A drawing surface (CTkCanvas / tk.Canvas)."),
        ltk.Canvas()
        .id("drawing")
        .width(680)
        .height(420)
        .fg_color("surface_alt")
        .draw(
            lambda c: (
                c.create_rectangle(20, 20, 180, 130, fill=ltk.color("primary"), outline=""),
                c.create_oval(
                    220, 40, 330, 150, fill=ltk.color("bg"), outline=ltk.color("text")
                ),
                c.create_line(30, 360, 640, 120, fill=ltk.color("text"), width=3),
            )
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
