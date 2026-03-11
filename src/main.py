"""
🎮 The Codex — Main Entry Point
=================================
Ties all compiler phases together and exposes a command-line interface.

Usage:
    python -m src.main <scroll_file> [--tokens] [--ast]
    python -m src.main --help

Flags:
    --tokens   Print the token list produced by The Scribe and exit.
    --ast      Print the AST produced by The Sage and exit.

Group: DnD
"""

import argparse
import sys

from .curses      import LexerError, ParserError, SemanticError, InterpreterError
from .scribe       import Lexer
from .sage      import Parser
from .archmage    import SemanticAnalyzer
from .enchanter import Interpreter


BANNER = """\
╔══════════════════════════════════════════════════════════╗
║   ⚔️   Welcome to the Codex of DnD — The Arcane Compiler ⚔️   ║
║              Group: DnD  |  Python Edition               ║
╚══════════════════════════════════════════════════════════╝"""


def compile_and_run(source: str, print_tokens: bool = False, print_ast: bool = False) -> None:
    """
    Run the full compilation pipeline on *source*.

    Parameters
    ----------
    source:
        Raw source code string.
    print_tokens:
        When ``True`` print tokens and return without further processing.
    print_ast:
        When ``True`` print the AST and return without executing.
    """
    # ------------------------------------------------------------------
    # Phase 1 — 🪶 The Scribe: Lexical Analysis
    # ------------------------------------------------------------------
    lexer  = Lexer(source)
    tokens = lexer.tokenize()

    if print_tokens:
        print("\n🪶 The Scribe's Token Scroll:")
        for tok in tokens:
            print(f"  {tok}")
        return

    # ------------------------------------------------------------------
    # Phase 2 — 📜 The Sage: Syntax Analysis
    # ------------------------------------------------------------------
    parser = Parser(tokens)
    ast    = parser.parse()

    if print_ast:
        print("\n📜 The Sage's Arcane Syntax Tree:")
        _print_ast(ast)
        return

    # ------------------------------------------------------------------
    # Phase 3 — 🔮 The Archmage: Semantic Analysis
    # ------------------------------------------------------------------
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    for warning in analyzer.warnings:
        print(warning, file=sys.stderr)

    # ------------------------------------------------------------------
    # Phase 4 — ⚡ The Enchanter: Execution
    # ------------------------------------------------------------------
    interpreter = Interpreter()
    interpreter.execute(ast)


def _print_ast(node, indent: int = 0) -> None:
    """Recursively pretty-print an AST node."""
    prefix = "  " * indent
    name   = type(node).__name__

    if hasattr(node, "statements"):
        print(f"{prefix}{name}:")
        for child in node.statements:
            _print_ast(child, indent + 1)
    elif hasattr(node, "value") and hasattr(node, "name"):
        # Assignment
        print(f"{prefix}{name}(name={node.name!r}, line={node.line}):")
        _print_ast(node.value, indent + 1)
    elif hasattr(node, "left") and hasattr(node, "right"):
        # BinaryOp
        print(f"{prefix}{name}(op={node.operator!r}, line={node.line}):")
        _print_ast(node.left,  indent + 1)
        _print_ast(node.right, indent + 1)
    elif hasattr(node, "name"):
        print(f"{prefix}{name}(name={node.name!r}, line={node.line})")
    elif hasattr(node, "value"):
        print(f"{prefix}{name}(value={node.value!r}, line={node.line})")
    else:
        print(f"{prefix}{name}")


def main(argv=None) -> int:
    """Parse command-line arguments and execute the compiler pipeline."""
    print(BANNER)

    arg_parser = argparse.ArgumentParser(
        prog="codex-dnd",
        description="⚔️  Codex-DnD: A D&D-themed compiler for the Scroll language.",
    )
    arg_parser.add_argument(
        "scroll",
        nargs="?",
        help="Path to the .scroll source file (omit to read from stdin)",
    )
    arg_parser.add_argument(
        "--tokens",
        action="store_true",
        help="Print the token list (The Scribe's output) and exit",
    )
    arg_parser.add_argument(
        "--ast",
        action="store_true",
        help="Print the AST (The Sage's output) and exit",
    )

    args = arg_parser.parse_args(argv)

    # Read source
    if args.scroll:
        try:
            with open(args.scroll, "r", encoding="utf-8") as fh:
                source = fh.read()
        except FileNotFoundError:
            print(
                f"💀 The Codex cannot find the scroll: '{args.scroll}'",
                file=sys.stderr,
            )
            return 1
    else:
        print("📖 Reading scroll from stdin (press Ctrl-D / Ctrl-Z to finish):")
        source = sys.stdin.read()

    try:
        compile_and_run(source, print_tokens=args.tokens, print_ast=args.ast)
    except (LexerError, ParserError, SemanticError, InterpreterError) as exc:
        print(exc, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
