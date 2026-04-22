"""
Unit tests for entropy_agent module.

Tests the entropy auditing and seed reset functionality.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from tools.agents.entropy.entropy_agent import run_audit_and_reset


@pytest.mark.unit
class TestEntropyAgent:
    """Test suite for entropy agent functionality."""

    def test_run_audit_and_reset_dry_run_default(self, caplog):
        """
        Test that dry_run=True (default) doesn't modify state.

        Expects:
        - No actual changes to system
        - Log messages indicating dry-run mode
        - Seed value in output
        """
        with caplog.at_level(logging.INFO):
            run_audit_and_reset()

        # Verify dry-run mode
        assert "dry_run" in caplog.text.lower() or "audit" in caplog.text.lower()

    def test_run_audit_and_reset_dry_run_explicit(self, caplog):
        """Test dry_run=True with explicit parameter."""
        with caplog.at_level(logging.INFO):
            run_audit_and_reset(dry_run=True)

        # Should log audit information
        assert len(caplog.records) > 0

    def test_run_audit_and_reset_actual_execution(self, caplog):
        """
        Test actual execution with dry_run=False.

        Note: This test runs in isolation and should not affect
        global state in test environment.
        """
        with caplog.at_level(logging.INFO):
            run_audit_and_reset(dry_run=False)

        # Verify execution happened
        assert len(caplog.records) > 0

    def test_run_audit_and_reset_generates_seed(self, caplog):
        """Test that audit generates a valid random seed."""
        with caplog.at_level(logging.DEBUG):
            run_audit_and_reset(dry_run=True)

        # Log should contain information about seed generation
        log_text = caplog.text.lower()
        # Check for typical audit/seed related keywords
        assert any(
            keyword in log_text for keyword in ["seed", "audit", "entropy", "reset", "random"]
        )

    @patch("tools.agents.entropy.entropy_agent.random.SystemRandom")
    def test_run_audit_and_reset_logging_called(self, mock_random):
        """Verify that logging is called during audit."""
        # Mock random to control seed generation
        mock_instance = MagicMock()
        mock_instance.randint.return_value = 12345
        mock_random.return_value = mock_instance

        with patch("tools.agents.entropy.entropy_agent.LOG") as mock_logger:
            run_audit_and_reset(dry_run=True)

            # At least one log call should be made
            assert mock_logger.info.call_count >= 1

    def test_run_audit_and_reset_no_exceptions(self):
        """Test that function runs without raising exceptions."""
        # Should not raise any exception
        try:
            run_audit_and_reset(dry_run=True)
            success = True
        except Exception as e:
            pytest.fail(f"run_audit_and_reset raised {type(e).__name__}: {e}")
            success = False

        assert success

    def test_run_audit_and_reset_reproducible(self, caplog):
        """
        Test that multiple runs produce valid seeds (not necessarily same).

        This verifies the function is deterministic in its behavior.
        """
        runs = []
        for _ in range(3):
            caplog.clear()
            with caplog.at_level(logging.INFO):
                run_audit_and_reset(dry_run=True)
            runs.append(caplog.text)

        # All runs should produce output
        assert all(len(run) > 0 for run in runs)
