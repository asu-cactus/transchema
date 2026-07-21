from src.llm.config import MODELS
from openai import OpenAI
import os
import json
import logging
import time
from datetime import datetime
from contextvars import ContextVar

current_case = ContextVar('current_case', default=None)

class LLMClient:
    def __init__(self, model_name):
        self.model_name = model_name
        self.config = MODELS[model_name]
        api_key = self.config['api_key'] or os.environ.get("OPENAI_API_KEY", "")
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.config['base_url'],
        )
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        self._setup_logger()

    def _setup_logger(self):
        os.makedirs("logs", exist_ok=True)
        self.llm_logger = logging.getLogger(f"llm_{self.model_name}")
        if not self.llm_logger.handlers:
            handler = logging.FileHandler(f"logs/llm_queries_{self.model_name}.jsonl")
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.llm_logger.addHandler(handler)
            self.llm_logger.setLevel(logging.INFO)

    def generate_response(self, prompt, n=1):
        start_time = time.time()
        try:
            generate_params = {
                "model": self.config['model'],
                "messages": [{"role": "user", "content": prompt}],
                "top_p": self.config.get('top_p', 0.8),
                "temperature": self.config.get('temperature', 0.7),
                "n": n
            }
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