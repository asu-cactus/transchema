# Reference: https://github.com/zou-group/textgrad/blob/main/textgrad/engine/openai.py

try:
    import vllm
except ImportError:
    raise ImportError("If you'd like to use VLLM models, please install the vllm package by running `pip install vllm`.")

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("If you'd like to use VLLM models, please install the openai package by running `pip install openai`.")

import os
import json
import base64
import platformdirs
from typing import List, Union
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from .base import EngineLM, CachedEngine

class ChatVLLM(EngineLM, CachedEngine):
    DEFAULT_SYSTEM_PROMPT = "You are a helpful, creative, and smart assistant."

    def __init__(
        self,
        model_string="Qwen/Qwen2.5-VL-3B-Instruct",
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        is_multimodal: bool=False,
        use_cache: bool=True,
        base_url=None,
        api_key=None,
        check_model: bool=True,
        max_tokens: int = 1024,
        **kwargs):
        """
        :param model_string:
        :param system_prompt:
        :param is_multimodal:
        """

        self.model_string = model_string
        self.use_cache = use_cache
        self.system_prompt = system_prompt
        self.is_multimodal = is_multimodal
        self.default_max_tokens = max_tokens

        if self.use_cache:
            root = platformdirs.user_cache_dir("agentflow")
            cache_path = os.path.join(root, f"cache_vllm_{self.model_string}.db")
            self.image_cache_dir = os.path.join(root, "image_cache")
            os.makedirs(self.image_cache_dir, exist_ok=True)
            super().__init__(cache_path=cache_path)
        
        self.base_url = base_url or os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
        self.api_key = api_key or os.environ.get("VLLM_API_KEY", "dummy-token")

        try:
            import httpx
            # Set an explicit HTTP timeout so requests never hang indefinitely.
            # connect=10s: fail fast if the server is unreachable.
            # read=300s: give vLLM enough time to generate on Blackwell GPUs
            #   (first request after wake_up can be slow; allow 5 min max).
            _timeout = httpx.Timeout(connect=10.0, read=300.0, write=10.0, pool=10.0)
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=_timeout,
            )
        except Exception as e:
            raise ValueError(f"Failed to connect to VLLM server at {self.base_url}. Please ensure the server is running and try again.")

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _generate_with_retry(self, content: Union[str, List[Union[str, bytes]]], system_prompt=None, **kwargs):
        """Inner call that raises on error so tenacity can retry."""
        if isinstance(content, str):
            return self._generate_text(content, system_prompt=system_prompt, **kwargs)
        elif isinstance(content, list):
            if all(isinstance(item, str) for item in content):
                return self._generate_text("\n".join(content), system_prompt=system_prompt, **kwargs)
            elif any(isinstance(item, bytes) for item in content):
                if not self.is_multimodal:
                    raise NotImplementedError(
                        f"Multimodal generation is only supported for {self.model_string}."
                    )
                return self._generate_multimodal(content, system_prompt=system_prompt, **kwargs)
            else:
                raise ValueError("Unsupported content in list: only str or bytes are allowed.")
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def generate(self, content: Union[str, List[Union[str, bytes]]], system_prompt=None, **kwargs):
        try:
            return self._generate_with_retry(content, system_prompt=system_prompt, **kwargs)
        except Exception as e:
            print(f"[ChatVLLM] generate FAILED after retries: {type(e).__name__}: {e}")
            print(f"[ChatVLLM] base_url={self.base_url}  model={self.model_string}")
            return {
                "error": type(e).__name__,
                "message": str(e),
                "details": getattr(e, 'args', None)
            }
        
    def _generate_text(
        self, prompt, system_prompt=None, max_tokens=None, top_p=0.99, response_format=None, **kwargs
    ):
        if max_tokens is None:
            max_tokens = self.default_max_tokens

        sys_prompt_arg = system_prompt if system_prompt else self.system_prompt

        if self.use_cache:
            cache_key = sys_prompt_arg + prompt
            cache_or_none = self._check_cache(cache_key)
            if cache_or_none is not None:
                return cache_or_none
        

        # Chat models without structured outputs
        response = self.client.chat.completions.create(
            model=self.model_string,
            messages=[
                {"role": "system", "content": sys_prompt_arg},
                {"role": "user", "content": prompt},
            ],
            frequency_penalty=kwargs.get("frequency_penalty", 1.2),
            presence_penalty=0,
            stop=None,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=max_tokens,
            top_p=top_p,
        )
        response = response.choices[0].message.content

        if self.use_cache:
            self._save_cache(cache_key, response)
        return response

    def __call__(self, prompt, **kwargs):
        return self.generate(prompt, **kwargs)

    def _format_content(self, content: List[Union[str, bytes]]) -> List[dict]:
        formatted_content = []
        for item in content:
            if isinstance(item, bytes):
                base64_image = base64.b64encode(item).decode('utf-8')
                formatted_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
            elif isinstance(item, str):
                formatted_content.append({
                    "type": "text",
                    "text": item
                })
            else:
                raise ValueError(f"Unsupported input type: {type(item)}")
        return formatted_content

    def _generate_multimodal(
        self, content: List[Union[str, bytes]], system_prompt=None, temperature=0, max_tokens=None, top_p=0.99, response_format=None
    ):
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        sys_prompt_arg = system_prompt if system_prompt else self.system_prompt
        formatted_content = self._format_content(content)

        if self.use_cache:
            cache_key = sys_prompt_arg + json.dumps(formatted_content)
            cache_or_none = self._check_cache(cache_key)
            if cache_or_none is not None:
                return cache_or_none


        response = self.client.chat.completions.create(
            model=self.model_string,
            messages=[
                {"role": "system", "content": sys_prompt_arg},
                {"role": "user", "content": formatted_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        response_text = response.choices[0].message.content

        if self.use_cache:
            self._save_cache(cache_key, response_text)
        return response_text
