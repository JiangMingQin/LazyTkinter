"""Example 03: Treeview and Listbox (data widgets).

Run with:
    python examples/example03.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()
    app.size("large").window_title("Treeview & Listbox").padding(12).gap(12).column(
        ltk.Label().text(
            "Select a row or an item; the selection is printed to the console."
        ),
        ltk.Row().gap(8).padding(8).width().fill().height().fill().add(
            ltk.Column().gap(8).padding(8).height().fill().add(
                ltk.Label().text("Treeview (columns + rows)"),
                ltk.Treeview()
                .id("table")
                .columns(["Task", "Priority"])
                .rows(
                    [
                        ("Write docs", "high"),
                        ("Fix bug #42", "high"),
                        ("Refactor UI", "medium"),
                        ("Review PR", "low"),
                    ]
                )
                .width().fill()
                .height().fill()
                .event(lambda row: print("tree selected:", row)),
            ),
            ltk.Column().gap(8).padding(8).height().fill().add(
                ltk.Label().text("Listbox (items)"),
                ltk.Listbox()
                .id("list")
                .items(["python", "javascript", "rust", "go", "zig"])
                .width().fill()
                .height().fill()
                .event(lambda item: print("list selected:", item)),
            ),
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
