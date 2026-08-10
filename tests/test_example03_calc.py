"""计算器示例（examples/example03.py）的纯逻辑单测。

通过 importlib 加载示例模块而不创建窗口：UI 全部在 ``main()`` 中。
"""

import importlib.util
import unittest

_MODULE_PATH = "examples/example03.py"


def _load_example():
    spec = importlib.util.spec_from_file_location("example03_calc", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


calc = _load_example()


class EvaluateTests(unittest.TestCase):
    """evaluate() / _apply_percent() 表达式求值。"""

    def test_mixed_expression_precedence(self):
        self.assertAlmostEqual(calc.evaluate("1+2-3×4÷5"), 0.6)

    def test_decimal_expression(self):
        self.assertAlmostEqual(calc.evaluate("0.1+0.2"), 0.3)

    def test_percent_standalone(self):
        self.assertAlmostEqual(calc.evaluate("50%"), 0.5)

    def test_percent_add(self):
        self.assertAlmostEqual(calc.evaluate("50+10%"), 55)

    def test_percent_subtract(self):
        self.assertAlmostEqual(calc.evaluate("50−10%"), 45)

    def test_percent_multiply(self):
        self.assertAlmostEqual(calc.evaluate("50×10%"), 5)

    def test_percent_divide(self):
        self.assertAlmostEqual(calc.evaluate("50÷10%"), 500)

    def test_percent_chain(self):
        self.assertAlmostEqual(calc.evaluate("50%+10%"), 0.55)

    def test_unary_minus_at_start(self):
        self.assertAlmostEqual(calc.evaluate("-5+3"), -2)

    def test_unary_minus_after_operator(self):
        self.assertAlmostEqual(calc.evaluate("5×-3"), -15)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calc.evaluate("8÷0")

    def test_double_operator_rejected(self):
        with self.assertRaises(ValueError):
            calc.evaluate("1++2")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            calc.evaluate("")

    def test_trailing_operator_is_ignored(self):
        self.assertAlmostEqual(calc.evaluate("5+"), 5)


class FormatResultTests(unittest.TestCase):
    """format_result() 显示格式。"""

    def test_integer(self):
        self.assertEqual(calc.format_result(2.0), "2")

    def test_plain_decimal(self):
        self.assertEqual(calc.format_result(0.6), "0.6")

    def test_float_artifact_removed(self):
        self.assertEqual(calc.format_result(0.1 + 0.2), "0.3")

    def test_repeating_decimal_capped(self):
        self.assertEqual(calc.format_result(1 / 3), "0.3333333333")

    def test_scientific_large(self):
        self.assertEqual(calc.format_result(1e15), "1e+15")

    def test_negative(self):
        self.assertEqual(calc.format_result(-2.5), "-2.5")


class CalculatorTests(unittest.TestCase):
    """Calculator 按键状态机。"""

    def setUp(self):
        self.calc = calc.Calculator()

    def type_keys(self, keys):
        for key in keys:
            self.calc.press(key)

    def test_initial_state(self):
        self.assertEqual(self.calc.current, "0")
        self.assertEqual(self.calc.ac_label, "AC")

    def test_basic_equals(self):
        self.type_keys("1+2=")
        self.assertEqual(self.calc.current, "3")
        self.assertEqual(self.calc.last, "1+2")
        self.assertEqual(self.calc.ac_label, "AC")

    def test_digit_after_result_starts_new(self):
        self.type_keys("1+2=")
        self.calc.press("5")
        self.assertEqual(self.calc.current, "5")
        self.assertEqual(self.calc.last, "1+2")

    def test_operator_after_result_continues(self):
        self.type_keys("1+2=")
        self.type_keys("×4=")
        self.assertEqual(self.calc.current, "12")
        self.assertEqual(self.calc.last, "3×4")

    def test_consecutive_operators_replace(self):
        self.type_keys("1+×")
        self.assertEqual(self.calc.current, "1×")

    def test_leading_dot_gets_zero(self):
        self.calc.press(".")
        self.assertEqual(self.calc.current, "0.")

    def test_dot_after_operator_gets_zero(self):
        self.type_keys("1+.")
        self.assertEqual(self.calc.current, "1+0.")

    def test_duplicate_dot_ignored(self):
        self.type_keys("1.2.")
        self.assertEqual(self.calc.current, "1.2")

    def test_del_backspace(self):
        self.type_keys("12")
        self.calc.press("Del")
        self.assertEqual(self.calc.current, "1")

    def test_del_after_result_edits_result(self):
        self.type_keys("1+2=")
        self.calc.press("Del")
        self.assertEqual(self.calc.current, "0")

    def test_c_keeps_history_ac_clears_all(self):
        self.type_keys("3+4=")
        self.calc.press("5")  # 输入中 → AC 显示为 C
        self.assertEqual(self.calc.ac_label, "C")
        self.calc.press("AC")  # C 语义：只清当前输入
        self.assertEqual(self.calc.current, "0")
        self.assertEqual(self.calc.last, "3+4")
        self.assertEqual(self.calc.ac_label, "AC")
        self.calc.press("AC")  # 空输入 → 全清
        self.assertEqual(self.calc.last, "")

    def test_error_then_any_key_recovers(self):
        self.type_keys("8÷0=")
        self.assertEqual(self.calc.current, "Error")
        self.calc.press("5")
        self.assertEqual(self.calc.current, "5")
        self.assertEqual(self.calc.ac_label, "C")

    def test_operator_after_error_resets_to_empty(self):
        self.type_keys("8÷0=")
        self.calc.press("+")  # 错误后按运算符：重置后空表达式忽略
        self.assertEqual(self.calc.current, "0")
        self.assertEqual(self.calc.ac_label, "AC")

    def test_equals_not_repeated(self):
        self.type_keys("2+3=")
        self.assertEqual(self.calc.current, "5")
        self.calc.press("=")
        self.assertEqual(self.calc.current, "5")
        self.assertEqual(self.calc.last, "2+3")

    def test_input_capped_at_24_chars(self):
        for _ in range(30):
            self.calc.press("7")
        self.assertEqual(len(self.calc.expr), 24)

    def test_percent_button(self):
        self.type_keys("50+10%=")
        self.assertEqual(self.calc.current, "55")
        self.assertEqual(self.calc.last, "50+10%")

    def test_toggle_sign(self):
        self.calc.press("±")
        self.calc.press("5")
        self.calc.press("±")
        self.assertEqual(self.calc.current, "5")

    def test_toggle_sign_after_result(self):
        self.type_keys("1+2=")
        self.calc.press("±")
        self.assertEqual(self.calc.current, "−3")
        self.type_keys("+1=")
        self.assertEqual(self.calc.current, "-2")


if __name__ == "__main__":
    unittest.main()
