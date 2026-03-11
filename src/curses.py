"""
💀 Curses — D&D-Themed Error Definitions
=========================================
Custom exception classes for each phase of the Codex-DnD compiler.

Group: DnD
"""


class LexerError(Exception):
    """🔥 Curse of the Unknown Rune — raised by The Scribe (lexer) on invalid input."""

    def __init__(self, message: str, line: int = None, column: int = None):
        self.line = line
        self.column = column
        if line is not None and column is not None:
            full_message = (
                f"🔥 Curse of the Unknown Rune: {message} "
                f"at line {line}, column {column}"
            )
        elif line is not None:
            full_message = f"🔥 Curse of the Unknown Rune: {message} at line {line}"
        else:
            full_message = f"🔥 Curse of the Unknown Rune: {message}"
        super().__init__(full_message)


class ParserError(Exception):
    """📜 The Sage's Confusion — raised by The Sage (parser) on invalid syntax."""

    def __init__(self, message: str, line: int = None):
        self.line = line
        if line is not None:
            full_message = f"📜 The Sage is confused: {message} at line {line}"
        else:
            full_message = f"📜 The Sage is confused: {message}"
        super().__init__(full_message)


class SemanticError(Exception):
    """🔮 The Archmage's Warning — raised by The Archmage (semantic analyzer)."""

    def __init__(self, message: str, line: int = None):
        self.line = line
        if line is not None:
            full_message = (
                f"🔮 The Archmage senses a disturbance: {message} — line {line}"
            )
        else:
            full_message = f"🔮 The Archmage senses a disturbance: {message}"
        super().__init__(full_message)


class InterpreterError(Exception):
    """⚡ The Enchanter's Fizzle — raised by The Enchanter (interpreter) at runtime."""

    def __init__(self, message: str, line: int = None):
        self.line = line
        if line is not None:
            full_message = (
                f"⚡ The Enchanter's spell fizzles: {message} at line {line}"
            )
        else:
            full_message = f"⚡ The Enchanter's spell fizzles: {message}"
        super().__init__(full_message)
