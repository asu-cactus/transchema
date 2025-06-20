import re
import pdb
import os
import time
from dataclasses import dataclass
import pandas as pd

from llm.llm_models import TokenUsageTracker, LLMClient
from methods.intermediate_materialization import (
    create_source_space,
    get_task,
    verify_result,
    allowed_operation_list,
    extract_ops_and_configs,
)
from util.utils import get_test_info, execute_python
from auto_suggest_llm_util import query_gpt, get_prompt, calculate_score
from log_util.log_util import create_logger
from quality.quality import analyze_functional_dependencies
from prompts.next_operator_prompt_with_intermediate_materialization import (
    deduplicate_same_operators_prompt,
)


@dataclass
class State:
    """
    State class to hold the state of the tree of thoughts.
    """

    step: int = 0
    history: tuple[str] = ()
    is_terminal: bool = False
    terminate_due_to_error: bool = False
    result_csv_path: str = ""
    col_mapping_score: float = 0.0
    fd_key_score: float = 0.0
    parent: "State" = None  # Reference to the parent state, if needed
    fds: tuple = ()  # Functional dependencies of the result CSV

    def __str__(self):
        return (
            f"Step: {self.step}, "
            f"History: {self.history}, "
            f"Is Terminal: {self.is_terminal}, "
            f"Terminate Due to Error: {self.terminate_due_to_error}, "
            f"Result CSV Path: {self.result_csv_path}, "
            f"Column Mapping Score: {self.col_mapping_score:.4f}, "
            f"FD Key Score: {self.fd_key_score:.4f}"
        )


# decided through parameters
source_space_name = "source_space"


def extract_operators_and_configurations(res: str, args) -> list[tuple[str, str]]:
    """
    Extract the operation and configuration from the LLM response.
    """
    if args.tot_branch_method == "sample":
        match = re.search(
            r"Deduplicated operators:(.*)",
            res,
            re.DOTALL | re.IGNORECASE,
        )
    elif args.tot_branch_method == "propose":
        match = re.search(
            r"Proposed next operators:(.*)",
            res,
            re.DOTALL | re.IGNORECASE,
        )
    else:
        raise ValueError(
            f"Unknown tot_branch_method: {args.tot_branch_method}. "
            "Please choose 'propose' or 'sample'."
        )

    if match:
        string = match.group(1)
        string = string.strip()

        ops_and_configs = []
        for line in string.split("\n"):
            # Extract from "1. operator: configuration_for_operator"
            op_and_config = line.split(":", 1)
            if len(op_and_config) == 2:
                op, op_config = op_and_config
                for allow_op in allowed_operation_list:
                    if allow_op.lower() in op.lower():
                        op = allow_op
                        break
                else:
                    print(f"Skipping unsupported operation: {op}, line: {line}")
                    continue

                op_config = op_config.strip()
                ops_and_configs.append((op, op_config))
                if len(ops_and_configs) >= args.branch_factor:
                    break
            else:
                print(f"Skipping line due to unexpected format: {line}")
                continue
    else:
        ops_and_configs = None
        print(f"Parsing error, response:\n{res}")

    return ops_and_configs


def get_operators(state, nth_intermediate_step, args, config):
    """
    Get the next operator from the LLM based on the operation history and configuration.
    This implementation has small difference from intermediate_materialization
    """
    if args.tot_branch_method == "propose":
        # Use the propose method to get the next operator
        ops_and_configs = get_operators_with_propose_method(
            state, nth_intermediate_step, args, config
        )
    elif args.tot_branch_method == "sample":
        ops_and_configs = get_operators_with_sample_method(
            state, nth_intermediate_step, args, config
        )
    else:
        raise ValueError(
            f"Unknown tot_branch_method: {args.tot_branch_method}. "
            "Please choose 'propose' or 'sample'."
        )
    return ops_and_configs


def get_operators_with_sample_method(
    state, nth_intermediate_step, args, config, temperature=0.5
) -> list[tuple[str, str]]:
    prompt = get_prompt(
        prompt_type="get_next_operator",
        max_tokens=args.token_limit,
        model=args.model,
        allowed_operation_list=allowed_operation_list,
        operation_history=state.history,
        target_data_name=config["target_data_name"],
        target_data_schema=config["target_data_schema"],
        target_samples=config["target_samples"],
        file_count=config["file_count"],
        source_data_name_list=config["source_data_name_list"],
        source_data_schema_list=config["source_data_schema_list"],
        directory=config["source_space_dir"],
        len_idx_target_idx=config["len_idx_target_idx"],
        target_perc=args.target_per,
        is_perc=args.is_perc,
        target_length=args.target_length,
        source_length=args.source_length,
        fd_flag=args.fd_flag,
        hint_source=args.hint_source,
        nth_intermediate_step=nth_intermediate_step,
        state=state,
        args=args,
    )

    ops_and_configs = []
    for _ in range(args.branch_factor):
        max_tries = 5

        for _ in range(max_tries):
            res = query_gpt(
                config["llm_client"],
                args.model,
                prompt,
                config["q_count"],
                config["logger"],
                config["cost_summary"],
                config["token_tracker"],
                type="Ask For Operator",
                temperature=temperature,  # Use a lower temperature for sampling
            )[0]

            op, op_config = extract_ops_and_configs(res)
            if op is None:
                # Cannot extract operation from the LLM output, try again
                continue
        if op is not None:
            ops_and_configs.append((op, op_config))

    # Deduplicate some op_config if they are the same

    if len(ops_and_configs) > 1:
        for _ in range(max_tries):
            dedup_prompt = deduplicate_same_operators_prompt(ops_and_configs)

            res = query_gpt(
                config["llm_client"],
                args.model,
                dedup_prompt,
                config["q_count"],
                config["logger"],
                config["cost_summary"],
                config["token_tracker"],
                type="Deduplicate Same Operators",
            )[0]

            ops_and_configs_deduped = extract_operators_and_configurations(res, args)
            if ops_and_configs_deduped:
                ops_and_configs = ops_and_configs_deduped
                break

    return ops_and_configs


def get_operators_with_propose_method(
    state, nth_intermediate_step, args, config
) -> list[tuple[str, str]]:
    prompt = get_prompt(
        prompt_type="get_next_operator",
        max_tokens=args.token_limit,
        model=args.model,
        allowed_operation_list=allowed_operation_list,
        operation_history=state.history,
        target_data_name=config["target_data_name"],
        target_data_schema=config["target_data_schema"],
        target_samples=config["target_samples"],
        file_count=config["file_count"],
        source_data_name_list=config["source_data_name_list"],
        source_data_schema_list=config["source_data_schema_list"],
        logger=config["logger"],
        directory=config["source_space_dir"],
        len_idx_target_idx=config["len_idx_target_idx"],
        target_perc=args.target_per,
        is_perc=args.is_perc,
        target_length=args.target_length,
        source_length=args.source_length,
        fd_flag=args.fd_flag,
        hint_source=args.hint_source,
        nth_intermediate_step=nth_intermediate_step,
        state=state,
        args=args,
    )

    max_tries = 5
    for _ in range(max_tries):

        res = query_gpt(
            config["llm_client"],
            args.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type="Ask For Operator",
        )[0]

        ops_and_configs = extract_operators_and_configurations(res, args)
        if ops_and_configs is None:
            # Cannot extract operation from the LLM output, try again
            continue

        return ops_and_configs

    raise Exception(f"Failed to get operation after 5 tries. Last response:\n{res}")


def materialize_chatgpt(
    operation_history, args, config, result_csv_path, result_python_path, max_trials=5
):
    """
    Materialize the state; save the result table to csv and python code to python file.
    TODO: merge this with intermediate_materialization
    """
    error_str = ""

    for _ in range(max_trials):
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=args.token_limit,
            model=args.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config["target_data_name"],
            target_data_schema=config["target_data_schema"],
            target_samples=config["target_samples"],
            file_count=config["file_count"],
            source_data_name_list=config["source_data_name_list"],
            source_data_schema_list=config["source_data_schema_list"],
            logger=config["logger"],
            directory=config["source_space_dir"],
            len_idx_target_idx=config["len_idx_target_idx"],
            target_perc=args.target_per,
            is_perc=args.is_perc,
            target_length=args.target_length,
            error_string=error_str,
            fd_flag=args.fd_flag,
            hint_source=args.hint_source,
            save_path=result_csv_path,
            args=args,
        )

        res = query_gpt(
            config["llm_client"],
            args.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type="Get Python Script",
        )[0]

        pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res)
        script = match.group(1).strip()

        response = execute_python(script)
        log_str = f"{result_python_path} Python execution: {response}"
        print(log_str)
        config["logger"].info(log_str)
        error_str += response + "\n"

        if response == "Success":
            assert os.path.exists(
                result_csv_path
            ), f"{result_csv_path} does not exist after successful execution."
            with open(result_python_path, "w") as f:
                f.write(script)
            return

    raise Exception(
        f"Exceed {max_trials} trails, {result_csv_path} materialization Failed"
    )


def calculate_fd_key_score(fds, target_fds) -> float:
    """Current implementation use only key matching, not functional dependency matching."""
    target_df_keys = [key for key, _ in target_fds]
    state_df_keys = [key for key, _ in fds]
    if not target_df_keys:
        # No keys in target_df_keys, returning 1.0
        return 1.0

    state_df_keys = set(state_df_keys)
    target_df_keys = set(target_df_keys)

    # Count number of keys in the intersection
    intersection = state_df_keys.intersection(target_df_keys)
    if len(target_df_keys) == 0:
        return 0.0
    return len(intersection) / len(target_df_keys)


def generate_next_states(
    args, state, config, save_dir, i_state, target_df, target_fds
) -> list[State]:
    """
    Generate the next states based on the current state.
    This is a placeholder function and should be implemented based on the specific requirements.
    """

    next_states = []
    ops_and_configs = get_operators(state, state.step + 1, args, config)

    for j, (op, op_config) in enumerate(ops_and_configs):
        terminate_due_to_error = False
        is_terminal = op == "NO_MORE_OPERATION"
        next_step = state.step + 1
        history = list(state.history) + [f"{op} : {op_config}"]
        if is_terminal:
            result_csv_path = state.result_csv_path
        else:
            result_csv_path = f"{save_dir}/tree_step{next_step}_{i_state}_{j}.csv"
            result_python_path = f"{save_dir}/tree_step{next_step}_{i_state}_{j}.py"

            # Materialize the operation
            try:
                materialize_chatgpt(
                    history, args, config, result_csv_path, result_python_path
                )

            except Exception as e:
                result_csv_path = state.result_csv_path
                terminate_due_to_error = True
                is_terminal = True

        # Calculate the column mapping score
        result_df = pd.read_csv(result_csv_path)
        col_mapping_score = calculate_score(target_df, result_df, config["logger"])
        # Calculate the functional dependency/key matching score
        fds = analyze_functional_dependencies(result_df, config["logger"])
        fd_key_score = calculate_fd_key_score(fds, target_fds)

        # Get hints for column mapping, functional dependencies, and keys
        next_state = State(
            step=next_step,
            history=tuple(history),
            is_terminal=is_terminal,
            terminate_due_to_error=terminate_due_to_error,
            result_csv_path=result_csv_path,
            col_mapping_score=col_mapping_score,
            fd_key_score=fd_key_score,
            parent=state,
            fds=tuple(fds),
        )
        next_states.append(next_state)

    log_str = f"Current state: {state}.\nNext states:\n"
    log_str += "\n".join([str(next_state) for next_state in next_states])
    print(log_str)
    config["logger"].info(log_str)
    return next_states


def llm_prune(states, config, args, max_trials=5) -> list[int]:
    """
    Prune the states based on some criteria using LLM.
    This is a placeholder function and should be implemented based on the specific requirements.
    """
    for _ in range(max_trials):
        prompt = get_prompt(
            prompt_type="prune_states",
            max_tokens=args.token_limit,
            model=args.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=None,
            target_data_name=config["target_data_name"],
            target_data_schema=config["target_data_schema"],
            target_samples=config["target_samples"],
            file_count=config["file_count"],
            source_data_name_list=config["source_data_name_list"],
            source_data_schema_list=config["source_data_schema_list"],
            logger=config["logger"],
            directory=config["source_space_dir"],
            len_idx_target_idx=config["len_idx_target_idx"],
            target_perc=args.target_per,
            is_perc=args.is_perc,
            target_length=args.target_length,
            source_length=args.source_length,
            fd_flag=args.fd_flag,
            hint_source=args.hint_source,
            args=args,
            states=states,
        )

        res = query_gpt(
            config["llm_client"],
            config["llm_client"].model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type="Prune States",
        )[0]

        # Extract the indices of the states to keep

        match = re.search(r"Final output indices:(.*)", res, re.IGNORECASE)
        if match:
            indices_str = match.group(1)
            try:
                indices = [int(num) for num in re.findall(r"\d+", indices_str)]
                return indices
            except:
                print(f"Failed to extract indices from: {indices_str}")
                continue
        else:
            continue

    raise Exception(
        f"Failed to prune states after {max_trials} tries. Last response:\n{res}"
    )


def fd_key_prune(states: list[State], keepn_every_criterion: int) -> list[int]:
    """
    Prune the states based on functional dependency keys.
    """
    # Sort states by fd_key_score
    indexed_list = list(enumerate(states))
    indexed_list.sort(key=lambda x: x[1].fd_key_score, reverse=True)
    top_n_indices = [index for index, _ in indexed_list[:keepn_every_criterion]]
    return top_n_indices


def col_mapping_prune(states: list[State], keepn_every_criterion: int) -> list[int]:
    """
    Prune the states based on column mapping.
    """
    # Sort states by col_mapping_score and fd_key_score
    indexed_list = list(enumerate(states))
    indexed_list.sort(key=lambda x: x[1].fd_key_score, reverse=True)
    # Keep the top N states based on the criteria
    top_n_indices = [index for index, _ in indexed_list[:keepn_every_criterion]]
    return top_n_indices


def prune_states(states, config, args) -> list[State]:
    """
    Prune the states based on some criteria.
    This is a placeholder function and should be implemented based on the specific requirements.
    """
    if len(states) <= args.keepn_every_criterion:
        # If the number of states is less than or equal to the keepn_every_criterion, return them as is
        return states

    llm_pruned_indices = llm_prune(states, config, args)
    fd_key_pruned_indices = fd_key_prune(states, args.keepn_every_criterion)
    col_mapping_pruned_indices = col_mapping_prune(states, args.keepn_every_criterion)
    # Combine pruned states; remove deplicated states
    pruned_indices = set(
        llm_pruned_indices + fd_key_pruned_indices + col_mapping_pruned_indices
    )
    pruned_states = [states[i] for i in pruned_indices if i < len(states)]

    log_str = "Pruned states:\n" + "\n".join([str(state) for state in pruned_states])
    print(log_str)
    config["logger"].info(log_str)
    return pruned_states


def get_best_state(states: list[State]) -> int:
    """Get the best state based on the col_mapping_score."""
    index = col_mapping_prune(states, 1)[0]
    # For critique, copy result_csv file to a new file named target_multisource.csv
    best_state = states[index]
    df = pd.read_csv(best_state.result_csv_path)
    target_csv_path = os.path.join(
        os.path.dirname(best_state.result_csv_path), "target_multisource.csv"
    )
    df.to_csv(target_csv_path, index=False)
    return best_state


def BFS(args, save_dir, config):
    terminal_states = []
    target_df = pd.read_csv(f"{save_dir}/target.csv")
    target_fds = analyze_functional_dependencies(target_df, config["logger"])
    initial_state = State(
        result_csv_path=f"{save_dir}/test_0.csv", fds=tuple(target_fds)
    )
    states = [initial_state]

    for step in range(1, args.max_steps + 1):
        states_at_next_step = []
        for i, state in enumerate(states):
            next_states = generate_next_states(
                args, state, config, save_dir, i, target_df, target_fds
            )
            states_at_next_step.extend(next_states)

        # Prune the states
        pruned_states = prune_states(
            terminal_states + states_at_next_step, config, args
        )

        terminal_states = []
        states = []
        for state in pruned_states:
            if state.is_terminal:
                terminal_states.append(state)
            else:
                states.append(state)
        if states == []:
            break

    best_state = get_best_state(terminal_states)
    return best_state


def tree_of_thoughts(args, length, id_, log_dir):
    start_time = time.time()
    len_id = length
    max_len_id = length
    target_id = id_
    max_target_id = id_

    main_folder = "autopipeline-benchmarks/github-pipelines"
    path_to_files = f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/"
    source_space_dir = create_source_space(main_folder, len_id, target_id)

    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )
    if file_count > 1:
        json_file_path = "data/chatgpt_github_ms.json"
    else:
        json_file_path = "data/chatgpt_github_ss.json"

    # logging
    logger = create_logger(
        "tree_of_thoughts", log_dir, len_id, target_id, max_target_id
    )
    task = get_task(
        logger, json_file_path, len_id, max_len_id, target_id, max_target_id
    )
    len_idx_target_idx = task.lstrip("Target")
    save_dir = f"{source_space_dir}/length{len_idx_target_idx}"

    q_count = {"total": 0, "in_task": 0}

    cost_summary = []
    token_tracker = TokenUsageTracker()
    cost_summary.append(token_tracker.cost_summary())
    # print(cost_summary)

    # Get the information of the target and source data
    (
        target_data_name,
        target_data_schema,
        target_samples,
        file_count,
        source_data_name_list,
        source_data_schema_list,
        source_samples_list,
    ) = get_test_info(
        json_file_path,
        len_idx_target_idx,
        main_folder,
        anon_flag=0,
    )

    llm_client = LLMClient(model=args.model, tracker=token_tracker, logger=logger)

    # configure all the remaining parameters used by later functions
    config = {}
    config["q_count"] = q_count
    config["cost_summary"] = cost_summary
    config["token_tracker"] = token_tracker
    config["logger"] = logger
    config["llm_client"] = llm_client
    config["source_space_dir"] = source_space_dir
    config["len_idx_target_idx"] = len_idx_target_idx
    config["target_data_name"] = target_data_name
    config["target_data_schema"] = target_data_schema
    config["target_samples"] = target_samples
    config["file_count"] = file_count
    config["source_data_name_list"] = source_data_name_list
    config["source_data_schema_list"] = source_data_schema_list
    config["source_samples_list"] = source_samples_list
    config["main_folder"] = main_folder
    config["path_to_files"] = path_to_files
    config["task"] = task

    best_state = BFS(args, save_dir, config)

    # Do the final verification
    hard_match_result, soft_match_result = verify_result(
        best_state.result_csv_path,
        f"{main_folder}/length{len_idx_target_idx}/target.csv",
        config,
    )

    end_time = time.time()
    time_elapsed = end_time - start_time
    cost_data = token_tracker.cost_summary()  # This returns a dictionary
    total_cost = cost_data.get("total_cost", 0.0)
    ms_info = (
        hard_match_result["is_correct"],
        soft_match_result["is_correct"],
        soft_match_result["avg_similarity"],
        total_cost,  # Use the extracted total_cost value
        time_elapsed,
        0,
        str(best_state.history),
    )
    return ms_info
