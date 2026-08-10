# LazyTkinter API 速查（API Reference）

> 本文档是 LazyTkinter 公开 API 的完整速查表，以当前源码为准（版本 0.13.0）。
> 布局规则的详细讲解见 [LAYOUT.md](LAYOUT.md)，整体架构见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 通用约定

- 所有 setter 都返回 `self`，可以无限链式调用：

  ```python
  ltk.Button().text("OK").width(100).event(on_click)
  ```

- **构建前 / 构建后**：布局与外观属性（`width`、`align`、`fg_color`、`font` 等）在 `app.run()` 之前设置；构建后通过 `.id("name")` + `app.config(类型).aim_id("name")` 类型化访问，继续链式调用即可实时更新，原生控件不支持的选项会被静默跳过。
- **事件约定**：`event(callback)` 的回调统一接收“当前值”——`Button` 收到 `None`；`Switch` / `CheckBox` / `RadioButton` 收到选中值；`Slider` / `SegmentedButton` / `ComboBox` / `OptionMenu` 收到当前值；`Treeview` 收到选中的行元组；`Listbox` 收到选中的项；`View` 收到切换后的页名。
- **值 API**：`get()` 读当前值，`set(v)` 写值（构建前 = 默认值，构建后 = 实时生效），`clear()` 清空（仅文本/数据类）。
- 颜色入参支持语义 token 名（如 `"primary"`），构建时解析为当前主题色。

## 公共方法（所有控件与容器）

所有组件继承自 `BaseWidget`，以下方法通用：

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `id(name)` | `name: str` | 注册 id，之后可用 `app.config(类型).aim_id(name)` 类型化访问、`app.read(name)` 快速读值、`app.native(name)` 获取原生控件 |
| `width(w=None)` | `int` / `"fit"` / `"fill"` / 无参 | 固定像素、包裹内容或撑满父容器；无参调用标记宽度轴，让后续 `.fill()` / `.fit()` 只作用于宽度 |
| `height(h=None)` | 同上 | 高度版本的 `width()` |
| `fill(weight=None)` | `weight: int` | 把（待定轴或双轴）设为 `fill`；`weight=n` 表示按 n 份参与主轴剩余空间分配（仅 Row/Column 主轴 fill 生效） |
| `fit()` | — | 把（待定轴或双轴）设为 `fit` |
| `radius(r)` | `r: int` | 圆角（映射 `corner_radius`） |
| `fg_color(color)` | 颜色或 token | 前景/主色（控件上通常是主色，容器上是背景色） |
| `bg_color(color)` | 颜色或 token | 背景色 |
| `text_color(color)` | 颜色或 token | 文字颜色 |
| `font(...)` | `family` / `size` / `weight` / `slant` / `underline` / `overstrike` | 关键字或字典形式，兼容旧元组与字体对象；非法键或值抛 `ValueError` |
| `state(state)` | `"normal"` / `"disabled"` | 控件状态 |
| `cursor(cursor)` | `str` | 鼠标样式 |
| `visible(active=True)` | `bool` | 构建后运行时显隐（`grid` / `grid_remove`）；构建前调用抛 `ValueError` |
| `align(a)` | `str` | 子元素在父容器中的对齐覆盖：Column 子元素 `left/center/right`，Row 子元素 `top/center/bottom`，ZStack 子元素支持九宫格锚点 |

## 基础组件

### Button

基于 `CTkButton`，用于触发即时动作。

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `text(text="Button")` | `str` | 按钮文字 |
| `event(command)` | 回调 | 点击回调，收到 `None` |
| `hover_color(color)` | 颜色或 token | 悬停色 |
| `border(width, color=None)` | `int`, 颜色 | 边框宽度与颜色 |
| `image(img)` | `CTkImage` | 图标 |
| `compound(mode)` | `top` / `bottom` / `left` / `right` / `center` | 图标与文字的排布方式（配合 `image()`） |
| `padding(n)` | `int` | 文字内边距（映射 CTk `border_spacing`） |
| `fix_size(active=True)` | `bool` | 锁定显式宽高，防止大字体撑大（需先设置 `width()` / `height()`） |

### Label

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `text(text="Label")` | `str` | 标签文字 |
| `variable(var)` | 变量 | 绑定 `StringVar` 等变量，联动更新 |
| `justify(mode)` | `"left"` / `"center"` / `"right"` | 多行文字的对齐 |
| `wrap_length(length)` | `int` | 换行宽度（像素） |
| `image(img)` | `CTkImage` | 图片 |
| `anchor(mode)` | tk 锚点 | 文字在标签内的对齐（`w` 左对齐、`center` 居中、`e` 右对齐等） |

### Entry

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `placeholder_text(text="Entry")` | `str` | 占位提示文字 |
| `show(char)` | `str` | 掩码字符（密码框：`show("*")`） |
| `border(width, color=None)` | `int`, 颜色 | 边框宽度与颜色 |
| `variable(var)` | 变量 | 绑定变量 |
| `get()` | — | 当前文本 |
| `set(text)` | `str` | 写文本（构建前 = 默认值，构建后 = 实时更新） |
| `clear()` | — | 清空（等价 `set("")`） |

### Textbox

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `border(width, spacing=None)` | `int`, `int` | 边框宽度与内边距 |
| `wrap(mode)` | `"char"` / `"word"` / `"none"` | 换行模式 |
| `scrollbar(active)` | `bool` | 是否启用内建滚动条（默认开启） |
| `get()` | — | 全文内容（去掉末尾换行） |
| `set(text)` | `str` | 写内容（构建前 = 默认值，构建后 = 实时更新） |
| `clear()` | — | 清空 |

### Canvas

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `draw(func)` | 回调 | 注册绘制回调，构建后按序执行，回调收到原生画布；可多次注册 |

> 基于 `CTkCanvas`（`tk.Canvas` 子类，绘图性能一致）；`.fg_color()` 映射为画布背景；交互通过 `.id()` + `app.native(id).bind(...)`。

## 选择组件

### Switch

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `text(text="")` | `str` | 开关旁的文字 |
| `event(command)` | 回调 | 切换回调，收到当前值 |
| `values(on_val, off_val)` | 任意 | 自定义开/关对应的值 |
| `variable(var)` | 变量 | 绑定变量 |
| `progress_color(color)` | 颜色或 token | 开启时的填充色 |
| `get()` / `set(value)` | — | 读当前值 / 选中或取消（构建前 = 默认状态，构建后 = 实时更新） |

### CheckBox

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `text(text)` | `str` | 勾选框旁的文字 |
| `event(command)` | 回调 | 勾选回调，收到当前值 |
| `variable(var)` | 变量 | 绑定变量 |
| `values(on_val, off_val)` | 任意 | 自定义勾选/未勾选对应的值 |
| `get()` / `set(value)` | — | 读当前值 / 勾选或取消 |

### RadioButton

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `text(text)` | `str` | 选项文字 |
| `value(val)` | 任意 | 该选项的值 |
| `variable(var)` | 变量 | 共享同一个变量即组成单选组 |
| `event(command)` | 回调 | 选中回调，收到当前值 |
| `radiobutton_width(rw=20)` | `int` | 圆点宽度 |
| `radiobutton_height(rh=20)` | `int` | 圆点高度 |
| `get()` / `set(value)` | — | 读组内选中值 / 选中匹配值的选项 |

### SegmentedButton

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `values(values)` | `list` | 选项列表（内部拷贝） |
| `set_value(val)` | `str` | 设置选中项（构建前 = 默认值，构建后 = 实时更新） |
| `set(val)` | `str` | `set_value` 的别名 |
| `get()` | — | 当前选中项（未显式设置时默认第一个） |
| `event(command)` | 回调 | 切换回调，收到选中项 |

### ComboBox

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `values(values)` | `list` | 下拉选项 |
| `set_value(val)` | `str` | 设置当前值（构建前 = 默认值，构建后 = 实时更新） |
| `set(val)` | `str` | `set_value` 的别名 |
| `get()` | — | 当前值 |
| `event(command)` | 回调 | 选择回调，收到当前值 |

### OptionMenu

方法与 `ComboBox` 相同（`values` / `set_value` / `set` / `get` / `event`）。

## 数值组件

### Slider

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `range(start, end)` | `float` ×2 | 取值范围（默认 0~1） |
| `steps(n)` | `int` | 离散步数（不设置则为平滑滑动） |
| `variable(var)` | 变量 | 绑定变量 |
| `event(command)` | 回调 | 滑动回调，收到当前值 |
| `orientation(orient)` | `"horizontal"` / `"vertical"` | 方向（默认水平） |
| `button_color(color)` | 颜色或 token | 滑块颜色 |
| `progress_color(color)` | 颜色或 token | 进度色 |
| `button_hover_color(color)` | 颜色或 token | 滑块悬停色 |
| `get()` / `set(value)` | — | 读当前值 / 设值（构建前 = 初始值，构建后 = 实时更新） |

### ProgressBar

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `orientation(orient)` | `"horizontal"` / `"vertical"` | 方向（默认水平） |
| `mode(mode)` | `"determinate"` / `"indeterminate"` | 模式（默认 determinate） |
| `value(val)` | `float` | 进度 0~1（默认 0.5；越界抛 `ValueError`） |
| `set(val)` | `float` | `value()` 的别名 |
| `get()` | — | 当前进度 |

## 数据组件（试验功能）

> 试验功能：使用 ttk/tk **原生控件**渲染，性能优先，但可能与 CTk 主题风格不完全统一；应用创建时自动把全局 ttk 主题切到 `clam`；切换主题或明暗后需重建窗口生效。

### Treeview

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `columns(columns)` | `list` | 列头（每个表头同时作为列 id） |
| `rows(rows)` | `list[tuple]` | 数据行 |
| `event(command)` | 回调 | 选中回调，收到选中的行元组 |
| `get()` | — | 当前选中的行元组（未选中为 `None`） |
| `set(rows)` | `list[tuple]` | 运行时替换数据 |
| `clear()` | — | 清空所有行 |

### Listbox

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `items(items)` | `list` | 列表项 |
| `event(command)` | 回调 | 选中回调，收到选中的项 |
| `get()` | — | 当前选中的项（未选中为 `None`） |
| `set(items)` | `list` | 运行时替换数据 |
| `clear()` | — | 清空所有项 |

## 布局容器

`Row` / `Column` 的布局规则见 [LAYOUT.md](LAYOUT.md)，这里只列方法签名。

### Row / Column

| 方法 | 说明 |
| --- | --- |
| `Row(*children)` / `Column(*children)` | 构造时直接传入子元素 |
| `add(*args)` | 追加子元素 |
| `gap(n)` | 主轴相邻子元素间距（非负整数） |
| `padding(n)` | 内边距（非负整数） |
| `align(a)` | 交叉轴对齐：Column `left/center/right`（默认 `left`），Row `top/center/bottom`（默认 `top`） |
| `justify(v)` | 主轴分布：`start/center/end`（默认 `start`；`center`/`end` 自动把主轴转 `fill`） |
| `center()` | = `justify("center") + align("center")` |
| `transparent(val=True)` | 透明背景（默认是主题色背景） |

### ZStack

`ZStack(*children)`、`add(*args)`、`align(a)`（九宫格锚点，默认 `center`）、`padding(n)`、`transparent(val=True)`。无 `gap` / `justify`；弹性 `Space` 会抛 `ValueError`。

### Space

| 方法 | 说明 |
| --- | --- |
| `Space()` | 默认弹性弹簧：按 `weight` 权重吃容器主轴剩余空间 |
| `weight(w)` | 弹性权重（正整数，默认 1） |
| `width(n)` / `height(n)` | 显式固定尺寸后变为刚性透明占位 |

`weight()` 与主轴固定尺寸同用抛 `ValueError`。

### Scroll

| 方法 | 说明 |
| --- | --- |
| `Scroll(child)` | 恰好包装一个子元素（如 `Scroll(Column(...))`） |
| `direction(d)` | 滚动方向，v1 仅支持 `"vertical"` |
| `transparent(val=True)` | 透明背景（默认主题色） |

默认双轴 `fill`。

### View

| 方法 | 说明 |
| --- | --- |
| `View(("name", page), ...)` | 构造时传入 `(页名, 页面)` 对 |
| `add(name, page)` | 追加命名页面（页名不可重复） |
| `show(name)` | 显示指定页（构建前 = 设默认页，构建后 = 实时切换） |
| `get()` | 当前显示的页名 |
| `event(command)` | 页面切换回调，收到页名 |
| `transparent(val=True)` | 透明背景 |

> 无内置选择器（区别于 Tabview），切换由外部控件驱动；页面构建一次、切换间状态保留；默认显示第一个页面。

### SplitPanel

| 方法 | 说明 |
| --- | --- |
| `SplitPanel(*children)` / `add(*args)` | 添加面板（至少两个） |
| `min_width(v)` / `max_width(v)` | **最后一个**面板的宽度约束（纵向切割 = 左右分栏时用） |
| `min_height(v)` / `max_height(v)` | **最后一个**面板的高度约束（横向切割 = 上下分栏时用） |
| `transparent(active=True)` | 最后一个面板透明 |
| `vertical()` / `horizontal()` | 切割线方向：`vertical()` = 竖线左右分栏，`horizontal()` = 横线上下分栏 |
| `orientation(orient=None)` | 字符串形式 `"vertical"` / `"horizontal"`；无参调用供链式 `.orientation().vertical()` |
| `sash_width(w)` | 分隔条厚度 |
| `proxy_sash(active=True)` | 幽灵分隔条（拖动显示预览、松开才落位） |

> 基于 `ttk.Panedwindow`，min/max 在拖动结束后用 `sashpos` 自动回夹；构建时从当前 CTk 主题取色；切换主题或明暗后需重建窗口生效。

### Divider

| 方法 | 说明 |
| --- | --- |
| `orientation(orient=None)` | `"horizontal"` / `"vertical"`（无参调用供链式 `.orientation().vertical()`） |
| `horizontal()` / `vertical()` | 快捷设置方向 |
| `line_width(n)` | 线粗细（正整数） |

默认水平，颜色取当前主题 border（可用 `fg_color()` 覆盖）。

## 值 API 覆盖矩阵

| 控件 | get | set | clear | set_value / value |
| --- | --- | --- | --- | --- |
| Entry | ✓ | ✓ | ✓ | — |
| Textbox | ✓ | ✓ | ✓ | — |
| Switch | ✓ | ✓ | — | — |
| CheckBox | ✓ | ✓ | — | — |
| RadioButton | ✓ | ✓ | — | — |
| Slider | ✓ | ✓ | — | — |
| ProgressBar | ✓ | ✓（=`value`） | — | `value()` |
| ComboBox | ✓ | ✓ | — | `set_value()` |
| OptionMenu | ✓ | ✓ | — | `set_value()` |
| SegmentedButton | ✓ | ✓ | — | `set_value()` |
| Treeview | ✓（选中行） | ✓（换数据） | ✓ | — |
| Listbox | ✓（选中项） | ✓（换数据） | ✓ | — |

## 窗口与应用（Application）

| 方法 | 参数 | 说明 |
| --- | --- | --- |
| `window_title(title)` | `str` | 窗口标题 |
| `size(size)` | `"fill"` / `"large"` / `"medium"` / `"small"` / `(w, h)` | 窗口尺寸（`fill` = 最大化） |
| `resizable(width, height)` | `bool` ×2 | 是否可缩放 |
| `min_size(w, h)` / `max_size(w, h)` | `int` ×2 | 最小 / 最大尺寸 |
| `fixed_size()` | — | 等价 `resizable(False, False)` |
| `center_window()` | — | 窗口屏幕居中（在 `size()` 之后调用） |
| `icon(path)` | `str` | 窗口图标（Windows 用 `.ico`） |
| `on_close(callback)` | 回调 | 关闭钩子（`WM_DELETE_WINDOW`），回调内需自行 `destroy()` |
| `padding(n)` | `int` | 根布局内边距 |
| `gap(n)` | `int` | 根布局子元素间距 |
| `align(v)` | `str` | 根布局交叉轴对齐：`column()` 用 `left/center/right`，`row()` 用 `top/center/bottom` |
| `justify(v)` | `"start"` / `"center"` / `"end"` | 根布局主轴分布 |
| `center()` | — | 根布局双轴居中 |
| `column(*args)` / `row(*args)` | 子元素 | 设置根布局，只能调用一次，重复调用抛 `RuntimeError` |
| `run()` | — | 构建并进入主循环 |
| `config(cls)` | 控件类型 | 开始类型化访问链：`app.config(ltk.Entry).aim_id("e")` |
| `aim_id(name)` | `str` | 在 `config(cls)` 返回的选择器上调用：按 id 返回类型为 `cls` 的配置包装；id 不存在抛 `KeyError`，类型不匹配抛 `TypeError` |
| `read(name)` | `str` | 快速读值：调用该 id 的 `get()` 并返回结果；控件没有 `get()` 时抛 `TypeError` |
| `native(name)` | `str` | 按 id 返回原生控件 |
| `ids()` | — | 所有已注册 id |
| `layout_tree()` | — | 构建后的控件树（调试用） |

模块级 API：`ltk.set_theme(theme_name)`（内置主题或主题名，找不到抛 `ValueError`）、`ltk.set_mode("light" / "dark" / "system")`、`ltk.Theme`（内置主题枚举）。

## 变量与工具

| 名称 | 说明 |
| --- | --- |
| `StringVar` / `IntVar` / `DoubleVar` / `BooleanVar` | CustomTkinter 变量（re-export，无需额外导入 customtkinter） |
| `Image` | `CTkImage`（配合 `.image()` 使用） |
| `Font` | `CTkFont`（配合 `.font()` 使用） |
| `select_file(**kwargs)` | `filedialog.askopenfilename` |
| `select_directory(**kwargs)` | `filedialog.askdirectory` |

## 语义化主题 token

颜色 setter 与 `ltk.color()` 都支持 token 名：

| 类别 | token |
| --- | --- |
| 语义色 | `primary` / `primary_hover` / `surface` / `surface_alt` / `text` / `text_secondary` / `border` / `success` / `danger` / `warning` / `bg` |
| 常用色 | `red` / `orange` / `yellow` / `green` / `cyan` / `blue` / `purple` / `black` / `white` / `gray`（各有 `*_hover`：深色主题自动变浅、浅色主题自动变深） |
| 常量 | `radius`（默认 10）、`spacing`（默认 8） |

用法：

```python
ltk.Button().fg_color("primary")     # 语义 token
ltk.Label().text_color("red")        # 常用色 token
ltk.color("primary")                 # 读取当前主题 token 值
ltk.Tokens.radius                    # 属性式访问常量
```

注意：token 名（如 `red`、`blue`）会覆盖同名 CSS 颜色字面量。token 表覆盖 7 个内置枚举主题；通过文件名加载 `nord-theme` 时 token 表回退到默认 catppuccin。
