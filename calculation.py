import math
import random
from fractions import Fraction

class CalculatorEngine:
    def __init__(self):
        self.expression = ""
        self.mode = "DEG"
        self.memory = 0.0
        self.last_answer = 0.0

    def toggle_mode(self, mode: str):
        if mode in ("DEG", "RAD"):
            self.mode = mode

    def append(self, text: str):
        if self.expression == "0" and text not in (".", "+", "−", "×", "÷", "%", "^"):
            self.expression = text
        else:
            self.expression += text

    def clear(self):
        self.expression = ""

    def backspace(self):
        self.expression = self.expression[:-1]

    def negate(self):
        if not self.expression:
            return
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression

    def add_random(self):
        self.append(str(round(random.random(), 4)))

    def to_fraction_or_decimal(self):
        val = self.evaluate()
        if val not in ("Error", "0"):
            try:
                frac = Fraction(float(val)).limit_denominator(1000)
                self.expression = f"{frac.numerator}/{frac.denominator}"
            except Exception:
                pass

    def _prepare_eval_string(self, expr_str: str) -> str:
        s = expr_str.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
        s = s.replace("π", str(math.pi)).replace("e", str(math.e))
        s = s.replace("Ans", str(self.last_answer))
        return s

    def _get_eval_context(self):
        def _sin(x): return math.sin(math.radians(x) if self.mode == "DEG" else x)
        def _cos(x): return math.cos(math.radians(x) if self.mode == "DEG" else x)
        def _tan(x): return math.tan(math.radians(x) if self.mode == "DEG" else x)
        def _asin(x): return math.degrees(math.asin(x)) if self.mode == "DEG" else math.asin(x)
        def _acos(x): return math.degrees(math.acos(x)) if self.mode == "DEG" else math.acos(x)
        def _atan(x): return math.degrees(math.atan(x)) if self.mode == "DEG" else math.atan(x)

        return {
            "sin": _sin, "cos": _cos, "tan": _tan,
            "asin": _asin, "acos": _acos, "atan": _atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
            "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
            "cbrt": lambda x: math.pow(x, 1/3) if x >= 0 else -math.pow(-x, 1/3),
            "fact": math.factorial, "exp": math.exp
        }

    def live_preview(self) -> str:
        if not self.expression or len(self.expression) < 2:
            return ""
        try:
            expr = self._prepare_eval_string(self.expression)
            open_parens = expr.count("(") - expr.count(")")
            if open_parens > 0:
                expr += ")" * open_parens

            res = eval(expr, {"__builtins__": None}, self._get_eval_context())
            if isinstance(res, float) and res.is_integer():
                return f"= {int(res)}"
            elif isinstance(res, float):
                return f"= {round(res, 6)}"
            return f"= {res}"
        except Exception:
            return ""

    def evaluate(self) -> str:
        if not self.expression:
            return "0"

        try:
            expr = self._prepare_eval_string(self.expression)
            result = eval(expr, {"__builtins__": None}, self._get_eval_context())

            if isinstance(result, float) and result.is_integer():
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 8)

            self.last_answer = result
            self.expression = str(result)
            return self.expression
        except Exception:
            self.expression = ""
            return "Error"

    # --- Specialty Financial Tools ---
    @staticmethod
    def calculate_gst(amount: float, rate: float, is_inclusive: bool = False):
        if is_inclusive:
            base = amount / (1 + (rate / 100))
            gst_amount = amount - base
            total = amount
        else:
            base = amount
            gst_amount = amount * (rate / 100)
            total = amount + gst_amount
        return round(base, 2), round(gst_amount, 2), round(total, 2)

    @staticmethod
    def calculate_discount(original_price: float, discount_percent: float):
        saved = original_price * (discount_percent / 100)
        final_price = original_price - saved
        return round(saved, 2), round(final_price, 2)

    @staticmethod
    def calculate_interest(principal: float, rate: float, time_years: float, is_compound: bool = False):
        if is_compound:
            total = principal * ((1 + (rate / 100)) ** time_years)
            interest = total - principal
        else:
            interest = (principal * rate * time_years) / 100
            total = principal + interest
        return round(interest, 2), round(total, 2)