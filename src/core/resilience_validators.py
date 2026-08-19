"""Validation module for frontend loading states, error handling, and confidence indicators."""

from pathlib import Path
from typing import Any, Final

from core.layout import get_project_root

REQUIRED_CONFIDENCE_INDICATOR_PROPS: Final[list[str]] = [
    "confidenceScore",
]

REQUIRED_CONFIDENCE_INDICATOR_IDS: Final[list[str]] = [
    "confidence-indicator",
    "confidence-score-badge",
    "confidence-tier-badge",
    "confidence-meter-bar",
    "confidence-threshold-marker",
]

REQUIRED_ERROR_BANNER_PROPS: Final[list[str]] = [
    "error",
]

REQUIRED_ERROR_BANNER_IDS: Final[list[str]] = [
    "error-banner",
    "error-title",
    "error-code-badge",
    "error-message-text",
    "retry-button",
]

REQUIRED_LOADING_INDICATOR_PROPS: Final[list[str]] = [
    "phase",
]

REQUIRED_LOADING_INDICATOR_IDS: Final[list[str]] = [
    "loading-indicator",
    "loading-spinner",
    "retrieval-phase-label",
    "loading-step-list",
    "loading-skeleton-pulse",
]


def validate_confidence_indicator_component(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit ConfidenceIndicator React component for tiers, meter and grounding compliance."""
    root = project_root or get_project_root()
    comp_file = root / "frontend" / "src" / "components" / "ConfidenceIndicator.tsx"
    if not comp_file.is_file():
        return {
            "valid": False,
            "error": "ConfidenceIndicator.tsx not found",
            "missing_props": REQUIRED_CONFIDENCE_INDICATOR_PROPS,
            "missing_ids": REQUIRED_CONFIDENCE_INDICATOR_IDS,
            "has_tiered_thresholds": False,
            "has_visual_meter": False,
        }

    content = comp_file.read_text(encoding="utf-8")
    missing_props = [p for p in REQUIRED_CONFIDENCE_INDICATOR_PROPS if p not in content]
    missing_ids = [i for i in REQUIRED_CONFIDENCE_INDICATOR_IDS if i not in content]
    has_thresholds = "0.7" in content and "0.35" in content
    has_meter = "progressbar" in content and "aria-valuenow" in content

    is_valid = (
        len(missing_props) == 0
        and len(missing_ids) == 0
        and has_thresholds
        and has_meter
    )
    return {
        "valid": is_valid,
        "missing_props": missing_props,
        "missing_ids": missing_ids,
        "has_tiered_thresholds": has_thresholds,
        "has_visual_meter": has_meter,
    }


def validate_error_banner_component(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit ErrorBanner React component for alert role, error code and retry actions."""
    root = project_root or get_project_root()
    comp_file = root / "frontend" / "src" / "components" / "ErrorBanner.tsx"
    if not comp_file.is_file():
        return {
            "valid": False,
            "error": "ErrorBanner.tsx not found",
            "missing_props": REQUIRED_ERROR_BANNER_PROPS,
            "missing_ids": REQUIRED_ERROR_BANNER_IDS,
            "has_alert_role": False,
            "has_retry_action": False,
        }

    content = comp_file.read_text(encoding="utf-8")
    missing_props = [p for p in REQUIRED_ERROR_BANNER_PROPS if p not in content]
    missing_ids = [i for i in REQUIRED_ERROR_BANNER_IDS if i not in content]
    has_alert = 'role="alert"' in content
    has_retry = "onRetry" in content and "retry-button" in content

    is_valid = (
        len(missing_props) == 0 and len(missing_ids) == 0 and has_alert and has_retry
    )
    return {
        "valid": is_valid,
        "missing_props": missing_props,
        "missing_ids": missing_ids,
        "has_alert_role": has_alert,
        "has_retry_action": has_retry,
    }


def validate_loading_indicator_component(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit LoadingIndicator React component for progress steps, spinner and skeleton."""
    root = project_root or get_project_root()
    comp_file = root / "frontend" / "src" / "components" / "LoadingIndicator.tsx"
    if not comp_file.is_file():
        return {
            "valid": False,
            "error": "LoadingIndicator.tsx not found",
            "missing_props": REQUIRED_LOADING_INDICATOR_PROPS,
            "missing_ids": REQUIRED_LOADING_INDICATOR_IDS,
            "has_pipeline_steps": False,
            "has_skeleton_shimmer": False,
        }

    content = comp_file.read_text(encoding="utf-8")
    missing_props = [p for p in REQUIRED_LOADING_INDICATOR_PROPS if p not in content]
    missing_ids = [i for i in REQUIRED_LOADING_INDICATOR_IDS if i not in content]
    has_steps = (
        "Dual Search" in content or "retrieving" in content
    ) and "loading-steps-track" in content
    has_skeleton = "skeleton-line" in content and "skeleton" in content

    is_valid = (
        len(missing_props) == 0 and len(missing_ids) == 0 and has_steps and has_skeleton
    )
    return {
        "valid": is_valid,
        "missing_props": missing_props,
        "missing_ids": missing_ids,
        "has_pipeline_steps": has_steps,
        "has_skeleton_shimmer": has_skeleton,
    }


def validate_resilience_and_confidence_components(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit all phase 9.5 components: ConfidenceIndicator, ErrorBanner, LoadingIndicator."""
    root = project_root or get_project_root()
    conf_res = validate_confidence_indicator_component(root)
    err_res = validate_error_banner_component(root)
    load_res = validate_loading_indicator_component(root)

    is_valid = bool(
        conf_res.get("valid") and err_res.get("valid") and load_res.get("valid")
    )
    return {
        "valid": is_valid,
        "confidence_indicator": conf_res,
        "error_banner": err_res,
        "loading_indicator": load_res,
    }
