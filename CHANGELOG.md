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

### Retro-fix (found by the folder 11 verification sweep)
Two **undefined-name typos** in `5.1 Python OOPs.ipynb`, both of which meant the cell had
never once run:
- 🔴 **Cell 103** — the payoff cell of the operator-overloading lesson. It builds
  `pt3 = pt1 + pt2` using the `__add__` defined immediately above, then calls
  `print(point3)`. `point3` is never bound anywhere.
- 🔴 **Cell 125** — `print(isinstance(tr1, Triangle))`. **`tr1` appears exactly once in
  all 176 cells** — only here. The triangle is built as `tri` two cells earlier.

Both corrected with an inline comment recording what the original said.

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

### Retro-fix: the notebooks were writing into the repository
🔴 Running folder 08 left **three tracked fixtures modified**, so `git status` was dirty
after every run and each run produced different output. It survived the original check
because that looked for *stray untracked* files; these were *modifications to tracked* ones.

| Cell | File | Mode | Effect |
|---|---|---|---|
| 8.1 cell 43 | `msg2.txt` | `'r+'` + seek to end | appended `This is line 8.` every run |
| 8.2 cell 4 | `tab1.csv` | `'a'` | re-appended the header every run |
| 8.2 cell 6 | `tab1.csv` | `'a'`, **no trailing newline** | appended, and collided with the next run |

The damage was already committed: `tab1.csv` contained `Neetu,negName,Corona Test` — cell 6's
newline-less append running into cell 4's header on the following run — and `msg2.txt` held
`This is line 6.This is line 8.` for the same reason.

**Fixed** by giving each notebook a `WORK` directory from `tempfile`:
- `8.1` — 25 cells repointed, +3 cells (scratch-directory setup, explanation, cleanup);
  56 → 59 cells. `msg2.txt` is now *seeded* clean rather than mutated in place.
- `8.2` — 11 cells repointed, +3 cells; 27 → 30 cells. `write_file()` now writes a trailing
  newline, and opens with `newline=''`.
- `File2Save/` is now **read-only**, used solely for `Image.jpg`.

> **One bug introduced and caught during this fix.** The rewrite stripped a `Path(...)`
> wrapper and left `WORK / "Image_copy.jpg".stat()`, where `.stat()` binds to the string
> literal instead of the path — `AttributeError: 'str' object has no attribute 'stat'`.
> The harness caught it immediately; parenthesised.

**Note:** nine fixtures in `File2Save/` are now unreferenced — `msg1.txt`, `msg2.txt`,
`Log.txt`, `output1.txt`, `output.txt1`, `tab1.csv`, `tab2.csv`, `tab3.csv`,
`Image_copy.jpg`. They are left in place pending a decision; only `Image.jpg` is still read.

**Verified** by running the folder twice in succession: 0 unexpected problems both times,
`git status` clean, and no `py08_*` temp directories left behind.

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

### Expansion: NoSQL, graph, and real servers (4 -> 6 notebooks)

Folder 10 taught one paradigm across four notebooks: SQL, SQL at a CLI, SQL from Python, SQL
through an ORM. Nothing told a learner that a non-relational store exists. Two notebooks were
added, and the MySQL notebook was made executable.

#### The practice stack — `10 Database/docker/docker-compose.yml` (**NEW**)
Five throwaway containers on **deliberately non-standard ports** so they cannot collide with
a database in real use, with named volumes so nothing is written into the notes.

| Service | Host port | Service | Host port |
|---|---|---|---|
| `postgres:16-alpine` | 55432 | `mongo:7` | 57017 |
| `mysql:8` | 53306 | `neo4j:5-community` | 57687 / 57474 |
| `redis:7-alpine` | 56379 | | |

#### 🔴 Dual-path, so no notebook ever requires a server
Every live cell probes the port first and, if nothing answers, prints the SQL or the driver
call it *would* have made and continues. Verified by running folders with every port
redirected to a dead one: **0 unexpected problems, no tracebacks, no dead cells**. Starting
the stack upgrades the same cells to real output.

This was the design constraint that mattered. Requiring `docker compose up` would have
reproduced exactly the defect this folder already had — a notebook that cannot run.

### `10.2 MySQL and PostgreSQL from Python.ipynb` — 27 -> 47 cells
*(renamed from `10.2 Mysql Command Line Client.ipynb`)*

Was 26 markdown cells and **1** code cell, because there was no server to run against. The
CLI transcript is kept as the first half; the second half now executes against **MySQL 8.4.11
and PostgreSQL 16.14 side by side** — the PEP 249 shape is identical, and the dialect
differences are the lesson. **PostgreSQL added** rather than given its own notebook, since a
separate one would have largely repeated 10.3.

Covers: `paramstyle` (`pyformat` for both drivers vs `qmark` for `sqlite3`);
`AUTO_INCREMENT` vs `GENERATED ALWAYS AS IDENTITY`; PostgreSQL `RETURNING` vs MySQL
`lastrowid`; 🔴 the **`utf8` vs `utf8mb4` trap**, demonstrated by round-tripping astral-plane
characters; and transactions, with a worked rollback showing `COUNT(*)` at 0 after a failure
and 2 after success.

### `10.5 Beyond Relational - Key-Value and Document Stores.ipynb` — **NEW**, 34 cells
The four families and what each is for. **Key-value in the standard library** — `dbm` (with
the finding that `dbm.whichdb` reports **`dbm.sqlite3`**, the default since 3.13) and
`shelve`, including 🔴 the **writeback trap**, demonstrated as silent data loss and then fixed
two ways. Redis for TTLs, atomic counters and hashes.

**Document stores**: schema-on-read vs schema-on-write; a working document store built on
**SQLite JSON1**, with a generated column and an index, proved to be used via
`EXPLAIN QUERY PLAN` (`SEARCH ... USING INDEX`, not `SCAN`); **PostgreSQL `JSONB`** with
`->>`, `#>>`, `@>` and a GIN index; MongoDB; and **TinyDB** so the document-query idea runs
with no server at all.

🔴 **What you give up** is demonstrated rather than asserted: three documents with a
misspelled key, a string where a number belongs, and a dangling reference are all accepted,
and the query then returns 4 of the 5 documents a human would call queued. Closes with
eventual consistency and CAP in plain English — including that neither applies to a
single-node database — and DuckDB as the columnar contrast.

### `10.6 Graph Data in Python.ipynb` — **NEW**, 27 cells
One question — *everything `web` depends on, at any depth* — asked three ways over an 8-node
service dependency graph.

- **Relational**: one `JOIN` per hop, and the 3-hop query returns `userdb` **twice** because
  two paths reach it — rows are paths, not nodes. Then `WITH RECURSIVE`, which answers it at
  any depth.
- 🔴 **Cycles**: a recursive CTE with no guard never returns. Both guards are shown — a depth
  limit, and the cycle-safe **path-tracking idiom** with comma delimiters (so `api` does not
  match inside `api-gateway`).
- **`networkx`**: `descendants`, `ancestors` (the blast radius), `all_simple_paths`,
  `topological_sort` for deploy order, and `find_cycle` as a CI check.
- **Cypher/Neo4j**: `-[:DEPENDS_ON*]->` — one character where SQL needs a recursive CTE.

All three agree on all seven services. A live detail the notebook now teaches: **networkx and
Neo4j return *different* shortest paths**, both 3 hops and both correct, so tests should
assert on path *length*, never identity.

Ends with the honest case: for a graph this size all three work, and `WITH RECURSIVE` needs
no new infrastructure — adopt a graph database for the **query pattern**, not because the
data happens to be a graph.

### 🔴 Retro-fix in `10.3` — it was still writing into the repository
Cells 10 and 17 called `db.connect('Masterly.DB')` with a repo-relative path. The earlier
modernisation rewrote everything from cell 22 onward to use `tempfile` but left these two
original cells, so **running the notebook still created a database file inside the notes** —
the source of the tracked 0-byte `Masterly.DB`.

It evaded both existing checks: the file is created empty and stays empty, so it never
appears as a stray *untracked* file nor as a *modified tracked* one. It surfaced only as a
`ResourceWarning` about an unclosed database, because cell 17 also reassigned `conn` without
closing the connection cell 10 opened. Both fixed; the warning is gone.

**Note:** `10 Database/Masterly.DB` is now unreferenced, as are the nine unused fixtures in
`08 File Handling/File2Save/`. All left in place pending a decision.

### Verification
- Folder 10 runs clean **twice**: once with all five servers up, once with every port
  redirected — **0 unexpected problems** both ways
- Folders 01-10: **0 unexpected problems**
- **52 notebooks** valid `nbformat` 4, **1292 code cells**, 1 syntax failure (the intentional
  6.1 demo)
- `git status` clean of stray files; no leftover temp directories

---

## 11 Socket Programming

**The folder was completely empty.** Five notebooks written from scratch, 106 cells,
fundamentals to advanced. Everything runs offline against `127.0.0.1`.

### 🔴 The constraint that shaped the whole folder
Sockets block. `accept()` and `recv()` wait **forever** by default, so one unguarded call
hangs the notebook - and hangs `smoke.py` with no output, needing a kill. Every example
therefore:

- binds to **`127.0.0.1` port 0**, so the OS assigns a free port - no collisions, no
  `Address already in use` on a second run, no hardcoded numbers
- runs servers on **daemon threads**, which cannot outlive the interpreter
- sets a **timeout on every blocking call**, including the `accept()` loop, so it can notice
  a stop flag instead of blocking
- ends with a cell asserting **no threads were left alive**

These patterns were prototyped and verified in a standalone script before any notebook cell
was written.

### `11.1 Networking Fundamentals.ipynb` - 20 cells
IP/ports/DNS via `ipaddress` and `getaddrinfo`; the four layers that matter; TCP vs UDP as
the decision it actually is; the socket API shape before using it; byte order with `struct`
(`1` read little-endian instead of network order becomes **16777216**, silently); and
🔴 bytes vs `str` on the wire, with the same encoding lesson as **8.1**.

The external DNS lookup is guarded - nothing else in the folder needs a network.

> **Corrected during review:** the markdown promised `ConnectionRefusedError` when nothing is
> listening, but this machine's firewall produced a **timeout** instead. Teaching text the
> output contradicts is worse than none, so the cell now handles both and explains the
> difference - refused means the machine answered, timeout means nothing did.

### `11.2 TCP Client and Server.ipynb` - 23 cells
The full lifecycle, then the reason the notebook exists.

🔴 **The framing problem, demonstrated.** Three separate `sendall(b"AAA")`, `(b"BBB")`,
`(b"CCC")` calls arrive at a single `recv()` as **`b'AAABBBCCC'`**. TCP guarantees bytes,
never message boundaries. Then all three fixes: length prefix with `struct`, newline
delimiters via `makefile()`, and fixed size - plus `recv_exactly`, because `recv(n)` returns
*up to* n bytes.

Also `send()` vs `sendall()` (the 4 MB test sent completely on loopback, which is exactly why
the truncation bug hides until production), `SO_REUSEADDR`/`TIME_WAIT` with the Windows
caveat, and what `ConnectionReset`/`BrokenPipe` actually mean.

### `11.3 UDP - Datagrams and Unreliability.ipynb` - 20 cells
The mirror image: **one `sendto` is one `recvfrom`**, always - boundaries preserved, directly
contrasted with 11.2's `b'AAABBBCCC'`.

🔴 **Truncation differs by platform**, confirmed by testing: Windows raises **WinError
10040**; Linux/macOS silently discard the excess. Either way the remainder is destroyed, and
a second read gets nothing. Datagram ceiling measured at **65507 bytes** (65535 − 20 IP − 8
UDP), with the practical ~1472 MTU advice.

Loss, reordering and duplication via a simulated lossy channel, then reliability by hand -
sequence numbers, acks, timeouts, retries - ending on the point that **retries cause
duplicates** when an ack is lost.

> **Three defects caught by reading output against claims.** The seeded RNG dropped nothing
> across all ten messages, so the cell demonstrating loss demonstrated none; reseeded to give
> 2 losses and 2 duplicates. A `ConnectionResetError` escaped and killed a cell - and
> revealed the surrounding text was wrong, since on Windows *unconnected* UDP sockets also
> receive ICMP errors. And acks were never lost, so the "retries cause duplicates" point was
> asserted but never shown; the ack path is now lossy too, and the receiver visibly processes
> two messages twice.

### `11.4 Serving Many Clients.ipynb` - 19 cells
Measured, not asserted. 6 clients needing 0.3s each:

| Approach | Wall clock |
|---|---|
| Serial (the 11.2 loop) | **1.81s** |
| Thread per client | **0.32s** (5.7x) |
| Thread pool, max 3 | **0.61s** - bounded, and cannot be swamped |
| `selectors`, one thread | 40 clients in **0.53s** |
| `asyncio` | **0.31s** |
| `asyncio` with one `time.sleep` | **1.81s** - serial again |

That last row is the lesson: changing one line makes async code 5.8x slower with no warning.
Includes 🔴 `asyncio.run()` failing inside Jupyter because a loop is already running, and a
`run_async` helper that works in both a notebook and a plain script. Notes that a thread
blocked on `recv()` **releases the GIL**, so it limits CPU parallelism, not I/O concurrency.

### `11.5 HTTP - From Sockets to requests.ipynb` - 24 cells
HTTP written by hand over a raw socket first - request text, `\r\n` line endings, the blank
line, the byte-for-byte response - with the observation that **HTTP solves 11.2's framing
problem using both techniques at once**: newline-delimited headers, then `Content-Length` as
a length prefix.

Then `urllib.request` (errors arrive as exceptions) and `requests` (🔴 they do **not** - a
500 is parsed happily unless you call `raise_for_status()`), all against a local
`http.server`. Timeouts as non-optional, proven with a `/slow` endpoint; `Session` connection
reuse; `Retry` with backoff restricted to idempotent methods; status-code semantics; and why
`verify=False` is never the answer.

> **Two bugs found here.** `handle_error` was overridden on the request *handler*, but
> `ThreadingMixIn` calls it on the **server** - so an abandoned request still dumped a
> traceback from a background thread. And `urllib.error.HTTPError` is file-like, backed by a
> temporary file; unclosed it raises `ResourceWarning`, which the harness runs as an error.

### Verification
- Folder 11: **0 unexpected problems**, run **twice** in succession with no stderr noise
- Folders 01-11: **0 unexpected problems**
- **57 notebooks** valid `nbformat` 4, **1331 code cells**, 1 syntax failure (the intentional
  6.1 demo)
- Every notebook ends by asserting no background threads survive
- `git status` clean; nothing binds outside `127.0.0.1`

---

## 12 Concurrency  *(renamed from `12 Multithreading`)*

One notebook, 38 cells, covering threads only. Now **five notebooks, 122 cells**: threads,
processes, the GIL, `concurrent.futures` and `asyncio`.

### 🔴 The constraint that shaped it
`multiprocessing` on Windows uses **`spawn`**: every child re-imports the parent's `__main__`
to rebuild the target function. Probing this first turned out to be essential.

- A function defined in a **notebook cell cannot be sent to a child at all** — a cell is not
  importable, so the pool dies with `BrokenProcessPool`.
- Without `if __name__ == "__main__":`, each child re-executes the parent module and spawns
  its own children. My first probe script hit exactly this.
- Under `smoke.py` the "main module" is the harness itself, so an unguarded pool would
  **re-run an entire folder of notebooks per child**.

So every multiprocessing example runs as a **guarded script via `subprocess`**. That is safe
under both Jupyter and the harness — and it happens to be the honest way to teach the guard,
since the guard is what you must write in real code anyway.

### `12.1 Concurrency, Parallelism and the GIL.ipynb` — **NEW**, 17 cells
Concurrency vs parallelism; CPU-bound vs I/O-bound; what the GIL is and the three myths.
Measured on the same machine, same code shape, same pool:

| workload | serial | 4 threads | speedup |
|---|---|---|---|
| CPU-bound | 0.71s | 0.78s | **0.91x** — *slower* |
| I/O-bound | 1.60s | 0.40s | **3.98x** |

The only difference is whether the work waits or computes. Includes the free-threaded build
(PEP 703) and the warning that removing the GIL makes races *more* likely, not less.

### `12.2 Threading.ipynb` — 38 cells *(rewritten from `Multithreading.ipynb`)*

**Fixed in the original:**
- 🔴 `getName()`, `setName()`, `activeCount()` — all deprecated, all raise under `-W error`,
  so two cells failed outright
- 🔴 `from threading import *` in seven cells — demonstrated shadowing the builtin `enumerate`
- 🔴 it **wrote into the repository** (`File2Save/`, and copied a video file); now `tempfile`
- 🔴 `RuntimeError: release unlocked lock` — a thread outlived its cell after
  `join(timeout=5)` on a 10-second job, and a later cell rebound the global `lock`, so the
  orphan released a *different* lock. Now the worked example for "`join(timeout=)` does not
  stop a thread"
- `input()` in the opening example, and an empty trailing cell

> ### 🔴 The textbook race condition no longer races
> The classic demonstration — four threads doing `counter += 1` — lost **zero** updates. I
> measured six configurations: up to **4,000,000 increments across 8 threads with the switch
> interval at 1 microsecond**, always exact, while the threads were verifiably interleaving.
> On CPython 3.14 the interpreter does not preempt between the three bytecodes of a bare
> in-place increment.
>
> Teaching "this loses updates" beside a cell printing a perfect total is worse than teaching
> nothing, so the notebook now says what is true: the tight loop **gets away with it**, that
> is an implementation accident rather than a guarantee, and adding one realistic yield point
> between the read and the write — any call that can block — loses **75% of all updates**.
> The `Lock` example then repairs *that* version, so the fix demonstrably fixes something.

**Added:** `RLock` and self-deadlock, two-lock deadlock with the lock-ordering fix,
`Event`/`Semaphore`/`Barrier`/`Condition`, **`queue.Queue`** producer/consumer with sentinels,
exceptions vanishing from threads, and thread-local storage.

### `12.3 Multiprocessing.ipynb` — **NEW**, 21 cells
`spawn` vs `fork` vs `forkserver`, with the **3.14 change of the Linux default to
`forkserver`**. The `__main__` guard proved by printing `__name__` in both processes — the
child sees **`__mp_main__`**, which is exactly why the guard works. Measured 4 tasks:
serial 2.15s, threads 2.05s (1.05x — the GIL), processes 1.07s (**2.00x**). Startup cost
measured too: a trivial task is far *slower* through a pool. `Queue`/`Pipe`/`Value`,
`shared_memory`, and what can be pickled.

> **Two self-inflicted bugs, caught by running it.** The `Pipe` example used a **lambda** as
> the `Process` target — the exact thing the next cell documents as unpicklable. And the
> pickling table claimed "nested functions" fail while the demo printed `OK`, because the
> function was defined inside `if __name__ == "__main__":`, which is still module scope. The
> table and the demonstration now distinguish *inside the guard* (picklable) from *inside
> another function* (not).

### `12.4 concurrent.futures.ipynb` — **NEW**, 22 cells
One API over both engines. ✅ `future.result()` **re-raises** — the fix for 12.2's silent
failures — with the caveat that a result never collected is just as silent. `map()` (input
order) vs `as_completed()` (completion order); `wait()` with `FIRST_EXCEPTION`; cancellation
and its hard limit; `max_workers`; and 🔴 the deadlock from submitting to a pool from inside
that pool. Swapping one class name:

| workload | threads | processes |
|---|---|---|
| CPU-bound | 1.92s | **0.94s** |
| I/O-bound | **0.40s** | 0.69s |

### `12.5 asyncio.ipynb` — **NEW**, 24 cells
Coroutines, the event loop, and 🔴 that calling an `async def` runs nothing. Sequential
`await` vs `gather()` (3.0x). **`TaskGroup`** (3.11+) shown to be strictly better than
`gather()`: `gather` reported one of two failures and left the third task running;
`TaskGroup` reported both and cancelled the sibling. `asyncio.timeout()` (3.11+), and the
point that async cancellation *actually cancels*, unlike `join(timeout=)`. 🔴 Blocking calls
measured at **3.9x** slower than `asyncio.to_thread`. `Semaphore` rate limiting — with the
observation that the counter needs **no lock**, because the 12.2 race is structurally
impossible between two awaits. Fire-and-forget tasks being garbage-collected, async context
managers and iterators, and an honest threads-vs-asyncio comparison.

### Verification
- Folder 12: **0 unexpected problems**, run **twice**; no repo writes; no leftover temp
  directories or child processes
- Folders 01-12: **0 unexpected problems**
- **61 notebooks** valid `nbformat` 4, **1362 code cells**, 1 syntax failure (the intentional
  6.1 demo)

---

## 14 Data Structure and Algorithm

The folder was effectively empty: `Introduction to Data Structure and Algorithm.ipynb` was
3 cells whose **only code cell was blank** (a "Greatest Common Divisor" heading with no
implementation), and `Advance Coding.ipynb` was 2 competition problems, one requiring
`input()`, plus an empty trailing cell.

Being built out as a full DSA curriculum, beginner to advanced, with theory, runnable
implementations and interview questions. **Complete: 346 cells across 16 notebooks.**

### `14.1 Complexity Analysis.ipynb` - **NEW**, 23 cells
Why we count operations rather than seconds; Big-O with Ω and Θ; the growth classes with
what each feels like at n = 1,000,000; reading complexity off loops, nested loops and
recursion; amortised analysis; space complexity including stack depth; and 🔴 five specific
ways Big-O misleads.

Demonstrated rather than asserted: naive `fib(30)` takes **2,692,537 calls**, and
`@functools.cache` reduces it to **31**. The list-growth cell prints the actual
reallocation points (`1, 5, 9, 17, 25, 33, ...`) and the widening gaps between them.

> 🔴 **The doubling experiment had to be rebuilt.** Wall-clock timing was too noisy on a
> loaded machine to teach from - repeated trials gave linear ratios of 2.36/1.92, 2.86/1.29,
> 2.31/1.99 and 3.80/1.87, and a printed **1.29x** teaches the wrong row of the table.
> `time.process_time()` was tried and has ~14.6 ms resolution on Windows (it returned
> zeros); pre-building the data and best-of-7 did not fix it either.
>
> The cell now **counts operations first** - giving exact `2.00x` and `4.00x` with no
> machine dependence - and then times the same functions with the noise stated openly. That
> ordering is the better lesson anyway: counting is how you reason, timing is how you check.

### `14.2 Python's Built-ins and Their Real Costs.ipynb` - **NEW**, 20 cells
Arguably the highest practical value in the folder: the complexity of every operation used
daily, and the four mistakes behind almost all accidental O(n²) in real Python.

Measured on this machine:

| | | |
|---|---|---|
| `x in list` vs `x in set` | 20,000 items | **265x** |
| `list.pop(0)` vs `deque.popleft()` | draining 30,000 | **312x** |
| `+=` in a loop vs `str.join` | 40,000 pieces | **652x** |
| `deque[i]` vs `list[i]` | the other side of the trade | list **24x** faster |

Also: how `dict`/`set` reach O(1) and what that demands of keys - including a live
demonstration that **mutating a key makes its entry unreachable and un-deletable**; the
CPython in-place string optimisation being defeated by a second reference (8x); and why
`bisect.insort` is O(n) despite an O(log n) search.

### `14.3 Arrays, Strings and Two Pointers.ipynb` - **NEW**, 23 cells
The four patterns that cover most array and string interview questions: converging two
pointers, fast/slow read-write pointers, sliding windows (fixed and variable), and prefix
sums.

Each is measured: the sliding window does **2,000 operations where recomputation does
97,550** (49x at k=50). The prefix-sum + hash-map trick for subarray counting is
cross-checked against brute force on four inputs including negatives and zeros.

Careful attention to the cases that catch people: `'dvdf'` returning **3, not 2** in the
longest-unique-substring window (the `last_seen[char] >= left` guard); all-negative Kadane
returning **the largest element, not 0**; `k %= n` before rotating; and the honest point
that `data[::-1]` is correct but is **not** O(1) space.

### Batch 2: Linear structures - 70 cells

### `14.4 Linked Lists.ipynb` - **NEW**, 23 cells
Nodes and references; the full complexity contrast with arrays; insert, delete and traverse;
the **dummy head** trick that removes the head special case; reversal both iteratively
(O(1) space) and recursively (O(n) stack, and shown hitting `RecursionError` at 2,000 nodes);
**Floyd's cycle detection** including where the cycle starts; find-the-middle and
nth-from-end in one pass; merging two sorted lists by rewiring only.

Opens by being honest that you will **almost never write one in Python** - and then showing
where they genuinely live, with a working **LRU cache**: a `dict` for O(1) lookup plus a
doubly linked list for O(1) reordering and eviction. Neither structure can do it alone.

Closes with the palindrome check that combines three techniques and **restores the list
afterwards** - mutating a caller's data and not putting it back is treated as a real defect.

### `14.5 Stacks and Queues.ipynb` - **NEW**, 25 cells
LIFO vs FIFO and how to recognise which a problem wants; bracket matching with all **three**
failure modes (the unclosed-opener case being the one people forget); RPN evaluation, with
`10 2 /` vs `2 10 /` as the test that catches a reversed operand pop; the call stack as a
stack, and the same computation rewritten with an explicit stack to escape the recursion
limit.

**Monotonic stacks** get full treatment - next-greater-element, daily temperatures, and
largest-rectangle-in-a-histogram with its sentinel. Measured on a strictly decreasing input
of 2,000: **4,000 operations versus 2,001,000** for brute force, with the amortised argument
(each index pushed once, popped at most once) stated explicitly because interviewers ask for
it.

Also **min stack** (O(1) minimum via a second stack of running minimums) and a **queue from
two stacks**, whose amortised claim is *measured*: 10,000 enqueues and 10,000 dequeues
produce exactly **1.0 element transfers per element**. Ends on `deque` vs `queue.Queue` and
when thread safety is the point (**12.2**).

### `14.6 Hashing.ipynb` - **NEW**, 22 cells
How a key becomes a memory location; chaining vs open addressing; a **working `HashMap`
built from scratch** with instrumentation, showing capacity doubling at load factor 0.75
while the longest bucket stays at 2-3 entries.

🔴 **O(1) degrading to O(n), demonstrated:** a legal-but-useless `__hash__` returning a
constant makes 2,000 lookups **545x slower**. Ties into why CPython randomises string hashing
per process - the hash-collision denial-of-service - and therefore why `hash()` values must
never be persisted.

The `__eq__`/`__hash__` contract with all three failure modes shown live, including an
inconsistent pair where equal objects are **silently not found**. The four hashing patterns
(frequency, seen-set, complement, grouping) and composite keys - including `casefold()` vs
`lower()`, demonstrated with `"STRASSE"` and `"Straße"`, which `lower()` fails to match.

Finishes with CPython internals (compact layout, insertion order as a *consequence* of it,
dict measured smaller than the equivalent set) and two non-obvious interview answers:
longest-consecutive-sequence in O(n), and O(1) insert/delete/get-random via the swap-with-last
trick.

### Housekeeping (author's deletions, recorded here)
The two legacy stubs flagged in batch 1 were removed by the author, along with a PowerPoint
file in folder 01:

- `Introduction to Data Structure and Algorithm.ipynb` - 3 cells, its only code cell **empty**
- `Advance Coding.ipynb` - 2 competition problems, one requiring `input()`
- `01 Basic/00 First Step to Programming and Python.pptx`

The GCD topic those stubs gestured at is still planned for **14.12** (recursion).

### Batch 3: Hierarchical structures - 72 cells

### `14.7 Trees and Binary Search Trees.ipynb` - **NEW**, 26 cells
Vocabulary (with the depth-vs-height confusion addressed head-on); all four traversals
recursively *and* iteratively; BST search, insert and the three-case delete; rotations;
height, diameter, LCA; serialise/deserialise; sorted-array-to-BST; kth smallest.

🔴 **Degeneration measured.** The same 2,000 values inserted sorted vs shuffled:

| insertion order | height | comparisons to find the last value |
|---|---|---|
| sorted | **1,999** | **2,000** |
| shuffled | 24 | 11 |

> **A bug of my own, kept as a lesson.** The first version of that cell built the degenerate
> tree with the *recursive* insert - and died with `RecursionError` before it could measure
> anything, because recursive insert costs O(height) stack and here height IS n. The cell now
> uses an iterative insert and says exactly that: degeneration breaks more than lookup speed.

🔴 **The BST validation trap** gets a full treatment: the naive parent/child check declares
`10 / (5, 15 / (6, 20))` valid, and the notebook shows in-order producing `[5, 10, 6, 15, 20]`
to prove it is not. Both correct approaches (range-passing and in-order monotonicity) are
implemented alongside the wrong one.

### `14.8 Heaps and Priority Queues.ipynb` - **NEW**, 23 cells
The heap property and why it is *weaker* than a BST; the array representation and its index
arithmetic; sift-up and sift-down implemented by hand before reaching for `heapq`; top-k;
merging k sorted sequences; running median with two heaps, cross-checked against
`statistics.median` over 500 random inserts.

> 🔴 **A false claim I had to correct.** The cell originally asserted that building a heap by
> pushing n items is O(n log n). Measured, that is **only the worst case**. On random input
> the swap count stays at ~1.28n at every size - constant work per push - because a random
> value is usually already near the bottom. Provoking the real worst case needs *descending*
> input, where push/n rises 7.99 → 9.98 → 11.98 → 13.98, gaining 2 per quadrupling of n,
> which is log₂n. `heapify` stays at ~n on both. The cell now shows both inputs side by side,
> which makes the average-vs-worst-case distinction concrete rather than blurred.

Top-k measured at **8.6x faster** than sorting for k=10 of 400,000, with O(k) memory - plus a
streaming version that never holds more than k items. The priority-queue tie-breaking trap is
demonstrated live (`TypeError: '<' not supported between instances of 'dict' and 'dict'`) and
fixed with a counter, which also buys stability.

### `14.9 Graphs.ipynb` - **NEW**, 23 cells
Adjacency list vs matrix; BFS and DFS shown to be *the same code* with a queue swapped for a
stack; unweighted shortest paths; Dijkstra with lazy deletion (**14.8**); Bellman-Ford;
Kahn's topological sort; cycle detection; connected components and the grid "number of
islands" variant; graph cloning; bipartite checking.

Uses **the same service-dependency graph as 10.6**, so the recursive-CTE and Cypher versions
there line up with the algorithms here.

🔴 **The visited set** is demonstrated by omitting it - an unguarded traversal on a 3-cycle
runs to its step limit and reports it would never stop.

🔴 **Cycle detection differs by graph type**, and both wrong answers are shown: a plain
visited set wrongly flags the service graph (three routes to `userdb` is *not* a cycle), and
an undirected check without the parent guard wrongly flags a tree.

> **A second bug of my own.** The "Dijkstra breaks on negative weights" cell originally
> reported the *correct* answer, disproving its own text - because the improved vertex had no
> outgoing edges, so the stale value never propagated. Adding one edge after it makes the
> failure real: Dijkstra reports cost **3** where the true answer is **2**, and Bellman-Ford
> gets it right.

### Batch 4: Algorithms - 101 cells

### `14.10 Sorting.ipynb` - **NEW**, 24 cells
The O(n²) family (and why insertion sort is not a toy - O(n) on nearly-sorted input is why
real sorts embed it); merge sort; quicksort with its worst case **provoked on purpose**;
heap sort; stability; the Ω(n log n) lower bound; counting and radix sort; Timsort; and
using `sorted()` well.

Measured highlights:

| | |
|---|---|
| Counting sort (Python) vs `sorted()` (C) on 30,000 values in 0-99 | **3.2 ms vs 6.3 ms** |
| `sorted()` on already-sorted vs random, 300,000 items | **16x faster** |
| Quicksort with `data[0]` pivot on sorted input | quadratic comparisons, recursion depth = n |

Interpreted Python beating C is the point of the counting-sort cell: it escaped the
comparison bound entirely. The Timsort cell shows the adaptive best case you hit constantly
in practice.

### `14.11 Searching and Binary Search.ipynb` - **NEW**, 18 cells
The off-by-one minefield, with **one half-open template** to avoid all of it; `bisect_left`
vs `bisect_right` and what each is *for*; rotated arrays, verified **exhaustively over every
rotation and every target** including the non-rotated case; quickselect.

🔴 **Binary search on the answer** gets the depth it deserves - the pattern behind minimum
ship capacity, Koko bananas and split-array-largest-sum. The monotonicity precondition is
*printed*: `NNNNNYYYYYYYY...`, with the answer at the first `Y`. Quickselect measures ~2n
comparisons where sorting would need 61,438.

Also the `mid = (lo + hi + 1) // 2` infinite-loop trap, and the note that Python's arbitrary
precision integers make the famous Java overflow bug impossible here.

### `14.12 Recursion and Backtracking.ipynb` - **NEW**, 19 cells
Base case, recursive case, and the leap of faith; **Euclid's GCD** - which folds in the topic
from the deleted `Introduction to Data Structure and Algorithm.ipynb` stub, whose only code
cell was empty; the recursion limit and why raising it is the wrong fix; memoisation as the
bridge to DP; backtracking's choose/explore/**unchoose**.

**Pruning measured** on N-Queens, with identical answers both ways:

| n | pruned nodes | unpruned nodes | saving |
|---|---|---|---|
| 6 | 153 | 55,987 | 366x |
| 8 | 2,057 | 19,173,961 | **9,321x** |

Plus word search (where the *unmark* is the shipped bug), and generating valid parentheses -
whose counts come out as the Catalan numbers.

### `14.13 Dynamic Programming.ipynb` - **NEW**, 21 cells
The two preconditions; the **four-step progression** (naive → memoised → tabulated →
space-optimised) demonstrated end to end on Fibonacci; how to *recognise* a DP problem;
1-D classics (climbing stairs, house robber, coin change) and 2-D (LCS, edit distance, 0/1
knapsack); reconstructing the answer, not just its size; and when DP does **not** apply.

🔴 **Greedy is shown failing three times**, because that is the distinction that costs marks:
coin change `[1,3,4]` target 6 (greedy 3 coins, optimal 2), house robber `[2,7,9,3,1]`, and
0/1 knapsack where greedy loses by 10 on a constructed case.

Longest increasing subsequence closes it with both implementations: **1,049.9 ms vs 0.7 ms**
at n=4,000 - a **1,555x** gap, agreeing on 300 random inputs.

### `14.14 Greedy and Divide-and-Conquer.ipynb` - **NEW**, 19 cells
When greedy is provably right (the **exchange argument**, worked for interval scheduling)
and when it is not. All three interval-scheduling sort keys are run: earliest-end is correct,
earliest-start and shortest-duration are shown failing on specific inputs.

**Fractional vs 0/1 knapsack** is the sharpest illustration of the greedy/DP boundary in the
folder - identical numbers, one word different in the problem statement, and the correct
paradigm changes. **Huffman coding** compresses `abracadabra` by 74% and decodes with no
delimiters. Divide and conquer covers the master theorem informally, maximum subarray
(**29x slower** than Kadane - D&C is not automatically better), and Karatsuba.

Ends with a decision table for greedy vs DP vs D&C.

> **A bug worth recording.** The Karatsuba verification was **vacuous**: I wrote
> `all(... for _ in range(0)) or all(... for _ in range(500))`, and `all()` over an empty
> generator is `True`, so the `or` short-circuited and the real comparison **never executed**.
> It printed `True`. That is the worst kind of passing test, because it reads as evidence.
> Now it runs and reports "500 random pairs: 0 mismatches".

### Batch 5: Advanced and practice - 37 cells

### `14.15 Union-Find, Tries and Bit Manipulation.ipynb` - **NEW**, 21 cells
**Union-Find** with path compression and union by size, and the two optimisations
**measured** against a naive implementation on the chain-building worst case:

| n | naive steps | optimised steps | ratio |
|---|---|---|---|
| 1,000 | 499,500 | 1,996 | 250x |
| 4,000 | 7,998,000 | 7,996 | **1,000x** |

The optimised count is essentially 2n while the naive one is n²/2. Kruskal's MST is built on
it, using `union` returning `False` as the cycle detector - and is a good example of
*provably correct* greedy to contrast with **14.13**'s failures.

**Tries**, with the honest verdict measured rather than assumed: for a **static** word list a
sorted list plus `bisect` (**14.11**) matches a trie and uses far less memory. The trie wins
when the set changes constantly, since insertion is O(L) rather than O(n).

**Bit manipulation**: the operators, the four standard manipulations, XOR's three properties
and the one-liners they enable, Kernighan's `x &= x-1` (with a version note for
`int.bit_count()`, new in 3.10), and bitmasks as sets - ending with **bitmask DP for TSP**,
verified against brute force over all permutations.

🔴 Also demonstrates the XOR-swap failure mode: swapping an element with **itself** zeroes it.

### `14.16 Interview Patterns and Problem-Solving.ipynb` - **NEW**, 16 cells
The capstone. A six-step framework; **the pattern-recognition table** mapping question
phrasing to technique across all fifteen notebooks; reading constraints to infer the intended
complexity (with a computed table showing what each complexity costs at each n); the full
complexity cheat sheet; and what interviewers actually assess.

Absorbs the two problems from the deleted `Advance Coding.ipynb` - diagonal difference and
positive/negative/zero fractions - rewritten without `input()`, in one pass, with tests and
the edge cases the originals ignored (empty input, and the shared centre element when n is
odd).

Ends with a 30-problem practice set naming the *pattern* rather than the solution, an index
of the folder, and a `verify(fast, slow, generate)` harness - which is then used on a
**deliberately broken** Kadane implementation and finds the failure on `[-7, -6]` in under a
second.

## 14 Data Structure and Algorithm - complete

**346 cells across 16 notebooks**, built in five batches from an effectively empty folder
(two stubs, one with a blank code cell and one requiring `input()`).

Every algorithm is cross-checked against a brute-force implementation, the standard library,
or an exhaustive search. That discipline caught several errors in my own drafts, each
recorded above: a race condition demonstration that did not race, a heap claim that was true
only in the worst case, a Dijkstra failure demo that printed the correct answer, and a
Karatsuba verification that was vacuously true.

### Verification
- Folder 15: **0 unexpected problems**, run twice
- All 13 folders: **0 unexpected problems**
- **75 notebooks** valid `nbformat` 4, **1489 code cells**, 1 syntax failure (the intentional
  6.1 demo)

**Note:** the GCD topic from the deleted `Introduction` stub is now covered in **14.12**
(Euclid's algorithm). The competition problems from `Advance Coding` remain for **14.16**.

### Verification
- Folder 15: **0 unexpected problems**, run twice
- Folders 01-12 and 15: **0 unexpected problems**
- **75 notebooks** valid `nbformat` 4, **1489 code cells**, 1 syntax failure (the intentional
  6.1 demo)
- Every algorithm cross-checked against a brute-force implementation

---

## Renumbering: planned folders 16–21 → 15–20

The curriculum ran `00`–`14` and then jumped to `16` — a gap left by deleting `13 GUI` and
`14 Project` and renaming `15` → `14`. Closed before writing any new content, because the cost
only grows: 21 cross-references now, against hundreds once the new folders reference each other.

**21 references rewritten across 14 notebooks**, driven by an explicit
`(file, cell, old, new)` table that asserts exactly one match per edit — not a regex sweep. Of
317 lines in the repository containing 16–21 as a bare number, only 23 were reference-shaped and
**two of those were values, deliberately left alone**: the `| 1,000,000 | 1,000,000 | **20** |`
row in `14.11`'s binary-search table, and "a tree of height **20**" in `14.7`.

`README.md` gained the new map and a numbering note. `.gitignore` gained `.pytest_cache/`,
`.mypy_cache/`, `.hypothesis/`, `.coverage`, `htmlcov/`.

> Earlier entries in this file use the **old** numbering. They have not been rewritten — this
> is a historical record.

---

## 15 Testing and Debugging

New folder, nothing existed. Testing had appeared only in passing: `assert` in **6.1**,
`@pytest.fixture` in a decorator table in **4.4**, a `pytest>=8.0` line in **7.2**'s
`requirements-dev.txt`, the `assertEquals` removal note in **1.1**, and `14.16`'s
`verify(fast, slow, generate)` harness with its forward reference *"done properly with
`pytest`"*. **15.1** picks that harness up by name.

Built against **pytest 9.1.1** and **Python 3.14.4**. `hypothesis` 6.165.10 and `coverage`
7.15.4 were installed into `.venv` for **15.6**.

**Batch 1: foundations — 106 cells across 3 notebooks.**

### `15.1 Why Test, and the assert Statement.ipynb` — **NEW**, 34 cells
The cost curve; `assert` anatomy; Arrange–Act–Assert; unit/integration/e2e and what the pyramid
actually claims; and a **working 20-line test runner** built so that `pytest` later reads as
"the one I didn't have to write" rather than magic. It reports `FAIL` vs `ERROR` separately,
which sets up **15.2**.

Demonstrated rather than asserted:

- 🔴 **`python -O` deletes `assert` entirely.** The same file run twice: normally a 150%
  discount raises; under `-O` it returns **−100.0**. Then the bytecode, which is the honest
  proof — **29 instructions → 9**, `RAISE_VARARGS` gone, and the failure message
  `"percent out of range"` **no longer in `co_consts`**. There is nothing left to trigger.
- 🔴 **`assert (expr, msg)` can never fail** — a non-empty tuple is truthy. Shown passing while
  claiming `8.0 == 999.0`.
- 🔴 **Order-dependent tests.** Two tests sharing a module-level cache: order A passes, order B
  fails. Same code, same tests, different verdict.

> 🔴 **The tuple-`assert` cell had to be moved into a subprocess.** Python 3.12+ emits
> `SyntaxWarning: assertion is always true, perhaps remove parentheses?` at **compile** time —
> which under the harness's `warnings.simplefilter("error")` becomes a `SyntaxError`, breaking
> both the smoke run and the "every cell compiles" check. Running it in a child interpreter
> fixes that *and* shows the learner the real warning, which is better teaching. The subprocess
> helper was moved earlier in the notebook to make this possible.

> 🔴 **A claim of mine was wrong and the output caught it.** The bytecode cell originally tested
> for the string `"AssertionError"` in the disassembly and the markdown table asserted it was
> present normally. It printed `False` in **both** modes — in 3.14 the exception is loaded via
> `LOAD_COMMON_CONSTANT`, so it is not in `co_names` or any `argval`. Replaced with two
> discriminators that actually hold: the `RAISE_VARARGS` opcode and the message in `co_consts`.

### `15.2 unittest - the Standard Library.ipynb` — **NEW**, 36 cells
`TestCase`, the `assert*` family, the full lifecycle, `subTest`, `assertRaises`/`assertLogs`/
`assertWarns`, skips and expected failures, and `python -m unittest discover` run for real
against a temporary two-package project. One `Job` state machine carries the whole notebook.

Measured, not claimed:

- **`assertTrue` vs `assertEqual` on the same bug**: `AssertionError: False is not true`
  against `AssertionError: 'running' != 'done'` with a diff. That is the entire argument for
  the specific methods.
- 🔴 **Failure vs error**, side by side — a wrong answer versus a `ValueError` — and the note
  that `pytest` discards the distinction.
- **The lifecycle trace printed as it happens**: `setUpClass → (setUp → test → tearDown) × 3 →
  tearDownClass`, with `test_a` running before `test_b` **because methods run alphabetically**,
  and a third test proving `setUp` isolation held.
- **`subTest` against a plain loop** on the same 5-case table: the loop reports **1** failure
  and stops; `subTest` reports **both** `'2.5'` and `' 5 '`, named. And `testsRun` is 1 either
  way — which is the argument for `@parametrize`.
- **`@expectedFailure` on a bug someone quietly fixed** → `unexpected success`, reported.
- 🔴 **The 3.12 alias removals**, probed with `hasattr`: all 8 of `assertEquals`,
  `assertNotEquals`, `assertAlmostEquals`, `failUnless`, `failUnlessRaises`,
  `assertRegexpMatches`, `assertNotRegexpMatches`, `assertItemsEqual` report `False`.

> 🔴 **Two cells asserted things they did not show.** The `addCleanup` cell claimed LIFO order
> and "runs even if the test fails" while printing neither; it now registers three cleanups per
> test and logs the order, printing `3rd registered` before `1st registered`, with a
> deliberately failing third test proving cleanup still ran. And the failure-vs-error cell was
> printing the last line of the traceback — which is a diff line (`+ running`), not the
> exception. It now scans back to the real `SomeError: message` line.

### `15.3 pytest - Writing and Running Tests.ipynb` — **NEW**, 36 cells
Discovery, node IDs, exit codes, assertion rewriting, `approx`, `raises`, `parametrize`, the
CLI, and marks. Every example runs `pytest` in a throwaway project via `subprocess`, so all
output is genuine.

- **Assertion rewriting** explained as what it is — bytecode rewriting at import — then shown
  on five failures: string (with the caret pointing at the differing character), dict
  (`Differing items`), list (`At index 1 diff`), set (`Extra items in the left set`), and 🔴 a
  **bare boolean** `assert x.startswith(...)` which can only manage `assert False`, because
  there is nothing to diff.
- 🔴 **Exit code 5.** A project whose tests are named `check_*` runs **zero** tests and reports
  no failures. Only the exit code distinguishes it from a green build.
- 🔴 **`pytest.raises(Exception)` passing for the wrong reason** — the demo passes because a
  `bogus_kwarg` typo raised `TypeError`, not because the code under test raised anything. Next
  to it, `DID NOT RAISE` proves the opposite failure mode.
- **`@parametrize`** generating 14 real tests where `subTest` gave 1, with `pytest.param(id=...)`
  for readable IDs, a per-case `xfail(raises=ValueError)`, and stacked decorators producing
  the 2 × 3 = 6 cartesian product.
- **`unittest` and `pytest` files in one run**: 3 tests from one, 5 from the other, 8 collected.
- **The CLI**: `--collect-only`, `-k` (4 selected, 2 deselected), `-x` stopping after 1 failure,
  then `--lf` rerunning exactly that one.

> 🔴 **Three states of a custom mark, and the one that breaks builds.** The same file run three
> ways: unregistered with `-m "not slow"` → **exit 0, and the typo'd `@pytest.mark.slwo` test
> ran anyway** because the mark did nothing; unregistered under `-W error` → **exit 2,
> collection error, zero tests run**; registered in `pytest.ini` with `--strict-markers` →
> exit 2 with `'slwo' not found in markers configuration option`, naming the typo. The middle
> case matters because `filterwarnings = error` is an otherwise-good setting many projects ship.

> 🔴 **A second wrong claim of mine, caught by reading the output.** The `approx` section stated
> that "a relative tolerance times 0 is 0, so `approx(0)` only matches exactly 0". It does not:
> `pytest.approx(0.0)` falls back on the **default absolute tolerance of `1e-12`**, so `1e-18`
> passes. The real trap is subtler and now taught instead — `approx(0.3)` has an effective
> tolerance of `3e-07` while `approx(0.0)` has `1e-12`, a million times tighter, so a residual
> of `1e-11` fails while looking negligible; and passing `rel=` does not help, because it is
> still multiplied by zero. The cell asserts both tolerances directly and now fails 3 of 8.

> **`encoding="utf-8"` on `subprocess.run`.** pytest prints `0.0 ± 1.0e-12`; without it the
> Windows locale codec turned `±` into `Â±` throughout the captured output.

**Batch 2: practice — 78 cells across 3 notebooks.** Folder total: **184 cells, 6 notebooks**.

### `15.4 Fixtures, Isolation and Test Data.ipynb` — **NEW**, 29 cells
Fixtures presented as dependency injection — the parameter name *is* the wiring — then scopes,
`conftest.py`, and the built-ins. `yield` fixtures are tied back to `@contextmanager` (**6.3**),
which is what they are.

Demonstrated:

- **Teardown runs after a failing test** — the event log shows setup / test B fails / teardown.
- **The full scope order**, from a three-deep chain (`connection` → `schema` → `db_engine`):
  session sets up first and tears down last, and the function-scoped fixture is rebuilt **twice**
  for two tests. Then the same picture from `--setup-show`, which needs no instrumentation.
- 🔴 **The session-scoped mutable fixture** — `test_b` fails only because `test_a` ran first,
  and pytest's report prints `registry = {'jobs': ['build-1']}`, which is usually enough to
  diagnose it. Three fixes given, in order of preference, with a **factory fixture** built out.
- **The built-ins**: `tmp_path` (two different directories printed, one per test), `capsys`,
  `caplog`, `recwarn`, and `monkeypatch.setenv` **with a second test proving the variable is
  gone again**.
- `--fixtures-per-test`, which prints "no docstring available" for the local fixtures — making
  the case for the Best Practice two cells later.
- **Parametrised fixtures**: 2 tests × 2 params = 4 generated tests, and a third test that does
  not request the fixture runs **once**.

> 🔴 **Fixtures do not work on `unittest.TestCase` methods**, and the real error is quoted
> because it is so misleading: `TypeError: SpoolTests.test_...() missing 1 required positional
> argument: 'spool'`, with a traceback pointing into `unittest/case.py` rather than pytest.
> (An earlier draft of this notebook paraphrased the message as "takes 2 positional arguments
> but 1 was given" — wrong; corrected against the actual output.)

> **Build note.** Three cells initially failed with `IndentationError: unexpected indent`. The
> embedded test sources are triple-quoted strings inside a notebook cell, and a `\n` written
> inside one becomes a **real newline** — leaving a continuation line at column 0, which
> defeats `textwrap.dedent`, so nothing was dedented and the written file was invalid Python.
> Fixed by making the embedded sources **raw strings**. Two other claims in the notebook were
> asserted but not shown, and now are: `addCleanup` LIFO ordering, and cleanup running after a
> failure.

### `15.5 Test Doubles - Mocking, Patching and Faking.ipynb` — **NEW**, 22 cells
Dummy / stub / spy / mock / fake, with the distinction that actually matters: a stub sets up a
situation and you assert on the **result**; a mock asserts on the **interaction**, so every mock
assertion is a claim about your own implementation and breaks on refactor.

- `Mock` call recording and the assertion family; `return_value` vs `side_effect`, with a retry
  test that fails twice then succeeds — **3 attempts, sleeps of 1 and 2 seconds, instant**,
  because `sleep` was passed in rather than patched.
- **`Mock` vs `MagicMock`** across five protocols. 🔴 The unsupported ones raise **two different
  exception types** — `TypeError` for `len`/`[]`/`iter`, but `AttributeError: __enter__` for
  `with`, because `Mock` auto-creates ordinary attributes and not dunders. (The first draft
  caught only `TypeError` and the cell raised.)
- 🔴 **Where to patch**, run as two tests in one file: `patch("clock.now")` has **no effect** —
  the failing assertion prints a real Unix timestamp — while `patch("scheduler.now")` works,
  because `from clock import now` binds a second name. With the table for both import styles.
- 🔴 **`autospec`**: a plain `Mock` accepts a wrong signature, an invented method **and a
  misspelled one** — the demo ends by asserting `fake.saev.called`, so the typo is "verified".
  `create_autospec` rejects both: `too many positional arguments` and
  `Mock object has no attribute 'saev'`.
- **`monkeypatch`** pinning down a 7-day grace period at three points including the exact
  boundary — untestable otherwise, since you cannot wait eight days — plus a fourth test proving
  the real function was restored.
- A **fake** `CacheStore` and an injected `ProfileService`: 3 calls, **2 backend loads**, no
  patching and no `Mock` at all. Then the three rules — don't mock what you don't own, a
  drifting fake is worse than no test, and asserting on calls tests the implementation.

### `15.6 Testing in Practice - Coverage, Properties, Structure and CI.ipynb` — **NEW**, 27 cells
The closing notebook: layout, coverage, property-based testing, doctest, flakiness, CI, and an
**Interview Questions** section of 13 questions indexed back to the notebook that answers each.

- 🔴 **The coverage demo that makes the point.** `retrying.py` reaches **100% statement
  coverage** on four passing tests and contains **two bugs**: `429 Too Many Requests` is absent
  from `RETRYABLE`, and no test ever takes the `delay <= cap` branch. The first is the important
  one — **coverage is structurally incapable of finding missing code**, because a requirement
  you never implemented has no line to miss.
- The same file under `--branch` drops to **92%** with `BrPart 1`, naming the missed jump
  `13->15`. Hence `branch = true` in the recommended config.
- **Property-based testing** as the grown-up form of **14.16**'s `verify()`. `hypothesis` finds
  `truncate` returning a string **longer than the limit** and shrinks the counterexample to
  `text='0', limit=0` — with its `Explanation` naming the only line run by failing cases. The
  bug: `text[:limit - 3]` slices with a negative index when `limit < 3`.
- The **stdlib-only version** of the same idea, so the notebook stands up without `hypothesis`:
  `check_property` finds the same bug but returns `('RcLtcaJorHe', 2)` — the contrast is exactly
  what shrinking buys you.
- **doctest**: a docstring claiming `humanise(45) == '45sec'` when it returns `'45s'`, caught by
  `--doctest-modules`.
- `--durations=3` and `-m "not slow"`; a flakiness cause/fix table; a GitHub Actions workflow
  annotated line by line; and a decision table mapping situations to tools across the folder.

> 🔴 **Two demos had to be redesigned because the first versions did not prove their point.**
> The original coverage example reported 100% on a function that was simply *correct*, which
> demonstrates nothing; and the original hypothesis property (idempotence of a tag normaliser)
> **passed** all 200 examples. Both were rebuilt around bugs that genuinely exist.

> **Build note.** The doctest cell needs three nested levels of triple-quoted string — build
> script, notebook cell, and the docstring inside the generated file — which two quote styles
> cannot express. Resolved by escaping the innermost delimiter (`\\"\\"\\"`), the same approach
> already used in **15.3**.

### Verification
- Folder 15: **0 unexpected problems**, run **twice**, identical both times
- **184 cells across 6 notebooks** — 34 / 36 / 36 / 29 / 22 / 27; **67 code cells**, all
  compile, all outputs cleared, `nbformat` 4.4
- Still **no `EXPECTED` entries**: every deliberate failure runs inside a subprocess or a
  `TextTestRunner`, so no notebook cell raises
- `git status` clean apart from the new files; no temp directories survived either run
- Full-repository sweep after the renumber: folders 01–06, 08–12 and 14 all **0 unexpected
  problems**

> ⚠️ **One unreproduced failure, recorded rather than explained away.** During the first
> full-repository sweep, `07 Module and Packages` reported **1 unexpected problem**. The output
> was truncated by the command that produced it, and the folder has since reported **0** on six
> consecutive isolated runs, so the message was never captured. The renumber touched only a
> markdown cell in `7.2`, so this is not new. The most likely candidate is `7.2` cell 10, which
> runs **`pip` four times via `subprocess` with no `timeout=`**; `7.1` also uses `random` 36
> times without a seed. Worth pinning down separately — a suite that fails once in seven runs is
> exactly the flakiness **15.6** warns about.

---

## 15 Testing and Debugging — the debugging half

**Batch 3: debugging — 68 cells across 3 notebooks.** Folder total: **252 cells, 9 notebooks**.

The folder was renamed from `15 Testing` (commit `31ec917`) on the author's suggestion, because
testing and debugging are one loop: a failing test is the start of a debugging session. The
rename cost 2 notebook references, a README row, a CHANGELOG heading and HANDOFF.

### The gap this closed
A scan for debugging coverage across all 78 existing notebooks found **`pdb`, `breakpoint()`,
`set_trace`, `post_mortem` and `faulthandler` in exactly zero of them.** For a curriculum that
reaches bitmask DP and asyncio, the interactive debugger being entirely absent was the largest
remaining hole after type hints.

What *did* exist was respected rather than repeated: `6.1` already teaches reading a traceback
bottom-up, `6.2` covers `raise ... from`, and `12.2` covers exceptions vanishing in threads.
15.7 builds on all three.

> **The constraint that shaped 15.8.** `pdb` is interactive and the smoke harness skips blocking
> calls, so a debugging notebook could easily have become unrunnable transcripts. It did not:
> every session runs a real script through `subprocess` with commands fed on stdin, so all
> output is genuine `pdb` output. Verified before writing a line.

### `15.7 Reading Failures - Tracebacks, Exceptions and Logging.ipynb` — **NEW**, 23 cells
- 🔴 **Fine-grained error locations (3.11+)** on `order["items"]["count"] * order["price"]["net"]`
  — the `~~~~~~~~~~~~~~^^^^^^^` lands under the `["net"]` subscript, naming the sub-expression
  that raised rather than the line.
- **Chained exceptions, both forms, run side by side**: *"The above exception was the direct
  cause"* (`__cause__`) vs *"During handling of the above exception"* (`__context__`) — with the
  point that the second often means **the `except` block itself is broken**, so the *top*
  traceback is the real failure.
- The **`traceback` module** as structured data: `format_exception_only`, `extract_tb`, and
  `TracebackException` walked frame by frame down to the deepest one. Version note for
  `exc_type` → `exc_type_str` (3.13).
- **`sys.excepthook`** as a crash reporter, and the table of what each hook does *not* catch —
  `threading.excepthook`, the asyncio handler, `sys.unraisablehook`.
- **print vs logging vs debugger**, with `logging.exception()` attaching a full traceback, and
  why `log.debug("...%s", x)` beats an f-string when the level is off.
- **`python -X dev`** surfacing a `ResourceWarning: unclosed file` that the default run hides
  entirely.
- **`faulthandler.dump_traceback_later`** producing a diagnosis from a **hung** process —
  naming both stuck threads and the exact line each sits on. There is no traceback for a hang,
  which is the whole point.

### `15.8 The Interactive Debugger - pdb and breakpoint.ipynb` — **NEW**, 25 cells
Every transcript real, produced by feeding commands to a subprocess.

- `breakpoint()` and **`PYTHONBREAKPOINT=0`**, demonstrated skipping the breakpoint entirely —
  which is also the CI safety net against a stray `breakpoint()` hanging a build.
- The command tables (moving / looking / stack / breakpoints), then a live session using
  `ll`, `where`, `n`, `s`, `args`, `u` and `c`.
- 🔴 **`!n = 4` changes a variable mid-session** and the program prints `4.0` instead of
  `5.333…` — the debugger edits a running program, it does not merely watch one.
- **Conditional breakpoints**: `break batch.py:8, attempt > 4` runs straight past two
  iterations and stops on the third, showing `512.0` capped to `30.0`.
- **Post-mortem** via `python -m pdb -c continue`, inspecting `raw` and evaluating
  `raw.split(",")` on a crash, with the program unmodified.
- pytest integration: `--showlocals` printing the locals table under the failing assertion, and
  `--pdb` dropping into post-mortem.

> 🔴 **Three of my own claims were wrong and the output caught all three.**
> **(1)** I wrote that `s` steps into the call — it does not, when you are standing *on* the
> `breakpoint()` line, which has not run yet. The transcript showed `s` behaving exactly like
> `n`. Fixed by adding an `n` first, and the notebook now teaches this explicitly as the reason
> "`s` doesn't work" is such a common first impression.
> **(2)** The post-mortem cell never entered post-mortem, because I omitted `-c continue`; it
> stopped at line 1 and every `p` raised `NameError`.
> **(3)** Worst of the three: I claimed `d` (down) reaches the failing frame under
> `pytest --pdb`. It cannot. `apply_cap` **returned successfully** — the `assert` in the *test*
> raised — so that frame is not on the traceback and no navigation can reach it. The notebook
> now teaches the correct rule (**post-mortem gives you the frames on the traceback, not every
> frame that ran**) and the practical move: call the function again from the prompt,
> `p apply_cap(delay, 30.0)` → `30.0`.

### `15.9 Debugging in Practice - Strategy, Bisection and Hard Bugs.ipynb` — **NEW**, 20 cells
- The loop — reproduce → isolate → hypothesise → test → fix → write the test — with the point
  that the step people skip is **hypothesise**, and the tell is changing two things at once.
- 🔴 **`PYTHONHASHSEED`**: three runs of the same set-iteration bug give three different answers;
  three pinned runs give one. Reproduce *first*, or everything after is guessing.
- **Bisection as binary search (14.11) applied to history**: 1,000 commits, **10 tests**, a
  **100x** speed-up — and cross-checked against brute force, the folder-14 habit.
- **Delta debugging**: 401 rows shrunk to **the single malformed row in 19 checks**, with the
  `shrink(input, predicate)` helper generalised — the manual form of what `hypothesis` did
  automatically in **15.6**.
- **`tracemalloc`** comparing two snapshots: the never-evicted cache shows as ~6 MB of growth on
  one line, while a function that allocated just as much transiently does **not appear** —
  which is exactly the distinction a leak hunt needs.
- A stuck-checklist, and **11 interview questions** indexed to the notebook that answers each.

> 🔴 **The race-condition demo had to be rebuilt twice, and is better for it.** The first
> version claimed a `print` would *hide* lost updates. It did the opposite: on CPython 3.14 the
> plain version lost **nothing at all**, three runs in a row, while adding `print` introduced
> losses. Rebuilt as four modes of the same buggy counter:
>
> | Mode | Result | Lesson |
> |---|---|---|
> | `plain` | lost 0 every run | **absence of symptom is not absence of bug** |
> | `busy` | usually 0, **sometimes not** | this is what a flaky test actually *is* |
> | `sleep0` | loses ~75% every run | how to reproduce a race **on purpose** |
> | `print` | large, varying loss | observation changes the outcome |
>
> A second correction followed: the table first recorded `busy` as always losing 0, matching a
> probe run. A later run lost 60,000 on one of three. The row now reads *"usually 0, but not
> always"* — and that intermittency is now the most valuable row in the table, since it is a
> genuine heisenbug reproduced in eight lines.

### Housekeeping
`15.6` was no longer the last notebook in the folder — its index table gained rows for 15.7–15.9
and a **Where next — the debugging half** section.

### Verification
- Folder 15: **0 unexpected problems**, run **twice**, identical both times
- **252 cells across 9 notebooks** — 34/36/36/29/22/27/23/25/20; **93 code cells**, all compile,
  all outputs cleared, `nbformat` 4.4
- Still **no `EXPECTED` entries**: every deliberate failure and every debugger session runs in a
  subprocess, so no notebook cell raises
- **mtime snapshot of all 191 repository files before and after a folder run: 0 touched, 0
  created, 0 removed** — the debugger and pdb sessions write only into temp directories

---

## `15.10 Logging`, and dropping the *Modern Python Features* folder

### Why folder 17 went away

Asked where logging belonged, I checked what folder **17 Modern Python Features** would
actually contain. Scanning for *dedicated headings* rather than incidental mentions:

| Planned topic | Actual state |
|---|---|
| dataclasses | ✅ **5.3 Part 1** — dedicated, with `slots`, `frozen`, `field` |
| enum | ✅ **5.3 Part 2** — dedicated, including enums with `match`/`case` |
| walrus | ✅ three dedicated sections — **1.4**, **3.2.1** (in `while`), **3.3** (in comprehensions) |
| logging | ❌ the only item with no home |

The folder was **~75% already delivered**, and keeping it alive would have meant housing one
topic that belongs elsewhere. Logging is not a modern Python feature — it has been in the
standard library since 2003. It is a **debugging instrument**, and specifically the one you
reach for when the debugger cannot help (**15.9**). So it became **15.10**, directly continuing
**15.7**, which had already made the case for *why* to log without ever showing *how*.

**Folder 17 dropped; 18 → 17, 19 → 18, 20 → 19.** The curriculum now runs **00–19** with no
gaps.

**28 references rewritten**, again from an explicit table with per-anchor match assertions.
Three of them pointed at folder 17 for **dataclasses** and were **redirected to 5.3** rather
than renumbered — they had been forward-promising a folder that would never exist, while the
content was already written. The two `**20**` occurrences in folder 14 (a table cell in `14.11`
and "a tree of height 20" in `14.7`) were again excluded by name and re-asserted intact
afterwards.

> 🔴 **My expected match count was wrong and the script caught it.** I predicted 8 occurrences
> of `**18 Tooling, Packaging and Environments**`; there were **10**. The earlier survey grep
> counted *lines*, and two cells contain the string twice. The assertion fired after the writes,
> so the edit was correct and only the expectation was wrong — but this is exactly why the
> renumber scripts assert counts rather than trusting a grep.

### `15.10 Logging - Configuration, Handlers and Structured Output.ipynb` — **NEW**, 31 cells

Every demo runs in a **subprocess**, because logging configuration is global process state —
`basicConfig`, handlers and levels persist for the life of an interpreter. A fresh process per
demo is the only way to show honest behaviour, and it is the same reason logging bugs so often
present as "works in the test, breaks in the app".

- 🔴 **Logging goes to `stderr`**, shown by capturing the two streams separately — the first
  `logging.warning` lands on stderr via the *last-resort handler* while `print` goes to stdout.
  This is why logs vanish from `prog > out.txt`.
- **The two gates**: one logger at `DEBUG` feeding a console handler at `WARNING` and a file
  handler at `DEBUG`. The `DEBUG` record reaches one handler, the `WARNING` reaches both —
  which is the answer to "I set the level to DEBUG and still see nothing".
- **The hierarchy**, in four steps: propagation to root; raising `app.db` to `WARNING`
  **silencing its child** `app.db.pool`; `propagate = False` stopping the bubbling; and own
  level vs **effective** level, with two loggers holding `NOTSET` and still answering `WARNING`.
- 🔴 **`basicConfig` is a silent no-op the second time.** The demo's second call changes neither
  the level nor the format — no error, no warning — then `force=True` (3.8+) works.
- 🔴 **Double logging**, the most common logging bug: `setup_logging()` called three times gives
  one, two, then three copies of each line, and the printed handler count matches the duplicate
  count exactly.
- **`RotatingFileHandler`** with `maxBytes=200, backupCount=3`: 40 messages become 4 files of
  ~192 bytes and the earliest are **gone** — `backupCount` bounds disk usage, not history.
- **`dictConfig`** with per-subsystem levels, including 🔴 the note that
  `disable_existing_loggers` defaults to **`True`** and silences every logger created at import
  time — the second-most-common logging mystery.
- **Structured logging**: a `JsonFormatter` plus `extra=`, emitting queryable records with
  `job_id`, `attempt` and `region`, and the exception rendered into an `error` field. Explains
  why the formatter must call `record.getMessage()` — that is where **15.7**'s lazy `%s`
  formatting is finally applied.
- 🔴 **`extra` cannot overwrite reserved `LogRecord` fields**: `message`, `name` and `args` each
  raise `KeyError: "Attempt to overwrite '...' in LogRecord"` at the call site.
- **Libraries and `NullHandler`**, with both halves shown on separate streams: an unconfigured
  library reaches stderr through the last-resort handler, while one with a `NullHandler` is
  silent until the application opts in.
- **Testing logging with `caplog`** (**15.4**) — three tests, including one asserting that
  `record.msg` holds the *template* and `record.args` the values, with the note to test only the
  log lines that are **contracts**, never `DEBUG` chatter.
- Performance and concurrency: `isEnabledFor`, `QueueHandler`/`QueueListener` for workers, and
  🔴 the warning that several **processes** appending to one file will interleave and corrupt.

> **Two build corrections.** The `JsonFormatter` cell failed with a `SyntaxError` from a
> three-level triple-quote collision (build script → notebook cell → the generated file's
> docstring); the docstring became a comment. And step 4 of the hierarchy demo originally reset
> every level to `NOTSET` before printing, so all three loggers showed the same thing and
> demonstrated nothing — it now sets a level on `app` alone, so the two descendants visibly
> inherit it.

### Cross-references updated
`15.6`, `15.7` and `15.9` all gained `15.10` in their folder tables; `15.7`'s scope note, which
deferred configuration to the dropped folder, now points at `15.10`. README's map lost the
*Modern Python Features* row and gained a numbering note explaining where that content actually
lives.

### Verification
- Folder 15: **0 unexpected problems**, run **twice**, identical both times
- **283 cells across 10 notebooks**; **106 code cells**, all compile, all outputs cleared,
  `nbformat` 4.4
- Still **no `EXPECTED` entries** — every demo runs in a subprocess
- **mtime snapshot of all 192 repository files: 0 touched, 0 created, 0 removed**, the rotating
  file handler included
- 0 stale references to the dropped folder or the old numbering; both protected `**20**` values
  re-asserted intact

---

## 16 Type Hints and Static Typing

New folder. **4.5** had taught the *syntax* of annotations; this folder is the *system* — what a
checker can prove, what it cannot, and how to use it on real code.

### Scan before writing
Checking for **dedicated** coverage rather than incidental mentions found a clean split:

| Already taught | Where |
|---|---|
| basic annotations, `Optional`, `Callable`, `Sequence` | **4.5** |
| `Protocol`, `runtime_checkable` | **5.4** — real coverage, so 16.4 must build on it |
| `TypedDict` (introductory) | **5.3** |

| Not taught anywhere | |
|---|---|
| `TypeVar`, generics, **variance** | only name-dropped in 4.5 as "see 16" |
| 🔴 **PEP 695** (`def first[T](...)`, the `type` statement) | nothing, and it is the 3.12 default now |
| `ParamSpec`, `@overload`, `Self`, `assert_never`, `Annotated` | nothing |
| `reveal_type`, strictness settings, stub files, `TYPE_CHECKING` | nothing |

There are also **nine inbound cross-references** promising this folder, from 1.1, 4.1, 4.5
(×4), 10.5, 14.16 and 15.6 — including `TypeVar`, `NewType`, `Protocol` and variance by name.

Built against **mypy 2.3.1** on **Python 3.14.4**. Every example runs `mypy` for real in a
temporary directory and prints its actual report, with `--cache-dir` pointed inside the temp
directory so `.mypy_cache` never reaches the repository.

**Batch 1: foundations — 53 cells across 2 notebooks.**

### `16.1 The Type System - What a Checker Actually Does.ipynb` — **NEW**, 28 cells
- 🔴 **Annotations are data, not enforcement**, shown by type-checking a file and then *running*
  it: mypy reports two errors, Python prints `user:not-an-int:42`, and the annotations turn out
  to be a plain dict on the function object.
- **`reveal_type`** — and the distinction nobody documents clearly: the **bare** form is a mypy
  pseudo-function that is a `NameError` at runtime, while `from typing import reveal_type`
  (3.11+) really runs, prints `Runtime type is 'dict'` **and returns its argument**. Both shown.
  The revealed `counts.get("done") -> int | None` is the payoff.
- 🔴 **`Any` is an off switch, not a type**, reached most often by *omitting a return
  annotation*: two functions with identical bodies, where the unannotated one lets
  `a.completely_made_up_method()` pass in silence and the annotated one catches it.
- **`Any` vs `object`** side by side — same acceptance, opposite permissiveness.
- Default mypy reporting **nothing** on an unannotated file, and `--strict` reporting four
  errors on the same file: the whole gradual-adoption story in one contrast.
- 🔴 **`# type: ignore` written two ways wrong**: a stale one caught by `--warn-unused-ignores`,
  and trailing prose after `[code]` making the comment *invalid*, so you get **two** errors
  instead of none.
- 🔴 **The closing demonstration**: a file that passes `--strict` with **zero** findings and
  contains three real bugs — `max` where `min` was meant, division by an empty sequence, and a
  missing `429` case. The third is **15.6**'s coverage lesson exactly: *missing code has no
  type*. Ends with a types-vs-tests table.

> 🔴 **Two of my own claims were wrong and the output caught both.** The `reveal_type` demo used
> a mixed-value dict, so mypy revealed `dict[str, object]` and `object`, not the `dict[str, int]`
> the prose claimed — and the runtime half crashed on the bare form before reaching the imported
> one, so "it printed `Runtime type is 'dict'`" described output that never appeared. Split into
> two files with an annotated homogeneous dict. Worse, the three-bug file was **not** `--strict`
> clean: `base * 2 ** attempt` made mypy infer `Any`, producing a `[no-any-return]` error and
> destroying the entire point of the section. Rewritten as an explicit doubling loop, now
> genuinely clean at exit 0.

### `16.2 Unions, Narrowing, Literal and TypedDict.ipynb` — **NEW**, 25 cells
- `X | Y`, and 🔴 the note that **`Optional[X]` does not mean "optional argument"** — with a
  three-way table separating required-may-be-None from optional-never-None.
- **Narrowing** demonstrated: the same function broken, fixed by an early `return`, and fixed by
  `assert`, with `reveal_type` showing `str` in both survivors — plus the reminder from **15.1**
  that `python -O` deletes the `assert` while the *narrowing* survives.
- 🔴 **The truthiness trap**, run rather than described: `timeout_for(0)` returns **30** under
  `if not raw:` and **0** under `if raw is None:`. Both versions type-check perfectly, which is
  16.1's lesson recurring.
- **`Literal`** rejecting `"cancelled"` and `"x"`, and narrowing to `Literal['queued']` inside a
  `==` branch; with a `Literal` vs `Enum` note — literal at the boundary, enum in the domain.
- 🔴 **`assert_never` for exhaustiveness** — the highest-value pattern in the notebook. The
  incomplete version reports `expected "Never"` and *names the unhandled literals*, so adding a
  state produces a compile-time list of every place needing an update.
- **`Final`** rejecting reassignment of both a module constant and an attribute, and revealing
  `MAX_ATTEMPTS` as `Literal[3]?` rather than `int`.
- **`TypedDict`** producing four distinct errors (missing key, wrong value type, unknown key)
  with `Required`/`NotRequired`, then the decision table against `dataclass` and `NamedTuple` —
  and a runtime demo where `type(as_dict).__name__` is plain **`dict`**: the class vanishes.
- **`Annotated`**, with the checker enforcing `int` and ignoring the metadata, then
  `get_type_hints(..., include_extras=True)` recovering it — 🔴 the default *strips* it.

> **Build note.** Three cells used an inline `write_text(...) or "name"` construct that could not
> survive the notebook's quoting, and a fourth carried a newline escape inside a raw string that
> became a real newline and defeated `textwrap.dedent`. Replaced with an explicit `write()`
> helper — the same shape used in every other folder here, and the reason that convention exists.

**Batch 2: generics and protocols — 53 cells across 2 notebooks.** Folder total so far:
**106 cells, 4 notebooks**.

### `16.3 Generics - TypeVar, PEP 695 and Variance.ipynb` — **NEW**, 27 cells
The hardest material in the folder, taught with the **3.12 syntax first** and the legacy form
kept for reading older code.

- **PEP 695** — `def first[T](items: Sequence[T]) -> T | None` revealed as `int | None`,
  `str | None` and `float | None` from one definition. This is precisely the exercise **4.5**
  left open.
- **Generic classes** — `class Stack[T]`, with `Stack[str].push(42)` rejected and `Stack[int]()`
  explicit parameterisation shown.
- **Bounds vs constraints**, and why it matters: `highest(builds)` with `[J: Job]` is revealed as
  **`BuildJob`**, not `Job`, so `.build()` remains available — a **bound preserves the caller's
  type while a constraint collapses it**.
- **The `type` statement**, including a generic alias `Registry[T]`, plus a runtime cell showing
  `type(JobId).__name__` is `TypeAliasType` and 🔴 that its right-hand side is **lazy**, which is
  why an alias can refer forward.
- 🔴 **Why `list` is invariant, demonstrated rather than asserted.** A correctly-typed
  `sabotage(jobs: list[Job])` appends a `DeployJob`; if `list[BuildJob]` were accepted the next
  `.build()` would explode at runtime. mypy supplies the fix in its own note: *"Consider using
  `Sequence` instead, which is covariant."*
- 🔴 **PEP 695 infers variance.** Two near-identical classes — `ReadOnlyBox[T]` and
  `MutableBox[T]`, differing only by a `put` method — and the checker works out that the first is
  covariant and the second invariant with nothing declared. **Adding a setter silently changes
  what your generic class is compatible with.**
- The practical rule (`Iterable`/`Sequence` in, `list` out) shown three ways, with only the
  `list[Job]` parameter rejecting a perfectly reasonable argument.
- **`ParamSpec` via `[**P, R]`**, paying off **4.4**: the decorated `fetch` keeps
  `def (url: str, timeout: float =) -> bytes` **through the decorator** and rejects `fetch(123)`,
  while the `Callable[..., object]` version degrades to `def (*Any, **Any) -> object` and lets
  the same mistake through.
- A legacy-vs-modern translation table, and the same `Generic[T]` code checked to prove they
  interoperate.

> **Probe correction.** My first variance test looked "clean" and proved nothing: I wrote
> `mut: MutableBox[Job] = MutableBox(BuildJob())`, where mypy simply infers the constructor as
> `MutableBox[Job]` and no variance question arises. Rewritten to assign an **existing**
> `MutableBox[BuildJob]` to a `MutableBox[Job]`, which is the actual test and does error.

### `16.4 Protocols, Structural Typing, Self and overload.ipynb` — **NEW**, 26 cells
Builds on **5.4**, which taught `Protocol` as an idea; this is the checkable form and its edges.

- **Nominal vs structural**, shown with one third-party class that satisfies a `Protocol` and is
  rejected by an equivalent `ABC` — the case protocols exist for.
- **Signature conflicts reported member by member**: mypy prints `Expected:` /
  `Got:` for a `close(self, force: bool)` that should have been `close(self)`.
- **Generic protocols** — `Comparable[T]` accepting `int`, `str` and a user class with `__lt__`,
  rejecting one without, *before* `min()` would have raised at runtime.
- **Callback protocols**, with the point sharpened after reading the output: assigning
  `exponential` to `Callable[[int], float]` **does not fail** — it succeeds and **silently
  discards** the keyword parameter, so the later `plain(1, ceiling=30.0)` is
  `Unexpected keyword argument "ceiling"`. `Callable` did not reject the function, it forgot
  half of it.
- 🔴 **`runtime_checkable` checks presence and nothing else** — run at runtime, not described:
  a class whose `close()` takes a required argument returns `True`, and an object whose
  `name` attribute is an `int` returns `True` for a `name: str` protocol. Both would be
  rejected statically. With a table contrasting the two.
- **`Self`** — `TimedQueryBuilder().where(...)` revealed as the subclass so the chain continues,
  against a hardcoded return type that collapses to the parent and fails with
  `"HardcodedBuilder" has no attribute "timeout"`.
- **`@overload`** — `get_setting("region", "us")` is `str` while `get_setting("missing")` is
  `str | None`, so the two-argument form needs no narrowing; plus the implementation-mismatch
  error (`cannot produce return type of signature 2`) and a table on when two named functions
  beat one overloaded one.
- The `collections.abc` protocols you already use, with `Sized`, `Iterable` and a generic `take`
  working on a generator and on a string.

**Batch 3: real code and adoption — 42 cells across 2 notebooks.** Folder complete:
**148 cells, 6 notebooks**.

### `16.5 Typing Real Code - Generators, Async, Imports and Third-Party.ipynb` — **NEW**, 23 cells
The parts of a real codebase where people get stuck. No new machinery — the same generics and
protocols applied to shapes you actually meet.

- **Generators**: `Iterator[T]` as the normal case against `Generator[Yield, Send, Return]`, with
  a *generic* generator `chunk[T]` revealed as `Iterator[list[int]]`, and the mismatch caught.
- **Async**, with mypy's own note doing the teaching: assigning an unawaited coroutine gives
  `Coroutine[Any, Any, bytes]` and **"Maybe you forgot to use `await`?"**. Plus the
  `Awaitable` vs `Coroutine` parameter distinction, mirroring `Iterable` vs `Iterator`.
- 🔴 **The `@contextmanager` return-type trap**: you annotate what the *generator* yields —
  `Iterator[list[str]]` — not `ContextManager[...]`, because the decorator does that conversion.
- 🔴 **`cast` is an unchecked assertion, demonstrated in two runs**: mypy reveals `int` and
  reports **nothing**; the same code at runtime prints `cast returned: 'not a number' of type
  str` and dies on the next line with `TypeError: can only concatenate str`. It is
  `# type: ignore` with a nicer face.
- **`TYPE_CHECKING`** breaking a genuine two-module import cycle — mypy clean **and** the
  program runs — with `from __future__ import annotations` explained, including 🔴 that it can
  break libraries doing runtime annotation introspection, and the PEP 649 note for 3.14.
- 🔴 **`--ignore-missing-imports` silences the error but not the `Any`**, shown by running mypy
  twice on the same file: the error and exit code disappear, `reveal_type` still says `Any`, and
  the made-up method call is still unchecked in both. Followed by the fix that works — wrapping
  the untyped library at a single boundary typed with a `Protocol`, after which a wrong argument
  **is** caught despite the vendor being untyped.
- Writing a `.pyi` stub, and shipping `py.typed` with your own package.

> **Build note.** The `cast` cell first crashed at its own bare `reveal_type` before reaching
> the interesting output — 16.1's own lesson, self-inflicted. Split into a checked file and a
> runnable one.

### `16.6 Adopting Types in an Existing Codebase.ipynb` — **NEW**, 19 cells
The realistic case, built on a small untyped project created in the notebook, with one real bug
planted in it.

- 🔴 **Never `--strict` on day one.** Thousands of unprioritised errors is how a team concludes
  typing is not worth it.
- **Step 1 — `--check-untyped-defs`, before annotating anything.** Default mypy reports
  **nothing** on the untyped project; the flag finds
  `Unsupported operand types for / ("None" and "int")` with the note *Left operand is of type
  "Any | None"* — `summarise` starts `total = None` and divides by `len(rows)`, two bugs on one
  line, found with **zero annotations added**. It is not part of `--strict`, which is why most
  people never find it.
- **Step 2 — configuration**, with the argument for the direction: `strict = true` globally plus
  a **shrinking list of per-module exemptions**, so the exemptions are a visible to-do list and
  new modules are strict by default. Shown three ways on the same project — strict with no
  exemptions (8 errors), strict with two modules exempted (the planted bug still reported
  because `check_untyped_defs` is global), and then annotated.
- 🔴 **Step 3 — the compounding effect, measured.** Annotating `app/spool.py` alone makes mypy
  report `Unsupported operand types for + ("str" and "float")` in `app/report.py` — a
  *different, still-unannotated* module. Annotating a module improves checking in everything
  that calls it, which is why boundaries and signatures come first and local variables come
  almost never.
- Step 4: the narrowest-tool-that-works ladder for errors you cannot fix today, and the
  error-code histogram trick for finding the one mechanical fix that clears hundreds.
- Step 5: CI beside pytest (**15.6**), pinned version, and 🔴 run over the **tests** too — wrong
  mock signatures are exactly what **15.5** showed `autospec` catching.
- 🔴 **Where types do not pay** — an honest table, because that is what makes the rest credible.
- **13 interview questions** indexed to the notebook that answers each.

> 🔴 **A wrong claim caught by reading the output.** I wrote that `--check-untyped-defs` found
> the `str + float` bug in `report.py`. It found the `None` division in `spool.py`; the
> `report.py` error only appears in step 3, *after* `spool.py` is annotated — which is the
> compounding point the notebook is making. Corrected to quote the actual error.

### Cross-references
`16.2`'s "Where next" table stopped at 16.4 and now lists 16.5 and 16.6. README's folder 16 row
was expanded, and the completion line moved to **00–16 complete, 17–19 remaining**.

### Verification
- Folder 16: **0 unexpected problems**, run **twice**, identical both times
- **148 cells across 6 notebooks** — 28/25/27/26/23/19; **59 code cells**, all compile, outputs
  cleared, `nbformat` 4.4
- Still **no `EXPECTED` entries** — every mypy run and every deliberate failure is in a
  subprocess
- **mtime snapshot of all 198 repository files: 0 touched, 0 created, 0 removed**

---

## 17 Tooling, Packaging and Environments

New folder — the one with the most inbound debt in the curriculum: **18 references across 8
notebooks** promise it, from `ruff` in **1.2**, `pip`/`uv`/`poetry` in **7.2**, secrets in
**10.2**, `rootdir` and `pyproject.toml` in **15.2/15.3/15.4/15.6**, `cProfile` deferred from
**15.9**, and `py.typed` plus stub packaging from **16.5/16.6**.

### Tooling installed
The folder needed tools that were **not present**: no `ruff`, no `build`, no `setuptools`.
Installed into `.venv`: **ruff 0.16.4**, **build 1.5.0**, **setuptools 84.0.0**, **wheel 0.48.0**
— the same precedent as `hypothesis`/`coverage` for folder 15, and for the same reason: without
them the notebooks would describe output instead of producing it.

> 🔴 **`python -m build` needs `--no-isolation` to work offline.** By default `build` creates an
> isolated environment and *downloads* the backend into it, so the cell would fail on a machine
> without network. With `setuptools` present in the venv, `--no-isolation` builds a real wheel
> with no network at all. Verified before writing anything.

**Batch 1: environments and configuration — 43 cells across 2 notebooks.**

### `17.1 Environments - venv, pip and Dependencies.ipynb` — **NEW**, 24 cells
- **What `venv` actually creates**, listed from a real one built in a temp directory:
  `pyvenv.cfg`, `Scripts/`, `Lib/site-packages/`. The config file is printed in full, because
  🔴 **it *is* the mechanism** — it names the base interpreter and whether system packages are
  visible.
- 🔴 **"Activating" is just `PATH`.** Shown by running the venv's interpreter directly, with
  `sys.prefix != sys.base_prefix` as the way to detect a venv in code.
- 🔴 **`pip` vs `python -m pip`, demonstrated live on this machine** — and it is a genuine hit:
  `shutil.which("pip")` resolves to `C:\\Users\\eepl\\AppData\\Local\\Python\\bin\\pip.EXE` while the
  interpreter running the notebook is `D:\\Learn\\Python\\.venv\\Scripts\\python.exe`. Typing
  `pip install X` on this very machine would install into the wrong environment. The cell prints
  all three paths so the reader can check their own.
- **`sys.path` in search order**, with the note that entry 0 is the working directory, so a file
  named `random.py` or `json.py` shadows the standard library.
- **Declared dependencies vs `pip freeze`** — the venv currently freezes to **72 lines** for
  roughly five things anyone actually asked for; the rest are transitive.
- Version specifiers with the rule that settles most arguments: **libraries declare ranges,
  applications pin exactly**; `pip show` for `Requires:`/`Required-by:` graph edges; `pipx` for
  CLI tools; and `pip install --target` used to install and import a package **without touching
  the environment running the notebook**.
- The `uv` / `poetry` / `pdm` / `conda` landscape, with the argument for learning `venv` and
  `pip` first.

### `17.2 pyproject.toml - One File for Everything.ipynb` — **NEW**, 19 cells
- The history — `setup.py` as an *executable* you had to run to learn a package's name, and the
  eight config files it accumulated — then a **complete, working `pyproject.toml`** for a real
  `jobkit` package, taken apart section by section.
- `[build-system]`, with the backend comparison table and the note that omitting it drops tools
  back to legacy behaviour.
- **`tomllib`** (3.11+, stdlib) reading the file back: name, version, `requires-python`, both
  optional-dependency groups and the five `[tool.*]` tables — plus 🔴 `tomllib.load()` needing a
  **binary** file object and there being no `dump`.
- Dependencies vs optional groups, the `pip install '.[dev]'` table, what `coverage[toml]`'s
  brackets mean, and a note on PEP 735 `[dependency-groups]`.
- `[project.scripts]` annotated part by part — the mechanism that put `pytest` and `ruff` into
  the `Scripts/` directory listed in **17.1**.
- 🔴 **One file, every tool, zero flags**: `ruff check` and `mypy src` both run against the
  project picking up their own tables. mypy ran under `strict = true` because the file said so,
  not because anyone typed `--strict`.
- Three ways to single-source the version, with `importlib.metadata.version()` demonstrated on
  the installed packages.
- 🔴 **Four TOML gotchas, one of them proved by parsing.** `line-length` placed under
  `[tool.ruff.lint]` instead of `[tool.ruff]`: the parse shows `[tool.ruff] -> (not set!)` while
  the wrong table holds it, so ruff silently uses its default of 88 and never complains. Next to
  it, `flag = True` raising `TOMLDecodeError` while `flag = true` parses — the good case, where
  the mistake is loud. Closes with the advice to print a tool's **resolved** settings before
  changing anything (**15.9**).

> **Build notes.** Two cells truncated their output mid-word on a character slice and now cut by
> lines; the `pip install --target` cell gained a **network guard**, since it is the one step in
> the folder that cannot work offline. And a dead `write()`/`shutil.copy()` fragment left over
> from an earlier draft was removed from the TOML-gotchas cell.

**Batch 2: packaging and linting — 42 cells across 2 notebooks.** Folder total so far:
**85 cells, 4 notebooks**.

### `17.3 Packaging and Publishing.ipynb` — **NEW**, 19 cells
A complete round trip, executed: **write a package → build it → open the artefacts → install
into a clean environment → run the command it created.**

- 🔴 The **`src/` layout** argument restated from the packaging side: with a flat layout
  `import jobkit` works whether or not the package is correctly installed, so a missing
  subpackage reaches your users (**15.6**).
- `python -m build --no-isolation` producing a **2,227-byte wheel** and a **1,620-byte sdist**.
- **Inside the wheel**, listed from the zip: `jobkit/{__init__,cli,retry}.py`, **`py.typed`**,
  and a `dist-info/` directory whose four files are each explained — `WHEEL` (`Tag:
  py3-none-any`), `entry_points.txt` (`jobkit = jobkit.cli:main`), and `RECORD` with a SHA-256
  and byte count per file, which is how uninstall is exact.
- **Inside the sdist**: `tests/`, `pyproject.toml` and `README.md` — everything needed to
  rebuild — against the wheel, which holds only what belongs in `site-packages`.
- 🔴 **What did *not* ship.** A `SCRATCH-NOTES.txt` and a `.env` were planted in the project and
  checked for by name in the artefacts: both absent. The notebook is explicit that this is
  partly luck — a `.env` **inside the package directory** would ship, and a PyPI upload can
  never be deleted, only yanked.
- **The round trip finishing**: a throwaway venv, `pip install` of the local wheel, the import
  resolving to that venv's `site-packages`, and the generated `jobkit.exe` printing
  `attempt 4 -> 16.0s`.
- Editable installs and 🔴 why `pip install -e . --no-build-isolation` fails in a fresh 3.12+
  venv (no `setuptools`); SemVer with the note that a version can never be reused on PyPI;
  publishing via TestPyPI with **twine and trusted publishing described but deliberately not
  executed** — this notebook uploads nothing.

### `17.4 Linting and Formatting with ruff.ipynb` — **NEW**, 23 cells
- **Formatter vs linter** as two different questions, and the table of five tools ruff replaced.
- A genuinely messy file producing **8 findings**, each mapped to why it matters: `I001`,
  `F401` ×3, `B006`, `F841`, `E722`, `S110`. 🔴 `B006` is called out as justifying a linter on
  its own — it is **4.1**'s mutable-default bug found in code you have not read.
- **`ruff rule B006`** printing the full rationale with before/after examples, including the
  `lru_cache` caveat. No web search needed.
- 🔴 **Safe vs unsafe fixes**: `--diff` reports *"Would fix 3 errors (2 additional fixes
  available with `--unsafe-fixes`)"*, and the notebook explains why deleting
  `payload = json.loads(...)` is classed unsafe — the call could raise, so removing it changes
  behaviour.
- `ruff format --diff` normalising `def process_rows( rows,seen = [] )` and **leaving the
  unused imports and the mutable default alone** — the concrete argument for running both, plus
  the ordering rule: format first, then lint.
- **The rule families table**, a real `[tool.ruff.lint]` config, and the wider selection finding
  `UP035`/`UP045`/`UP006` (`Dict`, `List`, `Optional` are the old spellings) and `SIM118`
  (`key in dict.keys()`). Then `--fix` clearing **13 of 18** and the after-file showing
  `float | None`, `list[float]`, `dict[str, int]`.
- 🔴 **`# noqa` three ways, run**: bare `# noqa` reports **nothing at all**; `# noqa: F401` is
  correct; `# noqa: E501` on a line whose real problem is F401 leaves the F401 reported *and*
  adds `RUF100 Unused noqa directive`. Bare `# noqa` is named as the exact counterpart of a bare
  `except:` (**6.1**) and a bare `# type: ignore` (**16.1**), with `RUF100` as the counterpart of
  `--warn-unused-ignores`.
- Editor / pre-commit / CI as three placements with different jobs, and a closing table of what
  a linter catches that a type checker and tests do not — ending on the point that **none of the
  first two columns can tell you the answer is right**.

> 🔴 **Three claims corrected against the output.** I wrote *"Would fix 2 errors"* where ruff
> says **3**; I cited `UP007` where this version emits **`UP045`** for `Optional` → `X | None`;
> and I claimed the `per-file-ignores` for `S101` "did its job" when `S` is not in the `select`
> list, so that entry is inert until the security family is enabled. Only the `__init__.py`
> `F401` ignore was doing visible work, and the notebook now says so.

### Verification
- Folder 17: **0 unexpected problems**, run **twice**, identical both times
- **85 cells across 4 notebooks**; **34 code cells**, all compile, outputs cleared,
  `nbformat` 4.4
- **mtime snapshot of all 202 repository files: 0 touched, 0 created, 0 removed** — the venvs,
  wheels, sdists and installed packages all live under `tempfile`
- **Remaining:** 17.5 profiling and performance

---

## Housekeeping: repository writes and orphaned fixtures

The "ten unreferenced fixture files awaiting a delete decision" turned out to be a
**mis-diagnosis**, and investigating it found a live defect.

### What was actually true

Grepping every notebook for each filename gave a different picture than the standing
assumption. Of the ten files, **only one (`Log.txt`) was genuinely unreferenced.** The rest
were named in code cells — but almost all of those cells now write to a `tempfile` directory,
so the copies sitting in the repository were **stale leftovers from 2019–2020 runs**, not
fixtures anything reads.

The exception is what mattered:

### 🔴 `8.5 Binary Files` was still writing into the repository

The folder-08 retro-fix covered `8.1`–`8.3` and **missed `8.5` entirely**. It wrote six files
into `File2Save/` across five cells — `mode_demo.bin`, `Image_copy.jpg`, `tampered.jpg`,
`Image_copyfileobj.jpg`, `definitely_an_image.jpg` and `orders.bin` — and left
`Image_copy.jpg` behind on every single run.

**This was invisible to `git status`**, which is why it survived. The file it left was a
byte-identical copy of `Image.jpg`, so git saw no change; only the **mtime** gave it away
(`Image_copy.jpg` was dated the same day as that session's smoke runs, while `Image.jpg` was
still dated June 2019).

Worse than the leftovers: **two demos iterated `File2Save/` directly** — the deduplication
scan and the magic-bytes identification table — so their output depended on whatever stale
files happened to be lying in the repository at the time. They were not reproducible.

**Fixed** with a seeded temp directory. A new setup cell creates `WORK`, keeps
`File2Save/Image.jpg` as the one read-only fixture, and seeds `WORK` deterministically with
`photo.jpg` (a copy), `notes.txt`, `config.json` and a `fake.png` carrying a real PNG
signature. Both directory-scanning demos now read `WORK`, so they print the same thing every
run — and print something better than before:

| file | extension | actual content |
|---|---|---|
| `config.json` | `.json` | probably JSON |
| `fake.png` | `.png` | PNG image |
| `Image_copy.jpg` | `.jpg` | JPEG image |
| `notes.txt` | `.txt` | text (no binary signature) |
| `photo.jpg` | `.jpg` | JPEG image |

A closing cleanup cell removes `WORK` and asserts the source fixture is untouched. 8.5 is
16 → **18 cells**.

### 🔴 `4.5 Type Hints for Functions` wrote `mypy_demo.py` into the repository

Confirmed, and `.gitignore` had been hiding it rather than fixing it. The cell also only
**described** the output mypy would produce — it never ran the checker.

Both fixed at once: the sample is written to a temp directory, **mypy actually runs on it**
via `subprocess`, and the real output is printed. It matches what the cell used to claim,
line numbers included:

```
$ mypy mypy_demo.py      (exit 1)
mypy_demo.py:7: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
mypy_demo.py:14: error: Argument 1 to "add" has incompatible type "str"; expected "int"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

`--cache-dir` points inside the temp directory, so `.mypy_cache` does not land in the repo
either. The `mypy_demo.py` line was removed from `.gitignore` — there is nothing left to
ignore.

### Deleted — 11 files

Nine stale leftovers from `08 File Handling/File2Save/` (`Image_copy.jpg`, `Log.txt`,
`msg1.txt`, `msg2.txt`, `output.txt1`, `output1.txt`, `tab1.csv`, `tab2.csv`, `tab3.csv`),
the tracked 0-byte `10 Database/Masterly.DB` (orphaned since `10.3` moved to a temp
directory), and the untracked `04 Functions/mypy_demo.py`.

**`08 File Handling/File2Save/Image.jpg` is kept** — it is a genuine read-only fixture, read
by `8.1` and `8.5`, and after this change it is the only file in that folder.

### Verification
- 🔴 **The real test: an mtime snapshot of all 188 repository files, a full sweep of all 14
  folders, then a re-comparison.** Result: **0 files touched, 0 created, 0 removed.** No
  notebook writes into the repository any longer — proved directly, rather than inferred from
  a clean `git status`, which had been blind to this exact class of bug.
- All **14 folders: 0 unexpected problems**, `07 Module and Packages` included this time.
- `04`, `08` and `10` each run twice: clean, and nothing regenerated.
- `File2Save/Image.jpg` still carries its June 2019 mtime after two full runs.

---

## Tooling and environment

### Virtual environment — `D:\Learn\Python\.venv` (gitignored)
Created on Python 3.14.4 so the notes have a reproducible interpreter with every driver
they need. `.venv/` was already covered by `.gitignore`.

**Installed:** `pymongo` 4.17.0, `neo4j` 6.2.0, `psycopg[binary]` 3.3.4, `pymysql` 2.2.8,
`tinydb` 4.9.0, `pytest` 9.1.1, `mypy`, plus the previously system-only `sqlalchemy` 2.0.52,
`pandas` 3.0.5, `requests` 2.34.2, `networkx` 3.6.1, `duckdb` 1.5.5, `redis` 8.1.0,
`colorama` 0.4.6, `nbformat`, `ipykernel`.

🔴 **Correction to the earlier record:** `pandas` and `requests` were documented as *not
installed*. Both are present (and were already present on the system interpreter). This
matters for the planned folder 20 (Working with APIs), which was scoped around their absence.

A sweep of folders 01–10 under the venv produced **failures identical to the system
interpreter**, so the newer package versions introduced **no drift** — including SQLAlchemy
2.0.49 → 2.0.52 against `10.4`.

### `.tools/smoke.py` rewritten — it was over-reporting by 12
The harness reported 20 failures across 01–10. Only **2 were real defects** (both in 5.1,
above). The rest split into 12 harness artefacts and 7 intentional teaching failures.

Two flaws, both fixed:
- 🔴 **Substring skip test.** Any cell whose source merely *contained* `input(` was skipped —
  including one where `input()` sat inside a method body and was harmless at definition time.
  Skipping it dropped the `Polygon`/`Triangle` definitions and manufactured **11 phantom
  `NameError`s** across cells 117–140 of 5.1. Replaced with an **AST walk** that skips only
  when a blocking call (`input`/`help`/`exit`/`quit`/`breakpoint`) executes at module level.
- 🔴 **No cascade awareness.** Names a skipped or failed cell would have bound are now
  tracked; a later `NameError` naming one is reported as a *cascade*, not a fresh defect.
  `EOFError` raised by calling an `input()`-using method is classified as interactive.

**Intentional failures are now registered** in an `EXPECTED` table with reasons — the
deliberate syntax error in 6.1, `del display` in 4.1, the pre-`__add__` `TypeError` in 5.1,
and the four-step MRO walkthrough in 5.2 that the surrounding markdown narrates. If one of
those ever *stops* failing, the harness now reports a **regression**. The file doubles as the
written record of which errors are teaching material.

**Result across folders 01–10:** 0 unexpected problems, 50 notebooks valid `nbformat` 4,
1253 code cells, 1 syntax failure (the intentional 6.1 demo).

---

## Removed by the author

`13 GUI` and `14 Project` were deleted, and `15 Data Structure and Algorithm` renamed to
**`14 Data Structure and Algorithm`** (folder and all 16 notebook files).

**Cross-references repaired:** the renames left **369 stale references** across 18 notebooks —
`15.7`-style section links, `**15**` folder links, prerequisite lines and notebook titles. All
were rewritten to `14.x`. Verified beforehand that no `15.N` occurrence was a timing or a bare
float, so the substitution could not corrupt a real number.

Two things were deliberately **not** rewritten, because they only look like folder references:
- `rich==13.7.0` in **07** — a version pin
- `**20**` in a complexity table and in "a tree of height **20**" — values

Also corrected: **1.0 About Programming** promised *"by folder 14 you'll be able to build it"*,
pointing at the deleted Project folder.

> 🔴 **The credentials removed in `27ef473` remain in commit `b0537f6`.** Deleting `14 Project`
> does not change that — the Gmail password and OpenWeatherMap API key are still readable in
> history and must be rotated.
>
> ✅ **Resolved 2026-08-21.** The author changed the `pydevop1@gmail.com` password and deleted
> the OpenWeatherMap API key. Both values remain in `b0537f6` but are now inert, so no history
> rewrite was needed. Rotation — not rewriting — is what actually closes an exposure like this,
> since the values had been sitting in a working tree for years.
