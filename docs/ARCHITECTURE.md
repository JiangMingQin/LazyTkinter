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

- `tests/test_logic.py`：纯逻辑单测（margin/padding 解析、溢出裁剪、参数过滤、构造子组件、单根布局守卫），不创建窗口。
- `tests/test_renderer.py`：用 FakeRenderer 注入验证 build 流程与参数收集，不创建窗口。
- 手动验收：三个示例在隐藏窗口下构建并自动关闭；ScrollableColumn 传 font/text_color 不再报错。

## 后续路线图（不在本分支）

1. 大列表性能：`ltk.Treeview` / `ltk.Listbox` 薄封装（数据型控件）。
2. 控件引用：`.id("name")` + `app.get("name")`，支持运行时更新。
3. 语义化主题 token 层。
4. 打包与工程化：`pyproject.toml`、CI。

## 分支流程

- 从 `main` 拉出 `refactor/three-layer-architecture`，分三次提交：文档 → 重构 → 测试。
- 未 push、未合并；确认稳定后由仓库 owner 决定合并。
