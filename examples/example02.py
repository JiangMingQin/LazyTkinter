"""Example 02: 布局与容器 / Layout & containers.

演示：Row / Column / ZStack / Scroll / Space / View / SplitPanel / Divider，
以及 fit / fill / weight、gap / padding / align / justify。
Run: python examples/example02.py
"""

import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()
    app.size("large").window_title("Layout & Containers").padding(10).gap(10)

    def go(page):
        return lambda _: app.config(ltk.View).aim_id("pages").show(page)

    # ---- 页面 1：基础布局 ----
    basic = ltk.Column().width().fill().height().fill().gap(10).padding(10).add(
        ltk.Label().text("Row / Column · fit / fill / weight").font(size=14, weight="bold"),
        ltk.Row().gap(8).width().fill().add(
            ltk.Button().text("A").fill(weight=1),
            ltk.Button().text("B").fill(weight=2),
            ltk.Button().text("C").fill(weight=1),
        ),
        ltk.Label().text("justify / align / center").font(size=14, weight="bold"),
        ltk.Row().gap(8).padding(8).width().fill().justify("center").add(
            ltk.Button().text("center"),
            ltk.Button().text("row"),
        ),
        ltk.Column().gap(8).padding(8).align("center").add(
            ltk.Button().width(160).text("align center"),
            ltk.Button().width(160).text("column"),
        ),
        ltk.Label().text("Space（弹性 / 固定）+ Divider").font(size=14, weight="bold"),
        ltk.Row().gap(8).padding(8).width().fill().add(
            ltk.Button().text("left"),
            ltk.Space(),
            ltk.Divider().vertical(),
            ltk.Space().width(30),
            ltk.Button().text("right"),
        ),
        ltk.Column().gap(8).padding(8).add(
            ltk.Label().text("above"),
            ltk.Divider(),
            ltk.Label().text("below"),
        ),
    )

    # ---- 页面 2：层叠与滚动 ----
    overlay = ltk.Column().width().fill().height().fill().gap(10).padding(10).add(
        ltk.Label().text("ZStack（重叠 + 九宫格锚点）").font(size=14, weight="bold"),
        ltk.ZStack().width(380).height(180).add(
            ltk.Button().width().fill().height().fill().text("base"),
            ltk.Label().text("top-left").align("top-left"),
            ltk.Label().text("center").align("center"),
            ltk.Label().text("bottom-right").align("bottom-right"),
        ),
        ltk.Label().text("Scroll（v1 仅 vertical）").font(size=14, weight="bold"),
        ltk.Scroll(
            ltk.Column().width().fill().gap(6).add(
                *[ltk.Button().width().fill().text(f"item {i:02d}") for i in range(20)],
            ),
        ),
    )

    # ---- 页面 3：分栏 ----
    split = ltk.Column().width().fill().height().fill().gap(10).padding(10).add(
        ltk.Label().text("SplitPanel.vertical()（左右分栏）").font(size=14, weight="bold"),
        ltk.SplitPanel().id("split_v").vertical()
        .add(ltk.Column().gap(8).padding(8).add(ltk.Label().text("left pane")))
        .min_width(140).max_width(320)
        .add(ltk.Column().gap(8).padding(8).add(ltk.Label().text("right pane")))
        .min_width(140),
        ltk.Label().text("SplitPanel.horizontal()（上下分栏）").font(size=14, weight="bold"),
        ltk.SplitPanel().id("split_h").horizontal()
        .add(ltk.Column().gap(8).padding(8).add(ltk.Label().text("top pane")))
        .min_height(80).max_height(220)
        .add(ltk.Column().gap(8).padding(8).add(ltk.Label().text("bottom pane")))
        .min_height(80),
    )

    # ---- 根布局：侧边栏 + View 分页 ----
    sidebar = ltk.Column().width(140).height().fill().gap(8).padding(8).add(
        ltk.Label().text("Menu").font(size=14, weight="bold"),
        ltk.Button().text("Basic layout").event(go("basic")),
        ltk.Button().text("Overlay / Scroll").event(go("overlay")),
        ltk.Button().text("SplitPanel").event(go("split")),
    )

    pages = (
        ltk.View().id("pages").width().fill().height().fill()
        .add("basic", basic)
        .add("overlay", overlay)
        .add("split", split)
    )

    app.row(sidebar, pages)
    app.run()


if __name__ == "__main__":
    main()
