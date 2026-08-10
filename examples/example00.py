"""Example 00: 快速上手——计数器 / Quickstart: a minimal counter.

演示：Application / set_theme / Label / Button / event / .id() + app.config(类型).aim_id()。
Run: python examples/example00.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Gruvbox)  # set theme

    # create program
    app = ltk.Application()

    # counter state
    count = 0

    # event: every click increments the counter label via the typed access channel
    def on_click(value=None):
        nonlocal count
        count += 1
        app.config(ltk.Label).aim_id("count").text(f"{count}")

    # build UI
    app.size("small").window_title("Counter").center().gap(10).column(
        ltk.Label().id("count").text("0").font(family="Arial", size=28, weight="bold"),
        ltk.Button().text("add count").event(on_click),
    )

    # run
    app.run()


if __name__ == "__main__":
    main()
