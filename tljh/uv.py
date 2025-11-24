"""
UV package manager wrapper for fast Python package installation.

UV is an extremely fast Python package installer written in Rust.
This module provides functions to use uv for package installation in TLJH,
which can be 10-100x faster than pip.
"""

import logging
import os
import shutil

from tljh import utils
from tljh.config import UV_BIN

# System-wide uv location (e.g., pre-installed in Docker image)
UV_SYSTEM_BIN = "/usr/local/bin/uv"


def is_uv_available():
    """
    Check if uv is available.

    Checks both the hub environment and system-wide locations.
    Returns True if uv binary exists and is executable.
    """
    return (
        (os.path.isfile(UV_BIN) and os.access(UV_BIN, os.X_OK))
        or (os.path.isfile(UV_SYSTEM_BIN) and os.access(UV_SYSTEM_BIN, os.X_OK))
    )


def get_uv_binary():
    """
    Get the path to the uv binary.

    Prefers the hub environment uv, falls back to system-wide uv.
    Returns the path to uv if available, None otherwise.
    """
    if os.path.isfile(UV_BIN) and os.access(UV_BIN, os.X_OK):
        return UV_BIN
    if os.path.isfile(UV_SYSTEM_BIN) and os.access(UV_SYSTEM_BIN, os.X_OK):
        return UV_SYSTEM_BIN
    return None


def ensure_uv_packages(prefix, packages, upgrade=False):
    """
    Ensure pip packages are installed in the given prefix using uv.

    Uses uv pip install for significantly faster package installation.
    Falls back to regular pip if uv is not available.

    Args:
        prefix: The path to the Python environment prefix
        packages: List of package specifications to install
        upgrade: If True, upgrade packages to latest version
    """
    logger = logging.getLogger("tljh")
    abspath = os.path.abspath(prefix)
    python_path = os.path.join(abspath, "bin", "python")

    uv_binary = get_uv_binary()
    if uv_binary:
        logger.debug(f"Using uv ({uv_binary}) for package installation in {prefix}")
        uv_cmd = [uv_binary, "pip", "install", "--python", python_path]
        if upgrade:
            uv_cmd.append("--upgrade")
        utils.run_subprocess(uv_cmd + packages)
    else:
        # Fallback to pip if uv is not available
        logger.debug(f"uv not available, falling back to pip for {prefix}")
        pip_executable = [python_path, "-m", "pip"]
        pip_cmd = pip_executable + ["install"]
        if upgrade:
            pip_cmd.append("--upgrade")
        utils.run_subprocess(pip_cmd + packages)


def ensure_uv_requirements(prefix, requirements_path, upgrade=False):
    """
    Ensure pip packages from given requirements file are installed using uv.

    Uses uv pip install -r for significantly faster package installation.
    Falls back to regular pip if uv is not available.

    Args:
        prefix: The path to the Python environment prefix
        requirements_path: Path to requirements.txt file (can be a file or URL)
        upgrade: If True, upgrade packages to latest version
    """
    logger = logging.getLogger("tljh")
    abspath = os.path.abspath(prefix)
    python_path = os.path.join(abspath, "bin", "python")

    uv_binary = get_uv_binary()
    if uv_binary:
        logger.debug(f"Using uv ({uv_binary}) for requirements installation in {prefix}")
        uv_cmd = [uv_binary, "pip", "install", "--python", python_path]
        if upgrade:
            uv_cmd.append("--upgrade")
        utils.run_subprocess(uv_cmd + ["--requirement", requirements_path])
    else:
        # Fallback to pip if uv is not available
        logger.debug(f"uv not available, falling back to pip for {prefix}")
        pip_executable = [python_path, "-m", "pip"]
        pip_cmd = pip_executable + ["install"]
        if upgrade:
            pip_cmd.append("--upgrade")
        utils.run_subprocess(pip_cmd + ["--requirement", requirements_path])


def upgrade_pip_with_uv(prefix):
    """
    Upgrade pip in the given prefix using uv.

    Args:
        prefix: The path to the Python environment prefix
    """
    logger = logging.getLogger("tljh")
    abspath = os.path.abspath(prefix)
    python_path = os.path.join(abspath, "bin", "python")

    uv_binary = get_uv_binary()
    if uv_binary:
        logger.debug(f"Upgrading pip using uv ({uv_binary}) in {prefix}")
        uv_cmd = [uv_binary, "pip", "install", "--python", python_path, "--upgrade", "pip"]
        utils.run_subprocess(uv_cmd)
    else:
        logger.debug(f"uv not available, using pip to upgrade itself in {prefix}")
        pip_executable = [python_path, "-m", "pip"]
        utils.run_subprocess(pip_executable + ["install", "--upgrade", "pip"])
