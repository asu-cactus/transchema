import time
import gymnasium as gym
from react.schema_trans_tools import SchemaTransformTools


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

        self.obs = None  # current observation
        self.steps = 0  # current number of steps
        self.observation_space = self.action_space = textSpace()
        self.search_time = 0

    def _get_obs(self):
        return self.obs

    def _get_info(self):
        return {"steps": self.steps, "answer": self.obs}

    def reset(self, seed=None, return_info=False, options=None):
        self.obs = ("Interact with data transformation tools, and "
                    "finish[].\n")
        self.steps = 0
        observation = self._get_obs()
        info = self._get_info()
        return (observation, info) if return_info else observation

    def step(self, action, num_generate_sample):
        reward = 0
        done = False
        action = action.strip()
        observation = []
        init_time = time.time()

        if (action.startswith("TypePredict")):
            # print("TypePredict")
            observation.append(self.transformer.type_predict())

        elif action.startswith("Mapping"):
            # print("DirectMapping")
            observation.append(self.transformer.column_mapping())
        elif action.startswith("Aggregation"):  # 1. sum 2. count 3. average 4. max 5. min
            # print("Aggregation")
            first_obs = self.transformer.aggregation()
            observation.append(first_obs)
            num_generate_sample -= 1
            agg_funcs = []
            agg_func_detected = self.transformer.agg_func_detect(first_obs)
            # print('observation', observation)
            agg_funcs.append(agg_func_detected)
            # provide another possible aggregations, given the current aggregations
            for i in range(num_generate_sample):
                new_observation = self.transformer.gen_new_agg_func(agg_funcs)
                observation.append(new_observation)
                if i + 1 < num_generate_sample:
                    agg_func_detected = self.transformer.agg_func_detect(new_observation)
                    agg_funcs.append(agg_func_detected)

        elif action.startswith("Clarify"):
            # print("Clarify")
            question = action[len("Clarify["):-1]
            observation.append(self.transformer.clarify(question))
        elif action.startswith("Filtering"):
            # print("Conditional")
            observation.append(self.transformer.conditional())
            self.performed_actions.add("Filtering")
        elif action.startswith("Finish"):
            # print("Finish")
            # response = action[len("Finish["):-1]#action
            # print('finish response', response)
            observation.append(self.transformer.finish(self.state))
            done = True
        else:
            observation = "Invalid action: {}".format(action)

        self.obs = observation
        self.search_time = time.time() - init_time
        self.steps += 1

        return observation, reward, done, self._get_info()

    def get_time_info(self):
        # speed = self.search_time / self.num_searches if self.num_searches else 0
        return {
            # "call_speed": speed,
            "call_time": self.search_time
        }
