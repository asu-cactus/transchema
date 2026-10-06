"""Drive an Azure OpenAI deployment past its token rate limit and record where the 429s start.

Run on the Azure machine with the same three constants as azure_relay.py / gpt_51_61sol.py.
Calls are sequential and every response's quota headers are printed as they come back, so the
remaining counts show the limit being used up. The run stops at the first 429, or at --max_calls.

    python3 azure_rate_stress.py gpt-5.1
    python3 azure_rate_stress.py gpt-5.1 --prompt_tokens 4000
    python3 azure_rate_stress.py gpt-5.1 --max_completion_tokens 20000   # test up-front reservation

The requests limit is 100 per minute, so tiny prompts hit the requests limit first. Use a prompt
large enough that the tokens limit is reached before the requests limit.

Note: this uses real quota. If the deployment is shared, other users get 429s while it runs,
so agree the run with whoever manages the endpoint first.
"""

import argparse
import time

from azure.identity import AzureCliCredential, get_bearer_token_provider
from openai import AzureOpenAI, RateLimitError

API_VERSION = ""      # same as azure_relay.py / gpt_51_61sol.py
TOKEN_SCOPE = ""
AZURE_ENDPOINT = ""


def build_client() -> AzureOpenAI:
    token_provider = get_bearer_token_provider(AzureCliCredential(), TOKEN_SCOPE)
    return AzureOpenAI(api_version=API_VERSION, azure_endpoint=AZURE_ENDPOINT,
                       azure_ad_token_provider=token_provider)


def quota(headers) -> str:
    h = headers
    return (f"tokens {h.get('x-ratelimit-remaining-tokens')}/{h.get('x-ratelimit-limit-tokens')} "
            f"requests {h.get('x-ratelimit-remaining-requests')}/{h.get('x-ratelimit-limit-requests')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--prompt_tokens", type=int, default=1000, help="approximate prompt size")
    ap.add_argument("--max_completion_tokens", type=int, default=16,
                    help="output cap per call; raise it to test whether the cap is reserved against the quota")
    ap.add_argument("--rps", type=float, default=0, help="max calls per second; 0 = no pause between calls")
    ap.add_argument("--max_calls", type=int, default=2000, help="safety cap on calls")
    args = ap.parse_args()

    client = build_client()
    prompt = "word " * args.prompt_tokens
    print(f"model={args.model} prompt~{args.prompt_tokens} tokens max_completion={args.max_completion_tokens} "
          f"rps={args.rps or 'unlimited'} max_calls={args.max_calls}", flush=True)

    for call in range(1, args.max_calls + 1):
        started = time.time()
        try:
            raw = client.chat.completions.with_raw_response.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=args.max_completion_tokens,
            )
            print(f"{time.strftime('%H:%M:%S')} call {call:4d} 200 | {quota(raw.headers)}", flush=True)
        except RateLimitError as exc:
            retry = exc.response.headers.get("retry-after", "?")
            print(f"{time.strftime('%H:%M:%S')} call {call:4d} 429 retry-after={retry} | "
                  f"{quota(exc.response.headers)}", flush=True)
            print(f"first 429 at call {call}", flush=True)
            return
        except Exception as exc:
            print(f"call {call} error: {type(exc).__name__}: {str(exc)[:160]}", flush=True)
            return
        if args.rps:
            time.sleep(max(0.0, 1.0 / args.rps - (time.time() - started)))

    print(f"stopped: reached max_calls={args.max_calls} without a 429", flush=True)


if __name__ == "__main__":
    main()
