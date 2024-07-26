# agent.py
from util.schema_trans_tools import SchemaTransformTools
from util.semantic_search import get_prompt_embeddings, get_fewshot_prompt
from llm.llm_models import LLMClient
from prompts import (
    init_template,
    init_template_no_clarify,
    ultimate_task,
    examples,
    examples_no_clarify,
    monolithic_template,
    cot_template,
    monolithic_template_join,
    cot_multi_source_template,
    cot_multi_source_python_template,
)
from langchain.prompts import PromptTemplate
from action import ActionGraph
import random

from copy import deepcopy
from search_algo.mcts_bk import mcts
from search_algo.mcts import MCTS


def get_input_variables(method):
    if method == "monolithic":
        return [
            "source_examples",
            "target_examples",
            "source_schema",
            "target_schema",
            "source_name",
            "target_name",
            "test_0_path",
            "result_path",
        ]
    elif method == "cot":
        return [
            "source_schema",
            "target_schema",
            "source_examples",
            "target_examples",
            "source_name",
            "target_name",
        ]
    else:
        return [
            "examples",
            "source_examples",
            "target_examples",
            "source_schema",
            "target_schema",
            "source_name",
            "target_name",
            "test_0_path",
            "result_path",
        ]


class Agent:
    def __init__(
        self,
        source_name,
        target_name,
        target_path,
        test_0_path,
        source_schema,
        target_schema,
        source_examples,
        target_examples,
        result_path,
        control_method,
        token_tracker,
        logger,
        backend,
        script_language,
        clarify_on=False,
        method="react",
        max_steps=20,
        k_shot=0,
        encoder=None,
    ):
        self.source_name = source_name
        self.target_name = target_name
        self.target_path = target_path
        self.test_0_path = test_0_path
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.source_examples = source_examples
        self.target_examples = target_examples
        self.result_path = result_path
        self.clarify_on = clarify_on
        self.max_steps = max_steps
        self.method = method
        self.token_tracker = token_tracker
        self.logger = logger
        self.backend = backend
        self.script_language = script_language
        self.llm_client = LLMClient(
            model=self.backend, tracker=self.token_tracker, logger=self.logger
        )
        self.state = None
        self.action_graph = ActionGraph()
        self.performed_actions = set()
        self.control_method = control_method
        self.agent_attrs = None

        if method == "monolithic" or method == "cot":
            template = PromptTemplate(
                input_variables=get_input_variables(method),
                template=monolithic_template,
            )
            self.prompt = template.format(
                source_schema=source_schema,
                target_schema=target_schema,
                source_examples=source_examples,
                target_examples=target_examples,
                source_name=source_name,
                target_name=target_name,
                test_0_path=test_0_path,
                result_path=result_path,
            )
            self.agent_attrs = self.get_all_agent_attrs_mono()
        elif method == "multi_source":
            template = PromptTemplate(
                input_variables=get_input_variables(method),
                template=(
                    cot_multi_source_template
                    if script_language == "sql"
                    else cot_multi_source_python_template
                ),
            )
            # show the source information one by one
            source_info = "\n"

            print(source_schema)

            for i in range(len(source_schema)):
                source_info += (
                    f"Source {i}:\n"
                    f"\tSource {i} Name: {source_name[i]}\n"
                    f"\tSource {i} Schema: {source_schema[i]}\n"
                    f"\tSource {i} Examples: {source_examples[i]}\n"
                    f"\tSource {i} Path: {test_0_path[i]}\n"
                )

            print("DEBUG-- RESULT PATH:" + result_path)
            self.prompt = template.format(
                target_name=target_name,
                target_schema=target_schema,
                target_examples=target_examples,
                source_info=source_info,
                test_0_path=test_0_path,
                result_path=result_path,
            )

            if k_shot > 0:
                # For example, search_len for Target3_x is 2, for Target4_x is 3, etc.

                embeddings = get_prompt_embeddings(
                    client=self.llm_client.client, encoder=encoder
                )
                fewshot_examples = get_fewshot_prompt(
                    self.prompt, k_shot, embeddings, target_name, encoder=encoder
                )
                self.prompt = f"{fewshot_examples}{self.prompt}\nResponse:\n"

            self.agent_attrs = self.get_all_agent_attrs_mono()
        elif method == "mcts":
            template = PromptTemplate(
                input_variables=get_input_variables(method),
                template=init_template if clarify_on else init_template_no_clarify,
            )
            self.prompt = template.format(
                examples=examples if clarify_on else examples_no_clarify,
                source_schema=source_schema,
                target_schema=target_schema,
                source_examples=source_examples,
                target_examples=target_examples,
                source_name=source_name,
                target_name=target_name,
                test_0_path=test_0_path,
                result_path=result_path,
            )

        self.ultimate_task = ultimate_task
        self.transformer = SchemaTransformTools(
            source_schema, target_schema, source_examples, target_examples
        )
        self.mcts = MCTS(
            self.backend,
            self.prompt,
            self.logger,
            self.llm_client,
            self.token_tracker,
            self.source_schema,
            self.target_schema,
            self.source_examples,
            self.target_examples,
            self.transformer,
        )
        self.mcts.fill_agent_attrs(self.get_all_agent_attrs_mcts())

    def get_state(self):
        return self.state

    def execute_action(self, action, transformer=None, reason_history=None):
        finish = False
        # print(f"Executing action: {action}")
        if action.strip().startswith("TypePredict"):
            # print("TypePredict")
            observation = transformer.type_predict()
            self.performed_actions.add("TypePredict")
        elif action.strip().startswith("Mapping"):
            # print("DirectMapping")
            observation = transformer.column_mapping()
            self.performed_actions.add("Mapping")
        elif action.strip().startswith("Aggregation"):
            # print("Aggregation")
            observation = transformer.aggregation()
            self.performed_actions.add("Aggregation")
        elif action.strip().startswith("Clarify"):
            # print("Clarify")
            question = action.strip()[len("Clarify[") : -1]
            observation = transformer.clarify(question)
            self.performed_actions.add("Clarify")
        elif action.strip().startswith("Conditional"):
            # print("Conditional")
            observation = transformer.conditional()
            self.performed_actions.add("Conditional")
        elif action.strip().startswith("Finish"):
            # print("Finish")
            # response = action[len("Finish["):-1]#action.strip()
            # print('finish response', response)
            observation = transformer.finish(self.state)
            finish = True
            self.performed_actions.add("Finish")
        else:
            observation = "Invalid action: {}".format(action)

        return observation, finish

    def run_baseline(self, verbose=True):
        res = self.llm_client.gpt(self.prompt)
        # print('Response - SQL', res)
        if self.script_language == "python":
            return res[0].split("```Python")[1].split("```")[0].strip()
        elif self.script_language == "sql":
            return res[0].split("```sql")[1].split("```")[0].strip()

    def run_mcts(self, verbose=True):
        # Use MCTS for action selection
        """
        i=0
        self.react_state = ReactState(self.performed_actions, self.state, self.action_graph,
                                      self.transformer, i)
        bestChild = self.mcts.search(
            self.react_state,
            needDetails=False
        )
        action = bestChild.state.current_action
        self.performed_actions.add(action)
        observation = bestChild.state.current_observation
        finish = bestChild.state.is_terminal

        # Craft a detailed prompt for generating thought
        # observation, finish = self.execute_action(action, transformer=self.transformer)
        step_str = f"Thought {i}: MCTS - {action}\nAction {i}: {action}\nObservation {i}: {observation}\n"
        return True
        """
        (
            best_node_state,
            best_node_value,
            all_nodes,
            best_node_reward,
            gpt_output,
            sql_result,
        ) = self.mcts.mcts_search()
        return True

    def run_pure_react(self, verbose=True):
        n_calls, n_badcalls = 0, 0
        for i in range(1, self.max_steps + 1):
            n_calls += 1
            if mcts:
                thought_action = self.llm_client.gpt(
                    self.state + f"Thougt{i}:", stop=[f"\nObservation {i}:"]
                )[0]
                try:
                    thought, action = thought_action.strip().split(f"\nAction {i}:")
                except:
                    print("ohh...", thought_action)
                    n_badcalls += 1
                    n_calls += 1
                    thought = thought_action.strip().split("\n")[0]
                    action = self.llm_client.gpt(
                        self.state + f"Thought {i}: {thought}\nAction {i}:",
                        stop=[f"\nObservation {i}:"],
                    )[0].strip()
                observation, finish = self.execute_action(
                    action, transformer=self.transformer
                )
                step_str = f"Thought {i}: {thought}\nAction {i}: {action}\nObservation {i}: {observation}\n"
            self.state += step_str
            if verbose:
                print(step_str)
            if finish:
                break
        return observation, n_calls, n_badcalls

    def run(self, verbose=True, method="mcts"):
        """
        Run the agent to generate a SQL script
        :param verbose: whether to print the intermediate steps
        :param method: the method to use for generating the SQL script
        :return: the generated SQL script
        """
        self.state = self.prompt + self.ultimate_task + "\n"
        if method == "mcts":
            return self.run_mcts(verbose)
        elif method == "monolithic":
            return self.run_baseline(verbose)
        elif method == "react":
            return self.run_pure_react(verbose)
        elif method == "cot":
            return self.run_baseline(verbose)
        elif method == "multi_source":
            return self.run_baseline(verbose)

    def get_all_agent_attrs_mcts(self):
        return {
            "source_name": self.source_name,
            "target_name": self.target_name,
            "test_0_path": self.test_0_path,
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
            "source_examples": self.source_examples,
            "target_examples": self.target_examples,
            "result_path": self.result_path,
            "clarify_on": self.clarify_on,
            "max_steps": self.max_steps,
            "method": self.method,
            "token_tracker": self.token_tracker,
            "logger": self.logger,
            "backend": self.backend,
            "llm_client": self.llm_client,
            "state": self.state,
            "action_graph": self.action_graph,
            "performed_actions": self.performed_actions,
            "prompt": self.prompt,
            "ultimate_task": self.ultimate_task,
            "transformer": self.transformer,
            "mcts": self.mcts,
        }

    def get_all_agent_attrs_mono(self):
        return {
            "source_name": self.source_name,
            "target_name": self.target_name,
            "test_0_path": self.test_0_path,
            "target_path": self.target_path,
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
            "source_examples": self.source_examples,
            "target_examples": self.target_examples,
            "result_path": self.result_path,
            "clarify_on": self.clarify_on,
            "max_steps": self.max_steps,
            "method": self.method,
            "token_tracker": self.token_tracker,
            "logger": self.logger,
            "backend": self.backend,
            "llm_client": self.llm_client,
            "state": self.state,
            "action_graph": self.action_graph,
            "performed_actions": self.performed_actions,
            "prompt": self.prompt,
            "control_method": self.control_method,
        }


class ReactState:
    def __init__(self, performed_actions, state, action_graph, transformer, i):
        self.current_action = None
        self.current_observation = None

        self.performed_actions = performed_actions
        self.action_graph = action_graph
        self.state_in_mcts = state
        self.transformer = transformer
        self.is_terminal = False
        self.i = i

    def getPossibleActions(self):
        print("performed actions", self.performed_actions)
        possible_actions = self.action_graph.get_possible_actions(
            self.performed_actions
        )
        print("possible actions", possible_actions)
        return possible_actions

    def takeAction(self, action):
        newState = deepcopy(self)
        print(f"Taking action: {action}")
        newState.performed_actions.add(action)
        newState.current_action = action  # result of the observation
        newState.is_terminal = True if action == "Finish" else False
        # TODO: add action support
        finish = False
        # print(f"Executing action: {action}")
        if action.strip().startswith("TypePredict"):
            # print("TypePredict")
            observation = self.transformer.type_predict()
            self.performed_actions.add("TypePredict")
        elif action.strip().startswith("DirectMapping"):
            # print("DirectMapping")
            observation = self.transformer.column_mapping()
            self.performed_actions.add("DirectMapping")
        elif action.strip().startswith("Aggregation"):
            # print("Aggregation")
            observation = self.transformer.aggregation()
            self.performed_actions.add("Aggregation")
        elif action.strip().startswith("Clarify"):
            # print("Clarify")
            prompt_q_mcts = f"""
            You are a Postgres SQL developer. Given the following prompt:\n{self.state_in_mcts}\nWhat would you ask for clarification? Provide only one concise question. Wrap the question between [START] and [END]
            """
            question_response = gpt3(prompt_q_mcts)
            question = self.transformer.result_extractor(question_response)
            # question = action.strip()[len("Clarify"):-1]
            observation = self.transformer.clarify(question)
            self.performed_actions.add("Clarify")
            newState.state_in_mcts = (
                self.state_in_mcts
                + f"Thought {self.i}: Use MCTS\nAction {self.i}: {action}+'['+{question}+']'+\nObservation {self.i}: {observation}\n"
            )
            return newState
        elif action.strip().startswith("Conditional"):
            # print("Conditional")
            observation = self.transformer.conditional()
            self.performed_actions.add("Conditional")
        elif action.strip().startswith("Finish"):
            # print("Finish")
            response = action.strip()  # [len("Finish["):-1]
            observation = self.transformer.finish(response)
            finish = True
            self.performed_actions.add("Finish")
        else:
            observation = "Invalid action: {}".format(action)

        newState.current_observation = observation
        newState.state_in_mcts = (
            self.state_in_mcts
            + f"Thought {self.i}: Use MCTS\nAction {self.i}: {action}\nObservation {self.i}: {observation}\n"
        )
        return newState

    def isTerminal(self):
        if self.current_action == "Finish":
            return True
        else:
            return False

    def getReward(self):
        print("get reward")
        return random.random() * 100
