"""Example 02: 控件全览——全部控件与事件反馈写法 / Widget gallery.

演示：全部 16 个控件、统一 print 事件反馈、Scroll、CTkImage + compound、
运行时更新（app.config(类型).aim_id / app.read / visible）、
窗口 API（on_close / center_window）、主题切换（set_theme / set_mode）。
Run: python examples/example02.py
"""

import lazytkinter as ltk

try:  # Pillow 未安装时跳过 image()/compound() 演示（CTkImage 依赖它）
    from PIL import Image as _PILImage
    from PIL import ImageDraw as _PILDraw
except ImportError:
    _PILImage = None
    _PILDraw = None


def _dot_image(color: str, size: int = 16):
    """生成一个纯色圆点 CTkImage，用于演示 image() / compound()；无 Pillow 时返回 None。"""
    if _PILImage is None or _PILDraw is None:
        return None
    img = _PILImage.new("RGBA", (size, size), (0, 0, 0, 0))
    _PILDraw.Draw(img).ellipse((1, 1, size - 2, size - 2), fill=color)
    return ltk.Image(light_image=img, dark_image=img, size=(size, size))


def _section(title: str, *children):
    """每个分组：一个加粗标题 + 若干控件。"""
    return ltk.Column().gap(8).padding(8).add(
        ltk.Label().text(title).font(size=14, weight="bold"),
        *children,
    )


def main() -> None:
    ltk.set_theme(ltk.Theme.Catppuccin)

    app = ltk.Application()

    # ---- 窗口 API ----
    def on_close():
        print("[Window] on_close: destroy")
        app.destroy()

    app.size("large").window_title("Widget Gallery").center_window().on_close(on_close)

    # ---- 顶部工具条：主题 / 明暗切换 ----
    def on_theme(value):
        ltk.set_theme(value)
        print(f"[Theme] {value}")

    mode = {"current": "light"}

    def toggle_mode():
        mode["current"] = "dark" if mode["current"] == "light" else "light"
        ltk.set_mode(mode["current"])
        print(f"[Mode] {mode['current']}")

    toolbar = ltk.Row().gap(10).padding(10).width().fill().add(
        ltk.Label().text("Theme:"),
        ltk.SegmentedButton()
        .id("theme_switch")
        .values([ltk.Theme.Catppuccin, ltk.Theme.Gruvbox, ltk.Theme.Dracula])
        .set_value(ltk.Theme.Catppuccin)
        .event(on_theme),
        ltk.Space(),
        ltk.Button().text("Toggle mode").event(lambda _: toggle_mode()),
    )

    # ---- 基础控件 ----
    basic = _section(
        "Basic: Label / Button / Entry / Textbox / Canvas",
        ltk.Label().id("hello").text("Hello, LazyTkinter!"),
        ltk.Row().gap(8).add(
            ltk.Button().id("btn").text("Button").event(lambda _: print("[Button] clicked")),
            ltk.Button().text("With icon").image(_dot_image("#cba6f7")).compound("left")
            .event(lambda _: print("[Button] icon button clicked")),
            ltk.Button().text("Disabled").state("disabled"),
        ),
        ltk.Row().gap(8).add(
            ltk.Entry().id("entry").placeholder_text("type here...").width(220),
            ltk.Textbox().id("textbox").width(220).height(72),
        ),
        ltk.Canvas()
        .id("canvas")
        .width(360)
        .height(140)
        .fg_color("surface_alt")
        .draw(lambda c: c.create_rectangle(16, 16, 116, 88, fill="#f38ba8", outline=""))
        .draw(lambda c: c.create_oval(150, 22, 230, 102, fill="#89b4fa", outline=""))
        .draw(lambda c: c.create_text(240, 62, text="draw()", fill="#cdd6f4")),
    )

    # ---- 选择控件 ----
    radio_var = ltk.StringVar(value="A")

    choice = _section(
        "Choice: Switch / CheckBox / RadioButton / SegmentedButton",
        ltk.Row().gap(16).add(
            ltk.Switch().id("switch").text("Switch").event(lambda v: print(f"[Switch] {v}")),
            ltk.CheckBox().id("check").text("CheckBox").event(lambda v: print(f"[CheckBox] {v}")),
        ),
        ltk.Row().gap(16).add(
            ltk.RadioButton().text("Option A").value("A").variable(radio_var)
            .event(lambda v: print(f"[RadioButton] {v}")),
            ltk.RadioButton().text("Option B").value("B").variable(radio_var)
            .event(lambda v: print(f"[RadioButton] {v}")),
        ),
        ltk.SegmentedButton().id("seg").values(["one", "two", "three"])
        .event(lambda v: print(f"[SegmentedButton] {v}")),
    )

    # ---- 下拉控件 ----
    dropdown = _section(
        "Dropdown: ComboBox / OptionMenu",
        ltk.Row().gap(8).add(
            ltk.ComboBox().id("combo").values(["python", "rust", "go"]).set_value("python")
            .event(lambda v: print(f"[ComboBox] {v}")),
            ltk.OptionMenu().id("menu").values(["light", "dark", "auto"]).set_value("auto")
            .event(lambda v: print(f"[OptionMenu] {v}")),
        ),
    )

    # ---- 数值控件：Slider 拖动实时驱动 ProgressBar ----
    def on_slider(value):
        app.config(ltk.ProgressBar).aim_id("progress").set(value)
        print(f"[Slider] {value}")

    numeric = _section(
        "Numeric: Slider / ProgressBar",
        ltk.Slider().id("slider").range(0, 1).steps(10).event(on_slider),
        ltk.ProgressBar().id("progress").value(0.5),
    )

    # ---- 数据控件 ----
    data = _section(
        "Data: Treeview / Listbox",
        ltk.Row().gap(8).width().fill().height(180).add(
            ltk.Column().width().fill().height().fill().add(
                ltk.Treeview()
                .id("table")
                .columns(["Task", "Priority"])
                .rows([("Write docs", "high"), ("Fix bug", "high"), ("Review PR", "low")])
                .width().fill().height().fill()
                .event(lambda row: print(f"[Treeview] {row}")),
            ),
            ltk.Column().width().fill().height().fill().add(
                ltk.Listbox()
                .id("list")
                .items(["python", "javascript", "rust", "go", "zig"])
                .width().fill().height().fill()
                .event(lambda item: print(f"[Listbox] {item}")),
            ),
        ),
    )

    # ---- 运行时更新：config(类型).aim_id / read / visible ----
    runtime = _section(
        "Runtime updates: config(类型).aim_id / read / visible",
        ltk.Label().id("toggle").text("I can be hidden at runtime."),
        ltk.Row().gap(8).add(
            ltk.Button().text("Hide label").event(
                lambda _: app.config(ltk.Label).aim_id("toggle").visible(False)
            ),
            ltk.Button().text("Show label").event(
                lambda _: app.config(ltk.Label).aim_id("toggle").visible(True)
            ),
        ),
        ltk.Row().gap(8).add(
            ltk.Button().text("read('entry')").event(
                lambda _: print(f"[app.read] entry={app.read('entry')!r}")
            ),
            ltk.Button().text("read('textbox')").event(
                lambda _: print(f"[app.read] textbox={app.read('textbox')!r}")
            ),
            ltk.Button().text("set textbox").event(
                lambda _: app.config(ltk.Textbox).aim_id("textbox").set("updated at runtime")
            ),
        ),
    )

    # ---- 根布局：顶部工具条 + 可滚动主体 ----
    app.padding(10).gap(10).column(
        toolbar,
        ltk.Scroll(
            ltk.Column().width().fill().gap(10).add(
                basic,
                choice,
                dropdown,
                numeric,
                data,
                runtime,
            )
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
