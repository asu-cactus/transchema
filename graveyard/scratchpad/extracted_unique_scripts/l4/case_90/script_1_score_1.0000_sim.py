import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_3.csv", index_col=0)

union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

result = union_df.groupby('occluded', as_index=False).size().rename(columns={'size': 'count'})

# The target schema only requires 'occluded' column, so we keep only that column.
# The target examples show just occluded values 0 and 1, so we output those unique occluded values.
# The aggregation count is not needed in the final output, so we drop it.
final_result = result[['occluded']]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_90/target_multisource_mcts.csv", index=False)