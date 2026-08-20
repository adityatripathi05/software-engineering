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

---

## 05 OOPs

2 notebooks -> 4 (two new). All retargeted to **3.12+**, outputs cleared, standard header
and **Common Mistakes / Best Practices / Exercises** block added to each.

This was already the best-developed folder — classes, all five inheritance types, MRO,
`@property` (including the backward-compatibility argument for *why*), class vs static
methods, composition vs aggregation, ABCs, operator overloading and custom iterators were
all covered. The gaps were modern class constructs, not errors.

> **New convention from this folder onward:** examples are drawn from real
> software-development scenarios (cache keys, HTTP responses, storage backends, retry
> policies, job states, connection pools) rather than textbook `Animal`/`Circle` classes.

### Two traps fixed
- 🔴 **`__repr__` was absent entirely** while `__str__` was covered — backwards, since
  `__repr__` is the one developers need. Containers, debuggers, the REPL and tracebacks all
  use `__repr__`, and `__str__` falls back to it but not the reverse. Added with a runnable
  demonstration of a list of objects printing as `<object at 0x...>` without it.
- 🔴 **`__eq__` was covered without `__hash__`.** Defining `__eq__` makes Python set
  `__hash__ = None`, so instances silently stop working as dict keys or set members. Added
  with a `CacheKey` example that fails, then the fix, plus why hashable objects must be
  immutable.

### Checklist gaps closed
`dataclasses`, `Enum`, `__slots__`, `Protocol`/structural typing, mixins,
`functools.total_ordering`, `__new__`, `__repr__`, `__hash__` and type hints in class bodies
had **zero occurrences** across the folder before this pass.

### `5.1 Python OOPs.ipynb` — 161 -> 176 cells
**Added:** **`__repr__` vs `__str__`** with the fallback rule and container behaviour;
**`__eq__` + `__hash__`** together; **`@total_ordering`** on a `Version` class;
**`__slots__`** with measured memory savings and the typo-protection side effect;
**`__new__` vs `__init__`** (singleton `ConnectionPool`, immutable `Port(int)` subclass);
and a **dunder reference table** with a `Repository` class implementing the container
protocol so it works with `len()`, `in`, `for`, `sorted()` and unpacking.

### `5.2 OOPs Elaborated - Payroll System.ipynb` — 59 -> 66 cells
The original walkthrough ends on the MRO fix for `TemporarySecretary`. That is where the
RealPython article it follows continues — so the narrative was incomplete.
**Added:** **mixins** (`LoggingMixin`, `SerialisableMixin`, `ComparableByIdMixin`) with the
rule that mixins go **first** in the base list, demonstrated by showing a mixin listed last
being silently ignored; and **composition over inheritance** — the same payroll domain
rebuilt from role and policy objects, turning N x M classes into N + M, with a run-time
policy swap that inheritance cannot express.

> The four `TypeError`/`AttributeError` results in this notebook are **intentional** — they
> are the class-explosion narrative ("that didn't work either... time to dive into MRO").

### `5.3 Dataclasses and Enums.ipynb` — **NEW**, 17 cells
`@dataclass`: what it generates, `field()`, `default_factory` (dataclasses refuse a mutable
default outright), `repr=False` for secrets, `compare=False`, `init=False`, `__post_init__`;
`frozen=True`, `slots=True`, `kw_only=True`, `order=True`, `replace()`, `asdict()`.
A **decision table** for plain class vs dataclass vs `NamedTuple` vs `TypedDict` vs `dict`,
plus a note that dataclasses do **not** validate types (pointing at `pydantic`).
Enums: `Enum`, `IntEnum`, `StrEnum` (3.11+), `auto()`, `Flag` for combinable permissions,
enums carrying methods, and **enums with `match`/`case`** — which sidestep the
capture-pattern trap from 3.4 because an enum member is always a dotted name.

### `5.4 Duck Typing, Protocols and Composition.ipynb` — **NEW**, 14 cells
Duck typing stated properly, and why `isinstance` checks usually fight it (EAFP vs LBYL).
**ABC vs Protocol** — nominal vs structural typing, as a comparison table and as runnable
code: an ABC that refuses to instantiate an incomplete subclass, and a Protocol that accepts
a class which inherits nothing. `@runtime_checkable`, and its limit (it checks method names,
not signatures). `ABC.register()` shown to be an unchecked promise.
**Dependency injection without a framework** — a `SessionCache` taking storage and clock
collaborators, made deterministic in tests by a `FrozenClock`. Closes with a decision table
and the folder's four design principles.

### Verification
- All 4 notebooks parse as valid `nbformat` 4
- All **142 code cells compile** cleanly
- 5.3 and 5.4 execute end to end with `warnings.simplefilter("error")` on Python 3.14.4

---

## 06 Exception Handling

1 notebook -> 3 (two new). Retargeted to **3.12+**, outputs cleared, standard header and
**Common Mistakes / Best Practices / Exercises** block added to each.

This was the thinnest folder relative to its importance — a single 33-cell notebook covering
try/except/else/finally, built-in exceptions, `assert` and `raise`.

### Errors fixed
- 🔴 **`assert` was taught as an input-validation technique** (`assert age > 0`). Assertions
  are **removed entirely** when Python runs with `-O`, so that validation silently vanishes
  in an optimised deployment. Rewritten with a prominent warning, a table of what `assert`
  is and is not for, and a runnable `subprocess` demo that proves the check disappears
  under `-O`.

> **Audit corrections:** custom exceptions were reported as missing — they are in fact
> covered (cells 30-31), just basic and with a non-PEP-8 class name. An earlier `except*`
> hit was a false positive matching a markdown bullet list.

### Checklist gaps closed
Context managers (`with`), `contextlib`, exception chaining (`raise ... from`),
`ExceptionGroup`/`except*`, the bare-`except:` anti-pattern, `logging.exception`,
`add_note()` and traceback reading had **zero occurrences** before this pass.

### `6.1 Exception Handling.ipynb` — 33 -> 47 cells
**Added:** the **exception hierarchy** (`BaseException` -> `Exception` -> families) and why
`except LookupError` catches both `IndexError` and `KeyError`; **reading a traceback**
bottom-up, with `traceback.extract_tb`; the **bare `except:` anti-pattern** demonstrated
swallowing a `BaseException`; `contextlib.suppress` as the explicit alternative to
`except: pass`; `else`/`finally` precisely, including why `else` prevents a handler from
lying about the cause; **bare `raise`** for re-raising with the traceback intact; and
**`logging.exception()`** compared against `print(exc)`.

> **Version finding — PEP 765.** The `return`-in-`finally` anti-pattern demo would not
> compile: **Python 3.14 makes `return`, `break` and `continue` inside `finally` a hard
> `SyntaxError`** (it was a `SyntaxWarning` in 3.12-3.13, and silently allowed before).
> The section now carries the full version table and detects the interpreter's behaviour at
> run time via `compile()`, so it works on any 3.x.

### `6.2 Custom Exceptions and Chaining.ipynb` — **NEW**, 13 cells
Designing an exception hierarchy for a package, motivated by a payments client that would
otherwise leak `requests` and `json` exceptions to its callers. Covers: one base exception
per package; PEP 8 `...Error` naming; carrying **structured data** and behaviour
(`is_retryable()`) on the exception; **`raise X from Y`** with a side-by-side traceback
comparison of implicit `__context__` vs explicit `__cause__` vs `from None`;
**`Exception.add_note()`** (3.11) accumulating context up the call stack without re-wrapping;
and **`ExceptionGroup` / `except*`** (3.11) for form validation and concurrent shutdown,
with a pointer to `asyncio.TaskGroup`.

### `6.3 Context Managers.ipynb` — **NEW**, 15 cells
What `with` desugars to, and why `try/finally` alone is insufficient. Covers: the
`__enter__`/`__exit__` protocol and what `as` actually binds; **returning `True` from
`__exit__` suppresses the exception** — including the *accidental* version where a truthy
return value silently swallows every error; **`@contextlib.contextmanager`** with a
commit/rollback transaction and a demonstration that omitting `try/finally` skips cleanup;
`suppress`, `closing`, `nullcontext`, **`ExitStack`** for run-time-determined resources, and
`redirect_stdout`; multiple managers and the parenthesised form (3.10+).

> **Version finding:** re-entering an exhausted `@contextmanager` raises **`AttributeError`
> on Python 3.14**, not the `RuntimeError` most references state. The notebook now says the
> exception type varies by version and catches broadly.

### Verification
- All 3 notebooks parse as valid `nbformat` 4
- All code cells compile except 6.1 cell 2, which is the notebook's **intentional**
  syntax-error demonstration
- All non-interactive cells execute without error on Python 3.14.4

---

## 07 Module and Packages

2 notebooks -> 3 (one new). Retargeted to **3.12+**, outputs cleared, standard header and
**Common Mistakes / Best Practices / Exercises** block added to each.

### Errors fixed in existing content
- 🔴 **Five hardcoded absolute paths** of the form
  `r'C:\Users\Aditya\Documents\Ducat Classes\Batch\Temp'` and
  `r'C:\Users\Aditya\Documents\My Final\Python\07 Module and Packages\Sample Mod'`.
  Every one failed on any machine but the original author's. All rewritten to use
  `tempfile.mkdtemp()` and clean up after themselves.
- 🔴 **`os.chdir()` into a hardcoded directory** partway through 7.1, which silently changed
  the working directory for every cell that followed. Now demonstrated inside a scratch
  directory and restored immediately, with a note pointing at `contextlib.chdir()` (3.11+).
- 🔴 `os.path.expanduser('~\local')` — `"\l"` is an **invalid escape sequence**
  (`SyntaxWarning` on 3.12+, an error under `-W error`). Replaced with raw-string,
  forward-slash and `os.path.join` variants.
- 🔴 **7.2 cells 1-3 imported `Sample_Package`**, a folder removed in the author's cleanup, so
  the notebook's only working examples raised `ModuleNotFoundError`. The notebook now builds
  a real package at run time instead of depending on files on disk.
- 🔴 **7.2 taught `pip3 install virtualenv`.** `venv` has been in the standard library since
  **Python 3.3**; no installation is needed. Replaced with `python -m venv`, including
  Windows *and* macOS/Linux activation.
- 🔴 **7.2 gave `ls` as the way to "see list of packages installed".** `ls` lists files. The
  command is `pip list`.
- Several `os`/`shutil`/`pickle` cells created files (`new.txt`, `Extra/`, `Extra2/`,
  `test.pkl`) in the repository and left them there. All now use temp directories.

### `7.1 Python Module.ipynb` — 116 -> 127 cells
**Added:** how importing actually works (search / execute / cache), the four import forms,
`__name__ == "__main__"`, `__all__`, and why `from module import *` is a trap — demonstrated
by having `math` overwrite a local name; **`pathlib`** with a full `os.path` translation
table and runnable examples; **`importlib`** including `import_module`, `find_spec` and
`reload`, with a note that **`imp` was removed in 3.12**; and **circular imports** with all
three fixes shown working.
**Rewrote:** the entire `os` directory/file sequence, the `shutil` sequence and the `pickle`
cells as portable, self-cleaning demonstrations. Added a security warning that
`pickle.load()` executes arbitrary code.

### `7.2 Python Packages.ipynb` — 6 -> 16 cells *(near-total rewrite)*
Was six cells, three of which no longer ran.
**Now covers:** module vs package; what `__init__.py` is actually for; namespace packages
(PEP 420) and why a *missing* `__init__.py` is now a silent surprise rather than an error;
**absolute vs relative imports**, with a subprocess demo of
`attempted relative import with no known parent package` and the `python -m` fix;
**`python -m venv`** and how to tell whether you are inside one (`sys.prefix` vs
`sys.base_prefix`); **`pip`** — `list` vs `freeze`, version specifiers, editable installs,
and why to prefer `python -m pip`; **`requirements.txt`**, pinning exactly for applications
vs ranges for libraries, and split runtime/dev files.
The whole notebook builds a real four-module package with a subpackage in a temp directory,
imports from it, and tears it down.

### `7.3 Standard Library - itertools, functools, datetime.ipynb` — **NEW**, 15 cells
The three highest-value stdlib modules that had no home.
**`itertools`:** `chain`, `islice`, **`batched` (3.12+)**, **`pairwise` (3.10+)**,
`accumulate`, `groupby` (with the sort-first trap demonstrated), `product`, `combinations`,
`zip_longest`, `takewhile`/`dropwhile`.
**`functools`:** **`cached_property`** — including the staleness trap and how to invalidate
it — plus `partial` and `reduce`, and a reference table pointing at where `cache`, `wraps`,
`singledispatch` and `total_ordering` were introduced.
**`datetime`:** the four classes and the arithmetic rules; 🔴 **aware vs naive**, and why
mixing them raises `TypeError`; **`datetime.utcnow()` is deprecated in 3.12** with the
`datetime.now(timezone.utc)` replacement demonstrated live; `zoneinfo` (stdlib since 3.9,
no `pytz`); parsing, ISO 8601 round-tripping, and an expiry-window example.
Closes with all three modules used together on a log-processing pipeline.

### Tooling note
The verification harness was hardened during this folder: it now catches `BaseException`
(a `sys.exit()` in 7.1 was terminating the run silently, hiding every subsequent error) and
skips cells that call `sys.exit()`.

### Verification
- All 3 notebooks parse as valid `nbformat` 4
- All **105 code cells compile** cleanly
- All **103 non-interactive cells execute without error** on Python 3.14.4, leaving no files
  behind in the repository

---

## 08 File Handling

4 notebooks -> 5 (one new). Retargeted to **3.12+**, outputs cleared, standard header and
**Common Mistakes / Best Practices / Exercises** block added to each.

Two of the four notebooks were effectively empty: 8.3 had **three cells and no runnable
code at all**, and 8.4 had four cells, no headings, and two network calls with no error
handling.

### Errors fixed in existing content
- 🔴 **`./Files/Image.jpg` in two cells of 8.1.** There has never been a `Files` directory —
  the images are in `File2Save`. Both cells raised `FileNotFoundError`.
- 🔴 **`sys.stdout = open(...)` in 8.1, never restored.** Every subsequent `print` in the
  session went silently into that file, and the handle was never closed. Replaced with
  `contextlib.redirect_stdout`.
- 🔴 **`nwords = len(word)`** in the word-count cell — `word` was never defined. `NameError`;
  the cell could never run.
- 🔴 **Two leaked file handles** in the `print(file=open(...))` cell, plus a typo
  (`output.txt1` for `output1.txt`) that is why a stray file of that name exists in
  `File2Save`.
- **`x`-mode cells were not re-runnable** — they raised `FileExistsError` on a second pass.
  Rewritten to demonstrate the exclusive-creation behaviour deliberately.
- **8.4 used plain `http://`**, with no timeout and no exception handling.

### `8.1 File Handling — Text.ipynb` — 47 -> 56 cells
**Added:** 🔴 an **encoding** section — `open()`'s default is platform-dependent, which is
why files written on Windows break on Linux; plus `errors=` strategies and the
`utf-8` vs `utf-8-sig` BOM trap; **`pathlib` I/O** (`read_text`/`write_text`/`read_bytes`)
with a comparison table; **atomic writes** — write to a temp file in the same directory,
`fsync`, then `os.replace()` — demonstrated by crashing mid-write and showing the original
survives.

### `8.2 File Handling — CSV.ipynb` — 19 -> 27 cells
**Added:** 🔴 an explanation of **`newline=""`**, which the original used in every cell and
never justified — shown by writing the same rows with and without it and diffing the raw
bytes; 🔴 **why `line.split(",")` is wrong**, demonstrated with fields containing commas,
quotes and embedded newlines; explicit **type conversion** (the reader always returns
strings); `DictWriter` `restval`/`extrasaction`; **`csv.Sniffer`**; streaming 10,000 rows
without materialising them; and an honest "when to stop and use `pandas`" table.

### `8.3 File Handling — JSON.ipynb` — 3 -> 16 cells *(complete rewrite)*
Was two markdown cells and one empty code cell.
**Now covers:** why JSON beat the alternatives (including that it is safe to parse, unlike
`pickle`); all four functions with the `s`-means-string mnemonic; the full type-mapping
table; 🔴 **the two silent lossy conversions** — tuples become lists, and all dict keys
become strings; the types JSON cannot represent at all; **custom `default=` encoders and
`object_hook` decoders** round-tripping `datetime`, `Decimal` and `set`; **`JSONDecodeError`**
handling across seven malformed inputs, including the very common "API returned an HTML
error page"; and **JSON Lines**, with a demonstration that one corrupt line does not destroy
the file.
The external `imgix.net` meme image was removed.

### `8.4 File Handling — Online Text.ipynb` — 4 -> 11 cells
**Rewritten:** HTTPS, an explicit **timeout**, and `HTTPError`/`URLError`/`TimeoutError`
handling, with an **offline fallback** so the notebook runs without a network. Explains why
the network hands you `bytes` and where to decode (the Unicode-sandwich rule from 2.1),
taking the charset from the response headers; streaming line by line versus `.read()`;
downloading to disk with `shutil.copyfileobj`; and a comparison table showing why real
projects use `requests` (**20**).

### `8.5 Binary Files.ipynb` — **NEW**, 16 cells
Text mode vs binary mode, and what the text layer actually does — demonstrated by showing
non-UTF-8 bytes both failing to decode *and* being silently corrupted by newline
translation. Then: **chunked reading** with a `chunks()` generator so file size stops
mattering; **`hashlib`** for verification and deduplication, including `file_digest()`
(3.11+), a one-bit-flip demo, and a note that MD5/SHA-1 are broken and that no
general-purpose hash belongs near a password; `shutil.copyfileobj` and **`io.BytesIO`**;
**magic bytes** for identifying a file regardless of its extension, with a renamed-file demo;
and **`struct`** for fixed-width records, including a big-endian/little-endian misread that
turns 1 into 16,777,216.

### Verification
- All 5 notebooks parse as valid `nbformat` 4
- All **54 code cells compile** cleanly
- All **53 non-interactive cells execute without error** on Python 3.14.4

> Note: `File2Save/output.txt1` is a stray file produced by the filename typo fixed above.
> It is left in place rather than deleted unilaterally; it can be removed safely.

---

## 09 Regular Expression

1 notebook, 247 -> 259 cells. Retargeted to **3.12+**, outputs cleared, standard header and
**Common Mistakes / Best Practices / Exercises** block added.

This was already the most thorough notebook in the set — history, syntax, all the matching
functions, character classes, quantifiers, greediness, boundaries, substitution, every
compilation flag, grouping, backreferences, named and non-capturing groups, and both
lookahead and lookbehind. The work here was correction and completion, not expansion.

### 🔴 The headline defect: it teaches raw strings, then stops using them

Cells 42-54 are an excellent section called **"Backslash Plague"** explaining precisely why
regex patterns must be raw strings. **Then 41 of the following cells write
`re.compile("\w+")` instead of `r"\w+"`.**

| Escape | Occurrences |
|---|---|
| `\w` | 17 |
| `\d` | 10 |
| `\W` | 5 |
| `\s` | 4 |
| `\.` | 2 |
| `\$`, `\g` | 1 each |

These still **run** on Python 3.14 — an invalid escape is a `SyntaxWarning`, not an error —
but the warning is documented as becoming a `SyntaxError` in a future release, and the
notebook was contradicting its own advice 41 times.

All 41 converted to raw strings, verified by recompiling every cell with
`warnings.simplefilter("error")` until zero remained. Two needed hand conversion:
a multi-line Windows-path literal, and `re.compile("(\w+) \1")` — where the naive raw form
`r"(\w+) \1"` would have changed the backreference into a literal backslash. It is now
`r"(\w+) \1"`, which is also the idiomatic way to write it.

### Other errors fixed
- 🔴 **The `re.LOCALE` section was wrong for Python 3.** `re.compile(r"\w", re.LOCALE)` raises
  `ValueError: cannot use LOCALE flag with a str pattern` — the flag is **bytes-only** since
  Python 3, because `str` is Unicode and `re.UNICODE` is already the default. The prose
  described `str` behaviour while the demo quietly used `re.A` instead. Rewritten to
  demonstrate the `ValueError`, show the valid `bytes` form, and point at `re.ASCII` as the
  flag people actually want.
- 🔴 **`re.split(' ', txt, 2)`** — passing `maxsplit` positionally is **deprecated in Python
  3.13** (as is `count` for `re.sub`). Rewritten to the keyword form, with a live
  demonstration of the warning.
- **The flags section skipped number 6.** It ran 1, 2, 3, 4, 5, 7, 8 — `re.ASCII` was
  missing. Added, with the Unicode-vs-ASCII comparison for `\w`, `\d` and `\s`.
- **`import regex`** (third-party) was unguarded, so the notebook hard-failed if it was not
  installed. Now falls back to the standard library with an install hint.

### Added
- **`re.fullmatch()`** (3.4+) — the missing third matching function, with a table showing
  that `match`, `search` and `fullmatch` disagree on `"123abc"`, which is the classic
  validation bug.
- **The `Match` object properly** — `group()`, `groups()`, **`groupdict()`**, `span()`,
  `start()`, `end()`, `m[...]` subscripting, and the **walrus idiom**
  `if match := pattern.match(line):`.
- 🔴 **Catastrophic backtracking (ReDoS)** — a live timing loop showing `(a+)+$` doubling in
  cost per added character, a table of the warning signs, and why it is a security issue and
  not just a performance one.
- **Atomic groups `(?>...)` and possessive quantifiers `*+`** — **added to `re` in Python
  3.11** — as two of the three fixes, alongside restructuring. Includes the trade-off:
  `(?>a*)a` never matches, because atomic groups change semantics as well as speed.
- **Performance and when *not* to use a regex** — compile-once timings, and a table showing
  `str.startswith`, `in`, `split` and `replace` beating `re` on both speed and clarity for
  fixed strings.

### Tooling note
The harness was extended again during this folder: it now adds each notebook's own directory
to `sys.path`, as Jupyter does. Without that, `from utils import highlight_regex_matches`
failed and cascaded into 36 spurious `NameError`s — `utils.py` was present all along.

### Verification
- Parses as valid `nbformat` 4
- **Zero `SyntaxWarning`s remain** (from 41 cells)
- All **163 code cells execute without error** on Python 3.14.4

---

## 10 Database

3 notebooks -> 4 (one new, one renamed). Retargeted to **3.12+**, outputs cleared, standard
header and **Common Mistakes / Best Practices / Exercises** block added to each.

### Errors fixed in existing content
- 🔴 **`SQLite in Python.ipynb` stopped mid-lesson.** Cell 20 was a heading — `### Create
  Table` — followed by an **empty cell**. The notebook connected, created a cursor, and
  ended. No `CREATE TABLE`, no `INSERT`, no `SELECT`. That is why `Masterly.DB` was 0 bytes.
- 🔴 **`sqlite3.version` was removed in Python 3.14** (deprecated 3.12). The cell reading
  `db.version` raised `AttributeError`. Replaced with `sqlite3.sqlite_version`, plus a table
  of what was removed and a feature-gating example showing why the *library* version matters.
- 🔴 **A plain-text MySQL root password** was in a markdown cell of 10.2. Removed, with a note
  on reading credentials from the environment instead. (This is the second credential found
  in the notes; the first was a Gmail password in `14 Project`.)
- 🔴 **Twelve cells of 10.2 held MySQL statements in Python *code* cells**, so every one raised
  `SyntaxError` — the notebook could not be run at all. Converted to fenced SQL blocks, and
  the notebook now says up front that it is a CLI transcript requiring a server.
- **`from pymysql import *`** replaced with a guarded driver check that works with no MySQL
  installed.

### `10.1 Introduction to SQL.ipynb` — 20 -> 43 cells
Was 19 markdown cells and 1 code cell — a readable SQL reference where **nothing executed**.
Now every statement runs against an **in-memory SQLite database**, so the whole notebook is
explorable: `CREATE`, `INSERT` (with constraint violations demonstrated), `SELECT`, operators,
aliases, views, `ALTER`, aggregates, `GROUP BY`/`HAVING`, `UPDATE`/`DELETE`.
**Added JOINs**, which were absent entirely — inner, left, cross, the `LEFT JOIN ... IS NULL`
idiom for finding non-matches, and the observation that using `INNER` where you meant `LEFT`
silently drops rows. Also added NULL semantics (`= NULL` matching nothing, `COALESCE`), the
logical evaluation order of a query, and dialect notes wherever SQLite differs from MySQL.

### `10.2 MySQL Command Line Client.ipynb` — 23 -> 27 cells
Reframed honestly as a CLI transcript. **Added** how to reach MySQL from Python through a
**PEP 249** driver, with the point that the `connect`/`cursor`/`execute`/`commit` shape is
identical to `sqlite3`; the `%s` vs `?` placeholder difference; the `utf8` vs `utf8mb4` trap;
and a comparison table of MySQL / SQLite / PostgreSQL syntax.

### `10.3 SQLite in Python.ipynb` — 22 -> 41 cells *(renamed from `SQLite in Python.ipynb`)*
Renamed for consistency with the rest of the folder, and **completed** from the abandoned
"Create Table" heading onward.
**Added:** 🔴 **parameterised queries and SQL injection** — with a working `' OR '1'='1'`
data-leak attack against an f-string query, a `DROP TABLE` demonstration via
`executescript`, and the honest note that `execute()`'s single-statement rule is not a
defence; named placeholders and the single-element-tuple trap; `executemany`;
`fetchone`/`fetchmany`/`fetchall`/iteration; **`sqlite3.Row`**; **transactions** with a
worked all-or-nothing example showing an uncommitted stock decrement surviving without one;
**`PRAGMA foreign_keys = ON`** and the orphan row you get without it; a small data-access
layer; and **`:memory:` databases for testing**.

> **Two bugs found by executing it.** `Connection.backup()` **hangs indefinitely** if the
> source has an uncommitted write transaction holding a lock — no error, no timeout, the
> notebook simply stops. And writing the demo database into the repository meant a crashed
> run left a locked file that broke every subsequent run on Windows. Both fixed: commit
> before `backup()`, and use a `tempfile` directory.

### `10.4 ORM Intro - SQLAlchemy.ipynb` — **NEW**, 24 cells
Closes the "ORM intro (SQLAlchemy basics)" checklist item, fully runnable against
SQLAlchemy 2.0.
Covers: what an ORM is and its **honest trade-offs**; Core vs ORM; **2.0-style declarative
models** with `Mapped`/`mapped_column` (with a note that `session.query()` and
`declarative_base()` are the superseded 1.x idiom); `Engine` vs `Session`; CRUD via
`select()`/attribute assignment/`session.delete`; relationships and `back_populates`;
🔴 **the N+1 query problem**, demonstrated by counting the actual SQL statements emitted and
then fixed with `selectinload`; dropping down to Core and to `text()` — still with bound
parameters; and a decision table for ORM vs raw SQL.

### Housekeeping
The author removed `DB SQlite/`, `MySQL/` and the Practice directory (28 files); those
deletions are recorded in this commit.

### Verification
- All 4 notebooks parse as valid `nbformat` 4
- All **45 code cells compile** cleanly
- All **45 cells execute without error** on Python 3.14.4, leaving no database files behind
