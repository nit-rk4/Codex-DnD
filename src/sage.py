"""
📜 The Sage — Syntax Analysis / Parsing
=========================================
Converts a token stream produced by The Scribe into an Abstract Syntax Tree.

Grammar (EBNF):
    tome             ::= statement* EOF
    statement        ::= var_decl | assignment | input_stmt | output_stmt
    var_decl         ::= 'var' Artifact ';'
    assignment       ::= Artifact '=' expression ';'
    input_stmt       ::= 'input' Artifact ';'
    output_stmt      ::= 'output' Artifact ';'
    expression       ::= term ( ('+' | '-') term )*
    term             ::= factor ( ('*' | '/') factor )*
    factor           ::= RuneStone | Artifact | '(' expression ')'

AST Node types:
    Tome, SummonRitual, BindingSpell, DivinationRitual, CastingSpell,
    ArcaneFormula, RuneStone, Artifact

Group: DnD
"""

from .curses import ParserError
from .scribe  import TokenType


# ---------------------------------------------------------------------------
# AST Nodes
# ---------------------------------------------------------------------------

class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""


class Tome(ASTNode):
    """Root node — holds a list of top-level statements."""
    def __init__(self, statements: list):
        self.statements = statements

    def __repr__(self):
        return f"Tome(statements={self.statements!r})"


class SummonRitual(ASTNode):
    """Represents ``var <name>;``."""
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"SummonRitual(name={self.name!r}, line={self.line})"


class BindingSpell(ASTNode):
    """Represents ``<name> = <expression>;``."""
    def __init__(self, name: str, value, line: int):
        self.name  = name
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"BindingSpell(name={self.name!r}, value={self.value!r}, line={self.line})"


class DivinationRitual(ASTNode):
    """Represents ``input <name>;``."""
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"DivinationRitual(name={self.name!r}, line={self.line})"


class CastingSpell(ASTNode):
    """Represents ``output <name>;``."""
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"CastingSpell(name={self.name!r}, line={self.line})"


class ArcaneFormula(ASTNode):
    """Represents a binary arithmetic operation."""
    def __init__(self, left, operator: str, right, line: int):
        self.left     = left
        self.operator = operator
        self.right    = right
        self.line     = line

    def __repr__(self):
        return (
            f"ArcaneFormula(left={self.left!r}, op={self.operator!r}, "
            f"right={self.right!r}, line={self.line})"
        )


class RuneStone(ASTNode):
    """Represents an integer literal."""
    def __init__(self, value: int, line: int):
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"RuneStone(value={self.value!r}, line={self.line})"


class Artifact(ASTNode):
    """Represents a variable reference in an expression."""
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"Artifact(name={self.name!r}, line={self.line})"


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    📜 The Sage

    Implements a recursive-descent parser that converts a flat token list
    into a hierarchical :class:`Tome` AST.
    """

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def parse(self) -> Tome:
        """Parse all tokens and return the root :class:`Tome` node."""
        statements = []
        while self._current().type != TokenType.END_OF_TOME:
            statements.append(self._statement())
        return Tome(statements)

    # ------------------------------------------------------------------
    # Token navigation helpers
    # ------------------------------------------------------------------

    def _current(self):
        return self.tokens[self.pos]

    def _advance(self):
        tok = self.tokens[self.pos]
        if tok.type != TokenType.END_OF_TOME:
            self.pos += 1
        return tok

    def _expect(self, token_type: str):
        """
        Consume and return the current token if it matches *token_type*,
        otherwise raise :class:`~errors.ParserError`.
        """
        tok = self._current()
        if tok.type != token_type:
            raise ParserError(
                f"Expected '{token_type}' but found '{tok.value!r}'",
                tok.line,
            )
        return self._advance()

    # ------------------------------------------------------------------
    # Grammar rules
    # ------------------------------------------------------------------

    def _statement(self):
        tok = self._current()

        if tok.type == TokenType.SUMMON:
            return self._var_decl()

        if tok.type == TokenType.DIVINE:
            return self._input_stmt()

        if tok.type == TokenType.CAST:
            return self._output_stmt()

        if tok.type == TokenType.ARTIFACT:
            return self._assignment()

        raise ParserError(
            f"Unexpected token {tok.value!r} — expected a statement",
            tok.line,
        )

    def _var_decl(self) -> SummonRitual:
        """``'var' IDENTIFIER ';'``"""
        var_tok  = self._expect(TokenType.SUMMON)
        name_tok = self._expect(TokenType.ARTIFACT)
        self._expect(TokenType.SEAL)
        return SummonRitual(name_tok.value, var_tok.line)

    def _assignment(self) -> BindingSpell:
        """``IDENTIFIER '=' expression ';'``"""
        name_tok = self._expect(TokenType.ARTIFACT)
        self._expect(TokenType.BIND)
        expr = self._expression()
        self._expect(TokenType.SEAL)
        return BindingSpell(name_tok.value, expr, name_tok.line)

    def _input_stmt(self) -> DivinationRitual:
        """``'input' IDENTIFIER ';'``"""
        kw_tok   = self._expect(TokenType.DIVINE)
        name_tok = self._expect(TokenType.ARTIFACT)
        self._expect(TokenType.SEAL)
        return DivinationRitual(name_tok.value, kw_tok.line)

    def _output_stmt(self) -> CastingSpell:
        """``'output' Artifact ';'``"""
        kw_tok   = self._expect(TokenType.CAST)
        name_tok = self._expect(TokenType.ARTIFACT)
        self._expect(TokenType.SEAL)
        return CastingSpell(name_tok.value, kw_tok.line)

    # Expression hierarchy enforces precedence:
    #   expression → term ( ('+' | '-') term )*
    #   term       → factor ( ('*' | '/') factor )*
    #   factor     → RuneStone | IDENTIFIER | '(' expression ')'

    def _expression(self):
        """Parse an additive expression."""
        left = self._term()
        while self._current().type in (TokenType.ENCHANT, TokenType.CURSE):
            op_tok = self._advance()
            right  = self._term()
            left   = ArcaneFormula(left, op_tok.value, right, op_tok.line)
        return left

    def _term(self):
        """Parse a multiplicative expression."""
        left = self._factor()
        while self._current().type in (TokenType.AMPLIFY, TokenType.SPLIT):
            op_tok = self._advance()
            right  = self._factor()
            left   = ArcaneFormula(left, op_tok.value, right, op_tok.line)
        return left

    def _factor(self):
        """Parse a primary / atomic expression."""
        tok = self._current()

        if tok.type == TokenType.RUNE_STONE:
            self._advance()
            return RuneStone(tok.value, tok.line)

        if tok.type == TokenType.ARTIFACT:
            self._advance()
            return Artifact(tok.value, tok.line)

        if tok.type == TokenType.OPEN_SCROLL:
            self._advance()  # consume '('
            expr = self._expression()
            self._expect(TokenType.CLOSE_SCROLL)
            return expr

        raise ParserError(
            f"Expected a number, variable, or '(' but found {tok.value!r}",
            tok.line,
        )
