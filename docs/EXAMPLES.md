# EXAMPLES.md 示例索引 / Examples Index

> 4 个可运行示例覆盖全部公开 API，按教程顺序排列（example03 计算器为压轴）。讲解只写"关键点"，完整方法签名见 [API_REFERENCE.md](API_REFERENCE.md)，布局规则见 [LAYOUT.md](LAYOUT.md)。

## 示例总览 / Overview

| 编号 | 名称 | 一句话定位 | 演示的 API | 运行命令 |
| --- | --- | --- | --- | --- |
| example00 | 快速上手·计数器 | 最小可运行程序 | `Application` / `set_theme` / `Label` / `Button` / `event` / `.id()` + `app.config(类型).aim_id()` | `python examples/example00.py` |
| example01 | 控件全览 | 全部控件与事件反馈写法 | 16 个控件、统一 `print` 回调、`Scroll`、`CTkImage` + `compound`、运行时更新（`app.config(类型).aim_id()` / `app.read()` / `visible()`）、窗口 API、主题切换 | `python examples/example01.py` |
| example02 | 布局与容器 | 全部容器原语 | `Row` / `Column` / `ZStack` / `Scroll` / `Space` / `View` / `SplitPanel` / `Divider`、fit/fill/weight、gap/padding/align/justify | `python examples/example02.py` |
| example03 | 完整应用·计算器 | 逻辑与 UI 分离的完整小应用（压轴） | 布局组合（`Column`/`Row`/`fill`/`weight`）、`StringVar`、事件、语义 token 配色 | `python examples/example03.py` |

## example00 — 快速上手（计数器）

- 目标：十几行代码出一个可交互窗口。
- 关键点：`app.size(...)` / `window_title()` / `center()` 链式配置；`.id("count")` 注册控件；点击回调里用 `app.config(ltk.Label).aim_id("count").text(...)` 实时更新。

## example01 — 控件全览（Widget Gallery）

- 目标：一个窗口看完所有控件，并示范"事件反馈怎么写"。
- 关键点：每个控件都带 `.id()`；所有 `event()` 回调统一 `print("[控件名] ...")` 输出，与 API_REFERENCE 的事件约定表一一对应；Entry / Textbox / ProgressBar 等无事件的控件用 `app.read()` / `config(类型).aim_id()` 演示读取与更新；Slider 拖动实时驱动 ProgressBar；顶部工具条演示 `set_theme` / `set_mode`——其中明暗切换实时生效，而 **CTk 颜色主题只对新建控件生效，所以主题切换会销毁并重建整个窗口**（示例把 UI 构建抽成可重入函数）；底部面板演示 `visible()` / `on_close()` / `center_window()`。

## example02 — 布局与容器（Layout & Containers）

- 目标：一个窗口看完所有容器原语，页面切换本身由 `View` 驱动。
- 关键点：基础布局页演示 fit/fill/weight、gap/padding/align/justify、`Space`（弹性/固定）与 `Divider`；层叠滚动页演示 `ZStack` 九宫格锚点与 `Scroll`；分栏页演示 `SplitPanel` 纵/横两种切割与 min/max 约束。

## example03 — 完整应用（计算器）

- 目标：展示"逻辑与 UI 分离"的项目级写法，是完整应用的范本，也是示例合集的压轴。
- 关键点：求值与按键状态机是纯函数，可脱离窗口单测（见 `tests/test_example03_calc.py`）；UI 只负责按键分发与显示；`Row().fill(weight=1)` 实现等宽按钮组；按钮配色用语义 token（数字 `surface_alt`、功能键 `gray`、运算符 `blue` + `blue_hover`）。
