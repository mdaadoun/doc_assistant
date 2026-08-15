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
    result = run_project_tests(
        test_path="tests/unit/test_debug_retrieval_and_finops.py"
    )
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


def test_run_project_tests_docx_parser_suite() -> None:
    """Verify test runner successfully executes the DOCX parser test suite."""
    result = run_project_tests(test_path="tests/unit/test_docx_parser.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_markdown_parser_suite() -> None:
    """Verify test runner successfully executes the Markdown parser test suite."""
    result = run_project_tests(test_path="tests/unit/test_markdown_parser.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_recursive_chunker_suite() -> None:
    """Verify test runner successfully executes the recursive chunker test suite."""
    result = run_project_tests(test_path="tests/unit/test_recursive_chunker.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_ingestion_facade_suite() -> None:
    """Verify test runner successfully executes the ingestion facade test suite."""
    result = run_project_tests(test_path="tests/unit/test_ingestion_facade.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_differential_tracker_suite() -> None:
    """Verify test runner successfully executes the differential tracker test suite."""
    result = run_project_tests(test_path="tests/unit/test_differential_tracker.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_vector_store_suite() -> None:
    """Verify test runner successfully executes the vector store test suite."""
    result = run_project_tests(test_path="tests/unit/test_vector_store.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_embedding_client_suite() -> None:
    """Verify test runner successfully executes the embedding client test suite."""
    result = run_project_tests(test_path="tests/unit/test_embedding_client.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_bm25_index_suite() -> None:
    """Verify test runner successfully executes the BM25 index test suite."""
    result = run_project_tests(test_path="tests/unit/test_bm25_index.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_sparse_search_suite() -> None:
    """Verify test runner successfully executes the sparse search test suite."""
    result = run_project_tests(test_path="tests/unit/test_sparse_search.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_rrf_fusion_suite() -> None:
    """Verify test runner successfully executes the RRF fusion test suite."""
    result = run_project_tests(test_path="tests/unit/test_rrf_fusion.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_debug_retrieval_builder_suite() -> None:
    """Verify test runner successfully executes the debug retrieval builder test suite."""
    result = run_project_tests(test_path="tests/unit/test_debug_retrieval_builder.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_flashrank_reranker_suite() -> None:
    """Verify test runner successfully executes the FlashRank reranker test suite."""
    result = run_project_tests(test_path="tests/unit/test_flashrank_reranker.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_cohere_reranker_suite() -> None:
    """Verify test runner successfully executes the Cohere reranker test suite."""
    result = run_project_tests(test_path="tests/unit/test_cohere_reranker.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_reranker_service_suite() -> None:
    """Verify test runner successfully executes the RerankerService test suite."""
    result = run_project_tests(test_path="tests/unit/test_reranker_service.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_confidence_guard_suite() -> None:
    """Verify test runner successfully executes the ConfidenceGuard test suite."""
    result = run_project_tests(test_path="tests/unit/test_confidence_guard.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_grounded_generator_suite() -> None:
    """Verify test runner successfully executes the GroundedGenerator test suite."""
    result = run_project_tests(test_path="tests/unit/test_grounded_generator.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_sse_handler_suite() -> None:
    """Verify test runner successfully executes the SSEResponseHandler test suite."""
    result = run_project_tests(test_path="tests/unit/test_sse_handler.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_citations_suite() -> None:
    """Verify test runner successfully executes the citations test suite."""
    result = run_project_tests(test_path="tests/unit/test_citations.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_finops_collector_suite() -> None:
    """Verify test runner successfully executes the FinOps collector test suite."""
    result = run_project_tests(test_path="tests/unit/test_finops_collector.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_chat_endpoint_suite() -> None:
    """Verify test runner successfully executes the chat endpoint test suite."""
    result = run_project_tests(test_path="tests/unit/test_chat_endpoint.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_debug_retrieval_endpoint_suite() -> None:
    """Verify test runner successfully executes the debug retrieval endpoint test suite."""
    result = run_project_tests(test_path="tests/unit/test_debug_retrieval_endpoint.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_api_key_auth_suite() -> None:
    """Verify test runner successfully executes the API key authentication test suite."""
    result = run_project_tests(test_path="tests/unit/test_api_key_auth.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_cors_and_middleware_suite() -> None:
    """Verify test runner successfully executes the CORS and middleware test suite."""
    result = run_project_tests(test_path="tests/unit/test_cors_and_middleware.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_service_container_suite() -> None:
    """Verify test runner successfully executes the service container test suite."""
    result = run_project_tests(test_path="tests/unit/test_service_container.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_lifespan_di_suite() -> None:
    """Verify test runner successfully executes the lifespan DI test suite."""
    result = run_project_tests(test_path="tests/unit/test_lifespan_di.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0


def test_run_project_tests_frontend_suite() -> None:
    """Verify test runner successfully executes the frontend test suite."""
    result = run_project_tests(test_path="tests/unit/test_frontend.py")
    assert result["status"] == "PASSED"
    assert result["exit_code"] == 0
