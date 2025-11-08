#!/usr/bin/env python3
"""
Guardrail script to enforce the curated pytest core suite remains under 100 tests.

Usage:
    uv run python scripts/check_core_suite.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


MAX_CORE_TESTS = 99


def collect_core_suite_count() -> int:
    """Return the number of collected tests marked as core_suite."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-m",
        "core_suite",
        "-q",
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if result.returncode not in (0, 5):  # pytest returns 5 when collection is empty
        print(result.stdout)
        raise SystemExit(result.returncode)

    count = sum(
        1 for line in result.stdout.splitlines() if line and not line.startswith(("collecting", "warning", "="))
    )
    return count


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    print(f"Checking core_suite test count in {project_root}...")
    count = collect_core_suite_count()
    print(f"core_suite tests collected: {count}")
    if count > MAX_CORE_TESTS:
        print(
            f"❌ core_suite exceeds limit ({count} > {MAX_CORE_TESTS}). "
            "Please consolidate tests or remove redundant cases."
        )
        raise SystemExit(1)
    print("✅ core_suite size within limit.")


if __name__ == "__main__":
    main()

