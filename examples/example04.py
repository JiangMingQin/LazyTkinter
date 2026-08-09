"""Example 04: SplitPanel (resizable split panes themed with CTk colors).

Run with:
    python examples/example04.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()
    app.size("large").window_title("SplitPanel & Divider").padding(12).gap(12).column(
        ltk.Label().text("Drag the sash between the two panes to resize them."),
        ltk.Divider(),
        ltk.SplitPanel(
            ltk.Column().gap(8).padding(8).add(
                ltk.Label().text("Left pane"),
                ltk.Entry().placeholder_text("Name"),
                ltk.Button().text("OK").event(lambda _: print("OK clicked")),
            ),
            ltk.Column().gap(8).padding(8).add(
                ltk.Label().text("Right pane"),
                ltk.Canvas().width(220).height(140).fg_color("surface_alt").draw(
                    lambda c: c.create_rectangle(
                        10, 10, 100, 60, fill=ltk.color("primary"), outline=""
                    )
                ),
            ),
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
