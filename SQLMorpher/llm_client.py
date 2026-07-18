"""LLM client for SQLMorpher supporting both OpenAI and local Ollama models.

This mirrors the client used in the main Transchema harness
(`../llm/llm_models.py`) so SQLMorpher can run the same open-source models
(Qwen2.5/Qwen3, DeepSeek-R1, Mixtral, etc. via Ollama) with the same
token-usage/cost tracking mechanism, in addition to OpenAI models.
"""

import os

import backoff
import httpx
import openai
import tiktoken
from openai import OpenAI

try:
    from transformers import AutoTokenizer
except ImportError:  # transformers is optional unless an Ollama model is used
    AutoTokenizer = None

openai.api_key = os.getenv("OPENAI_API_KEY", "")

# OpenAI SDK defaults to ~600s; local Ollama runs (especially 30B+) often need longer.
# Override with SQLMORPHER_OLLAMA_HTTP_TIMEOUT (seconds), e.g. 7200.
_OLLAMA_READ_TIMEOUT = float(os.environ.get("SQLMORPHER_OLLAMA_HTTP_TIMEOUT", "3600"))
_OLLAMA_BASE_URL = os.environ.get("SQLMORPHER_OLLAMA_BASE_URL", "http://localhost:11434/v1")

# Models that should be routed to a local Ollama server instead of OpenAI.
_OLLAMA_MODEL_MARKERS = ("qwen2.5", "qwen3", "deepseek-r1", "mixtral", "llama", "codellama")


def _is_ollama_model(model: str) -> bool:
    ml = model.lower()
    return any(marker in ml for marker in _OLLAMA_MODEL_MARKERS)


def _ollama_openai_client():
    return OpenAI(
        base_url=_OLLAMA_BASE_URL,
        api_key="ollama",
        timeout=httpx.Timeout(
            connect=60.0,
            read=_OLLAMA_READ_TIMEOUT,
            write=120.0,
            pool=60.0,
        ),
    )


class TokenUsageTracker:
    """Tracks and calculates token usage/cost for each model used."""

    # Reference: https://platform.openai.com/docs/pricing (per-1K-token, USD)
    _RATES = {
        "gpt-3.5-turbo-0125": (0.0015, 0.0005),
        "gpt-4-turbo": (0.03, 0.01),
        "gpt-4-1106-preview": (0.03, 0.01),
        "gpt-4.1-mini": (0.0016, 0.0004),
    }

    def __init__(self):
        self.usage = {}

    def add_usage(self, model, completion_tokens, prompt_tokens):
        if model not in self.usage:
            self.usage[model] = {"completion_tokens": 0, "prompt_tokens": 0}
        self.usage[model]["completion_tokens"] += completion_tokens
        self.usage[model]["prompt_tokens"] += prompt_tokens

    def _calculate_cost(self, model):
        # Local/Ollama models are free to run, so cost is 0 for them.
        completion_rate, prompt_rate = self._RATES.get(model, (0, 0))
        model_usage = self.usage.get(model, {"completion_tokens": 0, "prompt_tokens": 0})
        completion_cost = model_usage["completion_tokens"] / 1000 * completion_rate
        prompt_cost = model_usage["prompt_tokens"] / 1000 * prompt_rate
        return {
            "completion_tokens": model_usage["completion_tokens"],
            "prompt_tokens": model_usage["prompt_tokens"],
            "cost": completion_cost + prompt_cost,
        }

    def cost_summary(self):
        total_cost = 0
        detailed_summary = {}
        for model in self.usage:
            model_cost = self._calculate_cost(model)
            total_cost += model_cost["cost"]
            detailed_summary[model] = model_cost
        return {"total_cost": total_cost, "detailed_cost": detailed_summary}


# Module-level tracker so all SQLMorpher scripts share one token/cost ledger
# unless a caller creates its own LLMClient with a fresh tracker.
default_tracker = TokenUsageTracker()


class LLMClient:
    """Wraps either an OpenAI or a local Ollama (OpenAI-compatible) model,
    with tokenizer-aware token counting and usage tracking."""

    def __init__(self, model="gpt-4-1106-preview", tracker=None, logger=None):
        self.model = model
        self.tracker = tracker if tracker is not None else default_tracker
        self.logger = logger

        ml = model.lower()
        if _is_ollama_model(model):
            if AutoTokenizer is None:
                raise ImportError(
                    "transformers is required to use Ollama models. "
                    "Install it with `pip install transformers`."
                )
            self.client = _ollama_openai_client()
            if "qwen2.5" in ml:
                hf_name = "Qwen/Qwen2.5-32B-Instruct" if "32b" in ml else "Qwen/Qwen2.5-7B-Instruct"
            elif "qwen3" in ml:
                hf_name = "Qwen/Qwen3-32B" if ("32b" in ml or "30b" in ml) else "Qwen/Qwen3-8B"
            elif "deepseek-r1" in ml:
                hf_name = "deepseek-ai/DeepSeek-V3"
            elif "mixtral" in ml:
                hf_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            else:
                hf_name = model
            self.encoding = AutoTokenizer.from_pretrained(hf_name)
        else:
            self.client = OpenAI(api_key=openai.api_key)
            if model == "gpt-4.1-mini":
                self.encoding = tiktoken.get_encoding("o200k_base")
            elif model in ("o4-mini", "o3"):
                self.encoding = tiktoken.get_encoding("cl100k_base")
            else:
                try:
                    self.encoding = tiktoken.encoding_for_model(model)
                except KeyError:
                    self.encoding = tiktoken.get_encoding("cl100k_base")

        base_url = str(getattr(self.client, "base_url", "") or "")
        self._uses_ollama = "11434" in base_url or "ollama" in base_url.lower()

    def __repr__(self):
        return f"LLMClient(model={self.model})"

    def calculate_token_length(self, text):
        return len(self.encoding.encode(text))

    def _log(self, level, msg, *args):
        if self.logger is not None:
            getattr(self.logger, level)(msg, *args)

    def chat(self, prompt, temperature=0, max_tokens=4096, stop=None):
        """Send a single-turn prompt and return the raw response text."""
        messages = [{"role": "user", "content": prompt}]
        response = self._request_completion(messages, temperature, max_tokens, stop)
        return response.choices[0].message.content

    def _request_completion(self, messages, temperature, max_tokens, stop):
        combined = "\n".join(str(m.get("content", "")) for m in messages)
        try:
            est_tokens = self.calculate_token_length(combined) if combined else 0
        except Exception:
            est_tokens = -1

        if self._uses_ollama:
            self._log(
                "info",
                "Ollama: sending chat.completions to %s model=%r prompt_chars=%s "
                "est_tokens=%s max_tokens=%s temp=%s",
                getattr(self.client, "base_url", "?"),
                self.model,
                len(combined),
                est_tokens,
                max_tokens,
                temperature,
            )

        @backoff.on_exception(
            backoff.expo,
            openai.OpenAIError,
            max_tries=5,
        )
        def _request_with_backoff():
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )

        response = _request_with_backoff()

        completion_tokens = response.usage.completion_tokens if response.usage else 0
        prompt_tokens = response.usage.prompt_tokens if response.usage else est_tokens
        self.tracker.add_usage(self.model, completion_tokens, prompt_tokens)

        if self._uses_ollama:
            self._log(
                "info",
                "Ollama: reply received model=%r usage_prompt_tokens=%s usage_completion_tokens=%s",
                self.model,
                prompt_tokens,
                completion_tokens,
            )

        return response
