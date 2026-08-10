# Changelog

本项目所有重要变更都会记录在此文件中。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 修改 (Changed)

- 示例重构：`examples/` 收敛为 4 个——`example00` 快速上手（计数器）、`example01` 完整应用（计算器）、`example02` 控件全览（全部控件 + 统一 print 事件反馈 + 运行时更新 + 主题切换）、`example03` 布局与容器（全部容器原语，View 分页演示）；删除 `example04/05/06`，其内容并入 02/03。`docs/EXAMPLES.md` 由占位改为正式示例索引。

### 修复 (Fixed)

- `RadioButton` 事件回调与 `get()` 不再调用原生 `CTkRadioButton.get()`（customtkinter 6.0 中该方法不存在）：有共享变量时返回变量当前值，否则返回该单选按钮自身的 `value`；此前点击单选按钮会抛 `AttributeError`。
- `Application` 创建时清空 id 注册表，每个应用从空注册表开始：同一进程内销毁后重建窗口（如切换主题后重建）不再因重复 id 抛 `ValueError`。

## [0.13.0] - 2026-08-11

### 修改 (Changed)

- **破坏性变更**：运行时访问重构——移除 `app.get(name)` 与 `BaseWidget.config(类型)`；新增 `app.config(类型).aim_id(name)`（类型化主通道：缺 id 抛 `KeyError`、类型不匹配抛 `TypeError`）与 `app.read(name)`（快速读值，控件无 `get()` 时抛 `TypeError`）；`app.native(name)` / `app.ids()` 保留。示例 00/01/05/06 与文档同步迁移。

## [0.12.0] - 2026-08-10

### 新增 (Added)

- `View`（视图容器）：命名页面共享同一区域、同一时刻只显示一个；`.show(name)` 切换（构建前设默认页、构建后实时切换）、`.get()` 返回当前页名、`.event(cb)` 回传页名；**无内置选择器**（区别于 Tabview），切换由外部控件（侧边栏按钮 / SegmentedButton）驱动；页面构建一次、状态保留。新增 `examples/example06.py`（侧边栏 + View）。

## [0.11.0] - 2026-08-10

### 新增 (Added)

- 窗口：`center_window()`（窗口在屏幕居中，`size()` 后调用）、`icon(path)`（Windows `iconbitmap`）、`on_close(callback)`（`WM_DELETE_WINDOW` 钩子，回调内需自行 `destroy()`）。
- `Label.anchor(mode)`（文字在标签内对齐）与 `Button.compound(mode)`（图标+文字排布，配合 `.image()`）。
- `BaseWidget.visible(active)`：构建后运行时显隐（`grid`/`grid_remove`），所有控件与容器统一可用。

## [0.10.0] - 2026-08-10

### 新增 (Added)

- 统一值 API：所有值类控件新增 `get()` / `set()`（构建前=默认值、构建后=实时更新），Entry/Textbox/Treeview/Listbox 另提供 `clear()`；`Slider().set(v)` 补上初始值缺口，Treeview/Listbox 的 `set()` 支持运行时换数据；`set_value` / `value` 保留为等价写法。

## [0.9.1] - 2026-08-10

### 修改 (Changed)

- example01 重写为可用的 iOS 手感计算器示例：整体表达式求值（标准数学优先级）、iOS 语境 `%`、`±`、AC/C 切换、Del/AC、结果续算、10 位有效数字显示。

## [0.9.0] - 2026-08-10

### 新增 (Added)

- 语义 token 新增常用色：每个主题内置 `red / orange / yellow / green / cyan / blue / purple / black / white / gray`，并规则化生成 `*_hover`（深色主题变浅、浅色主题变深，HSL 亮度 ±12%）；`fg_color("blue")`、`ltk.color("red")`、`Tokens.green` 等直接可用。注意：token 名会覆盖同名 CSS 颜色字面量（如 `red`、`blue`）。

## [0.8.1] - 2026-08-10

### 新增 (Added)

- `Application` 窗口尺寸控制：`resizable(width, height)`、`min_size(w, h)`、`max_size(w, h)`、`fixed_size()`（固定窗口大小）。
- `Button.padding(n)`（映射 CTk `border_spacing` 内边距）与 `Button.fix_size()`（锁定显式尺寸）。

### 修复 (Fixed)

- 大字体撑大固定尺寸按钮：CTkButton 内部 grid 未关闭 propagate，文本请求尺寸覆盖显式宽高；`fix_size()` 在构建时关闭 `grid_propagate` 钉住尺寸。

## [0.8.0] - 2026-08-10

### 新增 (Added)

- **数据控件主题化**：`Treeview` / `Listbox` 保留原生控件（性能优先），构建时用 `native_theme_colors()` 调色板为每个实例生成唯一 ttk style（仿 SplitPanel 的 per-instance 模式）——Treeview 与滚动条经 `ttk.Style` 上色（表面/文字/边框/选中色），Listbox 为 tk 控件、同一调色板走控件选项（`bg`/`fg`/`selectbackground` 等）；切换主题或明暗后需重建窗口。
- **新组件（v0.7.0）**：
  - `SplitPanel`（原 PanedWindow，可拖拽分栏，`ttk.Panedwindow`）：链式 `add()` + 面板属性——`min_width/max_width`（纵向切割）、`min_height/max_height`（横向切割）、`transparent()`；方向按**切割线方向**定义（`vertical()` = 左右分栏、`horizontal()` = 上下分栏，`orientation()` 字符串形式保留）；最小/最大尺寸用 `sashpos` 拖动后回夹实现（ttk 无原生支持）；`sash_width()`、`proxy_sash()`（默认幽灵分隔条）；每实例 ttk style + 主题调色板缓存。
  - `Divider`（分隔线，CTkFrame 薄层）：`orientation()` 链式、`line_width()`；默认色取当前 CTk 主题 border（`ctk.ThemeManager`，语义 token 兜底）。
  - 新增 `examples/example04.py` 演示。
- **新组件（v0.6.0）**：`Canvas`（画布）——基于 `CTkCanvas`（`tk.Canvas` 子类，绘图性能一致）；`.draw(func)` 注册绘制回调（可多次，构建后按序执行，收到原生画布）；`.fg_color()` 映射为画布背景（tk `bg`）；交互通过 `.id()` + `app.native(id).bind(...)`。新增 `examples/example03.py` 演示。
- **渲染层解耦**：新增 `lazytkinter/renderer.py`（`Renderer` 协议 + `CTkRenderer`），成为包内唯一直接依赖 `customtkinter` 的模块；控件/容器改为“描述对象 → build → 渲染器”三层结构，为后续接入其他后端留好扩展点。
- **布局引擎 v2**：
  - 尺寸策略：`width` / `height` 支持 `int`（固定像素）、`"fit"`（包裹内容）、`"fill"`（撑满父容器）；链式写法 `.width().fill()` / `.height().fit()` / `.fill()`，无轴前缀的 `.fill()` / `.fit()` 作用于双轴。
  - 占比分配：`fill(weight=n)` 让多个 fill 子元素按 `n` 的比例分配主轴剩余空间（默认等分）。
  - 布局原语：`ZStack`（重叠 + 锚点）、`Spacer`（弹性弹簧，`.weight(n)`）、`Scroll`（包装单个子元素，v1 仅 `vertical`）、`Empty`（固定尺寸占位）。
  - 容器属性：`gap`（子元素间距）、`padding`（内边距，仅整数）、`align`（交叉轴）、`justify`（主轴 `start`/`center`/`end`）、`.center()`。
  - 窗口属性：`size('fill' / 'large' / 'medium' / 'small' / (w, h))`，以及 `padding` / `gap` / `align` / `justify` / `center()` 直接作用于根 `column()` / `row()`，避免根布局再包一层容器。
  - 容器构造子组件：`Row(btn, label)` 与 `.add(...)` 追加语义。
- **外观**：容器默认使用主题色背景（自带可见圆角），`transparent()` 显式透明；`fg_color()` 自定义背景色，`radius()` 设置圆角。
- **字体**：`font(family=..., size=..., weight=..., slant=..., underline=..., overstrike=...)` 关键字/字典形式，支持 IDE 自动补全；旧元组写法兼容。
- **测试**：新增纯逻辑单测与隐藏窗口冒烟用例（`tests/test_logic.py`、`tests/test_renderer.py`、`tests/test_smoke_gui.py`），无显示环境自动跳过冒烟。
- **打包与工程化**：新增 `pyproject.toml`（`pip install -e .` 一键安装并自动拉取 `customtkinter`）、`py.typed` 类型标记、GitHub Actions CI（Windows/Linux × Python 3.10–3.13 全矩阵自动运行测试）。
- **数据型控件**：新增 `Treeview`（`.columns([...]).rows([...])`）与 `Listbox`（`.items([...])`），基于 ttk/tk 原生控件并内建垂直滚动条，大列表从“每行一个控件”变为“单控件 + 数据”。
- **控件引用**：`.id("name")` 注册构建后的原生控件，`app.get(name)` / `app.ids()` 访问；`app.layout_tree()` 输出构建后的控件树（类名 + id），便于调试。
- **语义化主题 token**：新增 `ltk.color("token")` 与 `ltk.Tokens`；颜色 setter（`fg_color`/`bg_color`/`text_color`/`hover_color`/`border_color`/`progress_color` 等）支持 token 名并在构建时解析。

### 修改 (Changed)

- Treeview / Listbox 标注为**试验功能**：使用系统（ttk/tk）控件渲染，可能与 CTk 主题风格不完全统一；版本升至 v0.8.0。
- `Spacer` 与 `Empty` 合并为 `Space`：`Space()` 默认弹性（等价旧 `Spacer`，按 `weight` 分配剩余空间），显式 `width()` / `height()` 固定像素时变为刚性透明占位（等价旧 `Empty`）；固定尺寸的 `Space` 不再触发 fill 子元素降级，仅弹性 `Space` 生效；ZStack 中弹性 `Space` 抛 `ValueError`、固定尺寸可用；显式 `weight()` 与主轴固定尺寸同用抛 `ValueError`。
- 示例 `example00/01/02` 与 README 全面适配 v2 API；README 新增「布局 API 速查」章节。
- 示例移除 `sys.path.append` 临时路径 hack，安装包后可直接运行。
- **破坏性变更**：所有 `event()` 回调统一接收“当前值”——`Button` 收到 `None`，`CheckBox`/`RadioButton` 收到 `get()`，其余控件保持传值；示例同步更新。
- example00 改为计数器示例（`.id("count")` + `app.get("count").configure(...)` 验证运行时更新）；example02 的 Scroll 列表替换为 Treeview + Listbox 展示。
- `app.get()` / `registry.get()` 返回类型标注为 `tkinter.Widget`，消除 Pylance 对 `.configure` 等方法的类型报错。
- `app.get()` 现在返回**配置包装对象**而非原生控件：构建后仍可用链式 setter（`.text()` / `.fg_color()` / `.state()` 等）实时更新（内部自动转发到原生控件，不支持的选项静默跳过）；需要原生控件时用 `app.native(name)`。example00 计数器改为 `app.get("count").text(...)` 写法。
- 新增 `.config(类型)` 泛型收窄：`app.get("name").config(ltk.Label).text(...)` 通过运行时 `isinstance` 校验并返回对应控件类型，解决 Pylance 对具体控件方法的类型报错；类型不匹配抛 `TypeError`。
- `docs/ARCHITECTURE.md` 新增布局引擎 v2 章节。
- 主题加载改用 `logging`；找不到主题时 `set_theme` 抛 `ValueError`（原为 print 输出后继续）。
- 容器布局从双层 Frame 改为单层 Frame；容器 `build` 不再自我 grid，统一由父容器放置，消除重复 grid。
- 控件 `build(parent, *, width=None, height=None)` 支持尺寸覆盖参数，容器溢出裁剪在本地计算，不再修改子组件配置。

### 修复 (Fixed)

- Treeview 背景与数据控件滚动条主题色不生效：Windows 默认 ttk 主题 `vista` 忽略 `style.configure` 的颜色选项；改为每次创建 `Application` 时自动确保全局 ttk 主题为 `clam`（CustomTkinter 每次建窗都会重置 ttk 主题，需反复确认）。
- 容器固定宽/高被内容撑塌：`pack_propagate` 对 grid 布局无效，改为 `grid_propagate(False)`。
- `window padding` 产生可见边框：padding 改为作用于根布局槽，根帧铺满窗口。
- `Application.padding((h, v))` 元组形式此前因类型判断错误而静默失效。
- `ScrollableColumn` 漏过滤不支持的参数（`font` / `text_color` 等），现与 Row/Column 共用统一过滤。
- example01 按钮组未居中：`Row().align("center")` 是交叉轴（垂直）语义，水平居中需由父容器 `align` 决定。
- example02 主区域 Row 未撑满窗口导致右侧内容挤压：补 `.width().fill()`。
- `set_value("")` 不再被跳过（`if self._default_value:` 改为 `is not None`）。
- `values()` 不再持有外部列表引用（改为拷贝）。
- `ProgressBar.value()` 增加 0~1 范围校验，越界抛 `ValueError`。

### 删除 (Removed)

- `Spacer`、`Empty` 类与导出移除，由 `Space` 取代（破坏性变更）。
- 旧布局 API：`weight()`、`sticky()`、`row_span()`、`col_span()`、`margin()` / `margin_x()` / `margin_y()`、`spacing()`、`ScrollableColumn`、`window_size()`。
- 容器与窗口 `padding` 的元组形式（仅接受整数像素）。
- 容器默认透明背景（改为默认主题色，透明需显式 `transparent()`）。
