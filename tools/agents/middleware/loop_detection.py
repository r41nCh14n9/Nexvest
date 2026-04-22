"""Minimal loop detection middleware for agents.

This is a lightweight, importable stub demonstrating how to detect simple
prompt/response loops using a short-term history fingerprint.
"""
from typing import List
import hashlib


class LoopDetector:
    def __init__(self, window: int = 8):
        self.window = window
        self.history: List[str] = []

    def _fingerprint(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def push(self, text: str) -> None:
        fp = self._fingerprint(text)
        self.history.append(fp)
        if len(self.history) > self.window:
            self.history.pop(0)

    def detect_loop(self) -> bool:
        """Return True if a repeated fingerprint is observed in the window."""
        return len(set(self.history)) < len(self.history)


if __name__ == "__main__":
    ld = LoopDetector()
    for t in ["a", "b", "a", "b"]:
        ld.push(t)
        print(t, ld.detect_loop())
