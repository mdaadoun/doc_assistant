"""Unit tests for app dashboard test runner across all project test suites."""

from typing import Final

import pytest

from tests.runner import run_project_tests

ALL_TEST_SUITES: Final[list[str]] = [
    "tests/unit/test_layout.py",
    "tests/unit/test_makefile.py",
    "tests/unit/test_docker.py",
    "tests/unit/test_base_model.py",
    "tests/unit/test_domain_schemas.py",
    "tests/unit/test_debug_retrieval_and_finops.py",
    "tests/unit/test_exceptions.py",
    "tests/unit/test_pdf_parser.py",
    "tests/unit/test_docx_parser.py",
    "tests/unit/test_markdown_parser.py",
    "tests/unit/test_recursive_chunker.py",
    "tests/unit/test_ingestion_facade.py",
    "tests/unit/test_differential_tracker.py",
    "tests/unit/test_vector_store.py",
    "tests/unit/test_embedding_client.py",
    "tests/unit/test_bm25_index.py",
    "tests/unit/test_sparse_search.py",
    "tests/unit/test_rrf_fusion.py",
    "tests/unit/test_debug_retrieval_builder.py",
    "tests/unit/test_flashrank_reranker.py",
    "tests/unit/test_cohere_reranker.py",
    "tests/unit/test_reranker_service.py",
    "tests/unit/test_confidence_guard.py",
    "tests/unit/test_grounded_generator.py",
    "tests/unit/test_sse_handler.py",
    "tests/unit/test_citations.py",
    "tests/unit/test_finops_collector.py",
    "tests/unit/test_chat_endpoint.py",
    "tests/unit/test_debug_retrieval_endpoint.py",
    "tests/unit/test_api_key_auth.py",
    "tests/unit/test_cors_and_middleware.py",
    "tests/unit/test_service_container.py",
    "tests/unit/test_lifespan_di.py",
    "tests/unit/test_frontend.py",
    "tests/unit/test_query_input.py",
    "tests/unit/test_streaming_response_view.py",
]


def test_run_project_tests_invocation() -> None:
    """Verify test runner executes and returns structured execution payload."""
    result = run_project_tests(
        test_path="tests/unit", extra_args=["-k", "test_get_python_version_tuple"]
    )
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0
    assert "target" in result


@pytest.mark.parametrize("suite_path", ALL_TEST_SUITES)
def test_run_project_test_suite(suite_path: str) -> None:
    """Verify test runner successfully executes individual unit test suites."""
    result = run_project_tests(test_path=suite_path)
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0
