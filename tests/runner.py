"""App dashboard test runner for Doc Assistant project test suites."""

import sys
from pathlib import Path
from typing import Any

import pytest


def run_project_tests(
    test_path: str = "tests", extra_args: list[str] | None = None
) -> dict[str, Any]:
    """Execute pytest suite and return structured runner outcome dictionary."""
    base_dir = Path(__file__).resolve().parent.parent
    target = str(base_dir / test_path)
    args = [target]
    if extra_args:
        args.extend(extra_args)

    exit_code = pytest.main(args)

    return {
        "status": "PASSED" if exit_code == 0 else "FAILED",
        "exit_code": int(exit_code),
        "target": target,
    }


if __name__ == "__main__":
    result = run_project_tests()
    sys.exit(result["exit_code"])
