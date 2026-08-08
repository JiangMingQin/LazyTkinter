# Changelog

本项目所有重要变更都会记录在此文件中。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增 (Added)

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

### 修改 (Changed)

- 示例 `example00/01/02` 与 README 全面适配 v2 API；README 新增「布局 API 速查」章节。
- 示例移除 `sys.path.append` 临时路径 hack，安装包后可直接运行。
- `docs/ARCHITECTURE.md` 新增布局引擎 v2 章节。
- 主题加载改用 `logging`；找不到主题时 `set_theme` 抛 `ValueError`（原为 print 输出后继续）。
- 容器布局从双层 Frame 改为单层 Frame；容器 `build` 不再自我 grid，统一由父容器放置，消除重复 grid。
- 控件 `build(parent, *, width=None, height=None)` 支持尺寸覆盖参数，容器溢出裁剪在本地计算，不再修改子组件配置。

### 修复 (Fixed)

- 容器固定宽/高被内容撑塌：`pack_propagate` 对 grid 布局无效，改为 `grid_propagate(False)`。
- `window padding` 产生可见边框：padding 改为作用于根布局槽，根帧铺满窗口。
- `Application.padding((h, v))` 元组形式此前因类型判断错误而静默失效。
- `ScrollableColumn` 漏过滤不支持的参数（`font` / `text_color` 等），现与 Row/Column 共用统一过滤。
- example01 按钮组未居中：`Row().align("center")` 是交叉轴（垂直）语义，水平居中需由父容器 `align` 决定。
- example02 主区域 Row 未撑满窗口导致右侧内容挤压：补 `.width().fill()`。

### 删除 (Removed)

- 旧布局 API：`weight()`、`sticky()`、`row_span()`、`col_span()`、`margin()` / `margin_x()` / `margin_y()`、`spacing()`、`ScrollableColumn`、`window_size()`。
- 容器与窗口 `padding` 的元组形式（仅接受整数像素）。
- 容器默认透明背景（改为默认主题色，透明需显式 `transparent()`）。
