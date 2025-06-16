def prune_states_prompt(
    states,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information,
    fd_hints,
    keepn_next_operators,
):

    fd_hints = f"\nFunctional Dependency Hints:\n{fd_hints}" if fd_hints.strip() else ""
    candidate_pipelines = "\n".join(
        [
            f"Pipeline {i}. Operation History: {state.history}; Completed: {state.is_terminal};"
            for i, state in enumerate(states)
        ]
    )
    prompt = f"""
You are an experienced data engineer.
Your colleague has generated some potential data pipelines to transform multiple source tables to target table. Some of them are complete pipeline, while some of them are not completed.
You need to decide which {keepn_next_operators} pipeline(s) are most likely to achieve correct data transformation.

Take this decision based on "operation history", intermediate tables and source, target table schema and examples.

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The above row examples provided are only part of the corresponding rows.

{fd_hints}

Here are candidate pipelines:
{candidate_pipelines}

More instructions:
1. For incomplete pipelines, you can consider its potential by completing the pipeline.
2. After thinking step by step, please output a python list of the indices of the {keepn_next_operators} most likely pipeline(s) strictly follow this format:
Final output indices: [index1,index2,...]
For example, 
Final output indices: [0,2,3]
    """
    return [prompt]
