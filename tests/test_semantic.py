"""
Unit tests for 🔮 The Archmage — Semantic Analysis (src/semantic.py).

Group: DnD
"""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scribe     import Lexer
from src.sage    import Parser
from src.archmage  import SemanticAnalyzer
from src.curses    import SemanticError


def _analyze(source):
    """Helper: lex → parse → semantic-analyze and return the analyzer."""
    tokens   = Lexer(source).tokenize()
    ast      = Parser(tokens).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer


class TestSemanticUndeclaredVariable(unittest.TestCase):
    """Using a variable that was never declared raises SemanticError."""

    def test_use_before_declare_in_assignment(self):
        with self.assertRaises(SemanticError):
            _analyze("x = 5;")

    def test_use_before_declare_in_expression(self):
        with self.assertRaises(SemanticError):
            _analyze("var x; x = y;")

    def test_use_before_declare_in_output(self):
        with self.assertRaises(SemanticError):
            _analyze("output x;")

    def test_use_before_declare_in_input(self):
        with self.assertRaises(SemanticError):
            _analyze("input x;")

    def test_error_message_is_dnd_themed(self):
        try:
            _analyze("output z;")
        except SemanticError as exc:
            self.assertIn("Archmage", str(exc))
        else:
            self.fail("Expected SemanticError")


class TestSemanticDuplicateDeclaration(unittest.TestCase):
    """Declaring the same variable twice raises SemanticError."""

    def test_duplicate_var(self):
        with self.assertRaises(SemanticError):
            _analyze("var x; var x;")

    def test_unique_vars_ok(self):
        # Should not raise
        _analyze("var x; var y;")

    def test_duplicate_error_message(self):
        try:
            _analyze("var a; var a;")
        except SemanticError as exc:
            self.assertIn("a", str(exc))


class TestSemanticValidPrograms(unittest.TestCase):
    """Well-formed programs pass semantic analysis without error."""

    def test_declare_then_assign(self):
        _analyze("var x; x = 10;")

    def test_declare_assign_output(self):
        _analyze("var x; x = 42; output x;")

    def test_multiple_vars_and_operations(self):
        _analyze("var a; var b; var c; a = 1; b = 2; c = a + b; output c;")

    def test_nested_expression(self):
        _analyze("var x; x = (1 + 2) * 3;")


class TestSemanticDivisionByZeroWarning(unittest.TestCase):
    """Division by a literal zero produces a warning (not an error)."""

    def test_div_by_zero_literal_gives_warning(self):
        analyzer = _analyze("var x; x = 10 / 0;")
        self.assertTrue(len(analyzer.warnings) > 0)
        self.assertIn("zero", analyzer.warnings[0].lower())

    def test_div_by_nonzero_no_warning(self):
        analyzer = _analyze("var x; x = 10 / 2;")
        self.assertEqual(len(analyzer.warnings), 0)

    def test_div_by_variable_no_warning(self):
        # Cannot detect variable value at compile time → no warning
        analyzer = _analyze("var x; var y; y = 0; x = 5 / y;")
        self.assertEqual(len(analyzer.warnings), 0)


if __name__ == "__main__":
    unittest.main()
