"""
Unit tests for 📜 The Sage — Syntax Analysis / Parsing (src/parser.py).

Group: DnD
"""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scribe  import Lexer
from src.sage import (
    Parser, Program, VarDeclaration, Assignment, InputStatement,
    OutputStatement, BinaryOp, Number, Identifier,
)
from src.curses import ParserError


def _parse(source):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


class TestParserVarDeclaration(unittest.TestCase):
    """var declarations are parsed into VarDeclaration nodes."""

    def test_simple_var(self):
        tree = _parse("var x;")
        self.assertIsInstance(tree, Program)
        self.assertEqual(len(tree.statements), 1)
        stmt = tree.statements[0]
        self.assertIsInstance(stmt, VarDeclaration)
        self.assertEqual(stmt.name, "x")

    def test_multiple_vars(self):
        tree = _parse("var a; var b;")
        self.assertEqual(len(tree.statements), 2)
        self.assertIsInstance(tree.statements[0], VarDeclaration)
        self.assertIsInstance(tree.statements[1], VarDeclaration)

    def test_var_missing_semicolon_raises(self):
        with self.assertRaises(ParserError):
            _parse("var x")

    def test_var_missing_name_raises(self):
        with self.assertRaises(ParserError):
            _parse("var ;")


class TestParserAssignment(unittest.TestCase):
    """Assignments produce Assignment nodes with correct children."""

    def test_literal_assignment(self):
        tree = _parse("var x; x = 5;")
        assign = tree.statements[1]
        self.assertIsInstance(assign, Assignment)
        self.assertEqual(assign.name, "x")
        self.assertIsInstance(assign.value, Number)
        self.assertEqual(assign.value.value, 5)

    def test_identifier_assignment(self):
        tree = _parse("var x; var y; x = y;")
        assign = tree.statements[2]
        self.assertIsInstance(assign.value, Identifier)
        self.assertEqual(assign.value.name, "y")

    def test_expression_assignment(self):
        tree = _parse("var x; x = 1 + 2;")
        assign = tree.statements[1]
        self.assertIsInstance(assign.value, BinaryOp)


class TestParserInputOutput(unittest.TestCase):
    """input / output statements are parsed correctly."""

    def test_input_statement(self):
        tree = _parse("var n; input n;")
        stmt = tree.statements[1]
        self.assertIsInstance(stmt, InputStatement)
        self.assertEqual(stmt.name, "n")

    def test_output_statement(self):
        tree = _parse("var n; output n;")
        stmt = tree.statements[1]
        self.assertIsInstance(stmt, OutputStatement)
        self.assertEqual(stmt.name, "n")


class TestParserOperatorPrecedence(unittest.TestCase):
    """Operator precedence: * / before + -."""

    def test_multiply_before_add(self):
        tree = _parse("var x; x = 2 + 3 * 4;")
        expr = tree.statements[1].value   # BinaryOp(+)
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.operator, "+")
        # right side must be 3 * 4
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.operator, "*")

    def test_left_to_right_same_precedence(self):
        tree = _parse("var x; x = 10 - 3 - 2;")
        expr = tree.statements[1].value   # BinaryOp(-)  left-assoc
        self.assertEqual(expr.operator, "-")
        self.assertIsInstance(expr.left, BinaryOp)  # (10 - 3)

    def test_parentheses_override_precedence(self):
        tree = _parse("var x; x = (2 + 3) * 4;")
        expr = tree.statements[1].value   # BinaryOp(*)
        self.assertEqual(expr.operator, "*")
        # left side must be (2 + 3)
        self.assertIsInstance(expr.left, BinaryOp)
        self.assertEqual(expr.left.operator, "+")


class TestParserErrors(unittest.TestCase):
    """Syntax errors raise ParserError with D&D-themed messages."""

    def test_missing_semicolon(self):
        with self.assertRaises(ParserError):
            _parse("var x; x = 1")

    def test_unexpected_token(self):
        with self.assertRaises(ParserError):
            _parse("+ ;")

    def test_unmatched_paren(self):
        with self.assertRaises(ParserError):
            _parse("var x; x = (1 + 2;")

    def test_error_message_is_dnd_themed(self):
        try:
            _parse("var x; x = ;")
        except ParserError as exc:
            self.assertIn("Sage", str(exc))
        else:
            self.fail("Expected ParserError")


class TestParserFullProgram(unittest.TestCase):
    """Parse a complete non-trivial program."""

    SOURCE = """\
var a;
var b;
var result;
a = 10;
b = 3;
result = a + b * 2;
output result;
"""

    def test_statement_count(self):
        tree = _parse(self.SOURCE)
        self.assertEqual(len(tree.statements), 7)

    def test_last_statement_is_output(self):
        tree = _parse(self.SOURCE)
        self.assertIsInstance(tree.statements[-1], OutputStatement)


if __name__ == "__main__":
    unittest.main()
