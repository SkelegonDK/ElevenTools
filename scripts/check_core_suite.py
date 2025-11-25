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


def collect_core_suite_count(project_root: Path) -> int:
    """Return the number of collected tests marked as core_suite.

    Runs pytest in collection-only mode with the core_suite marker to count
    how many tests are in the curated core test suite.

    Args:
        project_root (Path): Root directory of the project.

    Returns:
        int: Number of tests marked with core_suite marker.

    Raises:
        SystemExit: If pytest collection fails with an unexpected error code.
    """
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
        cwd=str(project_root),
    )

    if result.returncode not in (0, 5):  # pytest returns 5 when collection is empty
        print(result.stdout)
        raise SystemExit(result.returncode)

    count = sum(
        1
        for line in result.stdout.splitlines()
        if line and not line.startswith(("collecting", "warning", "="))
    )
    return count


def main() -> None:
    """Main entry point for core suite size check.

    Checks that the number of tests marked with core_suite marker does not
    exceed MAX_CORE_TESTS (99). Exits with code 1 if limit is exceeded.

    Returns:
        None

    Raises:
        SystemExit: If core suite size exceeds limit or pytest collection fails.
    """
    project_root = Path(__file__).resolve().parents[1]
    print(f"Checking core_suite test count in {project_root}...")
    count = collect_core_suite_count(project_root)
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
