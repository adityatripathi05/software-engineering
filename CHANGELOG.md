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

---

## 02 Datatypes

8 notebooks -> 9 (one new). All retargeted to **3.12+**, outputs cleared, standard header
and **Common Mistakes / Best Practices / Exercises** block added to each.

### Errors fixed in existing content
- 🔴 **2.1** — the immutable-types list included **`long`**, a Python 2 type that does not
  exist in Python 3. `frozenset` and `bytes` were missing. Table corrected.
- 🔴 **2.1** — "Other String Methods" linked to the **Python 2.4** documentation. Updated to
  the Python 3 reference.
- 🔴 **2.4** — the `array` typecode table listed **`'c'` (character, 1 byte)**, removed in
  Python 3. Table replaced with the current codes.
- 🔴 **2.5** — cell 48 contained `data3.setdefault('num,'CBSE')`: mismatched quotes, a
  `SyntaxError`. The cell could never have run. Corrected.
- 🔴 **2.5** — the opening line described dictionaries as **"unordered"**. Insertion order
  has been a language guarantee since **Python 3.7**. Rewritten with a version note.
- **2.2** — "Precision Handling" taught `%` formatting first; reordered around f-strings.

### `2.1 Python Strings Datatype.ipynb` — 85 -> 99 cells
**Added:** immutability demo with `id()`; guidance table on which of the four formatting
styles to use; `casefold()` and `partition()`; **`removeprefix()`/`removesuffix()` (3.9+)**
with the `strip()`-eats-too-much trap; **`join()` vs `+=` O(n²) benchmark**; expanded
`str` vs `bytes` section with encode/decode, mojibake and `bytearray`.

### `2.2 Python Numeric Datatype.ipynb` — 51 -> 64 cells
**Added:** complex numbers and the numeric tower; float-representation reality
(`0.1 + 0.2`, `math.isclose`); **banker's rounding**; **`decimal.Decimal`** for money and
**`fractions.Fraction`** for exact ratios; `int` unlimited precision vs float overflow to
`inf`; `nan` semantics; expanded `None` (sentinel, `is None`, `if not x` vs `is None`) and
`bool` (truthiness table, `bool` subclasses `int`).
**Fixed:** the empty cell under "Calculate Area and Perimeter of Rectangle" now contains
the promised solution. Cross-reference added to 1.4 for the duplicated operator drills.

### `2.3 Python Tuple Datatype.ipynb` — 36 -> 49 cells
**Added:** the single-element `(5)` vs `(5,)` trap; full **unpacking** section (basic,
starred, nested, `_`, in loops); "immutable means the bindings are fixed, not the contents"
with a hashability demo; **`namedtuple` and `typing.NamedTuple`** for self-documenting
records.

### `2.4 Python List-Array Datatype.ipynb` — 85 -> 96 cells
**Added:** slice assignment and deletion, `a[:] = [...]` vs `a = [...]`; shallow-copy
warning with pointer to 2.7; **three classic traps** (mutating while iterating,
`[[0]*3]*3` aliasing, `remove`/`del`/`pop`); **`sorted()` vs `.sort()`** with the
`x = lst.sort()` bug, `key=`, `itemgetter`, multi-key sorting and sort stability.
**Rewrote:** the `array` section now explains when to use `list` / `array` / NumPy.

### `2.5 Python Dictionary Datatype.ipynb` — 56 -> 68 cells
**Added:** `in` checks keys (with an O(1) vs O(n) benchmark); **dict views are live**, plus
set operations on key views and the mutate-during-iteration `RuntimeError`; **`|` and `|=`
merge operators (3.9+)** compared against `{**a, **b}` and `.update()`; `get()` vs
`setdefault()`; **`defaultdict` and `Counter`**.
**Note:** the three username/password programs were kept rather than merged — they form a
deliberate progression. A warning was added that they store plain-text passwords, which is
unacceptable outside a teaching example.

### `2.6 Python Sets Datatype.ipynb` — 25 -> 35 cells *(largest rewrite in this folder)*
Had only 5 markdown cells — essentially an unexplained method list.
**Added:** proper conceptual opening (three defining properties, guest-list analogy, what
sets are actually for); why membership is O(1), with a benchmark; set-operation tables
mapped to Venn diagrams; **mutating vs non-mutating twins** for every operation, and the
operator-vs-method difference; `add()` vs `update()` on a string; **`frozenset`**;
**set comprehensions**; real-world deduplication with and without order preservation;
set-difference for "what changed between two states".

### `2.7 Mutability, Copying, Nesting and Unpacking.ipynb` — **NEW**, 24 cells
Closes the "nested structures, slicing, unpacking / mutable vs immutable, copy vs
deepcopy" gap in the curriculum checklist. Covers: names vs objects vs values; aliasing;
rebinding vs mutating (incl. `a += b` vs `a = a + b`); mutable vs immutable; **shallow vs
`copy.deepcopy()`**; the **mutable default argument** trap; **hashability** as the rule
behind dict keys; building and safely navigating nested structures (`get_nested` helper);
and unpacking in every form including `*`/`**` at call sites.

### Structural changes
- `Student Management System.ipynb` moved from `02 Datatypes/` to
  `14 Project/Student Management System/` — it is an applied project, not datatype material.
- `Practice/2. Python Strings.ipynb` given a header marking it as scratch space and
  pointing at the taught content.

### Verification
- All 9 notebooks parse as valid `nbformat` 4
- All **259 code cells compile** cleanly
- All non-interactive cells **execute without error** on Python 3.14.4 with
  `warnings.simplefilter("error")`
