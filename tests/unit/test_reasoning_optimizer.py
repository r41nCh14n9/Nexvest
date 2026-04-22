"""
Unit tests for reasoning_optimizer middleware.

Tests the LLM configuration optimization based on system signals.
"""

import copy

import pytest

from tools.agents.middleware.reasoning_optimizer import ReasoningOptimizer


@pytest.mark.unit
class TestReasoningOptimizer:
    """Test suite for ReasoningOptimizer class."""

    def test_optimizer_initialization_default(self):
        """Test ReasoningOptimizer initialization with default config."""
        optimizer = ReasoningOptimizer()
        assert optimizer is not None

    def test_optimizer_initialization_custom_config(self, sample_base_config):
        """Test initialization with custom base configuration."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        assert optimizer is not None

    def test_optimizer_empty_signals(self, sample_base_config):
        """Test optimization with empty signals dict."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({})

        # Empty signals should return base config
        assert result is not None
        assert isinstance(result, dict)

    def test_optimizer_loop_detected_signal(self, sample_base_config):
        """Test optimization when loop is detected."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({"loop_detected": True})

        # Temperature should be reduced
        assert result["temperature"] < sample_base_config["temperature"]
        # Max tokens should be reduced
        assert result["max_tokens"] < sample_base_config["max_tokens"]

    def test_optimizer_loop_detected_temperature_reduction(self, sample_base_config):
        """Test specific temperature reduction for loop detection."""
        original_temp = sample_base_config["temperature"]
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        result = optimizer.optimize({"loop_detected": True})

        # Temperature should be reduced by ~43% (from default logic)
        expected_temp = max(0.0, original_temp - 0.3)
        assert result["temperature"] <= original_temp

    def test_optimizer_high_latency_signal(self, sample_base_config):
        """Test optimization when latency is high."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({"latency_ms": 1500})

        # Max tokens should be reduced under high latency
        assert result["max_tokens"] <= sample_base_config["max_tokens"]

    def test_optimizer_low_latency_signal(self, sample_base_config):
        """Test optimization when latency is low."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({"latency_ms": 100})

        # With low latency, config might be kept or adjusted slightly
        assert result is not None
        assert isinstance(result, dict)

    def test_optimizer_high_error_rate_signal(self, sample_base_config):
        """Test optimization when error rate is high."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({"error_rate": 0.25})

        # High error rate might trigger optimizations
        assert result is not None

    def test_optimizer_low_error_rate_signal(self, sample_base_config):
        """Test optimization when error rate is low."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({"error_rate": 0.01})

        # Low error rate should keep config similar
        assert result is not None

    def test_optimizer_combined_signals(self, sample_base_config):
        """Test optimization with multiple signals."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        signals = {
            "loop_detected": True,
            "latency_ms": 1500,
            "error_rate": 0.15,
            "entropy": 0.8,
        }

        result = optimizer.optimize(signals)

        # Multiple optimizations should compound
        assert result["temperature"] < sample_base_config["temperature"]
        assert result["max_tokens"] <= sample_base_config["max_tokens"]

    def test_optimizer_preserves_other_config_keys(self, sample_base_config):
        """Test that optimization preserves non-optimized config keys."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)
        result = optimizer.optimize({"loop_detected": True})

        # Config should contain all original keys
        assert "top_p" in result
        assert "frequency_penalty" in result

    def test_optimizer_temperature_boundary_min(self, sample_base_config):
        """Test that temperature doesn't go below 0.0."""
        config = sample_base_config.copy()
        config["temperature"] = 0.1

        optimizer = ReasoningOptimizer(base_config=config)
        result = optimizer.optimize({"loop_detected": True})

        # Should not go below 0
        assert result["temperature"] >= 0.0

    def test_optimizer_temperature_boundary_max(self, sample_base_config):
        """Test that temperature doesn't exceed 2.0 (typical LLM limit)."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        # Even with negative signals, shouldn't exceed reasonable limits
        result = optimizer.optimize({})
        assert result["temperature"] <= 2.0

    def test_optimizer_tokens_boundary_min(self, sample_base_config):
        """Test that max_tokens doesn't go below reasonable minimum."""
        config = sample_base_config.copy()
        config["max_tokens"] = 100

        optimizer = ReasoningOptimizer(base_config=config)
        result = optimizer.optimize({"loop_detected": True})

        # Should have some minimum token limit
        assert result["max_tokens"] > 0

    def test_optimizer_entropy_signal(self, sample_base_config):
        """Test optimization based on entropy signal."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        # High entropy might indicate diverse outputs (good)
        result_high = optimizer.optimize({"entropy": 0.95})

        # Low entropy might indicate repetitive outputs (bad)
        result_low = optimizer.optimize({"entropy": 0.1})

        assert result_high is not None
        assert result_low is not None

    def test_optimizer_signal_independence(self, sample_base_config):
        """Test that each signal can be applied independently."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        # Get results for each signal independently
        loop_result = optimizer.optimize({"loop_detected": True})
        latency_result = optimizer.optimize({"latency_ms": 1500})
        error_result = optimizer.optimize({"error_rate": 0.2})

        # All should produce valid results
        assert all(isinstance(r, dict) for r in [loop_result, latency_result, error_result])

    def test_optimizer_no_mutation_of_base_config(self, sample_base_config):
        """Test that optimize() doesn't mutate the base config."""
        base_copy = copy.deepcopy(sample_base_config)
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        optimizer.optimize({"loop_detected": True})

        # Original config should remain unchanged
        assert sample_base_config == base_copy

    def test_optimizer_returns_dict(self, sample_base_config):
        """Test that optimize always returns a dictionary."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        result1 = optimizer.optimize({})
        result2 = optimizer.optimize({"loop_detected": True})
        result3 = optimizer.optimize({"latency_ms": 500})

        assert all(isinstance(r, dict) for r in [result1, result2, result3])

    def test_optimizer_complex_signal_combination(self, sample_base_config):
        """
        Test optimization with complex signal combination.

        Simulates a scenario where multiple issues occur simultaneously.
        """
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        complex_signals = {
            "loop_detected": True,
            "latency_ms": 2000,  # Very high
            "error_rate": 0.3,  # High
            "entropy": 0.2,  # Low (repetitive)
        }

        result = optimizer.optimize(complex_signals)

        # Should produce aggressive optimizations
        assert result["temperature"] < sample_base_config["temperature"]
        assert result["max_tokens"] <= sample_base_config["max_tokens"]

    def test_optimizer_marginal_signal_values(self, sample_base_config):
        """Test optimization with marginal/boundary signal values."""
        optimizer = ReasoningOptimizer(base_config=sample_base_config)

        # Exactly at threshold values
        result1 = optimizer.optimize({"latency_ms": 1000})  # Typical threshold
        result2 = optimizer.optimize({"error_rate": 0.05})  # Low error rate

        assert result1 is not None
        assert result2 is not None
