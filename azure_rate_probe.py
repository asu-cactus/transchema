"""Probe the rate limits of an Azure OpenAI deployment.

Run on the Azure machine (same az login and the same three constants as azure_relay.py /
gpt_51_61sol.py). It calls the deployment directly, not through the relay, because the relay
drops the x-ratelimit-* and retry-after response headers.

    python3 azure_rate_probe.py gpt-5.1
    python3 azure_rate_probe.py gpt-6.1-sol --max_concurrency 8 --rounds 3

Step 1: one call, print every rate-limit related header (names vary by API version, so all
        headers containing "ratelimit", "rate-limit" or "retry" are printed).
Step 2: bursts at increasing concurrency with a prompt of about PROMPT_TOKENS tokens. Each burst
        reports how many calls returned 200, how many 429, and the remaining-token/request
        headers from the last success. The first concurrency level that produces 429s marks the
        ceiling for that prompt size.

Keep the probe short: it uses real quota and will slow any run that shares the deployment.
"""

import argparse
import concurrent.futures as cf
import time

from azure.identity import AzureCliCredential, get_bearer_token_provider
from openai import AzureOpenAI, RateLimitError

API_VERSION = ""      # same as azure_relay.py / gpt_51_61sol.py
TOKEN_SCOPE = ""
AZURE_ENDPOINT = ""
PROMPT_TOKENS = 1000  # approximate prompt size per call; the prompt is repeated words


def build_client() -> AzureOpenAI:
    token_provider = get_bearer_token_provider(AzureCliCredential(), TOKEN_SCOPE)
    return AzureOpenAI(api_version=API_VERSION, azure_endpoint=AZURE_ENDPOINT,
                       azure_ad_token_provider=token_provider)


def rate_headers(headers) -> dict:
    keys = ("ratelimit", "rate-limit", "retry")
    return {k: v for k, v in headers.items() if any(s in k.lower() for s in keys)}


def one_call(client, model, prompt):
    """Return (status, headers) where status is 200, 429 or an error string."""
    try:
        raw = client.chat.completions.with_raw_response.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=16,
        )
        return 200, rate_headers(raw.headers)
    except RateLimitError as exc:
        return 429, rate_headers(exc.response.headers)
    except Exception as exc:  # keep probing on any other failure, but report it
        return f"error: {type(exc).__name__}: {str(exc)[:120]}", {}


def burst(client, model, prompt, concurrency):
    with cf.ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(lambda _: one_call(client, model, prompt), range(concurrency)))
    ok = [h for s, h in results if s == 200]
    n429 = sum(1 for s, _ in results if s == 429)
    other = [s for s, _ in results if isinstance(s, str)]
    last_headers = ok[-1] if ok else (results[-1][1] if results else {})
    return len(ok), n429, other, last_headers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--max_concurrency", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=2, help="bursts per concurrency level")
    ap.add_argument("--prompt_tokens", type=int, default=PROMPT_TOKENS)
    args = ap.parse_args()

    client = build_client()
    prompt = "word " * args.prompt_tokens

    print(f"== {args.model}: single call, rate-limit headers")
    status, headers = one_call(client, args.model, prompt)
    print(f"status={status}")
    for k in sorted(headers):
        print(f"  {k}: {headers[k]}")
    if not headers:
        print("  (no rate-limit headers returned -- check the API version)")

    print(f"\n== bursts, prompt ~{args.prompt_tokens} tokens")
    concurrency = 1
    while concurrency <= args.max_concurrency:
        for r in range(args.rounds):
            ok, n429, other, last = burst(client, args.model, prompt, concurrency)
            remaining_tok = last.get("x-ratelimit-remaining-tokens", "?")
            remaining_req = last.get("x-ratelimit-remaining-requests", "?")
            print(f"concurrency={concurrency} round={r + 1}: 200={ok} 429={n429} "
                  f"other={other or '-'} remaining_tokens={remaining_tok} "
                  f"remaining_requests={remaining_req}")
            time.sleep(2)
        concurrency *= 2


if __name__ == "__main__":
    main()
