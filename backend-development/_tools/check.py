"""Conformance check for backend-development notebooks.

Run from the repo root:
    python backend-development/_tools/check.py                 # all written notebooks
    python backend-development/_tools/check.py 01              # one module
    python backend-development/_tools/check.py 01.4            # one notebook

Checks the mechanical parts of AUTHORING-GUIDE.md so a reviewer can spend their
attention on the parts only a human can judge (is the incident realistic? is the
example real-dev?). Exit code 1 if any notebook fails.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from curriculum import MODULES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_HEADINGS = [
    "## Concept",
    "### Plain-English Explanation",
    "### Technical Explanation",
    "### Mental Model",
    "## How It Works",
    "## Design Patterns / Tradeoffs",
    "## Production Scenario",
    "### Symptoms",
    "### Diagnosis",
    "### Root Cause",
    "### Fix",
    "### Prevention",
    "## Failure-First Checklist",
    "## Common Pitfalls",
    "## Interview Questions",
    "## Key Takeaways",
    "## Related",
]

# Prose-only word budgets, measured against module 01. The full template has ~17
# required headings; below these ranges a section is a stub rather than teaching.
WORD_RANGE = {"B": (1600, 3000), "I": (2000, 3200), "A": (2400, 3800)}

# Deprecated APIs that must not appear in examples (AUTHORING-GUIDE section 4.3).
BANNED = {
    r"\.dict\(\)": "Pydantic v1 .dict() - use .model_dump()",
    r"class Config:": "Pydantic v1 Config - use model_config = ConfigDict(...)",
    r"@validator\(": "Pydantic v1 @validator - use @field_validator",
    r"@app\.on_event": "deprecated FastAPI event hook - use lifespan=",
    r"declarative_base\(": "SQLAlchemy 1.x - use DeclarativeBase",
    r"session\.query\(": "SQLAlchemy 1.x Query API - use select()",
    r"datetime\.utcnow\(": "naive UTC - use datetime.now(UTC)",
    r"\bfoo\b|\bbar\b|\bbaz\b": "placeholder naming - use the module's running system",
}


def prose_words(text: str) -> int:
    """Word count excluding fenced code blocks and table rows."""
    without_code = re.sub(r"```.*?```", "", text, flags=re.S)
    lines = [ln for ln in without_code.splitlines() if not ln.strip().startswith("|")]
    return len("\n".join(lines).split())


def check(path: Path, difficulty: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []

    missing = [h for h in REQUIRED_HEADINGS if h not in text]
    if missing:
        problems.append(f"missing headings: {', '.join(missing)}")

    if not text.lstrip().startswith("# "):
        problems.append("no H1 title on the first line")
    if "> **Prerequisites:**" not in text:
        problems.append("no Prerequisites line in the header block")
    if "> **What you'll learn:**" not in text:
        problems.append("no 'What you'll learn' in the header block")

    words = prose_words(text)
    low, high = WORD_RANGE[difficulty]
    if not low <= words <= high:
        problems.append(f"prose length {words} outside {low}-{high} for level {difficulty}")

    # Banned APIs are checked inside code only: prose legitimately *names* them
    # in order to warn against them.
    blocks = re.findall(r"```([a-z]*)\n(.*?)```", text, flags=re.S)
    code = "\n".join(body for lang, body in blocks if lang in {"python", "py", ""})
    for pattern, why in BANNED.items():
        if re.search(pattern, code):
            problems.append(f"banned pattern {pattern!r} in code: {why}")

    # Listings need explanation. A shell command immediately followed by its output
    # is one unit, so only flag three or more consecutive blocks with no prose.
    # Parsed structurally: regexes over nested fences are not reliable.
    spans = [m.start() for m in re.finditer(r"^```", text, flags=re.M)]
    stacked = run = 0
    for close, nxt in zip(spans[1::2], spans[2::2]):        # close of block i, open of i+1
        gap = text[close:nxt].split("\n", 1)[-1]            # drop the closing fence line
        run = run + 1 if not gap.strip() else 0
        stacked = max(stacked, run)
    if stacked >= 2:
        problems.append("3+ consecutive code blocks with no prose between them")

    # Realistic file listings run longer than a snippet; 55 lines is the point at
    # which a reader stops reading and starts skimming.
    long_blocks = [b for _, b in blocks if len(b.splitlines()) > 55]
    if long_blocks:
        problems.append(f"{len(long_blocks)} code block(s) over 55 lines")

    return problems


def main() -> int:
    wanted = sys.argv[1] if len(sys.argv) > 1 else ""
    failures = 0
    checked = 0

    for module in MODULES:
        folder = ROOT / f"{module['n']}-{module['slug']}"
        for index, (slug, _title, difficulty) in enumerate(module["items"], start=1):
            nid = f"{module['n']}.{index}"
            if wanted and not nid.startswith(wanted):
                continue
            path = folder / f"{nid}-{slug}.md"
            if not path.exists():
                continue
            checked += 1
            problems = check(path, difficulty)
            if problems:
                failures += 1
                print(f"FAIL {nid} {path.name}")
                for problem in problems:
                    print(f"       - {problem}")
            else:
                print(f"ok   {nid} {path.name}")

    print(f"\n{checked - failures}/{checked} notebooks conform")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
