"""
🎮 The Codex Session — REPL Engine & GUI Bridge
==================================================
Provides a persistent, stateful compiler session that can execute
Scroll-language statements one at a time.

Your GUI should:
    1. Create ONE ``CodexSession`` instance when the app starts.
    2. Call ``session.execute_line(line)`` each time the user submits input.
    3. Read the returned dict to display output, errors, or input prompts.

Group: DnD
"""

import re

from .scribe    import Lexer
from .sage      import Parser
from .archmage  import SemanticAnalyzer
from .enchanter import Interpreter
from .curses    import LexerError, ParserError, SemanticError, InterpreterError


class _InputRequested(Exception):
    """Internal signal — not a real error, just pauses execution for input."""
    def __init__(self, variable_name):
        self.variable_name = variable_name
        super().__init__(f"Input requested for '{variable_name}'")


class CodexSession:
    """
    🎮 A persistent Codex-DnD compiler session.

    Keeps the symbol table and declared-variable set alive across
    multiple calls so users can type one statement at a time, like:

        >> summon a;
        >> a = 5;
        >> cast a;
        5

    The GUI only needs to interact with THREE methods:
        - ``execute_line(line)``   — for normal statements
        - ``provide_input(value)`` — when a ``divine`` prompt is waiting
        - ``reset()``              — to wipe the session clean
    """

    def __init__(self):
        # Persistent state across lines
        self._outputs = []
        self._interpreter = Interpreter(
            input_fn=self._request_input,
            output_fn=lambda val: self._outputs.append(str(val)),
        )
        self._analyzer = SemanticAnalyzer()

        # Input handling
        self._waiting_for_input = False
        self._input_variable = None

    # ------------------------------------------------------------------
    # PUBLIC API — This is what the GUI calls
    # ------------------------------------------------------------------

    def execute_line(self, line: str) -> dict:
        """
        Execute a single line of Scroll code.

        Parameters
        ----------
        line : str
            One statement, e.g. ``"summon a;"`` or ``"cast a;"``

        Returns
        -------
        dict with keys:
            "success"           : bool
            "output"            : str or None
            "error"             : str or None
            "waiting_for_input" : bool
            "input_prompt"      : str or None
        """
        self._outputs = []

        try:
            # Phase 1 — The Scribe
            lexer  = Lexer(line)
            tokens = lexer.tokenize()

            # Phase 2 — The Sage
            parser = Parser(tokens)
            ast    = parser.parse()

            # Phase 3 — The Archmage (persistent declared set)
            self._analyzer.analyze(ast)

            # Phase 4 — The Enchanter (persistent symbol table)
            try:
                self._interpreter.execute(ast)
            except _InputRequested:
                return {
                    "success": True,
                    "output": None,
                    "error": None,
                    "waiting_for_input": True,
                    "input_prompt": f"🎲 Enter integer value for '{self._input_variable}'",
                }

            return {
                "success": True,
                "output": "\n".join(self._outputs) if self._outputs else None,
                "error": None,
                "waiting_for_input": False,
                "input_prompt": None,
            }

        except (LexerError, ParserError, SemanticError, InterpreterError) as exc:
            return {
                "success": False,
                "output": None,
                "error": str(exc),
                "waiting_for_input": False,
                "input_prompt": None,
            }

    def provide_input(self, value: str) -> dict:
        """
        Provide a value for a pending ``divine`` (input) prompt.

        Parameters
        ----------
        value : str
            The integer value the user typed in the GUI.

        Returns
        -------
        dict — same shape as ``execute_line()``.
        """
        if not self._waiting_for_input:
            return {
                "success": False,
                "output": None,
                "error": "⚡ The Enchanter's spell fizzles: No divine ritual is waiting for input",
                "waiting_for_input": False,
                "input_prompt": None,
            }

        self._waiting_for_input = False
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            return {
                "success": False,
                "output": None,
                "error": f"⚡ The Enchanter's spell fizzles: '{value}' is not a valid integer",
                "waiting_for_input": False,
                "input_prompt": None,
            }

        self._interpreter.symbol_table[self._input_variable] = int_val
        self._input_variable = None

        return {
            "success": True,
            "output": None,
            "error": None,
            "waiting_for_input": False,
            "input_prompt": None,
        }

    def reset(self) -> dict:
        """
        Reset the session — clear all variables and start fresh.
        """
        self._interpreter.symbol_table.clear()
        self._analyzer.declared.clear()
        self._analyzer.warnings.clear()
        self._waiting_for_input = False
        self._input_variable = None
        return {
            "success": True,
            "output": "🔄 The Codex has been wiped clean. All artifacts are banished.",
            "error": None,
            "waiting_for_input": False,
            "input_prompt": None,
        }

    def get_variables(self) -> dict:
        """
        Return all currently declared variables and their values.
        Useful for a GUI "variable inspector" panel.
        """
        return dict(self._interpreter.symbol_table)

    # ------------------------------------------------------------------
    # INTERNAL — intercepts divine (input) requests from the Enchanter
    # ------------------------------------------------------------------

    def _request_input(self, prompt: str) -> str:
        """
        Called by the Interpreter when a ``divine`` statement runs.
        Instead of blocking on stdin, we flag that we need input
        and raise an exception to pause execution.
        """
        match = re.search(r"'(\w+)'", prompt)
        var_name = match.group(1) if match else "unknown"

        self._waiting_for_input = True
        self._input_variable = var_name
        raise _InputRequested(var_name)