# LazyTkinter 布局规则（Row / Column）

> 本文档专门讲解 `Row` 与 `Column` 的布局规则；`ZStack` / `Space` / `Scroll` / `View` / `SplitPanel` / `Divider` 等原语的方法签名见 [API_REFERENCE.md](API_REFERENCE.md)。

## 主轴与交叉轴

每个容器有两条轴：

- **主轴**：子元素排列的方向。`Row` 从左到右，`Column` 从上到下。
- **交叉轴**：垂直于主轴的方向。`Row` 的交叉轴是垂直方向（上/下），`Column` 的交叉轴是水平方向（左/右）。

```
Row:    [A][B][C]
         ↑
      主轴 = 水平（左右）    交叉轴 = 垂直（top / center / bottom）

Column: [A]
        [B]
        [C]
        ↑
      主轴 = 垂直（上下）    交叉轴 = 水平（left / center / right）
```

## 默认值速查

| 容器 | 主轴 | 默认宽度 | 默认高度 | 默认 align | 默认 justify |
| --- | --- | --- | --- | --- | --- |
| Row | 水平（左右） | fit | fit | top | start |
| Column | 垂直（上下） | **fill** | fit | left | start |
| ZStack | — | fill | fill | center | — |
| Scroll | — | fill | fill | — | — |

## 尺寸策略：fit / fill / 固定像素

`width()` / `height()` 接受三种值：

- `int`：固定像素（该轴视为 fit，不参与拉伸）；
- `"fit"`：包裹内容，取子元素的自然尺寸；
- `"fill"`：撑满父容器在该轴上的剩余空间。

链式写法与字符串写法等价，链式写法对 IDE 补全更友好：

```python
ltk.Button().width(120)            # 固定像素
ltk.Button().width("fill")         # 字符串形式
ltk.Button().width().fill()        # 链式：只把宽度设为 fill
ltk.Button().fill()                # 双轴都 fill
ltk.Button().fill(weight=2)        # 主轴 fill 且按 2 份参与分配
```

要点：

- 控件默认 `fit`；例外：`Column` 宽度默认 `fill`；`ZStack` / `Scroll` / `View` / `SplitPanel` 双轴默认 `fill`。
- 多个 fill 子元素按 `fill(weight=n)` 的比例分配主轴**剩余空间**，默认 1:1 等分；子元素的自然尺寸是分配下限，所以比例是“趋近”而非精确切分。
- `weight` 只对 Row/Column 的**主轴 fill** 生效；fit 子元素或已被 Space 降级的 fill 不能带 weight（构建时抛 `ValueError`）。

## 间距：gap 与 padding

- `gap(n)`：相邻子元素之间的间距，只出现在子项之间。
- `padding(n)`：容器四边的内边距（只加在首尾子项的外侧）。
- 两者都只接受非负整数，非法输入抛 `ValueError`。

```python
ltk.Column().gap(8).padding(16)
# 上下各有 16 内边距，每个子项之间 8
```

## 对齐：align 与 justify

- `align`：交叉轴。`Column().align("left" / "center" / "right")` 管左右；`Row().align("top" / "center" / "bottom")` 管上下。默认 `left` / `top`。
- 子元素可以自带 `align` 覆盖容器默认；子元素取值必须与所在容器匹配，否则构建时报 `ValueError`。
- `justify`：主轴分布，取值 `start` / `center` / `end`，默认 `start`。
  - `center`：子元素整体在主轴上居中 —— 等价于两端各插入一个隐式弹性 `Space`；
  - `end`：靠主轴末尾 —— 在起始端插入一个隐式弹性 `Space`；
  - `center` / `end` 会自动把容器主轴转为 `fill`（前提是未设固定尺寸），否则没有剩余空间可分。
- `.center()` = `justify("center") + align("center")`，一步让子元素上下左右居中。

```python
ltk.Row().width().fill().justify("center")   # 按钮水平居中
ltk.Column().center()                        # 上下左右都居中
```

## Space：弹性与固定占位

- `ltk.Space()` 默认是弹性弹簧：按 `weight(n)` 的权重吃容器主轴剩余空间（默认 1）。
- 显式 `width(n)` / `height(n)` 后变为固定尺寸的刚性透明占位。
- 容器内只要存在弹性 Space，所有 fill 子元素在主轴上**降级为自然尺寸**，剩余空间全部交给 Space；固定尺寸 Space 不触发降级。

```python
ltk.Row().width().fill().add(
    ltk.Button().text("left"),
    ltk.Space(),                 # 弹性：把左右按钮推开
    ltk.Button().text("right"),
)
```

非法组合（构建时报 `ValueError`）：

- `Space.weight()` 与主轴固定尺寸同用（Column 里设了固定高度 / Row 里设了固定宽度）；
- `fill(weight=...)` 用在 fit 子元素或已被 Space 降级的 fill 上；
- ZStack 里的弹性 Space（ZStack 没有可分配的剩余空间，需显式 `width` / `height`）。

## 常见误区

| 误区 | 正确理解 |
| --- | --- |
| `Row().align("center")` 以为水平居中 | Row 的 `align` 管交叉轴（垂直）；水平居中用 `justify("center")` |
| `Column().align("center")` 以为垂直居中 | Column 的 `align` 管交叉轴（水平）；垂直居中用 `justify("center")` |
| 以为 `Row()` 默认撑满宽度 | Row 默认 fit；需要 `.width().fill()` |
| `justify("center")` 没效果 | 主轴要先有剩余空间：`center`/`end` 会自动转 fill，但容器在父级里若也是 fit，就没有空间可分 |
| 给 fit 子元素写 `.fill(weight=2)` | `weight` 只用于主轴 fill 的子元素 |
| 把多个子元素塞进 `Scroll(...)` | `Scroll` 只接受恰好一个子元素：`Scroll(Column(...))` |
| 在根窗口调两次 `column()` / `row()` | 根布局只能设置一次，复杂布局用 Row/Column 嵌套 |

## 完整示例

“顶栏 + 内容区”的常见骨架：

```python
app.size("large").gap(10).padding(10).column(
    ltk.Row().height(50).width().fill().gap(10).add(        # 顶栏
        ltk.Label().text("LazyTkinter"),
        ltk.Entry().width().fill(),
        ltk.Button().text("search"),
    ),
    ltk.Row().width().fill().height().fill().gap(10).add(   # 内容区 1:2 分栏
        ltk.Column().width().fill(weight=1),
        ltk.Column().width().fill(weight=2),
    ),
)
```
