from src.llm.config import MODELS
from openai import OpenAI
import os
import json
import logging
import time
import httpx
from datetime import datetime
from contextvars import ContextVar

current_case = ContextVar('current_case', default=None)

# OpenAI SDK defaults to ~600s; local Ollama runs (e.g. qwen3:32b on Sol) often
# need longer. Override with TRANSCHEMA_OLLAMA_HTTP_TIMEOUT (seconds).
_OLLAMA_READ_TIMEOUT = float(os.environ.get("TRANSCHEMA_OLLAMA_HTTP_TIMEOUT", "3600"))

class LLMClient:
    def __init__(self, model_name, log_tag=None):
        # log_tag lets concurrent processes (e.g. one per benchmark length,
        # via run_length*.sh) write to separate logs/llm_queries_* files
        # instead of racing on the same shared one. None preserves the
        # original shared-file behavior for any other caller.
        self.model_name = model_name
        self.log_tag = log_tag
        self.config = MODELS[model_name]
        api_key = self.config['api_key'] or os.environ.get("OPENAI_API_KEY", "")
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.config['base_url'],
            timeout=httpx.Timeout(connect=60.0, read=_OLLAMA_READ_TIMEOUT, write=120.0, pool=60.0),
        )
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        self._setup_logger()

    def _setup_logger(self):
        os.makedirs("logs", exist_ok=True)
        suffix = f"_{self.log_tag}" if self.log_tag else ""
        logger_name = f"llm_{self.model_name}{suffix}"
        self.llm_logger = logging.getLogger(logger_name)
        if not self.llm_logger.handlers:
            handler = logging.FileHandler(f"logs/llm_queries_{self.model_name}{suffix}.jsonl")
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.llm_logger.addHandler(handler)
            self.llm_logger.setLevel(logging.INFO)

    def generate_response(self, prompt, n=1):
        start_time = time.time()
        try:
            generate_params = {
                "model": self.config['model'],
                "messages": [{"role": "user", "content": prompt}],
                "n": n
            }
            # OpenAI's o-series reasoning models reject any non-default
            # temperature/top_p ("Unsupported value: 'temperature' does not
            # support 0.1..."), so those set supports_temperature=False.
            # Ollama-served models (e.g. qwen3:32b) support both normally.
            if self.config.get('supports_temperature', True):
                generate_params["top_p"] = self.config.get('top_p', 0.8)
                generate_params["temperature"] = self.config.get('temperature', 0.7)
            # Qwen3 via Ollama is a "thinking" model - suppress hidden reasoning
            # tokens the same way MMTU/mcts_search.py do, via Ollama's extra param.
            if self.config.get('thinking_model'):
                generate_params["extra_body"] = {"think": False}
            completion = self.client.chat.completions.create(**generate_params)
            end_time = time.time()
            latency = end_time - start_time

            self.token_usage["prompt_tokens"] += completion.usage.prompt_tokens
            self.token_usage["completion_tokens"] += completion.usage.completion_tokens
            self.token_usage["total_tokens"] += completion.usage.total_tokens

            results = []
            for choice in completion.choices:
                result = {
                    "content": "",
                    "reasoning_content": ""
                }
                if self.config.get('is_inference', True):
                    result["content"] = choice.message.content
                    result["reasoning_content"] = getattr(choice.message, "reasoning_content", "")
                else:
                    result["content"] = choice.message.content
                results.append(result)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "case_id": current_case.get(),
                "model": self.config['model'],
                "prompt": prompt,
                "responses": results,
                "tokens": {
                    "prompt": completion.usage.prompt_tokens,
                    "completion": completion.usage.completion_tokens,
                    "total": completion.usage.total_tokens
                },
                "latency_seconds": latency,
                "error": False
            }
            self.llm_logger.info(json.dumps(log_entry, ensure_ascii=False))
            return results, False
        except Exception as e:
            end_time = time.time()
            latency = end_time - start_time
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "case_id": current_case.get(),
                "model": self.config['model'],
                "prompt": prompt,
                "responses": None,
                "tokens": None,
                "latency_seconds": latency,
                "error": True,
                "error_message": str(e)
            }
            self.llm_logger.info(json.dumps(log_entry, ensure_ascii=False))
            return [str(e)], True
        
    def reset_token_usage(self):
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
if __name__ == "__main__":
    llm = LLMClient("qwen")
    response, error = llm.generate_response("hello")
    print(response)