"""
🔮 The Archmage — Semantic Analysis
=====================================
Walks the AST produced by The Sage and validates semantic rules:

  1. Variables must be declared with ``summon`` before being used.
  2. Variables must not be declared more than once.
  3. Division by a literal zero is warned about at compile time.

Group: DnD
"""

from .curses import SemanticError
from .sage import (
    Tome, SummonRitual, BindingSpell, DivinationRitual, CastingSpell,
    ArcaneFormula, RuneStone, Artifact,
)


class SemanticAnalyzer:
    """
    🔮 The Archmage

    Performs a single-pass walk over the AST, maintaining a set of declared
    variable names and verifying usage rules.
    """

    def __init__(self):
        self.declared: set = set()   # names declared with 'var'
        self.warnings: list = []     # non-fatal advisory messages

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyze(self, node) -> None:
        """
        Recursively analyze *node*.  Raises :class:`~errors.SemanticError`
        on fatal violations; appends advisory messages to :attr:`warnings`.
        """
        method = f"_analyze_{type(node).__name__}"
        visitor = getattr(self, method, self._generic_analyze)
        visitor(node)

    # ------------------------------------------------------------------
    # Node visitors
    # ------------------------------------------------------------------

    def _analyze_Tome(self, node: Tome) -> None:
        for stmt in node.statements:
            self.analyze(stmt)

    def _analyze_SummonRitual(self, node: SummonRitual) -> None:
        if node.name in self.declared:
            raise SemanticError(
                f"Variable '{node.name}' has already been summoned (declared) — "
                "duplicate declarations are forbidden",
                node.line,
            )
        self.declared.add(node.name)

    def _analyze_BindingSpell(self, node: BindingSpell) -> None:
        if node.name not in self.declared:
            raise SemanticError(
                f"Variable '{node.name}' was never summoned (declared) before assignment",
                node.line,
            )
        self.analyze(node.value)

    def _analyze_DivinationRitual(self, node: DivinationRitual) -> None:
        if node.name not in self.declared:
            raise SemanticError(
                f"Variable '{node.name}' was never summoned (declared) before input",
                node.line,
            )

    def _analyze_CastingSpell(self, node: CastingSpell) -> None:
        if node.name not in self.declared:
            raise SemanticError(
                f"Variable '{node.name}' was never summoned (declared) before output",
                node.line,
            )

    def _analyze_ArcaneFormula(self, node: ArcaneFormula) -> None:
        self.analyze(node.left)
        self.analyze(node.right)
        # Division-by-literal-zero warning
        if node.operator == "/" and isinstance(node.right, RuneStone) and node.right.value == 0:
            self.warnings.append(
                f"🔮 The Archmage warns: Division by zero detected in scroll "
                f"at line {node.line} — this spell will fizzle at runtime"
            )

    def _analyze_Artifact(self, node: Artifact) -> None:
        if node.name not in self.declared:
            raise SemanticError(
                f"Variable '{node.name}' was never summoned (declared)",
                node.line,
            )

    def _analyze_RuneStone(self, node: RuneStone) -> None:  # noqa: D102
        pass  # Rune Stones need no validation

    def _generic_analyze(self, node) -> None:
        raise SemanticError(
            f"The Archmage does not recognise the incantation '{type(node).__name__}'"
        )
