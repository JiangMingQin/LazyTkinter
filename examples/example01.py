"""计算器示例：整体表达式求值，按键手感参考 iOS 计算器。

- 计算模型：输入完整表达式后按 ``=`` 一次性求值（标准数学优先级），
  如 ``1+2-3×4÷5 = 0.6``。
- iOS 手感：AC/C 切换、``±`` 取反、小数点自动补 ``0``、结果续算、
  错误一键恢复、``=`` 不连按重复。
- ``%`` 采用 iOS 语境语义：``50+10% = 55``、``50×10% = 5``、
  单独 ``50% = 0.5``。

纯逻辑（求值 / 状态机）与 UI 分离，方便单测；窗口在 ``main()`` 中构建。
"""

from __future__ import annotations

import re

import lazytkinter as ltk

# ---------------------------------------------------------------------------
# 纯逻辑：表达式求值
# ---------------------------------------------------------------------------

_OPERATORS = "+−×÷"                 # 四则运算符（减号统一用 U+2212）
_DIGITS = set("0123456789.")
_MAX_LEN = 24                       # 输入长度上限，防止显示溢出
_PERCENT_RE = re.compile(r"(-?\d+(?:\.\d+)?)%")
_TRAILING_NUMBER_RE = re.compile(r"([−-]?\d+(?:\.\d*)?|\.\d+)$")


def _apply_percent(expr: str) -> str:
    """iOS 语境 ``%``：把 ``N%`` 改写为等价表达式，再交给 ``evaluate`` 解析。

    从左到右处理第一个 ``N%``：

    - 前一位是 ``+``/``−`` 且左侧有表达式段 A：``A±N%`` → ``A±(A×N/100)``；
    - 前一位是 ``×``/``÷``：``N%`` → ``(N/100)``；
    - 单独出现：``N%`` → ``(N/100)``。
    """
    match = _PERCENT_RE.search(expr)
    while match:
        number = float(match.group(1))
        prev = expr[match.start() - 1] if match.start() > 0 else ""
        if prev in "+−" and match.start() > 1:
            base = expr[: match.start() - 1]
            replacement = f"({evaluate(base)}×{number}÷100)"
        else:
            replacement = f"({number}÷100)"
        expr = expr[: match.start()] + replacement + expr[match.end():]
        match = _PERCENT_RE.search(expr)
    return expr


def evaluate(expr: str) -> float:
    """按标准数学优先级求值（``+−`` 低于 ``×÷``，支持一元负号与括号）。

    非法表达式抛 ``ValueError``；除零抛 ``ZeroDivisionError``。
    """
    expr = _apply_percent(expr.strip()).rstrip("+−×÷.-")
    if not expr:
        raise ValueError("empty expression")

    pos = 0

    def parse_number() -> float:
        nonlocal pos
        start = pos
        while pos < len(expr) and (expr[pos].isdigit() or expr[pos] == "."):
            pos += 1
        token = expr[start:pos]
        if token in ("", "."):
            raise ValueError(f"invalid number near {token!r}")
        return float(token)

    def parse_factor() -> float:
        nonlocal pos
        if pos < len(expr) and expr[pos] in "-−":
            pos += 1
            return -parse_factor()
        if pos < len(expr) and expr[pos] == "(":
            pos += 1
            value = parse_expr()
            if pos >= len(expr) or expr[pos] != ")":
                raise ValueError("unbalanced parentheses")
            pos += 1
            return value
        return parse_number()

    def parse_term() -> float:
        nonlocal pos
        value = parse_factor()
        while pos < len(expr) and expr[pos] in "×÷":
            op = expr[pos]
            pos += 1
            rhs = parse_factor()
            value = value * rhs if op == "×" else value / rhs
        return value

    def parse_expr() -> float:
        nonlocal pos
        value = parse_term()
        while pos < len(expr) and expr[pos] in "+-−":
            op = expr[pos]
            pos += 1
            rhs = parse_term()
            value = value + rhs if op in "+" else value - rhs
        return value

    result = parse_expr()
    if pos != len(expr):
        raise ValueError(f"unexpected character {expr[pos]!r} at position {pos}")
    return result


def format_result(value: float) -> str:
    """结果格式化：整数直接显示，去除浮点尾数，极大/极小用科学计数。"""
    if value == int(value) and abs(value) < 1e12:
        return str(int(value))
    if abs(value) >= 1e12 or (value != 0 and abs(value) < 1e-9):
        mantissa, exponent = f"{value:.6e}".split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        return f"{mantissa}e{int(exponent):+d}"
    return f"{value:.10g}"


# ---------------------------------------------------------------------------
# 纯逻辑：按键状态机
# ---------------------------------------------------------------------------


class Calculator:
    """计算器按键状态机（纯逻辑，不依赖 UI）。

    按键：``0-9 . + − × ÷ % ± Del AC C =``
    """

    def __init__(self) -> None:
        self.expr = ""            # 正在输入的表达式
        self.last = ""            # 上一次求值的表达式（历史行）
        self.last_result = "0"    # 最近一次结果；"Error" 表示错误态
        self.result_mode = False  # 是否处于"刚算出结果"的状态

    @property
    def current(self) -> str:
        """当前主显示内容。"""
        if self.result_mode:
            return self.last_result
        return self.expr or "0"

    @property
    def ac_label(self) -> str:
        """iOS 式 AC/C 切换：有输入时显示 C（只清当前输入），否则显示 AC。"""
        return "C" if self.expr and not self.result_mode else "AC"

    def press(self, key: str) -> None:
        """处理一次按键，改变内部状态。"""
        key = "−" if key == "-" else key
        if self.result_mode and self.last_result == "Error" and key != "=":
            self.reset()  # 错误态：任意非 = 键先重置，再正常处理

        if key in ("AC", "C"):
            if key == "C" or self.ac_label == "C":
                self.expr = ""  # C：只清当前输入，保留历史
                self.result_mode = False
            else:
                self.reset()  # AC：全部清空
        elif key == "Del":
            if self.result_mode:
                self.expr = self.last_result[:-1]  # 结果态：把结果当作输入继续编辑
                self.result_mode = False
            else:
                self.expr = self.expr[:-1]
        elif key == "=":
            if not self.result_mode:
                self._evaluate()
        elif key == "±":
            self._toggle_sign()
        elif key == "%":
            self._append_percent()
        elif key in _DIGITS:
            self._append_digit(key)
        elif key in _OPERATORS:
            self._append_operator(key)

    def reset(self) -> None:
        """清空全部状态（AC）。"""
        self.expr = ""
        self.last = ""
        self.last_result = "0"
        self.result_mode = False

    # -- 内部逻辑 -----------------------------------------------------------

    def _evaluate(self) -> None:
        expression = self.expr.rstrip("+−×÷.")
        if not expression:
            return
        try:
            value = evaluate(expression)
        except (ValueError, ZeroDivisionError):
            self.last_result = "Error"
        else:
            self.last = self.expr  # 历史行保留原始输入表达式
            self.last_result = format_result(value)
        self.expr = ""
        self.result_mode = True

    def _append_digit(self, key: str) -> None:
        if self.result_mode:
            self.expr = "0." if key == "." else key  # 结果态：开始新表达式
            self.result_mode = False
            return
        if len(self.expr) >= _MAX_LEN:
            return
        if key == ".":
            if self._current_number_has_dot():
                return
            self.expr += "0." if not self.expr or self.expr[-1] in _OPERATORS else "."
        else:
            self.expr += key

    def _append_operator(self, key: str) -> None:
        if self.result_mode:
            self.expr = self.last_result + key  # 结果态：从结果开始续算
            self.result_mode = False
            return
        if not self.expr:
            if key == "−":
                self.expr = "−"  # 空表达式只允许一元负号
            return
        if self.expr[-1] in _OPERATORS:
            self.expr = self.expr[:-1] + key  # 连续运算符：替换上一个
        elif self.expr[-1] == ".":
            return
        elif len(self.expr) < _MAX_LEN:
            self.expr += key

    def _append_percent(self) -> None:
        if self.result_mode:
            return
        if not self.expr or self.expr[-1] in _OPERATORS or self.expr[-1] == ".":
            return  # % 仅作后缀
        if len(self.expr) < _MAX_LEN:
            self.expr += "%"

    def _toggle_sign(self) -> None:
        if self.result_mode:
            if self.last_result != "Error":
                self.expr = self._negate(self.last_result)
                self.result_mode = False
            return
        if not self.expr:
            self.expr = "−"
            return
        if self.expr[-1] in _OPERATORS or self.expr[-1] == ".":
            return
        match = _TRAILING_NUMBER_RE.search(self.expr)
        if match:
            segment = match.group()
            replacement = segment[1:] if segment.startswith(("−", "-")) else "−" + segment
            self.expr = self.expr[: match.start()] + replacement

    def _current_number_has_dot(self) -> bool:
        match = _TRAILING_NUMBER_RE.search(self.expr)
        return bool(match and "." in match.group())

    @staticmethod
    def _negate(text: str) -> str:
        return text[1:] if text.startswith(("−", "-")) else "−" + text


# ---------------------------------------------------------------------------
# UI：声明式布局
# ---------------------------------------------------------------------------


def main() -> None:
    """构建计算器窗口并运行。"""
    ltk.set_theme(ltk.Theme.Catppuccin)
    app = ltk.Application()
    calc = Calculator()

    expr_var = ltk.StringVar(value=calc.current)
    last_var = ltk.StringVar(value=calc.last)

    def refresh() -> None:
        """按键后同步主显示、历史行与 AC/C 文案。"""
        expr_var.set(calc.current)
        last_var.set(calc.last)
        app.config(ltk.Button).aim_id("ac").text(calc.ac_label)

    def on_press(key: str) -> None:
        calc.press(key)
        refresh()

    def make_button(text: str, color: str = "primary") -> ltk.Button:
        """按钮工厂：等宽撑满行、统一圆角与字号。"""
        return (
            ltk.Button()
            .text(text)
            .width()
            .fill()
            .height(38)
            .radius(20)
            .fg_color(color)
            .font(family="Arial", size=16, weight="bold")
            .event(lambda _value, k=text: on_press(k))
        )

    def button_row(*buttons: ltk.Button) -> ltk.Row:
        """一行等宽按钮（无 Space/justify，fill 均分整行，不溢出）。"""
        return ltk.Row().width().fill().transparent().gap(8).add(*buttons)

    app.size((320, 400)).fixed_size().window_title("Calculator").gap(8).padding(8).column(
        # 显示区：历史表达式（小） + 当前输入/结果（大），右对齐
        ltk.Column().padding(8).gap(8).add(
            ltk.Row().width().fill().transparent().add(
                ltk.Space(),
                ltk.Label()
                .variable(last_var)
                .height(30)
                .wrap_length(280)
                .font(family="Arial", size=14),
            ),
            ltk.Row().width().fill().transparent().add(
                ltk.Space(),
                ltk.Label()
                .variable(expr_var)
                .height(76)
                .wrap_length(280)
                .font(family="Arial", size=32, weight="bold"),
            ),
        ),
        # 键盘区：5 行 × 4 键，功能键分布参考 iOS
        ltk.Column().gap(8).padding(8).add(
            button_row(
                make_button("AC", "#7f849c").id("ac"),
                make_button("Del", "#7f849c"),
                make_button("%", "#7f849c"),
                make_button("÷", "#89b4fa"),
            ),
            button_row(
                make_button("7"),
                make_button("8"),
                make_button("9"),
                make_button("×", "#89b4fa"),
            ),
            button_row(
                make_button("4"),
                make_button("5"),
                make_button("6"),
                make_button("−", "#89b4fa"),
            ),
            button_row(
                make_button("1"),
                make_button("2"),
                make_button("3"),
                make_button("+", "#89b4fa"),
            ),
            button_row(
                make_button("±", "#7f849c"),
                make_button("0"),
                make_button("."),
                make_button("=", "#89b4fa"),
            ),
        ),
    )

    app.run()


if __name__ == "__main__":
    main()
