import sys
import logging
from llm.llm_models import TokenUsageTracker, LLMClient

# set up a no-op logger so LLMClient is happy
logger = logging.getLogger("query_gpt")
logger.addHandler(logging.NullHandler())


def query_from_file(prompt_path: str, model_name: str = "gpt-4.1-mini") -> str:
    """
    Read the entire prompt from `prompt_path`, send it to the LLM, and return the generated text.
    """
    # 1. Load prompt text
    with open(prompt_path, "r") as f:
        prompt = f.read()

    # 2. Initialize the tracker and client (logger is required)
    token_tracker = TokenUsageTracker()
    llm_client = LLMClient(model=model_name, tracker=token_tracker, logger=logger)

    # 3. Query the model
    response_list = llm_client.gpt(prompt)

    # 4. Return the first element
    return response_list[0]


if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python query_gpt.py /path/to/prompt.txt")
    #     sys.exit(1)

    prompt_file = "few_shot_prompt.txt"  # sys.argv[1]
    reply = query_from_file(prompt_file)
    print("\n=== LLM response ===")
    print(reply)
