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
  pointing at the taught content. *(Superseded: the author subsequently deleted the
  `Practice/` folder — see the housekeeping note under 03.)*

### Verification
- All 9 notebooks parse as valid `nbformat` 4
- All **259 code cells compile** cleanly
- All non-interactive cells **execute without error** on Python 3.14.4 with
  `warnings.simplefilter("error")`

---

## 03 Flow Control Statement

6 notebooks -> 7 (one new). All retargeted to **3.12+**, outputs cleared, standard header
and **Common Mistakes / Best Practices / Exercises** block added to each.

### Errors fixed in existing content
- 🔴 **3.1** cell 6 ended with `print("Thankyou"))` — an unmatched closing parenthesis.
  A hard `SyntaxError`; the cell had never been runnable.
- 🔴 **3.2.2** the anagram cell used `x` and `y` without ever assigning them (the two
  `input()` lines were missing), so it raised `NameError`. Restored, plus a runnable
  three-method version that needs no input.
- 🔴 **3.3** cell 13 iterated `name` instead of `names` — `NameError`.
- **3.2.2** the "semiprime" heading had an empty code cell; the solution is now written.
- **3.2.4** the "Challenge for you!" had no solution; one is now provided.

> **Audit correction:** the original audit reported a *Python 2 print statement* in 3.1.
> That was a false positive — the real defect was the unmatched parenthesis above.

### Checklist gaps closed
`enumerate()`, `zip()`, the loop `else` clause, generator expressions, the walrus operator
in loops and comprehensions, and `match`/`case` had **zero occurrences** across the whole
folder before this pass.

### `3.1 Python Decision Statement.ipynb` — 27 -> 38 cells
**Added:** what counts as a condition (truthiness, the `not x` vs `x is None` bug, float
comparison, chained comparisons); **conditional expressions** with a syntax breakdown and
the precedence trap; **guard clauses** contrasted against a nested "pyramid of doom";
dict-lookup and `in` as alternatives to long `elif` chains; forward-reference to 3.4.

### `3.2.1 Python While Loop.ipynb` — 28 -> 38 cells
**Added:** infinite loops and how to escape them in Jupyter/terminal; `while True` + `break`
as the standard validation shape; **the walrus operator in a loop condition**; the
**`while ... else`** clause explained as "nobreak", with the flag-variable version it replaces.

### `3.2.2 Python For Loop.ipynb` — 47 -> 58 cells *(largest change)*
**Added:** **`enumerate()`** with the `range(len(x))` anti-pattern it replaces and `start=`;
**`zip()`** including unequal lengths, **`strict=True` (3.10+)**, `zip(*rows)` transpose and
single-consumption; the **`for ... else`** clause; `reversed()`/`sorted()` in loop headers;
loop-variable leakage; an **`itertools` signpost** table with runnable examples.
**Rewrote:** the iterator-protocol opening now shows `__iter__`/`__next__` directly instead
of dumping `dir()` output.

### `3.2.3 Python Loop Control.ipynb` — 15 -> 22 cells
**Added:** **`pass` vs `continue` vs `...`** comparison; `continue` as a guard clause;
**why `break` only exits the innermost loop**, with all three standard workarounds (flag,
function + `return`, `for/else` + `continue`).

### `3.2.4 Python Loop Pattern.ipynb` — 20 -> 27 cells
**Added:** how to reason about any pattern problem (rows / counts / spaces); three ways to
write the same pattern — nested loops, string multiplication, f-string alignment; solution
to the previously unanswered challenge.

### `3.3 Python Comprehension.ipynb` — 50 -> 63 cells
**Added:** full syntax breakdown, and the distinction between the **filter `if`** and the
**conditional-expression `if/else`**; a dedicated Set Comprehension heading;
**generator expressions** (laziness, `sys.getsizeof` comparison, single consumption, when
to drop the redundant brackets); **`any()`/`all()` with generators** including
short-circuiting and `all([]) == True`; **the walrus inside a comprehension**; and a
"when *not* to use a comprehension" section.
**Reframed:** the three "ways to implement a ternary" (tuple indexing, dict lookup, lambda
pair) are now labelled as pre-2006 workarounds, with each one's actual flaw named.

### `3.4 Structural Pattern Matching.ipynb` — **NEW**, 21 cells
`match`/`case` (3.10+) appeared nowhere in the original notes. Covers: why it is **not** a
switch statement; syntax breakdown; literal, capture and wildcard patterns; **the
capture-vs-comparison trap**; sequence patterns with `*rest` and why `str` is excluded;
mapping patterns (subset matching, `**rest`); class patterns and `__match_args__`; guards,
`as` patterns and or-patterns; a worked command parser; and a decision table for when
`match` beats `if`/`elif` — with a side-by-side comparison asserting both give identical
results.

> **Finding:** Python 3.10+ raises `SyntaxError: name capture makes remaining patterns
> unreachable` when a bare-name capture is followed by other cases — but stays **silent**
> when the capture is the *last* case. The notebook demonstrates both halves, since only
> the silent one can actually reach production.

### Verification
- All 7 notebooks parse as valid `nbformat` 4
- All **130 code cells compile** cleanly
- All non-interactive cells execute without error on Python 3.14.4 with
  `warnings.simplefilter("error")`

### Housekeeping (author's own cleanup)

Committed alongside 03: the author removed a set of legacy support files that the notebooks
no longer depend on — the per-folder `IDLE/` script directories, the `Practice/`/`Practise/`
`.docx` assignment files, `Sample_Package/`, all `.ipynb_checkpoints/` and `__pycache__/`
artefacts, and the duplicate `12 Multithreading/Multithreading-Copy1.ipynb`.

These deletions are the author's and were intentional; they are recorded here only so the
diff for this commit is not mistaken for part of the modernisation work. The taught content
is unaffected — no notebook referenced any of the removed files.

---

## 04 Functions

6 notebooks -> 7 (one new, two moved out). All retargeted to **3.12+**, outputs cleared,
standard header and **Common Mistakes / Best Practices / Exercises** block added to each.

This was already the strongest folder — closures and decorators were covered better than in
most tutorials. The gaps were modern additions rather than errors.

### The one real defect
- 🔴 **4.4** had a "Debugging Decorators" section that demonstrated the problem
  **`functools.wraps`** solves and never mentioned `wraps`. Cell 63 showed
  `decorated_function.__name__` returning the wrong value and stopped there. Every decorator
  in the notebook silently destroyed its target's `__name__`, `__doc__`, annotations and
  signature. Rewritten to show the fix, why it matters (Flask endpoint collisions, pytest
  collection, `help()`, tracebacks), and a runnable before/after including a registry that
  silently loses a handler without it.

### Checklist gaps closed
Positional-only (`/`) and keyword-only (`*`) parameters, type hints on signatures,
`functools.wraps`, `lru_cache`/`cache`, `yield from`, the generator `send`/`close`/`throw`
protocol, and `singledispatch` had **zero occurrences** across the folder before this pass.

### `4.1 Functions User-defined.ipynb` — 90 -> 100 cells
**Added:** **positional-only (`/`) and keyword-only (`*`) parameters** with a full syntax
breakdown and the flag-readability argument; **type hints on signatures**, introduced where
signatures are taught; **recursion depth limits** (`RecursionError`, no tail-call
optimisation) and **`@cache` memoisation** with a measured speedup on the existing
fibonacci.
**Rewrote:** "Scope of a Variable" expanded into the full **LEGB** model with `global` and
`nonlocal` demonstrated (including the `UnboundLocalError` that catches everyone).
**Corrected:** the heading **"Pass by Reference"** — Python is neither pass-by-value nor
pass-by-reference; it is *call by object reference*. The original body text was already
nuanced and correct, so this is a framing fix cross-referenced to 2.7.

### `4.2 Functions Builtins.ipynb` — 75 -> 85 cells
**Added:** an honest **"when to use `map`/`filter`/`reduce` — and when not to"** section with
timings showing a comprehension beats `map(lambda ...)` on both clarity and speed, and that
`sum()`/`math.prod()` beat `reduce`; **`key=` functions** with `itemgetter`/`attrgetter`;
`callable`, `getattr`/`setattr`/`hasattr`, `vars`, and the `isinstance(True, int)` trap.
**Added a note** that the `classmethod`/`staticmethod`/`property` sections at the end are
really OOP material, pointing at 05 and 4.4.

### `4.3 Function Generators.ipynb` — 25 -> 35 cells *(largest proportional change)*
**Added:** **`yield from`** for delegation and recursive traversal, with a table of what the
manual re-yield loop loses; **the full generator protocol** — `send()`, `close()`,
`throw()`, and `return` landing in `StopIteration.value`; **generator pipelines** over a log
file; infinite generators with `itertools.islice`; and how generators relate to
`async`/`await`.
**Fixed:** the memory and timing comparison cells depended on `input()` and used a `%timeit`
magic, so neither could run unattended. Rewritten to run standalone with `sys.getsizeof`
and `timeit`, and to show that laziness trades the same total time for flat memory plus the
ability to stop early.

### `4.4 Function Decorator.ipynb` — 70 -> 82 cells
**Added:** **`functools.wraps`** (above); **stacking order** made concrete — applied
bottom-up, executed outside-in, demonstrated by swapping two decorators; **class-based
decorators** with `update_wrapper`, and decorating methods; **the decorators you already
use** (`@property`, `@cache`, `@dataclass`, a miniature `@app.route`);
**`functools.singledispatch`** as the alternative to an `isinstance` chain.

### `4.5 Type Hints for Functions.ipynb` — **NEW**, 20 cells
The function-level slice of typing, sitting between 4.1's introduction and folder 17's full
treatment. Covers: why annotate at all; **the fact that nothing is enforced at run time**,
demonstrated; annotating parameters, defaults, returns, `*args`/`**kwargs`, and
positional-/keyword-only params; container generics and why `list[int]` replaced
`typing.List[int]`; **`X | None`** and the `None`-handling bug it exposes; `Callable` for
decorators and `key=` parameters; `Any`, type aliases and the 3.12 `type` statement;
**running `mypy`** — the notebook writes a deliberately buggy `mypy_demo.py` you can check;
and an honest section on how much typing is worth it, including the costs.

### Structural changes
- `Student Registration System.ipynb` -> `14 Project/Student Registration System/`
- `Advance Coding.ipynb` -> `15 Data Structure and Algorithm/` (HackerRank-style matrix and
  array problems — nothing to do with functions)
- `.gitignore`: added `mypy_demo.py`, generated by 4.5

### Verification
- All 5 notebooks parse as valid `nbformat` 4
- All code cells compile cleanly
- All non-interactive cells execute without error on Python 3.14.4 with
  `warnings.simplefilter("error")`
