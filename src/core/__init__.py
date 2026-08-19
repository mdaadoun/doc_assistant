"""Shared: config, exceptions, telemetry, logging, environment, layout, docker."""

from core.config import Settings, clear_settings_cache, get_settings
from core.docker import (
    REQUIRED_DOCKER_FILES,
    REQUIRED_DOCKER_SERVICES,
    REQUIRED_PORT_MAPPINGS,
    REQUIRED_VOLUMES,
    parse_docker_compose,
    validate_docker_setup,
)
from core.environment import (
    MIN_PYTHON_VERSION,
    check_python_version,
    get_environment_info,
    get_python_version_tuple,
    validate_poetry_config,
)
from core.exceptions import (
    AppBaseError,
    ConfigurationError,
    GenerationError,
    IngestionError,
    RetrievalError,
)
from core.frontend import (
    REQUIRED_CITATION_DRAWER_IDS,
    REQUIRED_CITATION_DRAWER_PROPS,
    REQUIRED_DEPENDENCIES,
    REQUIRED_DEV_DEPENDENCIES,
    REQUIRED_FRONTEND_FILES,
    REQUIRED_PACKAGE_SCRIPTS,
    REQUIRED_TS_INTERFACES,
    parse_frontend_package_json,
    parse_frontend_tsconfig,
    validate_citation_drawer_component,
    validate_frontend_setup,
)
from core.layout import (
    REQUIRED_DIRECTORIES,
    REQUIRED_PACKAGES,
    get_project_root,
    validate_package_layout,
)
from core.makefile import (
    REQUIRED_MAKEFILE_TARGETS,
    parse_makefile_targets,
    validate_makefile,
)
from core.quality import validate_quality_configs

__all__ = [
    "MIN_PYTHON_VERSION",
    "REQUIRED_CITATION_DRAWER_IDS",
    "REQUIRED_CITATION_DRAWER_PROPS",
    "REQUIRED_DEPENDENCIES",
    "REQUIRED_DEV_DEPENDENCIES",
    "REQUIRED_DIRECTORIES",
    "REQUIRED_DOCKER_FILES",
    "REQUIRED_DOCKER_SERVICES",
    "REQUIRED_FRONTEND_FILES",
    "REQUIRED_MAKEFILE_TARGETS",
    "REQUIRED_PACKAGES",
    "REQUIRED_PACKAGE_SCRIPTS",
    "REQUIRED_PORT_MAPPINGS",
    "REQUIRED_TS_INTERFACES",
    "REQUIRED_VOLUMES",
    "AppBaseError",
    "ConfigurationError",
    "GenerationError",
    "IngestionError",
    "RetrievalError",
    "Settings",
    "check_python_version",
    "clear_settings_cache",
    "get_environment_info",
    "get_project_root",
    "get_python_version_tuple",
    "get_settings",
    "parse_docker_compose",
    "parse_frontend_package_json",
    "parse_frontend_tsconfig",
    "parse_makefile_targets",
    "validate_citation_drawer_component",
    "validate_docker_setup",
    "validate_frontend_setup",
    "validate_makefile",
    "validate_package_layout",
    "validate_poetry_config",
    "validate_quality_configs",
]
