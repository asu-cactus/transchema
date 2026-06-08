import os

import backoff
import httpx
import openai
import tiktoken
from openai import OpenAI
from transformers import AutoTokenizer

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai.api_key) if openai.api_key else None

# OpenAI SDK defaults to ~600s; local Ollama runs (especially 30B+) often need longer.
# Override with TRANSCHEMA_OLLAMA_HTTP_TIMEOUT (seconds), e.g. 7200.
_OLLAMA_READ_TIMEOUT = float(os.environ.get("TRANSCHEMA_OLLAMA_HTTP_TIMEOUT", "3600"))


def _ollama_openai_client():
    return OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        timeout=httpx.Timeout(
            connect=60.0,
            read=_OLLAMA_READ_TIMEOUT,
            write=120.0,
            pool=60.0,
        ),
    )


def _console(msg: str) -> None:
    """Stdout progress (MCTS logger is file-only; users watch the terminal)."""
    print(msg, flush=True)


def _load_hf_tokenizer(logger, repo_id: str):
    """Load tokenizer with visible progress; first run may download from the Hub."""
    _console(
        f"[LLMClient] Loading Hugging Face tokenizer {repo_id!r} … "
        "(first run downloads from the Hub; set HF_TOKEN if you see rate limits)"
    )
    logger.info("Loading Hugging Face tokenizer: %s", repo_id)
    tok = AutoTokenizer.from_pretrained(repo_id)
    _console(f"[LLMClient] Tokenizer ready: {repo_id!r}")
    logger.info("Tokenizer ready: %s", repo_id)
    return tok


class CostBudgetExceeded(Exception):
    """Raised before an LLM request when the accumulated cost has already reached the budget."""
    pass


class TokenUsageTracker:
    """A class to track and calculate the token usage and cost for different OpenAI models."""

    def __init__(self):
        self.usage = {}

    def add_usage(self, model, completion, prompt):
        """Adds token usage to the tracker for a specific model."""
        if model not in self.usage:
            self.usage[model] = {"completion_tokens": 0, "prompt_tokens": 0}
        self.usage[model]["completion_tokens"] += completion
        self.usage[model]["prompt_tokens"] += prompt

    def total_tokens(self):
        """Returns the total number of prompt and completion tokens tracked."""
        total = 0
        for usage in self.usage.values():
            total += usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
        return total

    def _calculate_cost(self, model):
        """
        Calculates the cost based on the model and its token usage.
        Reference: https://platform.openai.com/docs/pricing
        """
        rate = {
            # "gpt-4-1106-preview": (0.06, 0.03),
            "gpt-3.5-turbo-0125": (0.0015, 0.0005),  # gpt-3.5-turbo-16k
            # "gpt-4-0125-preview": (0.06, 0.03),
            # gpt-4-turbo supports at most 4096 completion tokens
            "gpt-4-turbo": (0.03, 0.01),
            "gpt-4.1-mini": (0.0016, 0.0004),
        }.get(model, (0, 0))

        model_usage = self.usage.get(
            model, {"completion_tokens": 0, "prompt_tokens": 0}
        )
        completion_cost = model_usage["completion_tokens"] / 1000 * rate[0]
        prompt_cost = model_usage["prompt_tokens"] / 1000 * rate[1]
        return {
            "completion_tokens": model_usage["completion_tokens"],
            "prompt_tokens": model_usage["prompt_tokens"],
            "cost": completion_cost + prompt_cost,
        }

    def cost_summary(self):
        """Provides a summary of total usage and cost for all tracked models."""
        total_cost = 0
        detailed_summary = {}
        for model, usage in self.usage.items():
            model_cost = self._calculate_cost(model)
            total_cost += model_cost["cost"]
            detailed_summary[model] = model_cost
        return {"total_cost": total_cost, "detailed_cost": detailed_summary}


class LLMClient:
    """A client class for interacting with different GPT models and tracking usage."""

    def __init__(self, model, tracker, logger, cost_budget: float = 0.0):
        """Initializes the client with a specified model and a usage tracker."""
        self.model = model
        self.cost_budget = cost_budget
        self.tracker = tracker
        self.logger = logger
        self.logger.info("LLMClient init: model=%r", model)

        if "qwen2.5" in model.lower():
            _console("[LLMClient] Ollama OpenAI-compatible client (localhost:11434)")
            self.client = _ollama_openai_client()
            if "32b" in model.lower():
                self.encoding = _load_hf_tokenizer(logger, "Qwen/Qwen2.5-32B-Instruct")
            else:
                self.encoding = _load_hf_tokenizer(logger, "Qwen/Qwen2.5-7B-Instruct")
        elif "qwen3" in model.lower():
            _console("[LLMClient] Ollama OpenAI-compatible client (localhost:11434)")
            self.client = _ollama_openai_client()
            ml = model.lower()
            if "32b" in ml or "30b" in ml:
                self.encoding = _load_hf_tokenizer(logger, "Qwen/Qwen3-32B")
            else:
                self.encoding = _load_hf_tokenizer(logger, "Qwen/Qwen3-8B")
        elif "deepseek-r1" in model.lower():
            _console("[LLMClient] Ollama OpenAI-compatible client (localhost:11434)")
            self.client = _ollama_openai_client()
            self.encoding = _load_hf_tokenizer(logger, "deepseek-ai/DeepSeek-V3")
        elif "mixtral" in model.lower():
            _console("[LLMClient] Ollama OpenAI-compatible client (localhost:11434)")
            self.client = _ollama_openai_client()
            self.encoding = _load_hf_tokenizer(
                logger, "mistralai/Mixtral-8x7B-Instruct-v0.1"
            )
        else:
            self.client = openai.OpenAI(api_key=openai.api_key)
            if model == "gpt-4.1-mini":
                # According to https://github.com/openai/tiktoken/issues/395
                _console("[LLMClient] tiktoken encoding o200k_base")
                self.encoding = tiktoken.get_encoding("o200k_base")
            elif model == "o4-mini" or model == "o3":
                _console("[LLMClient] tiktoken encoding cl100k_base")
                self.encoding = tiktoken.get_encoding("cl100k_base")
            else:
                _console(f"[LLMClient] tiktoken encoding_for_model({model!r})")
                self.encoding = tiktoken.encoding_for_model(model)

        _base = str(getattr(self.client, "base_url", "") or "")
        self._uses_ollama = "11434" in _base or "ollama" in _base.lower()

    def __repr__(self):
        return f"LLMClient(model={self.model}, tracker={self.tracker})"

    def __str__(self):
        return f"LLMClient(model={self.model}, tracker={self.tracker})"

    def calculate_token_length(self, text):
        return len(self.encoding.encode(text))

    def chatgpt(self, messages, temperature=1.0, max_tokens=4096, n=1, stop=None):
        """Sends chat requests to the model and returns the responses."""
        outputs = []
        while n > 0:
            cnt = min(n, 20)  # Ensure at most 20 requests per batch
            n -= cnt
            for _ in range(cnt):
                res = self._request_completion(messages, temperature, max_tokens, stop)
                outputs.extend([choice.message.content for choice in res.choices])
        return outputs

    def gpt(self, prompt, **kwargs):
        """A convenient method to send a single prompt to the model."""
        return self.chatgpt([{"role": "user", "content": prompt}], **kwargs)

    def _backoff_handler(self, details):
        self.logger.warning(
            "Backing off {wait:0.1f} seconds after {tries} tries "
            "calling function {target} with args {args} and kwargs "
            "{kwargs}".format(**details)
        )

    def _success_handler(self, details):
        self.logger.info(f"Success after {details['tries']} tries")

    def _giveup_handler(self, details):
        self.logger.error("Giving up on request")

    def _request_completion(self, messages, temperature, max_tokens, stop):
        # Pre-call budget check: do not send the request if already over budget.
        if self.cost_budget > 0.0:
            if self._uses_ollama:
                token_budget = int(self.cost_budget / 0.00052 * 1000)
                current_tokens = self.tracker.total_tokens()
                if current_tokens >= token_budget:
                    raise CostBudgetExceeded(
                        f"Token budget {token_budget} reached "
                        f"(accumulated={current_tokens}) — request blocked."
                    )
            else:
                current_cost = self.tracker.cost_summary()["total_cost"]
                if current_cost >= self.cost_budget:
                    raise CostBudgetExceeded(
                        f"Cost budget ${self.cost_budget:.4f} reached "
                        f"(accumulated=${current_cost:.6f}) — request blocked."
                    )

        combined = "\n".join(
            str(m.get("content", "")) for m in messages if isinstance(m, dict)
        )
        prompt_chars = len(combined)
        try:
            est_tokens = self.calculate_token_length(combined) if combined else 0
        except Exception:
            est_tokens = -1

        if self._uses_ollama:
            msg = (
                f"[LLMClient] Ollama request → model={self.model!r} "
                f"prompt_chars={prompt_chars} est_tokens={est_tokens} "
                f"max_tokens={max_tokens} (waiting on server…)"
            )
            _console(msg)
            self.logger.info(
                "Ollama: sending chat.completions to %s model=%r "
                "prompt_chars=%s est_tokens=%s max_tokens=%s temp=%s (waiting on server…)",
                getattr(self.client, "base_url", "?"),
                self.model,
                prompt_chars,
                est_tokens,
                max_tokens,
                temperature,
            )

        @backoff.on_exception(
            backoff.expo,
            openai._exceptions.OpenAIError,
            max_tries=5,
            on_backoff=lambda details: self._backoff_handler(details),
            on_success=lambda details: self._success_handler(details),
            on_giveup=lambda details: self._giveup_handler(details),
        )
        def _request_with_backoff():

            if self.model == "o4-mini" or self.model == "o3":
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                    stop=stop,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )
            else:
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

        if self._uses_ollama:
            text = ""
            if response.choices:
                text = response.choices[0].message.content or ""
            pt = getattr(response, "usage", None)
            pt_in = getattr(pt, "prompt_tokens", None) if pt else None
            pt_out = getattr(pt, "completion_tokens", None) if pt else None
            _console(
                f"[LLMClient] Ollama reply ← model={self.model!r} response_chars={len(text)} "
                f"usage in/out={pt_in}/{pt_out}"
            )
            self.logger.info(
                "Ollama: reply received model=%r response_chars=%s "
                "usage_prompt_tokens=%s usage_completion_tokens=%s",
                self.model,
                len(text),
                pt_in,
                pt_out,
            )

        self.tracker.add_usage(
            self.model,
            response.usage.completion_tokens if response.usage else 0,
            response.usage.prompt_tokens if response.usage else 0,
        )
        return response


def gpt3(prompt_, stop=None):
    # if stop is None:
    #    stop = ["\n"]
    if client is None:
        raise ValueError("OpenAI API key not set. Cannot use GPT-3 model.")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt_}],
        temperature=0,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=stop,
    )
    return response.choices[0].message.content


def gpt4(prompt_, stop=None):
    # if stop is None:
    #    stop = ["\n"]
    if client is None:
        raise ValueError("OpenAI API key not set. Cannot use GPT-4 model.")
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",  # "gpt-4",
        messages=[{"role": "user", "content": prompt_}],
        temperature=0,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=stop,
    )
    return response.choices[0].message.content
