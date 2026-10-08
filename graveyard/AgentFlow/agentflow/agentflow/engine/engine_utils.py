import threading


# ─────────────────────────────────────────────────────────────
# Token usage tracking & cost calculation
# ─────────────────────────────────────────────────────────────

# USD cost per 1M tokens: {model_key: (input, output)}
MODEL_PRICING = {
    "gpt-4.1-mini":  (0.40,   1.60),
    "gpt-4.1-nano":  (0.10,   0.40),
    "gpt-4.1":       (2.00,   8.00),
    "gpt-4o-mini":   (0.15,   0.60),
    "gpt-4o":        (2.50,  10.00),
    "o1-mini":       (1.10,   4.40),
    "o3-mini":       (1.10,   4.40),
    "o1":           (15.00,  60.00),
    "o3":           (10.00,  40.00),
    "o4-mini":       (1.10,   4.40),
}


def get_model_pricing(model_string: str):
    """Return (input_$/1M, output_$/1M) for the given model string, or None."""
    for key, pricing in MODEL_PRICING.items():
        if key in model_string:
            return pricing
    return None


class TokenUsageTracker:
    """Thread-safe per-run accumulator for LLM token usage."""

    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.prompt_tokens = 0
            self.completion_tokens = 0
            self.total_tokens = 0
            self.num_calls = 0

    def add(self, prompt_tokens: int, completion_tokens: int):
        with self._lock:
            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.total_tokens += prompt_tokens + completion_tokens
            self.num_calls += 1

    def get_totals(self) -> dict:
        with self._lock:
            return {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
                "num_calls": self.num_calls,
            }

    def compute_cost(self, model_string: str):
        """Return total USD cost for accumulated tokens, or None if pricing unknown."""
        pricing = get_model_pricing(model_string)
        if pricing is None:
            return None
        input_per_m, output_per_m = pricing
        with self._lock:
            return (
                self.prompt_tokens * input_per_m
                + self.completion_tokens * output_per_m
            ) / 1_000_000


# Module-level singleton shared across all engine instances
TOKEN_TRACKER = TokenUsageTracker()


def is_jpeg(data):
    jpeg_signature = b'\xFF\xD8\xFF'
    return data.startswith(jpeg_signature)

def is_png(data):
    png_signature = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
    return data.startswith(png_signature)


def get_image_type_from_bytes(data):
    if is_jpeg(data):
        return "jpeg"
    elif is_png(data):
        return "png"
    else:
        raise ValueError("Image type not supported, only jpeg and png supported.")