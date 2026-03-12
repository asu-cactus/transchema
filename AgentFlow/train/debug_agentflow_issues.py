#!/usr/bin/env python3
"""
Debug common AgentFlow rollout failures:
1) OpenAI-compatible endpoint connectivity/auth/path issues.
2) Tool availability mismatch issues (prompt asks for tools not enabled).

Usage examples:
  python train/debug_agentflow_issues.py
  python train/debug_agentflow_issues.py --config train/datamorpherconfig.yaml
  python train/debug_agentflow_issues.py --log-file /path/to/transcript.jsonl
  python train/debug_agentflow_issues.py --chat-test
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import socket
import sys
from pathlib import Path
from typing import Any
from urllib import error, request

try:
    import yaml  # type: ignore[import-not-found,reportMissingModuleSource]
except ImportError:
    yaml = None


DEFAULT_CONFIG = "train/datamorpherconfig.yaml"
DEFAULT_URL_FILE = "/tmp/agentflow_vllm_url.txt"
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
TIMEOUT_S = 4


def _ok(msg: str) -> None:
    print(f"[OK]   {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def _section(title: str) -> None:
    print(f"\n=== {title} ===")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    text = path.read_text()
    if yaml is not None:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise RuntimeError(f"Invalid YAML root (expected dict): {path}")
        return data

    # Fallback parser for environments without PyYAML.
    # Extract only what this debugger needs from the "env:" section.
    env: dict[str, Any] = {}
    in_env = False
    base_indent = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if stripped == "env:":
            in_env = True
            base_indent = indent
            continue

        if in_env:
            if indent <= (base_indent or 0):
                in_env = False
                base_indent = None
                # Continue parsing this line in outer context.
            else:
                if ":" not in stripped:
                    continue
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith("#") or value == "":
                    env[key] = ""
                    continue
                if "#" in value:
                    value = value.split("#", 1)[0].rstrip()
                parsed = _safe_py_literal(value)
                if parsed is not None:
                    env[key] = parsed
                else:
                    env[key] = value.strip("'\"")
                continue

    return {"env": env}


def _safe_json_loads(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def _safe_py_literal(text: str) -> Any | None:
    try:
        return ast.literal_eval(text)
    except Exception:
        return None


def _extract_url_host_port(url: str) -> tuple[str, int] | None:
    m = re.match(r"^https?://([^/:]+)(?::(\d+))?", url.strip())
    if not m:
        return None
    host = m.group(1)
    port = int(m.group(2) or (443 if url.startswith("https://") else 80))
    return host, port


def _tcp_connect_ok(host: str, port: int, timeout_s: float = TIMEOUT_S) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True, "connected"
    except Exception as exc:
        return False, str(exc)


def _http_get_json(url: str, timeout_s: float = TIMEOUT_S) -> tuple[bool, int | None, Any | str]:
    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout_s) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
            parsed = _safe_json_loads(payload)
            return True, resp.status, parsed if parsed is not None else payload
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        parsed = _safe_json_loads(body)
        return False, exc.code, parsed if parsed is not None else body
    except Exception as exc:
        return False, None, str(exc)


def _http_post_json(
    url: str,
    payload: dict[str, Any],
    api_key: str | None = None,
    timeout_s: float = TIMEOUT_S,
) -> tuple[bool, int | None, Any | str]:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = request.Request(url, method="POST", data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            parsed = _safe_json_loads(body)
            return True, resp.status, parsed if parsed is not None else body
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        parsed = _safe_json_loads(body)
        return False, exc.code, parsed if parsed is not None else body
    except Exception as exc:
        return False, None, str(exc)


def _read_url_file(path: str) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    text = p.read_text().strip()
    return text or None


def _normalize_base_candidates(raw_base: str) -> list[str]:
    raw_base = raw_base.rstrip("/")
    candidates = [raw_base]
    if raw_base.endswith("/v1"):
        candidates.append(raw_base[:-3].rstrip("/"))
    else:
        candidates.append(raw_base + "/v1")
    out: list[str] = []
    seen = set()
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def probe_endpoint(base_url: str, run_chat_test: bool, model: str) -> bool:
    _section(f"Endpoint Probe: {base_url}")
    hp = _extract_url_host_port(base_url)
    if hp is None:
        _fail(f"Not a valid http(s) URL: {base_url}")
        return False
    host, port = hp
    tcp_ok, tcp_msg = _tcp_connect_ok(host, port)
    if not tcp_ok:
        _fail(f"TCP connect failed to {host}:{port} ({tcp_msg})")
        return False
    _ok(f"TCP connect succeeded to {host}:{port}")

    any_models_ok = False
    for candidate in _normalize_base_candidates(base_url):
        ok, status, data = _http_get_json(candidate.rstrip("/") + "/models")
        if ok:
            any_models_ok = True
            _ok(f"GET {candidate}/models -> HTTP {status}")
            if isinstance(data, dict) and "data" in data:
                entries = data.get("data") or []
                sample_ids = []
                for item in entries[:5]:
                    if isinstance(item, dict) and "id" in item:
                        sample_ids.append(item["id"])
                if sample_ids:
                    print(f"      models: {sample_ids}")
        else:
            body = data if isinstance(data, str) else json.dumps(data)[:300]
            _warn(f"GET {candidate}/models failed (status={status}) body={body[:200]}")

    if not any_models_ok:
        _fail("No OpenAI-compatible /models endpoint succeeded.")
        return False

    if run_chat_test:
        api_key = os.environ.get("OPENAI_API_KEY") or "dummy"
        chat_payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with: ok"}],
            "max_tokens": 8,
            "temperature": 0.0,
        }
        chat_ok = False
        for candidate in _normalize_base_candidates(base_url):
            url = candidate.rstrip("/") + "/chat/completions"
            ok, status, data = _http_post_json(url, payload=chat_payload, api_key=api_key)
            if ok:
                chat_ok = True
                _ok(f"POST {url} -> HTTP {status}")
                if isinstance(data, dict):
                    choices = data.get("choices", [])
                    if choices and isinstance(choices[0], dict):
                        msg = choices[0].get("message", {})
                        content = msg.get("content") if isinstance(msg, dict) else None
                        if content:
                            print(f"      sample response: {str(content)[:120]}")
                break
            else:
                body = data if isinstance(data, str) else json.dumps(data)[:300]
                _warn(f"POST {url} failed (status={status}) body={body[:200]}")
        if not chat_ok:
            _fail("Chat completion test failed on all candidate base URLs.")
            return False

    return True


def analyze_tool_mismatch(log_file: Path, enabled_tools: list[str]) -> bool:
    _section("Tool Mismatch Analysis")
    if not log_file.exists():
        _warn(f"Log/transcript file not found: {log_file}")
        return False

    text = log_file.read_text(errors="replace")
    has_no_matched_tool = "No matched tool given:" in text
    requested_tools = set(re.findall(r"No matched tool given:\s*([A-Za-z0-9_]+)", text))
    requested_tools = {t for t in requested_tools if t.endswith("_Tool")}

    available_in_prompt: list[str] = []
    for m in re.finditer(r"Available Tools.*?:\s*(\[[^\]]*\])", text):
        parsed = _safe_py_literal(m.group(1))
        if isinstance(parsed, list):
            for t in parsed:
                if isinstance(t, str):
                    available_in_prompt.append(t)
    available_in_prompt = sorted(set(available_in_prompt))

    forced_tool_mentions = sorted(
        set(
            re.findall(
                r"Configure_[A-Za-z0-9_]+_Tool|Critique_Pipeline_Tool|Code_Gen_And_Score_Tool",
                text,
            )
        )
    )

    print(f"enabled_tools (config): {enabled_tools}")
    if available_in_prompt:
        print(f"available_tools (prompt/log): {available_in_prompt}")
    if forced_tool_mentions:
        print(f"tool_names_mentioned (prompt/log): {forced_tool_mentions}")

    mismatch = False
    for t in requested_tools:
        if t not in enabled_tools:
            mismatch = True
            _fail(f"Runtime attempted unavailable tool: {t}")

    if has_no_matched_tool and not requested_tools:
        mismatch = True
        _fail("Detected tool lookup failures, but could not parse specific tool names.")

    if available_in_prompt and sorted(enabled_tools) != sorted(available_in_prompt):
        mismatch = True
        _warn("Enabled tools differ from prompt's declared available tools.")

    if not mismatch:
        _ok("No tool-mismatch signature detected in provided log file.")
    else:
        print("      fix: keep prompts constrained to enabled tools only, or enable needed tools.")
    return mismatch


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Debug AgentFlow endpoint connectivity and tool-mismatch issues."
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to YAML config.")
    parser.add_argument(
        "--url-file",
        default=os.environ.get("AGENTFLOW_VLLM_URL_FILE", DEFAULT_URL_FILE),
        help="Path to file containing resolved vLLM/OpenAI-compatible base URL.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("AGENTFLOW_VLLM_BASE_URL", "").strip(),
        help="Explicit base URL to probe (overrides URL file when provided).",
    )
    parser.add_argument(
        "--log-file",
        default="",
        help="Optional transcript/log file to scan for tool mismatch.",
    )
    parser.add_argument(
        "--chat-test",
        action="store_true",
        help="Also run a tiny /chat/completions request.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("BASE_MODEL", DEFAULT_MODEL),
        help="Model id for chat test payload.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    try:
        cfg = _load_yaml(config_path)
    except Exception as exc:
        _fail(str(exc))
        return 2

    env_cfg = cfg.get("env", {}) if isinstance(cfg.get("env"), dict) else {}
    enabled_tools = env_cfg.get("ENABLE_TOOLS", [])
    if not isinstance(enabled_tools, list):
        enabled_tools = [str(enabled_tools)]
    enabled_tools = [str(t) for t in enabled_tools]

    _section("Config Snapshot")
    print(f"config: {config_path}")
    print(f"enabled_tools: {enabled_tools}")
    print(f"model: {args.model}")

    explicit_base = args.base_url.strip()
    file_base = _read_url_file(args.url_file)
    if explicit_base:
        chosen_bases = [explicit_base]
        _ok(f"Using --base-url / AGENTFLOW_VLLM_BASE_URL: {explicit_base}")
    elif file_base:
        chosen_bases = [file_base]
        _ok(f"Using URL from file {args.url_file}: {file_base}")
    else:
        chosen_bases = ["http://127.0.0.1:8888", "http://127.0.0.1:8888/v1"]
        _warn(
            "No explicit base URL or URL file value found. Falling back to localhost defaults."
        )

    endpoint_ok = False
    for base in chosen_bases:
        endpoint_ok = probe_endpoint(base, run_chat_test=args.chat_test, model=args.model) or endpoint_ok

    if not endpoint_ok:
        _fail(
            "Endpoint diagnostics failed. This matches APIConnectionError / Connection refused behavior."
        )
    else:
        _ok("Endpoint diagnostics passed.")

    mismatch_found = False
    if args.log_file:
        mismatch_found = analyze_tool_mismatch(Path(args.log_file), enabled_tools)
    else:
        _section("Tool Mismatch Analysis")
        _warn("Skipped (no --log-file provided).")

    _section("Result")
    if endpoint_ok and not mismatch_found:
        _ok("No blocking issue detected by this debug script.")
        return 0
    if not endpoint_ok and mismatch_found:
        _fail("Detected BOTH endpoint failure and tool mismatch.")
        return 1
    if not endpoint_ok:
        _fail("Detected endpoint/connectivity failure.")
        return 1
    _fail("Detected tool mismatch issue.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
