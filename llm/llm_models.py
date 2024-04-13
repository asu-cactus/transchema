import os

import openai
from openai import OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai.api_key)

import backoff
import tiktoken


class TokenUsageTracker:
    """A class to track and calculate the token usage and cost for different OpenAI models."""

    def __init__(self):
        self.usage = {}

    def add_usage(self, model, completion, prompt):
        """Adds token usage to the tracker for a specific model."""
        if model not in self.usage:
            self.usage[model] = {'completion_tokens': 0, 'prompt_tokens': 0}
        self.usage[model]['completion_tokens'] += completion
        self.usage[model]['prompt_tokens'] += prompt

    def _calculate_cost(self, model):
        """Calculates the cost based on the model and its token usage."""
        rate = {
            #"gpt-4-1106-preview": (0.06, 0.03),
            "gpt-3.5-turbo-0125": (0.0015, 0.0005), #gpt-3.5-turbo-16k
            #"gpt-4-0125-preview": (0.06, 0.03),
            "gpt-4-turbo": (0.03, 0.01), # This model supports at most 4096 completion tokens,
        }.get(model, (0, 0))

        model_usage = self.usage.get(model, {'completion_tokens': 0, 'prompt_tokens': 0})
        completion_cost = model_usage['completion_tokens'] / 1000 * rate[0]
        prompt_cost = model_usage['prompt_tokens'] / 1000 * rate[1]
        return {
            "completion_tokens": model_usage['completion_tokens'],
            "prompt_tokens": model_usage['prompt_tokens'],
            "cost": completion_cost + prompt_cost
        }

    def cost_summary(self):
        """Provides a summary of total usage and cost for all tracked models."""
        total_cost = 0
        detailed_summary = {}
        for model, usage in self.usage.items():
            model_cost = self._calculate_cost(model)
            total_cost += model_cost['cost']
            detailed_summary[model] = model_cost
        return {
            "total_cost": total_cost,
            "detailed_cost": detailed_summary
        }


class LLMClient:
    """A client class for interacting with different GPT models and tracking usage."""

    def __init__(self, model, tracker, logger):
        """Initializes the client with a specified model and a usage tracker."""
        self.client = openai.OpenAI(api_key=openai.api_key)
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        self.tracker = tracker
        self.logger = logger

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
        self.logger.warning("Backing off {wait:0.1f} seconds after {tries} tries "
                            "calling function {target} with args {args} and kwargs "
                            "{kwargs}".format(**details))

    def _success_handler(self, details):
        self.logger.info(f"Success after {details['tries']} tries")

    def _giveup_handler(self, details):
        self.logger.error("Giving up on request")

    def _request_completion(self, messages, temperature, max_tokens, stop):
        @backoff.on_exception(backoff.expo,
                              openai._exceptions.OpenAIError,
                              max_tries=5,
                              on_backoff=lambda details: self._backoff_handler(details),
                              on_success=lambda details: self._success_handler(details),
                              on_giveup=lambda details: self._giveup_handler(details))
        def _request_with_backoff():
            return self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature,
                max_tokens=max_tokens, stop=stop, top_p=1, frequency_penalty=0.0, presence_penalty=0.0
            )

        response = _request_with_backoff()
        self.tracker.add_usage(self.model, response.usage.completion_tokens, response.usage.prompt_tokens)
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
        stop=stop
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
        stop=stop
    )
    return response.choices[0].message.content
