# 🦥 LazyTkinter

![Status](https://img.shields.io/badge/Status-Experimental-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

**LazyTkinter** 是一个基于 CustomTkinter 的 Python 界面库，通过声明式编程简化 Tkinter 的布局与开发流程：去除了手写 `grid` / `pack`，用 `Row` / `Column` / `ZStack` 容器配合 `fit` / `fill` 尺寸策略、`gap` / `padding` 间距和 `Space` 占位，像搭积木一样搭界面。
> LazyTkinter is a Python UI library built on CustomTkinter that simplifies layout and development via declarative programming, replacing hand-written `grid` / `pack` with `Row` / `Column` / `ZStack` containers, `fit` / `fill` size policies, `gap` / `padding` spacing and `Space` placeholders.

**目标受众**：适合希望快速开发简单 GUI 应用的开发者，尤其是觉得命令式编程繁琐、但又不想使用 PySide 或 QT 等大型框架的用户。
> Ideal for developers who want to build simple GUI applications quickly — especially those who find imperative programming cumbersome but don't want heavyweight frameworks like PySide or QT.

![light](assets/gruvbox-light.png)

---

## ⚠️ 免责声明 / Disclaimer

**这是一个实验性项目。**
**This is an experimental project.**

这是我个人开发的第一个开源项目，LazyTkinter 主要用于探索声明式 UI 在 Python 中的实现。

- ❌ **不保证**长期维护或更新；日常更新随缘，仅在出现严重 bug 且收到实际反馈时才会投入维护。
- ❌ **不建议**在生产环境中使用。
- ✅ **欢迎**学习、Fork 或作为灵感参考。

如果你对项目感兴趣，可以关注后续更新~

---

## 📌 项目现状与兼容性 / Status & Compatibility

| 项目 | 说明 |
| --- | --- |
| 当前版本 | 0.13.0（变更记录见 [CHANGELOG.md](CHANGELOG.md)） |
| 项目状态 | 实验性（Experimental），不建议生产环境使用 |
| Python | >= 3.10 |
| 平台 | Windows / Linux（GitHub Actions 全矩阵 CI） |
| 依赖 | `customtkinter>=5.2.0`（安装时自动拉取） |
| 试验功能 | `Treeview` / `Listbox`（原生控件渲染，可能与 CTk 主题风格不完全统一；切换主题或明暗后需重建窗口生效） |
| 已实现 | 声明式布局 v2、`.id()` + `app.config(类型).aim_id(名字)` 类型化访问、`app.read()` 快速读值、统一值 API、语义化主题 token、数据控件、`View` / `SplitPanel` / `Scroll` 等 |

---

## ✨ 核心特色 / Core Features

- **声明式布局（Declarative Layout）**：`Row` / `Column` / `ZStack` 容器 + `fit` / `fill` 尺寸策略 + `gap` / `padding` / `align` / `justify`，无需理解 `grid` 的 row/column/span。

  ```python
  ltk.Column().gap(8).padding(16).add(
      ltk.Row().width().fill().add(
          ltk.Button().text("OK").fill(weight=1),
          ltk.Button().text("Cancel").fill(weight=1),
      ),
      ltk.Label().text("done"),
  )
  ```

- **链式 API + 统一值 API（Fluent & Unified Value API）**：每个 setter 返回自身，一行配置到底；`get()` / `set()` / `clear()` 全组件统一；`.id()` + `app.config(类型).aim_id(名字)` 让构建后仍可类型安全地实时更新。

  ```python
  ltk.Button().text("add").width(100).event(on_click).id("btn")
  app.config(ltk.Button).aim_id("btn").text("added")  # 构建后继续链式更新
  app.config(ltk.Entry).aim_id("entry").set("hello")  # 统一值 API（写）
  app.read("entry")                        # 统一值 API（快速读）
  ```

- **内置主题 + 语义化 token（Themes & Semantic Tokens）**：Catppuccin / Gruvbox / Dracula / EVA02 与 CustomTkinter 原生主题开箱即用；颜色写语义名（如 `"primary"`），`ltk.color()` / `ltk.Tokens` 可读取当前值。

  ```python
  ltk.set_theme(ltk.Theme.Catppuccin)
  ltk.Button().fg_color("primary").text_color("white")
  ltk.color("primary")   # '#cba6f7'
  ```

- **轻量快速上手（Lightweight & Fast Start）**：只依赖 CustomTkinter，无重量级框架；安装后十几行就能出一个窗口。

  ```python
  app = ltk.Application()
  app.size("small").center().column(ltk.Button().text("Hi"))
  app.run()
  ```

---

## 📦 快速安装 / Quick Install

克隆仓库后安装（自动拉取 `customtkinter` 依赖）：

```bash
git clone https://github.com/JiangMingQin/lazytkinter.git
cd lazytkinter
pip install -e .          # 开发模式安装（含依赖）
```

也可以直接 `pip install .` 普通安装。

---

## 🚀 快速上手 / Quick Start

一个完整的计数器示例（也见 `examples/example00.py`）：

```python
import lazytkinter as ltk


def main() -> None:
    ltk.set_theme(ltk.Theme.Gruvbox)  # set theme

    app = ltk.Application()
    count = 0

    def on_click(value=None):
        nonlocal count
        count += 1
        app.config(ltk.Label).aim_id("count").text(f"{count}")

    app.size("small").window_title("Counter").center().gap(10).column(
        ltk.Label().id("count").text("0").font(family="Arial", size=28, weight="bold"),
        ltk.Button().text("add count").event(on_click),
    )

    app.run()


if __name__ == "__main__":
    main()
```

运行后你会看到这样的窗口，点击按钮计数递增：

![example00](assets/example00.png)

---

## 🧩 组件速查表 / Widget Quick Reference

| 分类 | 组件 | 说明 |
| --- | --- | --- |
| 布局 | `Row` | 水平排列子元素 |
| 布局 | `Column` | 垂直排列子元素 |
| 布局 | `ZStack` | 重叠层叠 + 九宫格锚点 |
| 布局 | `Space` | 弹性 / 固定占位 |
| 布局 | `Scroll` | 滚动包装（v1 仅垂直） |
| 布局 | `View` | 命名页面容器（无内置选择器） |
| 布局 | `SplitPanel` | 可拖拽分栏 |
| 布局 | `Divider` | 分隔线 |
| 基础 | `Button` | 按钮 |
| 基础 | `Label` | 文本标签 |
| 基础 | `Entry` | 单行输入框 |
| 基础 | `Textbox` | 多行文本框 |
| 基础 | `Canvas` | 画布 |
| 选择 | `Switch` | 开关 |
| 选择 | `CheckBox` | 复选框 |
| 选择 | `RadioButton` | 单选按钮 |
| 选择 | `SegmentedButton` | 分段选择按钮 |
| 选择列表 | `ComboBox` | 下拉选择框 |
| 选择列表 | `OptionMenu` | 下拉菜单 |
| 数值 | `Slider` | 滑块 |
| 数值 | `ProgressBar` | 进度条 |
| 数据（试验） | `Treeview` | 表格（原生控件，性能优先） |
| 数据（试验） | `Listbox` | 列表（原生控件，性能优先） |

完整方法签名与示例见 [API_REFERENCE.md](docs/API_REFERENCE.md)。

---

## 🎨 内置主题 / Built-in Themes

- `ltk.Theme.Catppuccin`（Catppuccin Mocha）——温馨且现代。
  ![Catppuccin](assets/catppucin.png)
- `ltk.Theme.Gruvbox` —— 经典复古风格。
  ![Gruvbox](assets/gruvbox-dark.png)
- 另有 `ltk.Theme.Dracula`、`ltk.Theme.EVA02` 与 CustomTkinter 原生 `Blue` / `Green` / `DarkBlue`，共 7 个枚举。
- 附带 `nord-theme.json`：可用 `ltk.set_theme("nord-theme")` 按文件名加载，但 `Theme` 枚举暂未提供 `Nord`。

---

## 📖 布局小抄 / Layout Cheat Sheet

```python
ltk.Button().width().fill(weight=2)           # 与兄弟控件按 2 份分剩余宽度
ltk.Row().width().fill().justify("center")    # 主轴（水平）居中
ltk.Column().add(ltk.Button(), ltk.Space(), ltk.Button())   # 上下弹开
```

> 完整规则（主轴/交叉轴、fill 降级、隐式 Space、常见误区等）见 [LAYOUT.md](docs/LAYOUT.md)。

---

## 📂 项目结构 / Project Structure

```Plaintext
lazytkinter/
├── __init__.py      # 统一导出接口
├── app.py           # Application / Theme / set_theme / set_mode
├── base.py          # BaseWidget 公共属性与链式 API
├── widgets.py       # 基础控件描述
├── containers.py    # Row / Column / ZStack / Space / Scroll / View / SplitPanel
├── data_widgets.py  # Treeview / Listbox
├── renderer.py      # Renderer 协议 + CTkRenderer（唯一依赖 customtkinter）
├── tokens.py        # 语义化主题 token
├── registry.py      # id 注册表
├── utils.py         # StringVar / Image / Font / 文件对话框
└── themes/          # 内置主题 JSON
```

---

## 📚 文档导航 / Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) —— 架构设计与布局引擎说明
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) —— 全部公开组件 API 速查
- [docs/LAYOUT.md](docs/LAYOUT.md) —— Row / Column 布局规则专题
- [docs/EXAMPLES.md](docs/EXAMPLES.md) —— 可运行示例索引（4 个示例覆盖全部 API）

---

## 🤝 贡献 / Contributing

欢迎 Fork 本项目并根据自己的想法进行修改！如果你发现 Bug 或有改进建议，可以通过以下方式参与：

1. **提交 Issue**：描述问题或建议改进的功能。
2. **提交 PR**：修复 Bug 或添加新功能。请确保代码风格一致，并附上测试用例。

这是一个实验性项目，维护随缘——我可能无法立即处理每个 PR，但会尽力回复每条 Issue 和讨论。感谢你的支持！

---

## 🙏 鸣谢 / Acknowledgments

LazyTkinter 建立在 [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)（[MIT License](https://opensource.org/licenses/MIT)，Copyright (c) 2023 Tom Schimansky）之上，感谢 Tom Schimansky 的出色工作。
内置主题的配色灵感来自 Catppuccin、Gruvbox、Dracula 等开源主题项目。

完整的第三方许可证声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

---

## 📄 许可证 / License

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。底层依赖 CustomTkinter 遵循其原有协议。这意味着你可以自由使用、修改和分发本项目，但需保留原许可证声明。
