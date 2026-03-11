# ⚔️ Codex-DnD — The Arcane Compiler ⚔️

> *"In the age before machines could think, brave scholars forged the Codex — a mystical tome that transforms ancient scrolls into executable incantations."*

**Group: DnD**

A D&D-themed compiler for a custom programming language, written entirely in Python. Write your programs in `.scroll` files and let the Codex translate them through four magical phases: lexical analysis, syntax analysis, semantic analysis, and interpretation.

---

## 🗺️ Table of Contents

- [Overview](#overview)
- [Compiler Phases](#compiler-phases)
- [Language Specification](#language-specification)
- [Grammar Reference](#grammar-reference)
- [Installation & Usage](#installation--usage)
- [Example Programs](#example-programs)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Credits](#credits)

---

## Overview

The Codex-DnD compiler translates programs written in the **Scroll language** — a simple, D&D-flavored programming language — into results. It supports:

- Integer variables
- Arithmetic with correct operator precedence
- Console input and output
- Multi-line block comments
- Meaningful, D&D-themed error messages

---

## Compiler Phases

| Phase | D&D Name | File | Description |
|-------|----------|------|-------------|
| 1. Lexical Analysis | 🪶 **The Scribe** | `src/scribe.py` | Reads the source scroll and identifies runes (tokens) |
| 2. Syntax Analysis | 📜 **The Sage** | `src/sage.py` | Interprets the structure of the spell — builds an AST |
| 3. Semantic Analysis | 🔮 **The Archmage** | `src/archmage.py` | Validates the spell's logic — type checking, declarations |
| 4. Interpretation | ⚡ **The Enchanter** | `src/enchanter.py` | Forges the final incantation — executes the program |
| Errors | 💀 **Curses** | `src/curses.py` | D&D-themed error messages for each phase |

### Error Message Examples

```
🔥 Curse of the Unknown Rune: Unexpected character '&' at line 3, column 5
📜 The Sage is confused: Expected ';' after statement at line 2
🔮 The Archmage senses a disturbance: Variable 'x' was never summoned (declared) — line 5
⚡ The Enchanter's spell fizzles: Division by zero at line 4
```

---

## Language Specification

1. **All statements end with a seal, a semicolon (`;`).**
2. **Whitespace is not significant** — `a+b` is the same as `a + b`.
3. **Comments** begin with `/*` and end with `*/` and can span multiple lines.
4. **Keywords**: `summon`, `divine`, `cast`
   - `summon` — declares a new integer variable. Variables must be declared before use.
   - `divine` — reads an integer value from the console into a variable.
   - `cast` — prints the value of a variable to the console.
5. **All variables are integers.**
6. **Operators**: `+`, `-`, `*`, `/`, `=`. Parentheses `()` may be used to force precedence.
7. **Variable names**: Letters, underscores, and digits only. Must not start with a digit.

---

## Grammar Reference

```ebnf
tome              ::= incantation* END_OF_TOME
incantation       ::= summon_ritual | binding_spell | divination_ritual | casting_spell
summon_ritual     ::= 'summon' ARTIFACT ';'
binding_spell     ::= ARTIFACT '=' arcane_formula ';'
divination_ritual ::= 'divine' ARTIFACT ';'
casting_spell     ::= 'cast' ARTIFACT ';'
arcane_formula    ::= power_term ( ('+' | '-') power_term )*
power_term        ::= rune ( ('*' | '/') rune )*
rune              ::= RUNE_STONE | ARTIFACT | '(' arcane_formula ')'
ARTIFACT          ::= [a-zA-Z_][a-zA-Z_0-9]*
RUNE_STONE        ::= [0-9]+
```

---

## Installation & Usage

### Requirements

- Python 3.8 or higher
- No external dependencies — stdlib only!

### Run a Scroll

```bash
# Run a .scroll source file
python -m src.main examples/hello.scroll

# Print the token list (debug)
python -m src.main examples/hello.scroll --tokens

# Print the AST (debug)
python -m src.main examples/hello.scroll --ast

# Read from stdin
echo "var x; x = 7; output x;" | python -m src.main
```

---

## Example Programs

### `examples/hello.scroll`

```scroll
/* The simplest scroll — hello world for the Codex */
summon x;
x = 42;
cast x;
```

**Output:** `42`

### `examples/arithmetic.scroll`

```scroll
summon a;
summon b;
summon result;
a = 10;
b = 3;
result = a + b * 2;
cast result;
```

**Output:** `16`  *(multiplication before addition)*

### `examples/input_output.scroll`

```scroll
summon name_value;
divine name_value;
summon doubled;
doubled = name_value * 2;
cast doubled;
```

**Interaction:**
```
🎲 Enter integer value for 'name_value': 5
10
```

### `examples/comments.scroll`

```scroll
/* Multi-line comment
   spanning several lines */
summon x; /* inline comment */
x = 7; /* lucky number */
cast x;
```

**Output:** `7`

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover tests/

# Run individual test modules
python -m unittest tests.test_lexer
python -m unittest tests.test_parser
python -m unittest tests.test_semantic
python -m unittest tests.test_interpreter
```

---

## Project Structure

```
Codex-DnD/
├── README.md                   # This file
├── requirements.txt            # No external dependencies
├── src/
│   ├── __init__.py
│   ├── curses.py               # 💀 Curses — D&D-themed exceptions
│   ├── scribe.py                # 🪶 The Scribe — lexical analysis
│   ├── sage.py               # 📜 The Sage — syntax analysis / AST
│   ├── archmage.py             # 🔮 The Archmage — semantic analysis
│   ├── enchanter.py          # ⚡ The Enchanter — execution engine
│   └── main.py                 # 🎮 The Codex — main CLI entry point
├── tests/
│   ├── __init__.py
│   ├── test_lexer.py           # Unit tests for The Scribe
│   ├── test_parser.py          # Unit tests for The Sage
│   ├── test_semantic.py        # Unit tests for The Archmage
│   └── test_interpreter.py    # Unit tests for The Enchanter
└── examples/
    ├── hello.scroll            # Simple hello world
    ├── arithmetic.scroll       # Arithmetic & precedence
    ├── input_output.scroll     # Reading from console
    └── comments.scroll         # Multi-line comments
```

---

## Credits

**Group: DnD**

Built with 🐉 and ⚔️ as a D&D-themed compiler project.

> *"May your scrolls compile without curses, and your spells execute without fizzling."*
