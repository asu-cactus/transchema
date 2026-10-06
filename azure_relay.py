"""OpenAI-compatible relay to the Azure OpenAI deployments gpt-5.1 and gpt-6.1-sol.

Run on the Azure machine (inside tmux) so an SSH tunnel can expose it to TreeMorpher the same
way the DMX proxy is exposed:

    python3 azure_relay.py            # listens on 127.0.0.1:8001

Accepts POST /v1/chat/completions with a JSON body; the "model" field selects the deployment
(gpt-5.1 or gpt-6.1-sol). Everything else in the body (messages, max_completion_tokens,
temperature, stop, reasoning_effort) is forwarded unchanged. Streaming is not supported.
GET /v1/models lists the deployments (handy as a health check).

Auth is the same as gpt_51_61sol.py: AzureCliCredential + get_bearer_token_provider, so the
machine's `az login` session is what the relay uses. Fill in the three constants below from
gpt_51_61sol.py before running.
"""

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from azure.identity import AzureCliCredential, get_bearer_token_provider
from openai import AzureOpenAI


API_VERSION = ""
TOKEN_SCOPE = ""
AZURE_ENDPOINT = ""
DEPLOYMENTS = ("gpt-5.1", "gpt-6.1-sol")
HOST = "127.0.0.1"
PORT = 8001


def build_client() -> AzureOpenAI:
    token_provider = get_bearer_token_provider(AzureCliCredential(), TOKEN_SCOPE)
    return AzureOpenAI(
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        azure_ad_token_provider=token_provider,
    )


CLIENT = None


def log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, payload) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            self._send_json(200, {"object": "list",
                                  "data": [{"id": d, "object": "model"} for d in DEPLOYMENTS]})
        else:
            self._send_json(404, {"error": {"message": f"unknown path {self.path}"}})

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/chat/completions":
            self._send_json(404, {"error": {"message": f"unknown path {self.path}"}})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": {"message": f"invalid JSON body: {exc}"}})
            return

        model = body.pop("model", "")
        if model not in DEPLOYMENTS:
            self._send_json(400, {"error": {"message": f"model must be one of {DEPLOYMENTS}, got {model!r}"}})
            return
        if body.get("stream"):
            self._send_json(400, {"error": {"message": "streaming is not supported by this relay"}})
            return

        started = time.time()
        try:
            response = CLIENT.chat.completions.create(model=model, **body)
        except Exception as exc:  # surface upstream errors to the caller instead of dropping the connection
            log(f"{model} upstream error after {time.time() - started:.1f}s: {exc}")
            self._send_json(502, {"error": {"message": f"upstream error: {exc}"}})
            return

        usage = getattr(response, "usage", None)
        log(f"{model} ok in {time.time() - started:.1f}s "
            f"(prompt={getattr(usage, 'prompt_tokens', '?')}, completion={getattr(usage, 'completion_tokens', '?')})")
        self._send_json(200, response.model_dump(mode="json"))

    def log_message(self, fmt, *args):  # route the default access log through our logger
        log(fmt % args)


def main() -> None:
    global CLIENT
    CLIENT = build_client()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    log(f"azure relay listening on {HOST}:{PORT} for {DEPLOYMENTS}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
