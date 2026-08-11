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


def test_run_project_tests_docker_suite() -> None:
    """Verify test runner successfully executes the docker test suite."""
    result = run_project_tests(test_path="tests/unit/test_docker.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_base_model_suite() -> None:
    """Verify test runner successfully executes the base domain model test suite."""
    result = run_project_tests(test_path="tests/unit/test_base_model.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_domain_schemas_suite() -> None:
    """Verify test runner successfully executes the domain schemas test suite."""
    result = run_project_tests(test_path="tests/unit/test_domain_schemas.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_debug_finops_suite() -> None:
    """Verify test runner successfully executes the debug retrieval and FinOps schema test suite."""
    result = run_project_tests(test_path="tests/unit/test_debug_retrieval_and_finops.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_exceptions_suite() -> None:
    """Verify test runner successfully executes the domain exception hierarchy test suite."""
    result = run_project_tests(test_path="tests/unit/test_exceptions.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_pdf_parser_suite() -> None:
    """Verify test runner successfully executes the PDF parser test suite."""
    result = run_project_tests(test_path="tests/unit/test_pdf_parser.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0



