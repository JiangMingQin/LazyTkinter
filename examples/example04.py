"""Example 04: Space (elastic and fixed-size placeholders).

Run with:
    python examples/example04.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()
    app.size("medium").window_title("Space").padding(16).gap(12).column(
        ltk.Label().text("Elastic Space pushes buttons apart."),
        ltk.Row().gap(8).padding(8).radius(0).width().fill().add(
            ltk.Button().text("left"),
            ltk.Space(),
            ltk.Button().text("right"),
        ),
        ltk.Label().text("Elastic Space with weights 1 : 2."),
        ltk.Row().gap(8).padding(8).radius(0).width().fill().add(
            ltk.Button().text("A"),
            ltk.Space().weight(1),
            ltk.Button().text("B"),
            ltk.Space().weight(2),
            ltk.Button().text("C"),
        ),
        ltk.Label().text("Fixed-size Space: an exact 40px gap."),
        ltk.Row().gap(8).padding(8).radius(0).width().fill().add(
            ltk.Button().text("left"),
            ltk.Space().width(40),
            ltk.Button().width().fill().text("right"),
        ),
        ltk.Label().text("Fixed-size Space in a Column: 10px vertical gap."),
        ltk.Column().gap(8).padding(8).radius(0).height().fill().add(
            ltk.Button().text("top"),
            ltk.Space().height(10),
            ltk.Button().height().fill().text("bottom"),
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
