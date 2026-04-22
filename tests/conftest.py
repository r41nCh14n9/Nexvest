"""
Pytest configuration and shared fixtures for Nexvest tests.

This module provides common fixtures and configuration for the test suite.
"""

import logging
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def caplog_with_level(caplog):
    """
    Fixture that sets log level to DEBUG for tests.

    Allows tests to capture log messages at DEBUG level.
    """
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture
def mock_logger():
    """Mock logger for entropy agent tests."""
    with patch("tools.agents.entropy.entropy_agent.LOG") as mock:
        yield mock


@pytest.fixture
def sample_texts():
    """
    Sample text data for loop detection tests.

    Returns a dictionary with various text samples.
    """
    return {
        "hello": "Hello, this is a test message.",
        "world": "World is a great place.",
        "python": "Python is an excellent programming language.",
        "testing": "Testing is crucial for code quality.",
        "repeated": "This message will be repeated.",
    }


@pytest.fixture
def sample_signals():
    """
    Sample signal data for reasoning optimizer tests.

    Returns dictionaries representing different signal combinations.
    """
    return {
        "no_signals": {},
        "loop_detected": {"loop_detected": True},
        "high_latency": {"latency_ms": 1500},
        "high_error_rate": {"error_rate": 0.15},
        "high_entropy": {"entropy": 0.95},
        "combined": {
            "loop_detected": True,
            "latency_ms": 1200,
            "error_rate": 0.08,
            "entropy": 0.7,
        },
    }


@pytest.fixture
def sample_base_config():
    """
    Sample base configuration for reasoning optimizer.

    Returns a typical optimizer configuration.
    """
    return {
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.95,
        "frequency_penalty": 0.0,
    }
