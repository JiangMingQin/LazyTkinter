# LazyTkinter 示例导读（EXAMPLES Guide）

> 本文档介绍 `examples/` 目录下各示例的**主要内容与关键代码**，帮助快速理解常用写法。
> 每个示例都给出运行方式，并摘录核心片段做辅助讲解；**完整源码以 `examples/` 下对应文件为准**，这里不重复贴全部代码。

## 示例总览

| 示例 | 文件 | 主要内容 | 运行 |
| --- | --- | --- | --- |
| 计数器 | `examples/example00.py` | 最小应用骨架；`.id()` + `app.config(类型).aim_id()` 运行时更新 | `python examples/example00.py` |
| 控件全览 | `examples/example01.py` | 全部 16 个控件、统一事件反馈、`Scroll`、`CTkImage` + `compound`、运行时更新（`config` / `read` / `visible`）、窗口 API、主题/明暗切换 | `python examples/example01.py` |
| 布局与容器 | `examples/example02.py` | `Row` / `Column` / `ZStack` / `Scroll` / `Space` / `View` / `SplitPanel` / `Divider`；fit / fill / weight、gap / padding / align / justify | `python examples/example02.py` |
| 计算器 | `examples/example03.py` | 逻辑与 UI 分离的完整应用；`StringVar` 值绑定、fill 等宽按钮、语义 token 配色 | `python examples/example03.py` |

---

## example00 — 计数器（最小应用骨架）

**主要内容**：`Application` / `set_theme` / `Label` / `Button` / `event` / `.id()` + `app.config(类型).aim_id()`。

应用骨架与注册 id：

```python
app.size("small").window_title("Counter").center().gap(10).column(
    ltk.Label().id("count").text("0").font(family="Arial", size=28, weight="bold"),
    ltk.Button().text("add count").event(on_click),
)
```

点击按钮后，通过类型化访问实时更新标签：

```python
def on_click(value=None):
    count += 1
    app.config(ltk.Label).aim_id("count").text(f"{count}")
```

Tips：

- `app.size("small")` 用内置尺寸预设；`.center()` 让根布局双轴居中；`.gap(10)` 设置子元素间距。
- `event(on_click)` 的回调收到 `None`（Button 约定）。
- `app.config(ltk.Label).aim_id("count")` 是构建后访问控件的主通道：id 不存在抛 `KeyError`，类型不匹配抛 `TypeError`。

---

## example01 — 控件全览（16 个控件 + 运行时更新）

**主要内容**：全部控件的事件反馈写法、`Scroll` 包装长列表、图标按钮、`app.config(类型).aim_id` / `app.read` / `visible`、窗口 API、主题/明暗切换。

滑块实时驱动进度条（跨控件运行时更新）：

```python
def on_slider(value):
    app.config(ltk.ProgressBar).aim_id("progress").set(value)

ltk.Slider().id("slider").range(0, 1).steps(10).event(on_slider)
```

快速读值与运行时显隐：

```python
app.read("entry")                                     # 快速读当前值
app.config(ltk.Label).aim_id("toggle").visible(False) # 运行时隐藏
```

图标按钮（Pillow 可选，未安装时跳过演示）：

```python
ltk.Button()
    .image(ltk.Image(light_image=img, dark_image=img, size=(16, 16)))
    .compound("left")
```

Tips：

- 主体内容放进 `ltk.Scroll(ltk.Column(...))`，一屏放不下时自动滚动（v1 仅垂直）。
- 切换主题时颜色只对**新建控件**生效，所以示例用 `app.destroy()` + `main()` 循环真实重建窗口；明暗切换（`ltk.set_mode`）是实时的，无需重建。
- `app.read(name)` 只读不改，适合事件回调里快速取值；控件没有 `get()` 时会抛 `TypeError`。

---

## example02 — 布局与容器（fit / fill / weight 与各容器）

**主要内容**：Row / Column / ZStack / Scroll / Space / View / SplitPanel / Divider 的组合用法。

fill 按权重分配主轴剩余空间：

```python
ltk.Row().gap(8).width().fill().add(
    ltk.Button().text("A").fill(weight=1),
    ltk.Button().text("B").fill(weight=2),
    ltk.Button().text("C").fill(weight=1),
)
```

主轴与交叉轴居中：

```python
ltk.Row().gap(8).padding(8).width().fill().justify("center")  # 水平居中（主轴）
ltk.Column().gap(8).padding(8).align("center")                # 交叉轴居中（左右）
```

Space 弹性/固定 + Divider：

```python
ltk.Row().gap(8).padding(8).width().fill().add(
    ltk.Button().text("left"),
    ltk.Space(),              # 弹性：吃掉剩余空间
    ltk.Divider().vertical(),
    ltk.Space().width(30),    # 固定 30px 占位
    ltk.Button().text("right"),
)
```

ZStack 重叠与九宫格锚点：

```python
ltk.ZStack().width(380).height(180).add(
    ltk.Button().width().fill().height().fill().text("base"),
    ltk.Label().text("top-left").align("top-left"),
    ltk.Label().text("bottom-right").align("bottom-right"),
)
```

侧边栏 + View 分页与 SplitPanel 分栏：

```python
# 侧边栏按钮切换页面
def go(page):
    return lambda _: app.config(ltk.View).aim_id("pages").show(page)

# SplitPanel：纵向切割 = 左右分栏；面板约束跟在 add() 之后
ltk.SplitPanel().vertical()
    .add(ltk.Column(...)).min_width(140).max_width(320)
    .add(ltk.Column(...)).min_width(140)
```

Tips：

- `Row().width().fill()` 是布局高频写法：Row 默认 fit，要撑满父容器需显式 fill。
- `justify` 管主轴、`align` 管交叉轴；`.center()` 是两者一起。
- 弹性 `Space` 存在时，fill 子元素在主轴上会降级为自然尺寸，剩余空间交给 Space。

---

## example03 — 计算器（逻辑与 UI 分离的完整应用）

**主要内容**：把“纯逻辑”与“声明式 UI”分开写的完整应用；UI 只负责把按键转发给状态机并刷新显示。

按键转发 + 刷新：

```python
def on_press(key):
    calc.press(key)   # 纯逻辑状态机
    refresh()
```

显示区用 `StringVar` 绑定，逻辑变了自动刷新，无需手动改控件文本：

```python
expr_var = ltk.StringVar(value=calc.current)
ltk.Label().variable(expr_var).font(family="Arial", size=32, weight="bold")
```

按钮工厂：一行等宽按钮，fill 均分整行；配色用语义 token：

```python
def button_row(*buttons):
    return ltk.Row().width().fill().transparent().gap(8).add(*buttons)

make_button("÷", "blue", "blue_hover")
```

Tips：

- 计算模型（iOS 语境 `%`、`±`、AC/C 切换、结果续算等）全部在 `Calculator` 类里，与 Tk 无关，可单测（`tests/test_example03_calc.py`）。
- 按钮文字统一用 `.width().fill()` 均分整行，避免手写像素宽度。
- 语义 token（`"gray"` / `"blue"` / `"blue_hover"`）让配色跟随主题，而不是写死 hex。

---

## 后续新增示例的选入标准

- 覆盖不同的 API 面（布局、事件、值 API、运行时访问、数据控件等）；
- 可独立运行，不依赖文档之外的文件；
- 与 README「快速上手」内容不重复；
- 新增或重排示例时，同步更新本文的总览表与代码摘录。
