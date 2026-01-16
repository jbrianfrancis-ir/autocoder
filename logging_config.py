# logging_config.py
"""
Centralized Logging Configuration
=================================

Provides dictConfig-based logging setup for all Python modules.
Supports environment variable configuration:
  - LOG_LEVEL: Global log level (default: INFO)
  - LOG_LEVEL_<MODULE>: Per-module overrides (e.g., LOG_LEVEL_AGENT=DEBUG)

Usage:
    from logging_config import configure_logging
    configure_logging()  # Call once at application startup
"""

import logging
import logging.config
import os

# Standard log format: timestamp, level, module, message
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_module_level(module_name: str) -> str:
    """
    Get log level for a specific module from environment.

    Checks for LOG_LEVEL_<MODULE> environment variable, falling back
    to global LOG_LEVEL if not set.

    Args:
        module_name: Name of the module (e.g., 'agent', 'server.routers')

    Returns:
        Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    env_key = f"LOG_LEVEL_{module_name.upper().replace('.', '_')}"
    return os.environ.get(env_key, global_level).upper()


def get_logging_config() -> dict:
    """
    Build logging configuration dictionary for dictConfig.

    Returns:
        dict: Configuration compatible with logging.config.dictConfig()
    """
    global_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    return {
        "version": 1,
        "disable_existing_loggers": False,  # Critical: preserve third-party loggers
        "formatters": {
            "standard": {
                "format": LOG_FORMAT,
                "datefmt": DATE_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",  # Handler accepts all; logger level filters
                "formatter": "standard",
                "stream": "ext://sys.stderr",
            },
        },
        "root": {
            "level": global_level,
            "handlers": ["console"],
        },
        "loggers": {
            # Per-module configuration
            "agent": {"level": get_module_level("agent")},
            "client": {"level": get_module_level("client")},
            "progress": {"level": get_module_level("progress")},
            "prompts": {"level": get_module_level("prompts")},
            "registry": {"level": get_module_level("registry")},
            "server": {"level": get_module_level("server")},
            "mcp_server": {"level": get_module_level("mcp_server")},
            # Third-party noise reduction
            "uvicorn": {"level": "WARNING"},
            "uvicorn.access": {"level": "WARNING"},
        },
    }


def configure_logging() -> None:
    """
    Configure logging for the application.

    Call once at application startup, before other imports that might log.
    Uses dictConfig for hierarchical logger configuration.
    """
    config = get_logging_config()
    logging.config.dictConfig(config)
