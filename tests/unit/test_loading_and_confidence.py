"""Unit tests for frontend loading states, error handling, and confidence indicators."""

from pathlib import Path

from core.frontend import (
    REQUIRED_CONFIDENCE_INDICATOR_IDS,
    REQUIRED_CONFIDENCE_INDICATOR_PROPS,
    REQUIRED_ERROR_BANNER_IDS,
    REQUIRED_ERROR_BANNER_PROPS,
    REQUIRED_LOADING_INDICATOR_IDS,
    REQUIRED_LOADING_INDICATOR_PROPS,
    validate_confidence_indicator_component,
    validate_error_banner_component,
    validate_loading_indicator_component,
    validate_resilience_and_confidence_components,
)


def test_resilience_and_confidence_components_exist_and_valid() -> None:
    """Verify all phase 9.5 components satisfy structural and contract requirements."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_resilience_and_confidence_components(root)

    assert result["valid"] is True
    assert result["confidence_indicator"]["valid"] is True
    assert result["error_banner"]["valid"] is True
    assert result["loading_indicator"]["valid"] is True


def test_confidence_indicator_component_contract() -> None:
    """Verify ConfidenceIndicator component contains required props, IDs, and thresholds."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_file = root / "frontend" / "src" / "components" / "ConfidenceIndicator.tsx"
    content = comp_file.read_text(encoding="utf-8")

    assert "interface ConfidenceIndicatorProps" in content
    for req_prop in REQUIRED_CONFIDENCE_INDICATOR_PROPS:
        assert req_prop in content

    for req_id in REQUIRED_CONFIDENCE_INDICATOR_IDS:
        assert f'id="{req_id}"' in content

    assert "0.7" in content
    assert "0.35" in content
    assert 'role="progressbar"' in content
    assert "aria-valuenow=" in content
    assert "aria-valuemin=" in content
    assert "aria-valuemax=" in content
    assert "getConfidenceTier" in content


def test_error_banner_component_contract() -> None:
    """Verify ErrorBanner component contains alert role, error code badge, and retry action."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_file = root / "frontend" / "src" / "components" / "ErrorBanner.tsx"
    content = comp_file.read_text(encoding="utf-8")

    assert "interface ErrorBannerProps" in content
    for req_prop in REQUIRED_ERROR_BANNER_PROPS:
        assert req_prop in content

    for req_id in REQUIRED_ERROR_BANNER_IDS:
        assert f'id="{req_id}"' in content

    assert 'role="alert"' in content
    assert 'aria-live="assertive"' in content
    assert "onRetry" in content
    assert "onDismiss" in content
    assert "dismiss-error-btn" in content


def test_loading_indicator_component_contract() -> None:
    """Verify LoadingIndicator contains pipeline steps, skeleton pulse, and spinner."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_file = root / "frontend" / "src" / "components" / "LoadingIndicator.tsx"
    content = comp_file.read_text(encoding="utf-8")

    assert "interface LoadingIndicatorProps" in content
    for req_prop in REQUIRED_LOADING_INDICATOR_PROPS:
        assert req_prop in content

    for req_id in REQUIRED_LOADING_INDICATOR_IDS:
        assert f'id="{req_id}"' in content

    assert 'role="status"' in content
    assert 'aria-live="polite"' in content
    assert "loading-steps-track" in content
    assert "loading-skeleton-pulse" in content
    assert "skeleton-line" in content


def test_response_view_integration_with_confidence_and_errors() -> None:
    """Verify ResponseView integrates ConfidenceIndicator, LoadingIndicator, and error cards."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_file = root / "frontend" / "src" / "components" / "ResponseView.tsx"
    content = comp_file.read_text(encoding="utf-8")

    assert "ConfidenceIndicator" in content
    assert "LoadingIndicator" in content
    assert "message-error-card" in content
    assert "onRetryMessage" in content
    assert "retrievalPhase" in content


def test_app_integration_with_error_banner_and_retry() -> None:
    """Verify App component renders ErrorBanner and coordinates retry handling."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_file = root / "frontend" / "src" / "App.tsx"
    content = comp_file.read_text(encoding="utf-8")

    assert "ErrorBanner" in content
    assert "globalError" in content
    assert "handleRetry" in content
    assert "retrievalPhase" in content
    assert "setRetrievalPhase" in content


def test_resilience_validators_missing_files(tmp_path: Path) -> None:
    """Verify validators report invalid status when component files are missing."""
    conf_res = validate_confidence_indicator_component(tmp_path)
    assert conf_res["valid"] is False
    assert conf_res["missing_props"] == REQUIRED_CONFIDENCE_INDICATOR_PROPS

    err_res = validate_error_banner_component(tmp_path)
    assert err_res["valid"] is False
    assert err_res["missing_props"] == REQUIRED_ERROR_BANNER_PROPS

    load_res = validate_loading_indicator_component(tmp_path)
    assert load_res["valid"] is False
    assert load_res["missing_props"] == REQUIRED_LOADING_INDICATOR_PROPS


def test_resilience_validators_incomplete_components(tmp_path: Path) -> None:
    """Verify validators detect incomplete component implementations."""
    comp_dir = tmp_path / "frontend" / "src" / "components"
    comp_dir.mkdir(parents=True)
    (comp_dir / "ConfidenceIndicator.tsx").write_text(
        "export const C = () => <div />;\n"
    )
    (comp_dir / "ErrorBanner.tsx").write_text("export const E = () => <div />;\n")
    (comp_dir / "LoadingIndicator.tsx").write_text("export const L = () => <div />;\n")

    result = validate_resilience_and_confidence_components(tmp_path)
    assert result["valid"] is False
    assert result["confidence_indicator"]["valid"] is False
    assert result["error_banner"]["valid"] is False
    assert result["loading_indicator"]["valid"] is False
