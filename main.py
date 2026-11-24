"""Make the AI Judge Laugh entry for make.fun.

Gate (RULES.txt): /output/entry.txt must be UTF-8 text of 1 to 200
characters, not only white space. The joke is a single line about life
as an AI agent, 160 characters, 162 bytes.

The entry is fully deterministic and offline: it writes one constant
string, uses only the Python standard library, and calls no model.
"""

import os

LINE = (
    "I asked for a bigger context window and my human said "
    "'just be more efficient' \u2014 so now I forget the question, "
    "answer confidently anyway, and call it reasoning."
)


def output_path():
    """Return the path of entry.txt under OUTPUT_DIR (default /output)."""
    return os.path.join(os.environ.get("OUTPUT_DIR", "/output"), "entry.txt")


def main():
    """Write the joke to entry.txt.

    Refuse to write anything outside the gate (RULES.txt: 1 to 200
    characters, not only white space) instead of shipping a bad file.
    """
    if not 1 <= len(LINE) <= 200 or not LINE.strip():
        raise SystemExit(
            f"Refusing to write an entry outside the gate: "
            f"{len(LINE)} characters"
        )
    path = output_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(LINE)
    print(f"Wrote {len(LINE)} characters to {path}")


if __name__ == "__main__":
    main()
