import os

qwen_api = ""
openai_api = os.environ.get("OPENAI_API_KEY", "")

MODELS = {
    'gpt-4.1-mini': {
        'api_key': openai_api,
        'base_url': "https://api.openai.com/v1",
        'model': "gpt-4.1-mini",
        'is_inference': False,
        'top_p': 0.8,
        'temperature': 0
    },
    'o4-mini': {
        'api_key': openai_api,
        'base_url': "https://api.openai.com/v1",
        'model': "o4-mini",
        'is_inference': True,
        'top_p': 0.8,
        'temperature': 0.1
    },
    'qwen': {
        'api_key': qwen_api,
        'base_url': "https://dashscope.aliyuncs.com/compatible-mode/v1",
        'model': "qwen2.5-coder-32b-instruct",
        'is_inference': False,
        'top_p': 0.8,
        'temperature': 0.1    
    },
    'qwen_7B': {
        'api_key': qwen_api,
        'base_url': "https://dashscope.aliyuncs.com/compatible-mode/v1",
        'model': "qwen2.5-coder-7b-instruct",
        'is_inference': False,
        'top_p': 0.8,
        'temperature': 0.1    
    },
    'qwen_14B': {
        'api_key': qwen_api,
        'base_url': "https://dashscope.aliyuncs.com/compatible-mode/v1",
        'model': "qwen2.5-coder-14b-instruct",
        'is_inference': False,
        'top_p': 0.8,
        'temperature': 0.1    
    }
}
# Ollama local OSS model entries
ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODELS['qwen3:32b'] = {
    'api_key': 'ollama',
    'base_url': ollama_base_url,
    'model': 'qwen3:32b',
    'is_inference': False,
    'top_p': 0.8,
    'temperature': 0
}

# Microsoft DMX models via the SSH tunnel to the Azure VM proxy (same convention as
# llm/llm_models.py: "dmx-" prefix picks the route, stripped before sending; the proxy adds
# the Azure token, so the key here is a placeholder). Proxy verified to accept top_p and n>1.
dmx_base_url = os.environ.get("DMX_OPENAI_BASE_URL", "http://localhost:8000/v1")
MODELS['dmx-gpt-oss-120b'] = {
    'api_key': 'unused',
    'base_url': dmx_base_url,
    'model': 'gpt-oss-120b',
    'is_inference': False,
    'top_p': 0.8,
    'temperature': 0
}

for _m in ("deepseek-v4-flash", "deepseek-v4-pro"):
    MODELS[f"dmx-{_m}"] = {
        'api_key': 'unused',
        'base_url': dmx_base_url,
        'model': _m,
        'is_inference': False,
        'top_p': 0.8,
        'temperature': 0
    }
