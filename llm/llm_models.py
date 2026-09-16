import os

import openai
from openai import OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai.api_key)
import backoff
import httpx
import tiktoken
from transformers import AutoTokenizer

# OpenAI SDK defaults to ~600s; local Ollama runs (especially 30B+) often need longer.
# Override with TRANSCHEMA_OLLAMA_HTTP_TIMEOUT (seconds), e.g. 7200.
_OLLAMA_READ_TIMEOUT = float(os.environ.get("TRANSCHEMA_OLLAMA_HTTP_TIMEOUT", "3600"))


def _ollama_base_url():
    # Some clusters (e.g. Sol) bind the Ollama server to the node's real interface
    # per $OLLAMA_HOST rather than loopback, so "localhost" refuses the connection.
    # Honor $OLLAMA_HOST (Ollama's own env var, e.g. "sg238:11434") the same way
    # the ollama CLI does; default to localhost for normal single-machine use.
    host = os.environ.get("OLLAMA_HOST", "localhost:11434").strip()
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    return f"{host.rstrip('/')}/v1"


def _ollama_openai_client():
    return OpenAI(
        base_url=_ollama_base_url(),
        api_key="ollama",
        timeout=httpx.Timeout(
            connect=60.0,
            read=_OLLAMA_READ_TIMEOUT,
            write=120.0,
            pool=60.0,
        ),
    )


# ASU Research Computing hosts open-weight models behind an OpenAI-compatible API.
# The key comes from $OPENSOURCE_API_KEY; the endpoint can be overridden for testing.
_ASU_BASE_URL = os.environ.get("ASU_OPENAI_BASE_URL", "https://openai.rc.asu.edu/v1")

# Model-name substrings routed to the ASU endpoint. The endpoint serves ~50 models;
# add a marker here to route another one.
ASU_MODEL_MARKERS = ("gpt-oss",)

# gpt-oss is a reasoning model: its hidden reasoning is billed against max_tokens, so a
# caller asking for max_tokens=4096 of CODE can get back an empty message when reasoning
# eats the whole budget (observed with reasoning_effort=high: finish_reason=length,
# content=""). This headroom is added on top of the caller's max_tokens so the answer
# keeps the budget the caller intended. Override with TRANSCHEMA_REASONING_HEADROOM.
_REASONING_HEADROOM = int(os.environ.get("TRANSCHEMA_REASONING_HEADROOM", "8192"))

# Optional low|medium|high. Unset = the server's default. Higher effort is slower and
# spends more of the headroom above.
_REASONING_EFFORT = os.environ.get("TRANSCHEMA_REASONING_EFFORT", "").strip().lower() or None


# Microsoft DMX PayGo models, reached through an SSH tunnel to the collaborator's Azure VM,
# where a small proxy adds the Azure token (see dmx_proxy.py on the VM). Select them with a
# "dmx-" prefix, e.g. --model dmx-deepseek-v4-flash; the prefix is stripped before sending.
# The prefix keeps dmx-gpt-oss-120b from being routed to the ASU endpoint above.
_DMX_BASE_URL = os.environ.get("DMX_OPENAI_BASE_URL", "http://localhost:8000/v1")
DMX_PREFIX = "dmx-"


def is_dmx_model(model):
    return (model or "").lower().startswith(DMX_PREFIX)


def is_asu_model(model):
    ml = (model or "").lower()
    return not is_dmx_model(model) and any(marker in ml for marker in ASU_MODEL_MARKERS)


def gpt_oss_encoding():
    """Tokenizer for gpt-oss. tiktoken.encoding_for_model() raises KeyError for it.
    o200k_harmony is o200k_base plus chat special tokens, so for counting plain prompt
    text o200k_base is identical; use harmony when the installed tiktoken has it."""
    try:
        return tiktoken.get_encoding("o200k_harmony")
    except ValueError:
        return tiktoken.get_encoding("o200k_base")


def dmx_encoding(model):
    """Tokenizer for prompt-length counting with DMX models. DeepSeek-V4 has no tiktoken
    entry; the DeepSeek-V3 tokenizer is used as a close approximation."""
    if "gpt-oss" in model.lower():
        return gpt_oss_encoding()
    return AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3")


def _dmx_openai_client():
    return OpenAI(
        base_url=_DMX_BASE_URL,
        api_key="unused",  # the proxy on the VM adds the real Azure token
        timeout=httpx.Timeout(connect=60.0, read=_OLLAMA_READ_TIMEOUT, write=120.0, pool=60.0),
    )


def _asu_openai_client():
    api_key = os.environ.get("OPENSOURCE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENSOURCE_API_KEY is not set, so the ASU open-source model endpoint cannot be "
            "used. Export it before running. Note that the stock ~/.bashrc returns early for "
            "non-interactive shells, so an export placed below that guard is invisible to "
            "scripts launched via nohup/sbatch/bash -c."
        )
    return OpenAI(
        base_url=_ASU_BASE_URL,
        api_key=api_key,
        timeout=httpx.Timeout(connect=60.0, read=_OLLAMA_READ_TIMEOUT, write=120.0, pool=60.0),
    )


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
            "o4-mini": (0.0044, 0.0011),  # $4.40/1M output, $1.10/1M input
            "o3": (0.060, 0.010),          # $60/1M output, $10/1M input
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

        ml = model.lower()
        self._is_thinking_model = False
        self._is_reasoning_model = False
        if "qwen2.5" in ml:
            self.client = _ollama_openai_client()
            if "32b" in ml:
                self.encoding = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-32B-Instruct")
            else:
                self.encoding = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
        elif "qwen3" in ml:
            self.client = _ollama_openai_client()
            self._is_thinking_model = True
            if "32b" in ml or "30b" in ml:
                self.encoding = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")
            else:
                self.encoding = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
        elif "deepseek-r1" in ml:
            self.client = _ollama_openai_client()
            self._is_thinking_model = True
            # DeepSeek-R1 uses the same tokenizer as DeepSeek-V3
            self.encoding = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3")
        elif "mixtral" in ml:
            self.client = _ollama_openai_client()
            # Mixtral uses the Mistral tokenizer
            self.encoding = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
        elif is_dmx_model(model):
            self.client = _dmx_openai_client()
            self._is_reasoning_model = True
            self.encoding = dmx_encoding(model)
        elif is_asu_model(model):
            self.client = _asu_openai_client()
            self._is_reasoning_model = True
            self.encoding = gpt_oss_encoding()
        else:
            self.client = openai.OpenAI(api_key=openai.api_key)
            if model == "gpt-4.1-mini":
                # According to https://github.com/openai/tiktoken/issues/395
                self.encoding = tiktoken.get_encoding("o200k_base")
            elif model == "o4-mini" or model == "o3":
                self.encoding = tiktoken.get_encoding("cl100k_base")
            else:
                self.encoding = tiktoken.encoding_for_model(model)

        _base = str(getattr(self.client, "base_url", "") or "")
        self._uses_ollama = "11434" in _base or "ollama" in _base.lower()
        self._uses_asu = is_asu_model(model)
        self._uses_dmx = is_dmx_model(model)

    def __repr__(self):
        return f"LLMClient(model={self.model}, tracker={self.tracker})"

    def __str__(self):
        return f"LLMClient(model={self.model}, tracker={self.tracker})"

    def calculate_token_length(self, text):
        return len(self.encoding.encode(text))

    def chatgpt(self, messages, temperature=None, max_tokens=4096, n=1, stop=None):
        """Sends chat requests to the model and returns the responses."""
        if temperature is None:
            # o3/o4-mini only accept temperature=1.0, hence the name check. gpt-oss must NOT
            # fall into that branch: replaying the same code-gen prompt, temperature 1.0 gave
            # a compilable script 1/3 times (prose spliced into code, runaway reasoning to the
            # token cap) vs 3/3 at 0.0, which was also ~2x faster.
            temperature = 0.0 if ("4.1" in self.model or self._uses_asu or self._uses_dmx) else 1.0
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
        # Output tokens of an in-flight request are allowed to exceed (can't stop mid-generation).
        if self.cost_budget > 0.0:
            current_cost = self.tracker.cost_summary()["total_cost"]
            if current_cost >= self.cost_budget:
                raise CostBudgetExceeded(
                    f"Cost budget ${self.cost_budget:.4f} reached "
                    f"(accumulated=${current_cost:.6f}) — request blocked."
                )

        if self._uses_ollama:
            combined = "\n".join(
                str(m.get("content", "")) for m in messages if isinstance(m, dict)
            )
            try:
                est_tokens = self.calculate_token_length(combined) if combined else 0
            except Exception:
                est_tokens = -1
            self.logger.info(
                "Ollama: sending chat.completions to %s model=%r "
                "prompt_chars=%s est_tokens=%s max_tokens=%s temp=%s (waiting on server…)",
                getattr(self.client, "base_url", "?"),
                self.model,
                len(combined),
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

            if self._uses_dmx:
                # Azure's v1 API takes max_completion_tokens; the budget includes reasoning.
                kwargs = dict(
                    model=self.model[len(DMX_PREFIX):],
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens + _REASONING_HEADROOM,
                )
                if stop is not None:
                    kwargs["stop"] = stop
                if _REASONING_EFFORT:
                    kwargs["reasoning_effort"] = _REASONING_EFFORT
                return self.client.chat.completions.create(**kwargs)

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
                kwargs = dict(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    # max_completion_tokens=max_tokens,
                    stop=stop,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )
                if self._is_reasoning_model:
                    kwargs["max_tokens"] = max_tokens + _REASONING_HEADROOM
                    if _REASONING_EFFORT:
                        kwargs["reasoning_effort"] = _REASONING_EFFORT
                if self._is_thinking_model:
                    # Ollama-specific: skip the reasoning/"thinking" pass so the
                    # full max_tokens budget goes to the actual code response
                    # instead of being consumed by hidden reasoning tokens.
                    kwargs["extra_body"] = {"think": False}
                return self.client.chat.completions.create(**kwargs)

        response = _request_with_backoff()

        if self._uses_ollama:
            text = response.choices[0].message.content or "" if response.choices else ""
            usage = getattr(response, "usage", None)
            self.logger.info(
                "Ollama: reply received model=%r response_chars=%s "
                "usage_prompt_tokens=%s usage_completion_tokens=%s",
                self.model,
                len(text),
                getattr(usage, "prompt_tokens", None) if usage else None,
                getattr(usage, "completion_tokens", None) if usage else None,
            )

        if (self._uses_asu or self._uses_dmx) and response.choices:
            choice = response.choices[0]
            if choice.finish_reason == "length" and not (choice.message.content or "").strip():
                self.logger.warning(
                    "%s hit its token cap during reasoning and returned no content "
                    "(completion_tokens=%s). Raise TRANSCHEMA_REASONING_HEADROOM or lower "
                    "TRANSCHEMA_REASONING_EFFORT.",
                    self.model,
                    getattr(response.usage, "completion_tokens", None) if response.usage else None,
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
