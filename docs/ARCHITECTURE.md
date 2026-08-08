# LazyTkinter 架构设计文档

> 分支：`refactor/three-layer-architecture`（尚未合并到 `main`）

## 背景与目标

LazyTkinter 的目标是用声明式语法快速构建美观的 tkinter 界面。原型阶段的核心验证点是“控件描述 + build 两阶段”的 DSL 手感。本分支在不改变这套 DSL 的前提下，把内部结构重构为三层：

1. **描述层**：`BaseWidget` 与各控件/容器类，只保存配置，不碰 Tk。
2. **布局层**：`Row` / `Column` / `ScrollableColumn` 负责排列子项。
3. **渲染层**：新增 `renderer.py`，是包内唯一直接依赖 `customtkinter` 的模块。

## 改前 vs 改后

| 维度 | 改前 | 改后 |
|---|---|---|
| 依赖方向 | base/widgets/containers/app 全部直接 import customtkinter | 只有 renderer.py import customtkinter |
| 控件创建 | 每个 build() 手写 ctk.CTkButton(...) | build() 收集参数后交给 renderer.create_widget(...) |
| 容器 | 每个容器两层 Frame，布局与 CTk 类绑死 | 单层 Frame，布局逻辑保留在容器内，Frame 创建走 renderer |
| 溢出裁剪 | build 时修改子组件配置（副作用） | 本地计算有效尺寸，通过 build 的 width/height 覆盖参数传入，不修改子对象 |
| 根布局 | column()/row() 可重复调用，静默覆盖/重叠 | 只允许一次根布局调用，重复调用抛 RuntimeError |
| 参数过滤 | Row/Column 过滤，ScrollableColumn 漏过滤 | 三容器共用 _frame_props 统一过滤 |
| 主题 | set_theme 用 print 输出、吞掉异常 | logging 输出，找不到主题抛 ValueError |
| 窗口访问 | Application 继承 ctk.CTk | Application 组合窗口对象，__getattr__ 转发，原 CTk 方法仍可用 |

## 模块依赖（改后）

```text
lazytkinter/
├── base.py          # 描述基类（纯 Python，无 Tk 依赖）
├── widgets.py       # 控件描述（无 Tk 依赖）
├── containers.py    # 容器 + 布局（无 Tk 依赖）
├── renderer.py      # Renderer 协议 + CTkRenderer（唯一依赖 customtkinter）
├── app.py           # Application / Theme / set_theme / set_mode
├── utils.py         # 变量与资源别名（从 renderer 转发）
└── themes/          # 内置主题 JSON
```

## 公开 API 与行为变化

- **保持不变**：全部链式 DSL（text/width/height/event/padding/spacing/add...）、`Application.window_*`、`ltk.Theme`、`set_theme`/`set_mode`、`__init__.py` 导出。
- **新增**：`Row(btn, label)` / `Column(...)` / `ScrollableColumn(...)` 支持构造参数直接传入子组件（README 原有示例从此可运行）；`.add()` 从整体替换改为追加。
- **行为变更（刻意）**：
  - `Application.column()/row()` 只能调用一次，重复调用抛 `RuntimeError`（原行为是静默覆盖/重叠）。
  - 找不到主题时 `set_theme` 抛 `ValueError`（原来是 print 后继续）。
  - `Application.padding((h, v))` 元组形式现在真正生效。
  - `ScrollableColumn.padding()` 从无效 no-op 变为生效。
- **内部**：控件 `build(parent, *, width=None, height=None)` 新增可选尺寸覆盖参数，供容器裁剪使用；`renderer.set_renderer()` 供测试注入假后端。

## 渲染器协议

```python
class Renderer:
    def create_window(self): ...
    def create_widget(self, kind, parent, props): ...
    def create_container(self, kind, parent, props): ...
    def set_theme(self, theme_name): ...
    def set_mode(self, mode): ...
```

`CTkRenderer` 是当前唯一实现；协议假设后端控件兼容 tkinter 的 grid/pack。后续接入 ttkbootstrap 或其他后端只需实现该协议。

## 测试策略

- `tests/test_logic.py`：纯逻辑单测（尺寸策略解析、align 校验与 sticky 映射、布局槽解析、ZStack 锚点、Window size 预设、Spacer/Scroll 校验），不创建窗口。
- `tests/test_renderer.py`：用 FakeRenderer 注入验证 build 流程与参数收集，不创建窗口。
- `tests/test_smoke_gui.py`：隐藏窗口冒烟用例（三个示例 + ZStack/Spacer/Scroll 场景），无显示环境自动跳过。

## 后续路线图（不在本分支）

1. 大列表性能：`ltk.Treeview` / `ltk.Listbox` 薄封装（数据型控件）。
2. 控件引用：`.id("name")` + `app.get("name")`，支持运行时更新。
3. 语义化主题 token 层。
4. 打包与工程化：`pyproject.toml`、CI。

## 布局引擎 v2（破坏性重构）

布局 v2 在 `feat/layout-v2` 分支上把公开布局 API 从 grid 概念（`weight` / `sticky` / `row_span` / `col_span` / `margin` / `spacing` / `ScrollableColumn`）替换为声明式原语，`main` 上的旧 API 不再保留。

### 新布局 API

- **尺寸策略**：所有控件与容器的 `width` / `height` 接受 `int`（固定像素）、`'fit'`（包裹内容）或 `'fill'`（撑满父容器）。默认 `'fit'`，例外：Column 宽度默认 `'fill'`，ZStack / Scroll 宽度与高度默认 `'fill'`。支持链式写法 `.width().fill()` / `.height().fit()`（无轴前缀的 `.fill()` / `.fit()` 作用于双轴），与字符串写法等价，便于 IDE 自动补全发现。
- **间距**：容器 `gap`（子元素之间）与 `padding`（内边距）只接受整数像素。
- **对齐**：Column 交叉轴 `align`（`left`/`center`/`right`，默认 `left`），Row 交叉轴 `align`（`top`/`center`/`bottom`，默认 `top`），ZStack 锚点 `align`（`center`/`top-left`/... 默认 `center`）。子元素可自带 `align` 覆盖容器默认。主轴分布用 `justify`（`start`/`center`/`end`，默认 `start`；`center`/`end` 会自动把主轴转为 `fill`）；`.center()` = `justify("center") + align("center")`。
- **外观**：容器默认透明背景，背景色由 `fg_color()` 显式设置（映射到 frame 填充色），圆角由 `radius()` 设置（映射到 `corner_radius`）。
- **新原语**：`Spacer`（弹性弹簧，`weight` 正整数，默认 1）、`ZStack`（同格重叠）、`Scroll`（包装单个子元素，v1 仅 `direction='vertical'`）、`Empty` 保留为固定尺寸占位。
- **Window**：`size('fill' | 'large' | 'medium' | 'small' | (w, h))`，`padding` 仅整数。

### 布局槽解析规则

容器把每个子元素解析为 grid 布局槽（纯函数，可单测）：

- fit → 槽 weight 0；fill → weight 1，多个 fill 平分剩余空间；容器内存在 Spacer 时，fill 在主轴上降为自然尺寸，Spacer 独占剩余空间。
- sticky = 交叉轴 align 映射 + 主轴/交叉轴 fill 拉伸；fill 与 align 同轴时 fill 优先。
- ZStack 全部子元素 grid 到同一格，锚点由子元素 `align`（缺省用容器默认）决定。
- `justify="center"` 在主轴两端各插入一个 weight=1 的隐式弹性槽，`justify="end"` 只在起始端插入；隐式弹性槽与显式 `Spacer` 同样触发“fill 降级”规则。

### 渲染层

布局 v2 不改动 Renderer 协议本身，只更新容器种类映射（`Column` / `Row` / `ZStack` / `Empty` / `Spacer` / `Scroll` / `RootFrame`），移除 `ScrollableColumn`。

## 分支流程

- 从 `main` 拉出 `refactor/three-layer-architecture`，分三次提交：文档 → 重构 → 测试。
- 未 push、未合并；确认稳定后由仓库 owner 决定合并。
