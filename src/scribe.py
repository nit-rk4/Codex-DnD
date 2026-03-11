"""
🪶 The Scribe — Lexical Analysis
==================================
Tokenizes Codex-DnD source code into a stream of tokens.

Token types:
    SUMMON, DIVINE, CAST                    — keywords
    ARTIFACT                                — variable names
    RUNE_STONE                              — integer literals
    ENCHANT, CURSE, AMPLIFY, SPLIT          — arithmetic operators
    BIND                                    — assignment operator (=)
    SEAL                                    — statement terminator (;)
    OPEN_SCROLL, CLOSE_SCROLL               — parentheses
    END_OF_TOME                              — end of file sentinel

Group: DnD
"""

from .curses import LexerError


# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------

class TokenType:
    """Enumeration of all token types recognised by The Scribe."""
    SUMMON       = "SUMMON"
    DIVINE       = "DIVINE"
    CAST         = "CAST"
    ARTIFACT     = "ARTIFACT"
    RUNE_STONE   = "RUNE_STONE"
    ENCHANT      = "ENCHANT"
    CURSE        = "CURSE"
    AMPLIFY      = "AMPLIFY"
    SPLIT        = "SPLIT"
    BIND         = "BIND"
    SEAL         = "SEAL"
    OPEN_SCROLL  = "OPEN_SCROLL"
    CLOSE_SCROLL = "CLOSE_SCROLL"
    END_OF_TOME  = "END_OF_TOME"


KEYWORDS = {
    "summon":    TokenType.SUMMON,
    "divine":  TokenType.DIVINE,
    "cast": TokenType.CAST,
}


# ---------------------------------------------------------------------------
# Token dataclass
# ---------------------------------------------------------------------------

class Token:
    """A single lexical unit produced by The Scribe."""

    __slots__ = ("type", "value", "line", "column")

    def __init__(self, type_: str, value, line: int, column: int):
        self.type   = type_
        self.value  = value
        self.line   = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.column})"


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    """
    🪶 The Scribe

    Reads raw source text and produces a list of :class:`Token` objects.
    Whitespace is ignored and multi-line ``/* ... */`` comments are skipped.
    """

    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0          # current character index
        self.line    = 1
        self.column  = 1

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def tokenize(self) -> list:
        """Return the complete list of tokens for the source text."""
        tokens = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type == TokenType.END_OF_TOME:
                break
        return tokens

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current(self):
        """Return the character at the current position, or ``None`` at EOF."""
        return self.source[self.pos] if self.pos < len(self.source) else None

    def _peek(self):
        """Return the character one position ahead, or ``None`` at EOF."""
        pos = self.pos + 1
        return self.source[pos] if pos < len(self.source) else None

    def _advance(self):
        """Consume the current character and move to the next one."""
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line   += 1
            self.column  = 1
        else:
            self.column += 1
        return ch

    def _skip_whitespace(self):
        """Skip all whitespace characters (spaces, tabs, newlines)."""
        while self._current() is not None and self._current() in " \t\r\n":
            self._advance()

    def _skip_comment(self):
        """
        Skip a ``/* ... */`` block comment.

        Raises :class:`~errors.LexerError` if the comment is never closed.
        """
        start_line   = self.line
        start_column = self.column
        # consume '/*'
        self._advance()  # '/'
        self._advance()  # '*'
        while self._current() is not None:
            if self._current() == "*" and self._peek() == "/":
                self._advance()  # '*'
                self._advance()  # '/'
                return
            self._advance()
        raise LexerError(
            "Unterminated comment scroll — the '*/' seal is missing",
            start_line,
            start_column,
        )

    def _read_number(self) -> Token:
        """Consume a sequence of digits and return a NUMBER token."""
        start_col = self.column
        digits = []
        while self._current() is not None and self._current().isdigit():
            digits.append(self._advance())
        return Token(TokenType.RUNE_STONE, int("".join(digits)), self.line, start_col)

    def _read_identifier_or_keyword(self) -> Token:
        """
        Consume a word (letters, digits, underscores) and return either
        a keyword token (VAR / INPUT / OUTPUT) or an IDENTIFIER token.
        """
        start_col = self.column
        chars = []
        while self._current() is not None and (
            self._current().isalpha()
            or self._current().isdigit()
            or self._current() == "_"
        ):
            chars.append(self._advance())
        word = "".join(chars)
        tok_type = KEYWORDS.get(word, TokenType.ARTIFACT)
        return Token(tok_type, word, self.line, start_col)

    def _next_token(self) -> Token:
        """Produce and return the next token from the source stream."""
        # Skip whitespace and comments (comments begin with /*)
        while True:
            self._skip_whitespace()
            if self._current() == "/" and self._peek() == "*":
                self._skip_comment()
            else:
                break

        if self._current() is None:
            return Token(TokenType.END_OF_TOME, None, self.line, self.column)

        ch        = self._current()
        line      = self.line
        col       = self.column

        # Digits → NUMBER
        if ch.isdigit():
            return self._read_number()

        # Letters / underscore → identifier or keyword
        if ch.isalpha() or ch == "_":
            return self._read_identifier_or_keyword()

        # Single-character tokens
        single = {
            "+": TokenType.ENCHANT,
            "-": TokenType.CURSE,
            "*": TokenType.AMPLIFY,
            "/": TokenType.SPLIT,
            "=": TokenType.BIND,
            ";": TokenType.SEAL,
            "(": TokenType.OPEN_SCROLL,
            ")": TokenType.CLOSE_SCROLL,
        }
        if ch in single:
            self._advance()
            return Token(single[ch], ch, line, col)

        # Unknown character — cast a curse
        self._advance()
        raise LexerError(
            f"Unexpected character {ch!r}",
            line,
            col,
        )
