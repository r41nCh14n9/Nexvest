"""Minimal reasoning optimizer middleware stub.

Provides a hook to adjust reasoning settings (temperature, max_tokens, etc.)
based on simple heuristics such as recent latency, error rate or detected loops.
"""
from typing import Dict


class ReasoningOptimizer:
    def __init__(self, base_config: Dict = None):
        self.base_config = base_config or {"temperature": 0.7, "max_tokens": 512}

    def optimize(self, signals: Dict) -> Dict:
        """Return an adjusted config based on provided signals.

        signals may include keys: latency_ms, error_rate, loop_detected, entropy
        """
        cfg = dict(self.base_config)
        if signals.get("loop_detected"):
            cfg["temperature"] = max(0.0, cfg.get("temperature", 0.7) - 0.4)
            cfg["max_tokens"] = int(cfg.get("max_tokens", 512) * 0.5)
        if signals.get("latency_ms", 0) > 1000:
            cfg["max_tokens"] = int(cfg.get("max_tokens", 512) * 0.8)
        return cfg


if __name__ == "__main__":
    ro = ReasoningOptimizer()
    print(ro.optimize({"loop_detected": True, "latency_ms": 1200}))
