import numpy as np
import env.tool_env as tool_env
import env.wrappers as wrappers
import requests
import os
from util.utils import (create_connection, execute_sql)
from quality.quality import schema_quality, reverse_quality, fd_quality, data_quality
import csv
import pandas as pd


class Node:
    def __init__(self, state, init_prompt, parent=None):
        self.state = {'thought': '', 'action': '', 'observation': ''} if state is None else state
        self.parent = parent
        self.init_prompt = init_prompt
        self.children = []
        self.current_prompt = None
        self.num_visits = 0
        self.value = 0
        self.depth = 0 if parent is None else parent.depth + 1
        self.is_terminal = False
        self.reward = 0
        self.exhausted = False  # If all children are terminal

    def uct(self):
        if self.num_visits == 0:
            return self.value
        return self.value / self.num_visits + np.sqrt(2 * np.log(self.parent.num_visits) / self.num_visits)

    def __str__(self):
        return f"Node(depth={self.depth}, value={self.value:.2f}, num_visits={self.num_visits}, thought={self.state['thought']}, action={self.state['action']}, observation={self.state['observation']})"

    def to_dict(self):
        return {
            'state': self.state,
            'init_prompt': self.init_prompt,
            'parent': self.parent.to_dict() if self.parent else None,
            'children': [child.to_dict() for child in self.children],
            'num_visits': self.num_visits,
            'value': self.value,
            'depth': self.depth,
            'is_terminal': self.is_terminal,
            'reward': self.reward,
        }


class Environment:
    def __init__(self, llm_client, source_schema, target_schema, source_examples, target_examples):
        self.gpt = llm_client
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.source_examples = source_examples
        self.target_examples = target_examples

        self.env = self._construct_env()

    def _construct_env(self):
        tools_env = tool_env.ToolEnv(self.source_schema, self.target_schema, self.source_examples, self.target_examples,
                                     self.gpt)
        trans_env = wrappers.TransWrapper(tools_env)
        log_env = wrappers.LoggingWrapper(trans_env)
        return log_env

    def reset(self):
        return self.env.reset()

    def step(self, action, num_generate_sample):
        attempts = 0
        while attempts < 10:
            try:
                return self.env.step(action, num_generate_sample)
            except requests.exceptions.Timeout:
                attempts += 1


class MCTS:
    def __init__(self, backend, prompt, logger, llm_client, token_tracker, source_schema, target_schema,
                 source_examples, target_examples, transformer):
        self.env = Environment(llm_client, source_schema, target_schema, source_examples, target_examples)
        self.failed_trajectories = []
        self.reflection_map = []
        self.logger = logger
        self.llm_client = llm_client
        self.gpt = llm_client.gpt
        self.token_tracker = token_tracker
        self.value_cache = {}
        self.sample_method = 'tot'
        self.num_generate_sample = 1  # TODO: to be passed in
        self.n_evaluate_sample = 1  # TODO: to be passed in
        self.init_prompt = prompt
        self.agent_attrs = None
        self.transformer = transformer

    def _extract_val(self, prompt_to_evaluate: str):
        prompt_to_evaluate = prompt_to_evaluate[0]

        return np.random.uniform(0, 1)  # for testing

    def _construct_val_eval_promt(self, current_prompt: str, child_prompt: str, unique_trajectories: list = [],
                                  reflections: list = []) -> str:
        question = current_prompt.split('\n')[0]
        # unique_trajectories = []
        val_eval_prompt = ""
        """
        Contruct the prompt for the value network. It should force the model to rollout with 0 lookahead.
        It does the following:
        1. gather all the quality metric information
        2. construct a prompt using the quality information   
        The goal is to let LLM give us a score 

        Given the current prompt and a trajectory, evaluate its correctness and provide your reasoning and analysis in detail. 
        Focus on the latest thought, action, and observation. 
        Incomplete trajectories can be correct if the thoughts and actions so far are correct, even if the answer is not found yet. 
        Do not generate additional thoughts or actions. 
        Then at the last line conclude "Thus the correctness score is {s}", where s is an integer from 1 to 10.

        """

        return val_eval_prompt

    def _get_value(self, current_prompt, child_prompt, n_evaluate_sample, cache_val=True) -> float:
        """
        Given a current prompt and a child prompt, evaluate the value of the child prompt.

        Args:
            current_prompt (str): The current prompt
            child_prompt (str): The child prompt
            n_evaluate_sample (int): The number of samples to evaluate
            cache_val (bool): Whether to cache the value of the child prompt

        Returns:
            float: The value of the child prompt

        """
        unique_trajectories = self._get_unique_trajectories()
        val_eval_prompt = self._construct_val_eval_promt(current_prompt, child_prompt, unique_trajectories,
                                                         self.reflection_map)
        self.logger.info(f"Current: {current_prompt}")
        self.logger.info(f"Current: {child_prompt}")
        if cache_val and val_eval_prompt in self.value_cache:
            return self.value_cache[val_eval_prompt]
        self.logger.info(f"VALUE PROMPT: {val_eval_prompt}")
        # call the llm model with the value evaluation prompt
        val_outputs = self.gpt(val_eval_prompt, n=n_evaluate_sample, stop=None)
        self.logger.info(f"VALUE OUTPUTS: {val_outputs}")
        val = self._extract_val(val_outputs)
        self.logger.info(f"VALUES: {val}")
        if cache_val:
            self.value_cache[val_eval_prompt] = val
        return val

    def _get_values(self, current_prompt, child_prompts, n_evaluate_sample, cache_val=True):
        values = []
        local_value_cache = {}
        for child_prompt in child_prompts:
            if child_prompt in local_value_cache:
                value = 0
            else:
                value = self._get_value(current_prompt, child_prompt, n_evaluate_sample, cache_val=cache_val)
                local_value_cache[child_prompt] = value
            values.append(value)
        return values

    def _node_trajectory_to_text(self, node_string):
        lines = node_string.split('\n')
        formatted_lines = []
        for line in lines:
            try:
                depth = int(line.split(",")[0].split("=")[1].strip())
                thought = line.split(", thought=")[1].split(", action=")[0].strip()
                action = line.split(", action=")[1].split(", observation=")[0].strip()
                observation = line.split(", observation=")[1].split(")")[0].strip()
            except IndexError:
                continue

            if depth != 0:
                if thought:
                    formatted_lines.append(f"Thought {depth}: {thought}")
                if action:
                    formatted_lines.append(f"Action {depth}: {action}")
                if observation:
                    formatted_lines.append(f"Observation {depth}: {observation}")
        return '\n'.join(formatted_lines)

    def _get_unique_trajectories(self, num=5):
        unique_trajectories = []
        seen_final_answers = set()
        for traj in self.failed_trajectories:
            final_answer = traj.get('final_answer')
            if final_answer not in seen_final_answers:
                unique_trajectories.append(self._node_trajectory_to_text(traj['trajectory']))
                seen_final_answers.add(final_answer)
            if len(unique_trajectories) >= num:
                break
        return unique_trajectories

    @staticmethod
    def _get_prompt_at_node(node):
        trajectory = []
        init_prompt = node.init_prompt
        while node:
            new_segment = []
            if node.state['thought']:
                new_segment.append(f"Thought {node.depth}: {node.state['thought']}")
            if node.state['action']:
                new_segment.append(f"Action {node.depth}: {node.state['action']}")
            if node.state['observation'] and node.depth != 0:
                new_segment.append(f"Observation {node.depth}: {node.state['observation']}")
            trajectory.append('\n'.join(new_segment))
            node = node.parent
        return init_prompt + '\n'.join(reversed(trajectory))

    def mcts_search(self, iterations=30, to_print=True, threshold=0.65):
        root = Node(state=None, init_prompt=self.init_prompt)

        all_nodes = []
        self.failed_trajectories = []
        #terminal_nodes = []
        self.reflection_map = []

        for i in range(iterations):
            self.logger.info(f"Iteration {i + 1}...")
            node = self._select_node(root)

            if node is None:
                self.logger.info("All paths lead to terminal nodes with reward 0. Ending search.")
                break

            self._expand_node(node)
            value = self._evalutate_node(node)
            reward, rollout_node, gpt_output, sql_result = self.rollout(max(node.children, key=lambda child: child.value), max_depth=4)

            #terminal_nodes.append(terminal_node)

            if reward >= threshold:
                self.logger.info("SUCCESSFUL TRAJECTORY FOUND DURING SIMULATION")
                return rollout_node.state, rollout_node.value, [], rollout_node.reward, gpt_output, sql_result

            self.backpropagate(rollout_node, reward)

            all_nodes = [(node, node.value) for node in self._collect_all_nodes(root)]

            for j, (node, value) in enumerate(all_nodes):
                self.logger.info(f"Node {j + 1}: {str(node)}")

        all_nodes_list = self._collect_all_nodes(root)
        all_nodes_list.extend(rollout_node)
        best_child = max(all_nodes_list, key=lambda x: x.reward)
        if best_child.reward >= threshold:
            self.logger.info("Successful trajectory found")
        else:
            self.logger.info("Unsuccessful trajectory found")
        if best_child is None:
            best_child = root
        return best_child.state, best_child.value, all_nodes, best_child.reward, None, None

    def _select_node(self, node, threshold=0.65):
        while node and node.children:
            self.logger.info(f"Selecting from {len(node.children)} children at depth {node.depth}.")

            terminal_children = [child for child in node.children if child.is_terminal]
            if len(terminal_children) == len(node.children):
                self.logger.info(f"All children are terminal at depth {node.depth}. Backtracking...")
                if node.parent:
                    node.parent.children.remove(node)
                node = node.parent
                continue

            node_with_reward_gt_threshold = next((child for child in terminal_children if child.reward >= threshold),
                                                 None)
            if node_with_reward_gt_threshold:
                self.logger.info(f"Found terminal node with reward 1 at depth {node.depth}.")
                return node_with_reward_gt_threshold

            node = max((child for child in node.children if not child.is_terminal), key=lambda child: child.uct(),
                       default=None)

            while node.is_terminal and node.reward != 1:
                node = max((child for child in node.parent.children if not child.is_terminal),
                           key=lambda child: child.uct(), default=None)

            self.logger.info(f"Selected node at depth {node.depth} with UCT {node.uct()}.")

        return node  # This will return None if all paths from the root are exhausted

    def _generate_new_states(self, node, num_generate_sample, sample_method):
        # this layer should be getting the general type of action
        prompt = self._get_prompt_at_node(node)
        sampled_actions = self._sample_next_actions(prompt, f"Thought {node.depth + 1}: ",
                                                    sample_method, "Observation")
        sampled_actions_log = "\n".join(
            [f"Sampled Action {index + 1}:\n{action}" for index, action in enumerate(sampled_actions)])
        self.logger.info(f"SAMPLED ACTIONS:\n{sampled_actions_log}")

        unique_states = {}

        # interact with the environment, get rewards
        for action in sampled_actions:
            thought_line = next((line.split(":")[1].strip() for line in action.split("\n") if
                                 line.startswith(f"Thought {node.depth + 1}")), '')
            action_line = next((line.split(":")[1].strip() for line in action.split("\n") if
                                line.startswith("Action") and ":" in line), None)

            if action_line:
                action_type = action_line.split('[')[0] if '[' in action_line else action_line
                action_param = action_line.split('[')[1].split(']')[0] if '[' in action_line else ""
                # this layer should be getting the specific action
                obs, r, done, info = self.env.step(f"{action_type}[{action_param}]", num_generate_sample)

                for i in range(len(obs)):
                    unique_key = f"{thought_line}::{action_line}::{i}"

                    new_state = node.state.copy()
                    new_state['thought'] = thought_line
                    new_state['action'] = action_line
                    new_state['observation'] = obs

                    new_node = Node(state=new_state, init_prompt=node.init_prompt, parent=node)
                    new_node.current_prompt = self._get_prompt_at_node(new_node)

                    new_node.is_terminal = r == 1 or done
                    new_node.reward = r
                    new_node.depth = node.depth + 1
                    if r == 1:
                        new_node.em = info.get('em')
                    unique_states[unique_key] = new_node
                    self.logger.info(f"NEW NODE: {new_node}")
                    self.logger.info(f"Feedback: {info}")

                    if new_node.is_terminal and r == 0:
                        trajectory = self._collect_trajectory(new_node)
                        self.failed_trajectories.append(
                            {'trajectory': trajectory, 'final_answer': f"{action_type.lower()}[{action_param}]"})

        return list(unique_states.values())

    def _sample_next_actions(self, current_prompt, thought_sequence_intro, sample_method, stop, num_generate_sample=1):
        unique_trajectories = self._get_unique_trajectories()
        if len(unique_trajectories) > len(self.reflection_map) and len(unique_trajectories) < 4:
            print("generating reflections")
            self.reflection_map = self.task.generate_self_reflection(unique_trajectories, current_prompt)
        if sample_method == 'tot':
            # prompt = self._construct_action_sampling_prompt(current_prompt, thought_sequence_intro, self.reflection_map)
            prompt = current_prompt + thought_sequence_intro
        else:
            raise ValueError(f'prompt_sample {sample_method} not recognized')
        self.logger.info(f"PROMPT: {prompt}")
        samples = self.gpt(prompt, n=num_generate_sample, stop=stop)
        return samples  # [thought_sequence_intro + _ for _ in samples]

    def _construct_action_sampling_prompt(self, current_prompt: str, thought_sequence_intro: str = '',
                                          reflection_mapping_list=[]):
        input = current_prompt + '\n' + thought_sequence_intro
        trajectories = ""

        if reflection_mapping_list:
            for reflection_mapping in reflection_mapping_list:
                traj_with_reflection = reflection_mapping['trajectory'] + "FAILED TRAJECTORY\nReflection: " + \
                                       reflection_mapping['reflection'] + "\n\n"
                trajectories += traj_with_reflection

            """
            prompt = cot_prompt_feedback.format(trajectories=trajectories, input=input)
            if self.token_tracker(prompt) > max_token_length:
                print("Too long")
                trajectories = ""
                for reflection_mapping in reflection_mapping_list[:3]:
                    traj_with_reflection = reflection_mapping['trajectory'] + "FAILED TRAJECTORY\nReflection: " + \
                                           reflection_mapping['reflection'] + "\n\n"
                    trajectories += traj_with_reflection

                #prompt = cot_prompt_feedback_short.format(trajectories=trajectories, input=input)

            return prompt
        else:
            prompt = cot_prompt.format(input=input)
            if self.llm_client.calculate_tokens(prompt)> max_token_length:
                prompt = cot_prompt_short.format(input=input)
            """
        return "prompt"

    def _expand_node(self, node):
        if node.depth >= 7:
            self.logger.info("Depth limit reached")
            node.is_terminal = True
            return
        new_nodes = self._generate_new_states(node, self.num_generate_sample, self.sample_method)
        node.children.extend(new_nodes)

    def _evalutate_node(self, node):
        child_prompts = [self._get_prompt_at_node(child) for child in node.children if not child.is_terminal]
        current_prompt = ""
        votes = self._get_values(current_prompt, child_prompts, self.n_evaluate_sample)

        self.logger.info(f"Length of votes: {len(votes)}")
        self.logger.info(f"Length of node.children: {len(node.children)}")

        votes = votes + [0] * (len(node.children) - len(votes))
        for i, child in enumerate(node.children):
            child.value = votes[i]

        return sum(votes) / len(votes) if votes else 0

    def rollout(self, node, max_depth=4):
        self.logger.info("ROLLING OUT")
        depth = node.depth
        rewards = [0]
        # forcing the rollout with 0-lookahead
        num_lookahead = 0
        max_depth = node.depth + num_lookahead

        if num_lookahead == 0:
            # force to conclude the sql generation
            response = self.gpt(node.current_prompt, n=1, stop=None)[0]
            gpt_output = self.transformer.finish(response)
            #gpt_output = response.split("Finish[")[1].split("]")[0].strip() #this is not stable
            print("SQL Script Extracted from GPT Response:")
            print(gpt_output)

            conn = create_connection()

            # Execute the SQL script on the specified table
            sql_result = execute_sql(conn, gpt_output)
            if not sql_result:
                self.logger.warning("The SQL result is empty. Skipping to the next iteration.")

            if "Error:" in sql_result:
                return 0, node
            # not using sql_result directly, as numeric vs string values will occur while validation
            our_result = []
            if os.path.exists(self.agent_attrs['result_path']):
                with open(self.agent_attrs['result_path'], 'r', encoding="utf-8") as file:
                    reader = csv.reader(file)
                    header = next(reader)  # Assuming you want to skip the header
                    for row in reader:
                        our_result.append(tuple(row))
                sql_result_df = pd.DataFrame(our_result)
            else:
                print(f"File not found: {self.agent_attrs['result_path']}.")

            data_quality_score, low_diversity_columns = data_quality(sql_result, self.agent_attrs['target_schema'])

            schema_score, schema_feedback, column_mappings, target_handle = schema_quality(gpt_output, **self.agent_attrs)
            fd_score, fd_comparison = fd_quality(gpt_output, column_mappings, **self.agent_attrs)
            reverse_score = reverse_quality(conn, **self.agent_attrs)

            final_score = (schema_score + data_quality_score + fd_score) / 3 if reverse_score < 0.5 else (
                                                                                                       reverse_score + schema_score + data_quality_score + fd_score) / 4

        self.logger.info("ROLLOUT FINISHED")
        return final_score, node, gpt_output, sql_result


    def backpropagate(self, node, value):
        while node:
            node.num_visits += 1
            if node.is_terminal:
                if node.reward == 0:
                    self.logger.info(f"Backpropagating  with reward 0 at depth {node.depth}. New value: {node.value}.")
                    node.value = (node.value * (node.num_visits - 1) + (-1)) / node.num_visits
                else:
                    node.value = (node.value * (node.num_visits - 1) + value) / node.num_visits
                    self.logger.info(f"Backpropagating with reward 1 at depth {node.depth}. New value: {node.value}.")
            else:
                node.value = (node.value * (node.num_visits - 1) + value) / node.num_visits
                self.logger.info(f"Backpropagating at depth {node.depth}. New value: {node.value}.")

            node = node.parent

    def _collect_all_nodes(self, node):
        nodes = [node]
        for child in node.children:
            nodes.extend(self._collect_all_nodes(child))
        return nodes


    def _collect_trajectory(self, node):
        trajectory = []
        while node:
            trajectory.append(str(node))
            node = node.parent
        return '\n'.join(reversed(trajectory))

    def fill_agent_attrs(self, attrs):
        self.agent_attrs = attrs





