# Python — From Basics to Professional

A complete, self-paced Python curriculum built as Jupyter notebooks.

Originally written in 2019 against Python 3.7, now being modernised to **Python 3.12+**
with version notes for 3.13 / 3.14.

---

## How to use these notes

Each folder is a topic. Notebooks are numbered in teaching order — work through them
top to bottom. Every notebook follows the same shape:

1. **Header** — prerequisites and what you'll learn
2. **Concept** — plain-English explanation, with an analogy where it helps
3. **Syntax breakdown** — the form, named part by part
4. **Examples** — runnable, simple → advanced
5. **Common Mistakes & Pitfalls**
6. **Best Practices** — PEP 8 and modern idioms
7. **Practice Exercises**

### Running the notebooks

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install jupyterlab
jupyter lab
```

Code cells are shipped **unexecuted** so the notebook shows you what *should* happen
rather than what happened on someone else's machine in 2019. Run them yourself.

> Some notebooks need extras (a database server, a GUI display, network access).
> Those state their requirements in the header cell.

---

## Curriculum map

| # | Folder | Covers |
|---|--------|--------|
| 00 | Books and References | Reference PDFs — Van Rossum's tutorial, Kuhlman, *Fluent Python*, *Architecture Patterns with Python* |
| 01 | Basic | Programming concepts, Python intro, REPL, syntax, I/O, operators |
| 02 | Datatypes | str, numbers, tuple, list, dict, set; mutability, copying, unpacking |
| 03 | Flow Control Statement | if/elif/else, `match`/`case`, loops, comprehensions, generators |
| 04 | Functions | Parameters, scope, closures, decorators, generators |
| 05 | OOPs | Classes, inheritance, MRO, dunder methods, ABCs |
| 06 | Exception Handling | try/except, custom exceptions, chaining, context managers |
| 07 | Module and Packages | Imports, packages, pip, venv, standard library |
| 08 | File Handling | Text, CSV, JSON, binary, `pathlib` |
| 09 | Regular Expression | The `re` module, patterns, groups |
| 10 | Database | SQL, `sqlite3`, MySQL/PostgreSQL, SQLAlchemy ORM, key-value and document stores, graph data |
| 11 | Socket Programming | Networking fundamentals, TCP framing, UDP, concurrent servers, HTTP and `requests` |
| 12 | Concurrency | The GIL, threading, multiprocessing, `concurrent.futures`, `asyncio` |
| 14 | Data Structure and Algorithm | Complexity, Python's real costs, arrays and two pointers, linked lists, trees, graphs, sorting, DP, interview patterns |
| 15 | Testing and Debugging | `assert`, `unittest`, `pytest`, fixtures, mocking, coverage, property-based testing; tracebacks, `pdb`, debugging strategy, logging |
| 16 | Type Hints and Static Typing | `mypy`, narrowing, `Literal`, `TypedDict`, generics and variance, protocols, adoption |
| 17 | Tooling, Packaging and Environments | venv, `pyproject.toml`, `ruff`, profiling |
| 18 | Working with APIs | `requests`, REST/JSON, auth, error handling |
| 19 | Capstone Projects | End-to-end builds tying it together |

Folders 00–16 are complete and verified. Folders 17–19 are still to be written. See
[CHANGELOG.md](CHANGELOG.md) for what has been done so far.

> **Numbering note.** `13 GUI` and the old `14 Project` were removed, and `15 Data Structure
> and Algorithm` became **14**. A planned *Modern Python Features* folder was dropped, because
> it was already delivered elsewhere — dataclasses and enums in **5.3**, the walrus operator in
> **1.4**, **3.2.1** and **3.3** — and its one remaining topic, logging, belongs with debugging
> and is now **15.10**. The curriculum runs **00–19** with no gaps. Earlier CHANGELOG entries
> use the older numbering.

---

## Conventions used in these notes

- **f-strings** are the default for formatting. `.format()` and `%` appear once, labelled *legacy*.
- **`pathlib`** is preferred over `os.path` for filesystem work.
- **Type hints** are introduced gradually and used in later folders.
- ⚠️ marks a genuine trap — something that runs but does the wrong thing.
- **Version note** callouts flag behaviour that differs across 3.12 / 3.13 / 3.14.
