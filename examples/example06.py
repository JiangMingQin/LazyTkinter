"""Example 06: View (sidebar + content page switching).

Run with:
    python examples/example06.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()

    def go(page):
        return lambda _: app.config(ltk.View).aim_id("main").show(page)

    app.size("large").window_title("View").padding(10).gap(10).row(
        ltk.Column().width(140).height().fill().gap(8).padding(8).add(
            ltk.Label().text("Menu").font(size=14, weight="bold"),
            ltk.Button().text("Home").event(go("home")),
            ltk.Button().text("Settings").event(go("settings")),
            ltk.Button().text("About").event(go("about")),
        ),
        ltk.View().id("main").width().fill().height().fill()
        .add(
            "home",
            ltk.Column().gap(8).padding(8).add(
                ltk.Label().text("Home page"),
                ltk.Label().text("This is the home page."),
            ),
        )
        .add(
            "settings",
            ltk.Column().gap(8).padding(8).add(
                ltk.Label().text("Settings page"),
                ltk.Switch().text("Dark mode"),
            ),
        )
        .add(
            "about",
            ltk.Column().gap(8).padding(8).add(
                ltk.Label().text("About page"),
                ltk.Label().text("LazyTkinter 0.12.0"),
            ),
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
