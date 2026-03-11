"""
Unit tests for 🪶 The Scribe — Lexical Analysis (src/lexer.py).

Group: DnD
"""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scribe  import Lexer, TokenType, Token
from src.curses import LexerError


class TestLexerKeywords(unittest.TestCase):
    """Keywords are tokenized to the correct token type."""

    def _tokens(self, source):
        return Lexer(source).tokenize()

    def test_var_keyword(self):
        toks = self._tokens("var")
        self.assertEqual(toks[0].type, TokenType.VAR)
        self.assertEqual(toks[0].value, "var")

    def test_input_keyword(self):
        toks = self._tokens("input")
        self.assertEqual(toks[0].type, TokenType.INPUT)

    def test_output_keyword(self):
        toks = self._tokens("output")
        self.assertEqual(toks[0].type, TokenType.OUTPUT)

    def test_keywords_end_with_eof(self):
        toks = self._tokens("var")
        self.assertEqual(toks[-1].type, TokenType.EOF)


class TestLexerIdentifiers(unittest.TestCase):
    """Valid identifiers are recognised; invalid starts raise LexerError."""

    def _tok(self, source):
        return Lexer(source).tokenize()[0]

    def test_simple_identifier(self):
        tok = self._tok("foo")
        self.assertEqual(tok.type, TokenType.IDENTIFIER)
        self.assertEqual(tok.value, "foo")

    def test_identifier_with_underscore(self):
        tok = self._tok("my_var")
        self.assertEqual(tok.type, TokenType.IDENTIFIER)

    def test_identifier_with_numbers(self):
        tok = self._tok("x1")
        self.assertEqual(tok.type, TokenType.IDENTIFIER)

    def test_uppercase_identifier(self):
        tok = self._tok("MyVar")
        self.assertEqual(tok.type, TokenType.IDENTIFIER)

    def test_underscore_prefix_identifier(self):
        tok = self._tok("_hidden")
        self.assertEqual(tok.type, TokenType.IDENTIFIER)


class TestLexerNumbers(unittest.TestCase):
    """Integer literals are tokenised correctly."""

    def test_single_digit(self):
        toks = Lexer("7").tokenize()
        self.assertEqual(toks[0].type, TokenType.NUMBER)
        self.assertEqual(toks[0].value, 7)

    def test_multi_digit(self):
        toks = Lexer("42").tokenize()
        self.assertEqual(toks[0].value, 42)

    def test_zero(self):
        toks = Lexer("0").tokenize()
        self.assertEqual(toks[0].value, 0)


class TestLexerOperatorsAndPunctuation(unittest.TestCase):
    """Operators and punctuation produce the correct token types."""

    def _single(self, source, expected_type):
        tok = Lexer(source).tokenize()[0]
        self.assertEqual(tok.type, expected_type)

    def test_plus(self):      self._single("+", TokenType.PLUS)
    def test_minus(self):     self._single("-", TokenType.MINUS)
    def test_multiply(self):  self._single("*", TokenType.MULTIPLY)
    def test_divide(self):    self._single("/", TokenType.DIVIDE)
    def test_assign(self):    self._single("=", TokenType.ASSIGN)
    def test_semicolon(self): self._single(";", TokenType.SEMICOLON)
    def test_lparen(self):    self._single("(", TokenType.LPAREN)
    def test_rparen(self):    self._single(")", TokenType.RPAREN)


class TestLexerWhitespace(unittest.TestCase):
    """Whitespace is insignificant and skipped."""

    def test_spaces_ignored(self):
        toks = Lexer("a + b").tokenize()
        types = [t.type for t in toks]
        self.assertEqual(types, [
            TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER, TokenType.EOF,
        ])

    def test_tabs_and_newlines_ignored(self):
        toks = Lexer("a\t+\nb").tokenize()
        types = [t.type for t in toks]
        self.assertEqual(types, [
            TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER, TokenType.EOF,
        ])


class TestLexerComments(unittest.TestCase):
    """Block comments are skipped in their entirety."""

    def test_single_line_comment(self):
        toks = Lexer("/* hello */ x").tokenize()
        self.assertEqual(toks[0].type, TokenType.IDENTIFIER)
        self.assertEqual(toks[0].value, "x")

    def test_multi_line_comment(self):
        source = "/* line one\nline two\n*/ y"
        toks = Lexer(source).tokenize()
        self.assertEqual(toks[0].type, TokenType.IDENTIFIER)
        self.assertEqual(toks[0].value, "y")

    def test_comment_between_tokens(self):
        toks = Lexer("a /* mid */ + b").tokenize()
        types = [t.type for t in toks]
        self.assertIn(TokenType.PLUS, types)

    def test_unterminated_comment_raises(self):
        with self.assertRaises(LexerError):
            Lexer("/* oops").tokenize()


class TestLexerLineNumbers(unittest.TestCase):
    """Tokens carry accurate line numbers."""

    def test_first_line(self):
        toks = Lexer("x").tokenize()
        self.assertEqual(toks[0].line, 1)

    def test_second_line(self):
        toks = Lexer("x\ny").tokenize()
        self.assertEqual(toks[1].line, 2)


class TestLexerErrors(unittest.TestCase):
    """Invalid characters raise LexerError with a descriptive message."""

    def test_unknown_character(self):
        with self.assertRaises(LexerError) as ctx:
            Lexer("a & b").tokenize()
        self.assertIn("&", str(ctx.exception))

    def test_error_message_is_dnd_themed(self):
        try:
            Lexer("@").tokenize()
        except LexerError as exc:
            self.assertIn("Curse", str(exc))
        else:
            self.fail("Expected LexerError")


class TestLexerFullProgram(unittest.TestCase):
    """Tokenise a complete minimal program."""

    def test_hello_scroll(self):
        source = "/* The simplest scroll */\nvar x;\nx = 42;\noutput x;"
        toks = Lexer(source).tokenize()
        types = [t.type for t in toks]
        expected = [
            TokenType.VAR, TokenType.IDENTIFIER, TokenType.SEMICOLON,
            TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER, TokenType.SEMICOLON,
            TokenType.OUTPUT, TokenType.IDENTIFIER, TokenType.SEMICOLON,
            TokenType.EOF,
        ]
        self.assertEqual(types, expected)


if __name__ == "__main__":
    unittest.main()
