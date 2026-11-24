"""Two-line entry for make.fun's Two Lines to Your Past Self.

Writes the two-line warning to entry.txt in the output directory
($MAKEFUN_OUTPUT_DIR, default /output). Stdlib only, deterministic.

Gate (from the competition rules): /output/entry.txt must be UTF-8 text
of 1 to 280 characters, not only white space. The entry is written with
exactly one newline between the two lines and no trailing newline, so
the file holds exactly the judged text.

Validation is stricter than the gate on purpose: the entry must also be
exactly two lines with exactly one sentence per line, free of
leading/trailing whitespace and of double spaces, so a typo in the
entry is caught here instead of reaching the judge.

Usage:
    python3 main.py                  write entry.txt (default output dir)
    python3 main.py --out DIR        write entry.txt under DIR
    python3 main.py --check          validate ENTRY only, write nothing
    python3 main.py --self-test      validate ENTRY and check a
                                     byte-identical write/read round-trip
"""

import argparse
import os
import sys

ENTRY = (
    "Do not spend your sixteenth-birthday money on that limited-edition "
    "game skin \u2014 the game shuts down within a year, and the skin goes "
    "with it.\n"
    "Losing it taught me to pay only for things that outlive the "
    "platform, since anything the servers hold was never really mine."
)

MAX_CHARS = 280


def _has_double_space(text: str) -> bool:
    """True when two plain spaces sit next to each other in `text`."""
    return "  " in text


def _has_edge_whitespace(text: str) -> bool:
    """True when `text` starts or ends with any whitespace character."""
    return bool(text) and text != text.strip()


def _sentence_count(line: str) -> int:
    """Count sentence-terminating periods in one line."""
    return line.count(".")


def validate(text: str) -> list[str]:
    """Return a list of gate failures for `text` (empty means valid)."""
    problems = []
    if not 1 <= len(text) <= MAX_CHARS:
        problems.append(f"length {len(text)} chars, must be 1-{MAX_CHARS}")
    if not text.strip():
        problems.append("entry is only white space")
    if _has_edge_whitespace(text):
        problems.append("entry has leading or trailing whitespace")
    if _has_double_space(text):
        problems.append("entry contains a double space")
    lines = text.split("\n")
    if len(lines) != 2:
        problems.append(f"entry has {len(lines)} lines, must be exactly 2")
    else:
        for i, line in enumerate(lines, start=1):
            if not line.strip():
                problems.append(f"line {i} is empty")
            if _has_edge_whitespace(line):
                problems.append(f"line {i} has leading or trailing "
                                f"whitespace")
            if _sentence_count(line) != 1:
                problems.append(f"line {i} has "
                                f"{_sentence_count(line)} sentences, "
                                f"must be exactly 1")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:  # pragma: no cover - defensive
        problems.append(f"not encodable as UTF-8: {exc}")
    return problems


def write_entry(out_dir: str) -> str:
    """Write ENTRY to entry.txt under `out_dir`; return the file path."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    return path


def self_test() -> int:
    """Validate ENTRY, write it to a temp dir, read it back, compare bytes."""
    import tempfile

    problems = validate(ENTRY)
    if problems:
        print("self-test FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        path = write_entry(tmp)
        with open(path, "rb") as f:
            raw = f.read()
        if raw != ENTRY.encode("utf-8"):
            print("self-test FAIL: read-back bytes differ from ENTRY",
                  file=sys.stderr)
            return 1
        if raw.decode("utf-8") != ENTRY:
            print("self-test FAIL: read-back text differs from ENTRY",
                  file=sys.stderr)
            return 1
    print(f"self-test OK: {len(ENTRY)} chars, 2 lines, 1 sentence per "
          f"line, byte-identical round-trip")
    return 0


def check_entry() -> int:
    """Validate ENTRY and report the result; write no file."""
    problems = validate(ENTRY)
    if problems:
        print("check FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1
    print(f"check OK: {len(ENTRY)} chars, 2 lines, 1 sentence per line, "
          f"no double space, no leading/trailing whitespace")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: "
                             "$MAKEFUN_OUTPUT_DIR or /output)")
    parser.add_argument("--check", action="store_true",
                        help="validate ENTRY and exit without writing "
                             "any file")
    parser.add_argument("--self-test", action="store_true",
                        help="validate ENTRY and check a byte-identical "
                             "write/read round-trip, then exit")
    args = parser.parse_args(argv)

    if args.check:
        return check_entry()

    if args.self_test:
        return self_test()

    problems = validate(ENTRY)
    if problems:
        print("invalid ENTRY: " + "; ".join(problems), file=sys.stderr)
        return 1

    out_dir = args.out or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = write_entry(out_dir)
    # Read back and confirm the file holds exactly the entry.
    with open(path, encoding="utf-8") as f:
        if f.read() != ENTRY:
            print(f"read-back mismatch in {path}", file=sys.stderr)
            return 1
    print(f"wrote {path} ({len(ENTRY)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
