"""Regenerate CURRICULUM.md and every module README.md from curriculum.py.

Run from the repo root:  python backend-development/_tools/build.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from curriculum import MODULES, STATUS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIFF = {"B": "Beginner", "I": "Intermediate", "A": "Advanced"}
BOX = {"todo": "[ ]", "draft": "[~]", "review": "[r]", "done": "[x]"}


def nid(m: dict, i: int) -> str:
    return f"{m['n']}.{i + 1}"


def main() -> None:
    total = done = 0
    out = [
        "# backend-development - Curriculum & Progress\n",
        "Generated from `_tools/curriculum.py`. Edit that file (incl. `STATUS`) and run "
        "`python backend-development/_tools/build.py` from the repo root.",
        "Legend: `[ ]` todo · `[~]` draft · `[r]` in review · `[x]` done.\n",
        "Authoring rules for every notebook: [AUTHORING-GUIDE.md](AUTHORING-GUIDE.md). "
        "Design rationale: [CURRICULUM-REVIEW.md](CURRICULUM-REVIEW.md).\n",
    ]
    summary = [
        "| # | Module | Notebooks | Done | Prereq (modern-python) | Depends on |",
        "|---|---|---|---|---|---|",
    ]
    body: list[str] = []
    for m in MODULES:
        folder = f"{m['n']}-{m['slug']}"
        n = len(m["items"])
        mdone = sum(STATUS.get(nid(m, i)) == "done" for i in range(n))
        total += n
        done += mdone
        summary.append(
            f"| {m['n']} | [{m['title']}]({folder}/README.md) | {n} | {mdone} | {m['prereq']} | {m['depends']} |"
        )
        body.append(f"\n## {m['n']} {m['title']}\n")
        body.append(f"Folder `{folder}/` · Prereq: {m['prereq']} · Depends on: {m['depends']}\n")
        rlines = [
            f"# {m['n']} {m['title']}\n",
            f"Prerequisites: {m['prereq']} · Depends on backend modules: {m['depends']}\n",
            "Read top to bottom. Every notebook follows [AUTHORING-GUIDE.md](../AUTHORING-GUIDE.md).\n",
            "| # | Notebook | Level | Status |",
            "|---|---|---|---|",
        ]
        for i, (slug, title, d) in enumerate(m["items"]):
            st = STATUS.get(nid(m, i), "todo")
            f = f"{nid(m, i)}-{slug}.md"
            body.append(f"- {BOX[st]} **{nid(m, i)}** [{title}]({folder}/{f}) - {DIFF[d]}")
            rlines.append(f"| {nid(m, i)} | [{title}]({f}) | {DIFF[d]} | {st} |")
        d = ROOT / folder
        d.mkdir(exist_ok=True)
        # A hand-written _quiz.md (retrieval practice; AUTHORING-GUIDE section 11)
        # is linked below the table so readers hit it before the recap.
        if (d / "_quiz.md").exists():
            rlines += ["", "Self-test: [_quiz.md](_quiz.md) - attempt every question "
                           "before opening the answers at the bottom."]
        # A hand-written _recap.md (added when a module is finished) is preserved
        # across regenerations by appending it below the generated table.
        recap = d / "_recap.md"
        if recap.exists():
            rlines += ["", "---", "", recap.read_text(encoding="utf-8").rstrip()]
        (d / "README.md").write_text("\n".join(rlines) + "\n", encoding="utf-8")

    out.append(f"**Progress: {done}/{total} notebooks done.**\n")
    out += summary + body
    (ROOT / "CURRICULUM.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{done}/{total} done; {len(MODULES)} module READMEs written")


if __name__ == "__main__":
    main()
