"""
Unit tests for loop_detection middleware.

Tests the circular message detection functionality.
"""

import pytest

from tools.agents.middleware.loop_detection import LoopDetector


@pytest.mark.unit
class TestLoopDetector:
    """Test suite for LoopDetector class."""

    def test_loop_detector_initialization(self):
        """Test LoopDetector initialization with default window."""
        detector = LoopDetector()
        assert detector is not None

    def test_loop_detector_custom_window(self):
        """Test LoopDetector initialization with custom window size."""
        detector = LoopDetector(window=16)
        assert detector is not None

    def test_loop_detector_no_loop_empty_history(self):
        """Test that empty history shows no loop."""
        detector = LoopDetector()
        assert detector.detect_loop() is False

    def test_loop_detector_no_loop_single_message(self):
        """Test that single message shows no loop."""
        detector = LoopDetector()
        detector.push("Hello, world!")
        assert detector.detect_loop() is False

    def test_loop_detector_no_loop_different_messages(self, sample_texts):
        """Test that different messages show no loop."""
        detector = LoopDetector()
        for text in sample_texts.values():
            detector.push(text)
        assert detector.detect_loop() is False

    def test_loop_detector_detects_identical_message(self):
        """Test that identical message repeated twice is detected as loop."""
        detector = LoopDetector()
        message = "This is a test message."

        detector.push(message)
        detector.push(message)

        assert detector.detect_loop() is True

    def test_loop_detector_detects_repeated_sequence(self, sample_texts):
        """Test that repeated message sequence is detected."""
        detector = LoopDetector()

        # Push first message
        text1 = sample_texts["hello"]
        text2 = sample_texts["world"]

        detector.push(text1)
        detector.push(text2)
        detector.push(text1)

        # After pushing text1 again, should detect loop
        assert detector.detect_loop() is True

    def test_loop_detector_window_respects_size(self):
        """Test that loop detection respects window size."""
        detector = LoopDetector(window=2)

        # Push 3 different messages
        for i in range(3):
            detector.push(f"Message {i}")

        # With window=2, only last 2 messages should be in history
        # Push first message again - should not detect loop as it's outside window
        detector.push("Message 0")
        assert detector.detect_loop() is False

    def test_loop_detector_fingerprinting(self):
        """Test that same content has same fingerprint."""
        detector = LoopDetector()

        message = "Test message for fingerprinting"
        detector.push(message)
        detector.push(message)

        # Should detect loop with identical text
        assert detector.detect_loop() is True

    def test_loop_detector_similar_not_identical(self):
        """Test that similar but different messages don't trigger loop."""
        detector = LoopDetector()

        message1 = "This is a test message"
        message2 = "This is a test message."  # Extra period

        detector.push(message1)
        detector.push(message2)

        # Different content = different fingerprint
        assert detector.detect_loop() is False

    def test_loop_detector_multiple_cycles(self):
        """Test detection after multiple cycles."""
        detector = LoopDetector()

        message_a = "Message A"
        message_b = "Message B"

        # First cycle
        detector.push(message_a)
        detector.push(message_b)

        # Second cycle
        detector.push(message_a)
        assert detector.detect_loop() is True

    def test_loop_detector_large_window(self):
        """Test behavior with large window size."""
        detector = LoopDetector(window=100)

        # Push 50 messages
        for i in range(50):
            detector.push(f"Message {i}")

        assert detector.detect_loop() is False

        # Push first message again
        detector.push("Message 0")
        # Still in window, should detect
        assert detector.detect_loop() is True

    def test_loop_detector_push_and_detect_sequence(self):
        """Test mixed push and detect operations."""
        detector = LoopDetector(window=8)  # Larger window to keep all messages

        # Push A, B, C, D, A - the second A creates a duplicate
        detector.push("A")
        detector.push("B")
        detector.push("C")
        detector.push("D")

        # No loop yet - all different
        assert detector.detect_loop() is False

        # Now push A again - should detect loop
        detector.push("A")
        assert detector.detect_loop() is True

    def test_loop_detector_empty_string(self):
        """Test behavior with empty string."""
        detector = LoopDetector()

        detector.push("")
        assert detector.detect_loop() is False

        detector.push("")
        # Empty strings are identical
        assert detector.detect_loop() is True

    def test_loop_detector_long_messages(self):
        """Test with very long messages."""
        detector = LoopDetector()

        long_msg = "x" * 10000
        detector.push(long_msg)
        detector.push(long_msg)

        assert detector.detect_loop() is True

    def test_loop_detector_unicode_messages(self):
        """Test with Unicode messages."""
        detector = LoopDetector()

        unicode_msg1 = "你好世界"
        unicode_msg2 = "Hello 世界"

        detector.push(unicode_msg1)
        detector.push(unicode_msg2)
        assert detector.detect_loop() is False

        detector.push(unicode_msg1)
        assert detector.detect_loop() is True

    def test_loop_detector_whitespace_sensitivity(self):
        """Test that whitespace differences are detected."""
        detector = LoopDetector()

        msg1 = "Hello  world"  # Double space
        msg2 = "Hello world"  # Single space

        detector.push(msg1)
        detector.push(msg2)

        # Different strings due to whitespace
        assert detector.detect_loop() is False
