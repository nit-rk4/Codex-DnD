"""
⚡ The Enchanter — Interpreter / Code Execution
=================================================
Walks the AST and executes the Codex-DnD program.

Responsibilities:
  - Maintain a symbol table (variable store) for integer variables.
  - Implement ``var`` (declare), ``=`` (assign), ``input`` (read), ``output`` (print).
  - Evaluate arithmetic expressions with correct operator precedence.
  - Raise D&D-themed runtime errors for illegal operations.

Group: DnD
"""

from .curses import InterpreterError
from .sage import (
    Tome, SummonRitual, BindingSpell, DivinationRitual, CastingSpell,
    ArcaneFormula, RuneStone, Artifact,
)


class Interpreter:
    """
    ⚡ The Enchanter

    Executes a Codex-DnD AST produced by The Sage.

    Parameters
    ----------
    input_fn:
        Callable used to read user input (defaults to :func:`input`).
        Provided as a parameter so tests can supply mock implementations.
    output_fn:
        Callable used to produce output (defaults to :func:`print`).
    """

    def __init__(self, input_fn=None, output_fn=None):
        self.symbol_table: dict = {}         # name → int value
        self._input_fn  = input_fn  or input
        self._output_fn = output_fn or print

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(self, node) -> None:
        """Recursively execute *node*."""
        method = f"_execute_{type(node).__name__}"
        visitor = getattr(self, method, self._generic_execute)
        visitor(node)

    def evaluate(self, node) -> int:
        """Recursively evaluate an expression *node* and return its integer value."""
        method = f"_evaluate_{type(node).__name__}"
        visitor = getattr(self, method, self._generic_evaluate)
        return visitor(node)

    # ------------------------------------------------------------------
    # Statement executors
    # ------------------------------------------------------------------

    def _execute_Tome(self, node: Tome) -> None:
        for stmt in node.statements:
            self.execute(stmt)

    def _execute_SummonRitual(self, node: SummonRitual) -> None:
        # Initialise to 0 — the uninitialised artifact rests dormant.
        self.symbol_table[node.name] = 0

    def _execute_BindingSpell(self, node: BindingSpell) -> None:
        value = self.evaluate(node.value)
        if node.name not in self.symbol_table:
            raise InterpreterError(
                f"Variable '{node.name}' was never summoned (declared)",
                node.line,
            )
        self.symbol_table[node.name] = value

    def _execute_DivinationRitual(self, node: DivinationRitual) -> None:
        if node.name not in self.symbol_table:
            raise InterpreterError(
                f"Variable '{node.name}' was never summoned (declared)",
                node.line,
            )
        raw = self._input_fn(f"🎲 Enter integer value for '{node.name}': ")
        try:
            self.symbol_table[node.name] = int(raw)
        except (ValueError, TypeError):
            raise InterpreterError(
                f"'{raw}' is not a valid integer — only whole numbers may be conjured",
                node.line,
            )

    def _execute_CastingSpell(self, node: CastingSpell) -> None:
        if node.name not in self.symbol_table:
            raise InterpreterError(
                f"Variable '{node.name}' was never summoned (declared)",
                node.line,
            )
        self._output_fn(self.symbol_table[node.name])

    # ------------------------------------------------------------------
    # Expression evaluators
    # ------------------------------------------------------------------

    def _evaluate_RuneStone(self, node: RuneStone) -> int:
        return node.value

    def _evaluate_Artifact(self, node: Artifact) -> int:
        if node.name not in self.symbol_table:
            raise InterpreterError(
                f"Variable '{node.name}' was never summoned (declared)",
                node.line,
            )
        return self.symbol_table[node.name]

    def _evaluate_ArcaneFormula(self, node: ArcaneFormula) -> int:
        left  = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if node.operator == "+":
            return left + right
        if node.operator == "-":
            return left - right
        if node.operator == "*":
            return left * right
        if node.operator == "/":
            if right == 0:
                raise InterpreterError(
                    "Division by zero — the enchantment collapses",
                    node.line,
                )
            return left // right  # integer division

        raise InterpreterError(
            f"Unknown operator '{node.operator}'",
            node.line,
        )

    # ------------------------------------------------------------------
    # Fallbacks
    # ------------------------------------------------------------------

    def _generic_execute(self, node) -> None:
        raise InterpreterError(
            f"The Enchanter cannot execute '{type(node).__name__}'"
        )

    def _generic_evaluate(self, node) -> int:
        raise InterpreterError(
            f"The Enchanter cannot evaluate '{type(node).__name__}'"
        )
