"""
Test uv package manager wrapper
"""

import os
import subprocess
import tempfile
from unittest import mock

import pytest

from tljh import uv


class TestUvAvailability:
    """Test uv availability detection"""

    def test_is_uv_available_when_missing(self):
        """Test that is_uv_available returns False when uv is not installed"""
        with mock.patch.object(uv, "UV_BIN", "/nonexistent/path/uv"):
            with mock.patch.object(uv, "UV_SYSTEM_BIN", "/nonexistent/system/uv"):
                assert uv.is_uv_available() is False

    def test_get_uv_binary_when_missing(self):
        """Test that get_uv_binary returns None when uv is not installed"""
        with mock.patch.object(uv, "UV_BIN", "/nonexistent/path/uv"):
            with mock.patch.object(uv, "UV_SYSTEM_BIN", "/nonexistent/system/uv"):
                assert uv.get_uv_binary() is None

    def test_get_uv_binary_prefers_hub_env(self):
        """Test that get_uv_binary prefers hub environment over system"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hub_uv = os.path.join(tmpdir, "hub_uv")
            system_uv = os.path.join(tmpdir, "system_uv")

            # Create both files as executable
            for path in [hub_uv, system_uv]:
                with open(path, "w") as f:
                    f.write("#!/bin/bash\n")
                os.chmod(path, 0o755)

            with mock.patch.object(uv, "UV_BIN", hub_uv):
                with mock.patch.object(uv, "UV_SYSTEM_BIN", system_uv):
                    # Should prefer hub env
                    assert uv.get_uv_binary() == hub_uv

    def test_get_uv_binary_falls_back_to_system(self):
        """Test that get_uv_binary falls back to system when hub env missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_uv = os.path.join(tmpdir, "system_uv")

            # Create only system uv
            with open(system_uv, "w") as f:
                f.write("#!/bin/bash\n")
            os.chmod(system_uv, 0o755)

            with mock.patch.object(uv, "UV_BIN", "/nonexistent/hub/uv"):
                with mock.patch.object(uv, "UV_SYSTEM_BIN", system_uv):
                    assert uv.get_uv_binary() == system_uv


class TestUvPackageInstallation:
    """Test uv package installation functions"""

    def test_ensure_uv_packages_falls_back_to_pip(self):
        """Test that ensure_uv_packages falls back to pip when uv not available"""
        with mock.patch.object(uv, "get_uv_binary", return_value=None):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.ensure_uv_packages("/test/prefix", ["package1", "package2"])
                # Should have called pip, not uv
                args = mock_run.call_args[0][0]
                assert "-m" in args
                assert "pip" in args
                assert "package1" in args
                assert "package2" in args

    def test_ensure_uv_packages_uses_uv_when_available(self):
        """Test that ensure_uv_packages uses uv when available"""
        with mock.patch.object(uv, "get_uv_binary", return_value="/usr/local/bin/uv"):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.ensure_uv_packages("/test/prefix", ["package1"])
                args = mock_run.call_args[0][0]
                assert "/usr/local/bin/uv" in args
                assert "pip" in args
                assert "install" in args
                assert "package1" in args

    def test_ensure_uv_packages_with_upgrade(self):
        """Test that ensure_uv_packages passes upgrade flag"""
        with mock.patch.object(uv, "get_uv_binary", return_value="/usr/local/bin/uv"):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.ensure_uv_packages("/test/prefix", ["package1"], upgrade=True)
                args = mock_run.call_args[0][0]
                assert "--upgrade" in args

    def test_ensure_uv_requirements_falls_back_to_pip(self):
        """Test that ensure_uv_requirements falls back to pip when uv not available"""
        with mock.patch.object(uv, "get_uv_binary", return_value=None):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.ensure_uv_requirements("/test/prefix", "/path/to/requirements.txt")
                args = mock_run.call_args[0][0]
                assert "-m" in args
                assert "pip" in args
                assert "--requirement" in args
                assert "/path/to/requirements.txt" in args

    def test_ensure_uv_requirements_uses_uv_when_available(self):
        """Test that ensure_uv_requirements uses uv when available"""
        with mock.patch.object(uv, "get_uv_binary", return_value="/usr/local/bin/uv"):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.ensure_uv_requirements("/test/prefix", "/path/to/requirements.txt")
                args = mock_run.call_args[0][0]
                assert "/usr/local/bin/uv" in args
                assert "--requirement" in args
                assert "/path/to/requirements.txt" in args

    def test_upgrade_pip_with_uv_uses_uv(self):
        """Test that upgrade_pip_with_uv uses uv when available"""
        with mock.patch.object(uv, "get_uv_binary", return_value="/usr/local/bin/uv"):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.upgrade_pip_with_uv("/test/prefix")
                args = mock_run.call_args[0][0]
                assert "/usr/local/bin/uv" in args
                assert "--upgrade" in args
                assert "pip" in args

    def test_upgrade_pip_with_uv_falls_back_to_pip(self):
        """Test that upgrade_pip_with_uv falls back to pip when uv not available"""
        with mock.patch.object(uv, "get_uv_binary", return_value=None):
            with mock.patch("tljh.utils.run_subprocess") as mock_run:
                uv.upgrade_pip_with_uv("/test/prefix")
                args = mock_run.call_args[0][0]
                assert "-m" in args
                assert "pip" in args
                assert "--upgrade" in args
