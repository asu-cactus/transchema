import ast
import json
import time
import gymnasium as gym
import requests
from bs4 import BeautifulSoup
from react.schema_trans_tools import SchemaTransformTools


# import wikipedia

def clean_str(p):
    try:
        return p.encode().decode("unicode-escape").encode("latin1").decode("utf-8")
    except UnicodeDecodeError:
        return p


class textSpace(gym.spaces.Space):
    def contains(self, x) -> bool:
        """Return boolean specifying if x is a valid member of this space."""
        return isinstance(x, str)


class ToolEnv(gym.Env):

    def __init__(self, source_schema, target_schema, source_examples, target_examples, llm_agent):
        """
          Initialize the environment.
        """
        super().__init__()
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.source_examples = source_examples
        self.target_examples = target_examples
        self.llm_agent = llm_agent
        self.transformer = SchemaTransformTools(source_schema, target_schema, source_examples, target_examples)

        self.page = None  # current Wikipedia page
        self.obs = None  # current observation
        self.lookup_keyword = None  # current lookup keyword
        self.lookup_list = None  # list of paragraphs containing current lookup keyword
        self.lookup_cnt = None  # current lookup index
        self.steps = 0  # current number of steps
        self.answer = None  # current answer from the agent
        self.observation_space = self.action_space = textSpace()
        self.search_time = 0
        self.num_searches = 0

    def _prompt_constructor(self, template, include_vars=None, additional_vars=None):
        vars_to_include = {}
        for var in include_vars:
            if hasattr(self, var):
                vars_to_include[var] = getattr(self, var)
            else:
                raise AttributeError(f"The attribute '{var}' is not found in the instance.")
        if additional_vars is not None:
            vars_to_include.update(additional_vars)
        final_prompt = template.format(**vars_to_include)
        return final_prompt

    def _result_extractor(self, full_response):
        try:
            result: str = full_response.split('[START]')[1].split('[END]')[0]
            return result
        except Exception as e:
            print(f"Error extracting result: {e}")
            return None



    def _get_obs(self):
        return self.obs

    def _get_info(self):
        return {"steps": self.steps, "answer": self.answer}

    def reset(self, seed=None, return_info=False, options=None):
        self.obs = ("Interact with Wikipedia using search[], lookup[], and "
                    "finish[].\n")
        self.page = None
        self.lookup_keyword = None
        self.lookup_list = None
        self.lookup_cnt = None
        self.steps = 0
        self.answer = None
        observation = self._get_obs()
        info = self._get_info()
        return (observation, info) if return_info else observation


    def step(self, action):
        reward = 0
        done = False
        action = action.strip()
        observation = None
        if (action.startswith("TypePredict")):
            # print("TypePredict")
            observation = self.transformer.type_predict()
        elif action.startswith("Mapping"):
            # print("DirectMapping")
            observation = self.transformer.column_mapping()
        elif action.startswith("Aggregation"): # 1. sum 2. count 3. average 4. max 5. min
            # print("Aggregation")
            observation = self.transformer.aggregation()
        elif action.startswith("Clarify"):
            # print("Clarify")
            question = action[len("Clarify["):-1]
            observation = self.transformer.clarify(question)
        elif action.startswith("Filtering"):
            # print("Conditional")
            observation = self.transformer.conditional()
            self.performed_actions.add("Filtering")
        elif action.startswith("Finish"):
            # print("Finish")
            # response = action[len("Finish["):-1]#action
            # print('finish response', response)
            observation = self.transformer.finish(self.state)
            finish = True
        else:
            observation = "Invalid action: {}".format(action)

        return observation, reward, done, self._get_info()

    def get_time_info(self):
        speed = self.search_time / self.num_searches if self.num_searches else 0
        return {
            "call_speed": speed,
            "call_time": self.search_time,
            "num_calls": self.num_searches,
        }
