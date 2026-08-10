"""Unit tests for app dashboard test runner."""

from tests.runner import run_project_tests


def test_run_project_tests_invocation() -> None:
    """Verify test runner executes and returns structured execution payload."""
    result = run_project_tests(
        test_path="tests/unit", extra_args=["-k", "test_get_python_version_tuple"]
    )
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0
    assert "target" in result


def test_run_project_tests_layout_suite() -> None:
    """Verify test runner successfully executes the package layout test suite."""
    result = run_project_tests(test_path="tests/unit/test_layout.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_makefile_suite() -> None:
    """Verify test runner successfully executes the makefile test suite."""
    result = run_project_tests(test_path="tests/unit/test_makefile.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0
