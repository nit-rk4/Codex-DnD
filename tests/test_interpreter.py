"""
Unit tests for ⚡ The Enchanter — Interpreter (src/interpreter.py).

Group: DnD
"""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scribe       import Lexer
from src.sage      import Parser
from src.archmage    import SemanticAnalyzer
from src.enchanter import Interpreter
from src.curses      import InterpreterError


def _run(source, inputs=None):
    """
    Helper: lex → parse → analyze → execute.

    Returns a list of values passed to the output function.
    *inputs* is an optional list of strings returned in sequence for 'input'
    statements.
    """
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)

    output_log = []
    input_iter = iter(inputs or [])

    def mock_input(_prompt=""):
        return next(input_iter)

    def mock_output(value):
        output_log.append(value)

    interp = Interpreter(input_fn=mock_input, output_fn=mock_output)
    interp.execute(ast)
    return output_log


class TestInterpreterBasicExecution(unittest.TestCase):
    """Variables can be declared, assigned, and output."""

    def test_literal_output(self):
        result = _run("var x; x = 42; output x;")
        self.assertEqual(result, [42])

    def test_zero_assignment(self):
        result = _run("var x; x = 0; output x;")
        self.assertEqual(result, [0])

    def test_multiple_outputs(self):
        result = _run("var a; var b; a = 1; b = 2; output a; output b;")
        self.assertEqual(result, [1, 2])


class TestInterpreterArithmetic(unittest.TestCase):
    """Arithmetic operations are evaluated correctly."""

    def test_addition(self):
        self.assertEqual(_run("var x; x = 3 + 4; output x;"), [7])

    def test_subtraction(self):
        self.assertEqual(_run("var x; x = 10 - 4; output x;"), [6])

    def test_multiplication(self):
        self.assertEqual(_run("var x; x = 6 * 7; output x;"), [42])

    def test_integer_division(self):
        self.assertEqual(_run("var x; x = 10 / 3; output x;"), [3])

    def test_operator_precedence(self):
        # 2 + 3 * 4 = 14, not 20
        self.assertEqual(_run("var x; x = 2 + 3 * 4; output x;"), [14])

    def test_parentheses(self):
        # (2 + 3) * 4 = 20
        self.assertEqual(_run("var x; x = (2 + 3) * 4; output x;"), [20])

    def test_complex_expression(self):
        result = _run("var a; var b; var r; a = 10; b = 3; r = a + b * 2; output r;")
        self.assertEqual(result, [16])

    def test_negative_result(self):
        self.assertEqual(_run("var x; x = 3 - 10; output x;"), [-7])


class TestInterpreterInput(unittest.TestCase):
    """input statements read values from the input function."""

    def test_input_then_output(self):
        result = _run("var n; input n; output n;", inputs=["7"])
        self.assertEqual(result, [7])

    def test_input_used_in_expression(self):
        result = _run("var n; var d; input n; d = n * 2; output d;", inputs=["5"])
        self.assertEqual(result, [10])


class TestInterpreterRuntimeErrors(unittest.TestCase):
    """Runtime errors raise InterpreterError with D&D-themed messages."""

    def test_division_by_zero(self):
        with self.assertRaises(InterpreterError) as ctx:
            _run("var x; x = 1 / 0;")
        self.assertIn("zero", str(ctx.exception).lower())

    def test_runtime_error_is_dnd_themed(self):
        try:
            _run("var x; x = 5 / 0;")
        except InterpreterError as exc:
            self.assertIn("Enchanter", str(exc))
        else:
            self.fail("Expected InterpreterError")

    def test_invalid_input_value(self):
        """Providing a non-integer to 'input' raises InterpreterError."""
        with self.assertRaises(InterpreterError):
            _run("var n; input n;", inputs=["hello"])


class TestInterpreterSymbolTable(unittest.TestCase):
    """The symbol table is maintained correctly across statements."""

    def test_reassignment(self):
        result = _run("var x; x = 1; x = 2; output x;")
        self.assertEqual(result, [2])

    def test_variable_initialized_to_zero(self):
        result = _run("var x; output x;")
        self.assertEqual(result, [0])

    def test_var_to_var_assignment(self):
        result = _run("var a; var b; a = 7; b = a; output b;")
        self.assertEqual(result, [7])


if __name__ == "__main__":
    unittest.main()
