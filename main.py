
import ast
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_calculate(expression):
    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](
                evaluate(node.left), evaluate(node.right)
            )
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](evaluate(node.operand))
        raise ValueError("Invalid expression")

    return evaluate(ast.parse(expression, mode="eval"))


class CalculatorApp(App):
    def build(self):
        self.title = "Pro Calculator"
        Window.clearcolor = (0.08, 0.09, 0.13, 1)
        self.history = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        self.display = TextInput(
            hint_text="0",
            multiline=False,
            font_size=sp(34),
            halign="right",
            size_hint_y=None,
            height=dp(75)
        )
        root.add_widget(self.display)

        root.add_widget(Label(
            text="HISTORY",
            size_hint_y=None,
            height=dp(24)
        ))

        scroll = ScrollView(
            size_hint_y=None,
            height=dp(75)
        )
        self.history_label = Label(
            text="",
            size_hint_y=None,
            height=dp(70),
            halign="left",
            valign="top"
        )
        self.history_label.bind(
            size=lambda obj, size:
            setattr(obj, "text_size", size)
        )
        scroll.add_widget(self.history_label)
        root.add_widget(scroll)

        rows = [
            ["C", "(", ")", "⌫"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["%", "0", ".", "+"],
            ["−", "=", "÷", "×"]
        ]

        for values in rows:
            row = BoxLayout(spacing=dp(7))
            for value in values:
                button = Button(
                    text=value,
                    font_size=sp(24),
                    background_normal="",
                    background_color=self.get_color(value)
                )
                button.bind(
                    on_release=lambda instance, v=value:
                    self.press(v)
                )
                row.add_widget(button)
            root.add_widget(row)

        return root

    def get_color(self, value):
        if value == "C":
            return (0.85, 0.25, 0.42, 1)
        if value == "=":
            return (0.32, 0.43, 0.99, 1)
        if value in ("÷", "×", "−", "+", "%"):
            return (0.22, 0.29, 0.48, 1)
        return (0.16, 0.20, 0.28, 1)

    def press(self, value):
        current = self.display.text

        if value == "C":
            self.display.text = ""
        elif value == "⌫":
            self.display.text = current[:-1]
        elif value == "=":
            self.calculate()
        elif value == "%":
            self.display.text = current + "/100"
        else:
            replacements = {"÷": "/", "×": "*", "−": "-"}
            self.display.text = current + replacements.get(
                value, value
            )

    def calculate(self):
        current = self.display.text.strip()
        if not current:
            return

        try:
            result = safe_calculate(current)
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            result_text = str(result)
            self.history.append(f"{current} = {result_text}")
            self.history = self.history[-10:]
            self.history_label.text = "\n".join(
                reversed(self.history)
            )
            self.display.text = result_text
        except Exception:
            self.display.text = "Error"


if __name__ == "__main__":
    CalculatorApp().run()
