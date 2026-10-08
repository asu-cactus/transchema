"""Approximate USD cost per LLM call, from token usage.

Prices are USD per 1K tokens, as (prompt_rate, completion_rate). Same figures used
in llm/llm_models.py's TokenUsageTracker (duplicated here rather than imported, to
keep this file dependency-free — llm_models.py pulls in tiktoken/transformers/etc.
just for this dict). Reference: https://platform.openai.com/docs/pricing — update
both places if OpenAI changes pricing.
"""

PRICE_PER_1K_TOKENS = {
    "gpt-4-1106-preview": (0.01, 0.03),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-3.5-turbo-0125": (0.0005, 0.0015),
    "gpt-4.1-mini": (0.0004, 0.0016),
    "o4-mini": (0.0011, 0.0044),
    "o3": (0.010, 0.060),
}


def estimate_cost(model, usage):
    """usage: dict with prompt_tokens/completion_tokens (as returned by
    gpt.chat_with_gpt(..., return_usage=True)). Returns None if the model isn't
    in the price table or usage is missing, rather than silently reporting $0."""
    if not usage:
        return None
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    if prompt_tokens is None or completion_tokens is None:
        return None
    rates = PRICE_PER_1K_TOKENS.get(model)
    if rates is None:
        return None
    prompt_rate, completion_rate = rates
    return (prompt_tokens / 1000 * prompt_rate) + (completion_tokens / 1000 * completion_rate)
