# Changelog

Modernisation of the 2019 Python notes to Python 3.12+.
Baseline: commit `b0537f6` (original 2019 content, unmodified).

Format: one section per folder, listing what was **updated**, **added**, and **fixed**.

---

## Root

**Added**
- `README.md` — curriculum map, how to run, conventions used across the notes
- `CHANGELOG.md` — this file
- `.gitignore` — excludes `__pycache__/`, `.ipynb_checkpoints/`, bundled `.exe`/`.whl` binaries

---

## 01 Basic

All 5 notebooks retargeted from Python 3.7 to **3.12+**, stale 2019 outputs cleared,
standard header (prerequisites / what you'll learn) and closing
**Common Mistakes -> Best Practices -> Exercises** block added to each.

### `1.0 About Programming.ipynb` — 3 cells -> 16
**Added**
- Compiled vs interpreted, with a recipe/translator analogy and a comparison table
- "What an instruction looks like at each level" (machine / assembly / Python)
- "Why learn Python specifically" — the domains it actually wins in
- First runnable cells: `Hello, world!`, a formatted-output example, `import this`
- Common Mistakes / Best Practices / Exercises

**Fixed**
- Removed 2 empty trailing code cells (the notebook had no runnable content at all)
- Split one 2.6 KB markdown blob into teachable sections

### `1.1 Introduction to Python.ipynb` — 21 cells -> 25
**Fixed**
- 🔴 **Factual error:** the static-vs-dynamic typing definitions were **inverted** —
  the notes claimed static-typed languages "need not define variables before use" and
  dynamic-typed ones "must necessarily define" them. Both sections rewritten correctly.
- 6 `raw` cells (C / Java / PHP / Python snippets) converted to fenced markdown so they
  render with syntax highlighting instead of as unstyled plain text

**Updated**
- **"Python 2.x Vs Python 3.x" section replaced** with "Python versions: what changed,
  and what to target" — release cadence, a 3.6→3.14 feature table, and a table of
  removals (`distutils`, `imp`, `asyncio.coroutine`, `assertEquals`)
- Install section: `py` launcher, macOS/Homebrew and Debian/Ubuntu instructions,
  verification commands, warning about building on the system Python
- Dev-environment section: added **VS Code**, plus a `.py` vs `.ipynb` comparison table
  and a note on out-of-order cell execution

**Added**
- Live version-check code cell (`sys.version_info`, feature guarding)
- Dedicated **REPL** section incl. the 3.13 rewritten-REPL version note
- Note that Python's *dynamic* typing is orthogonal to its *strong* typing

### `1.2 Python Basic.ipynb` — 49 cells -> 61
**Fixed**
- 🔴 The notes taught `'''...'''` as a multiline comment. It is a **string expression**;
  added a correction explaining `#` vs docstrings.
- 🔴 "Python allocates the same memory location to variables with the same value" was
  stated as a general rule. It is **CPython small-integer caching** (-5..256) plus string
  interning. Added a correction with a runnable demonstration of where it breaks.

**Added**
- **Hard keywords vs soft keywords** (3.10+) — why adding `match`/`case` didn't break
  existing code; `keyword.softkwlist` generated live so the cell never goes stale
- **PEP 8 naming conventions** table + runnable example, incl. builtin-shadowing demo
- **Modern literal forms** — underscore separators (`1_400_000_000`), `0b`/`0o`/`0x`
  prefixes, scientific and complex literals

### `1.3 Python Input Output.ipynb` — 19 cells -> 36
**Fixed**
- 🔴 **Security:** `eval(input())` was taught as a normal technique for reading typed
  input. Rewritten with an explicit warning (arbitrary code execution), a demonstration,
  and a table of correct alternatives — `int()`, **`ast.literal_eval()`**, `json.loads()`.
  The safe replacement cell is runnable.
- 🔴 Incorrect note claiming "conversion from int to string is not possible". Corrected:
  `str(7)` works; what fails is `int("abc")`.

**Added**
- All four `print()` parameters (`sep`, `end`, `file`, `flush`) with a table and examples
- **Formatting section**: f-string syntax breakdown, format specs (`.2f`, `,`, `%`,
  alignment, zero-padding), `{value=}` debugging (3.8+), `!r`
- Aligned invoice-style table example using only format specs
- `.format()` and `%` shown once, explicitly labelled legacy, with guidance on when
  `.format()` is still the right call
- **Input validation loop** — `try` / `except ValueError` / range check / `.strip()`
- Defensive `.split()` unpacking (field-count check) alongside the original

### `1.4 Python Operators.ipynb` — 38 cells -> 52
**Fixed**
- 🔴 `print(num1 is 10)` raises **`SyntaxWarning: "is" with a literal`** on Python 3.8+.
  Replaced with a correct `==` comparison plus an explanation of the three valid uses of `is`.
- Pre-existing `IndentationError` in the operator-precedence cell (stray leading space) —
  the cell could never have run as written.

**Added**
- **Division section**: `/` vs `//` vs `%` vs `**`, the negative-number floor-vs-truncate
  trap (`-7 // 2` is `-4` in Python, `-3` in C/Java), the `(a//b)*b + (a%b) == a` identity,
  `divmod()`, and right-associativity of `**`
- **Walrus operator `:=`** (3.8+) — syntax breakdown, why `if x = 5:` is a SyntaxError,
  loop / comprehension / file-chunk examples
- **Chained comparisons** (`18 <= age <= 65`) and why other languages can't do this
- **Short-circuit evaluation** — guard clauses, and the fact that `and`/`or` return an
  *operand* rather than a boolean (the `name or "anonymous"` idiom)
- **`is` vs `==`** section with a comparison table, banknote analogy, mutation-through-
  alias demo, float-equality trap (`math.isclose`, `decimal.Decimal`)

### Verification
- All 5 notebooks parse as valid `nbformat` 4
- All 80 code cells compile cleanly
- All 67 non-interactive code cells **execute without error** on Python 3.14.4
  with `warnings.simplefilter("error")`
