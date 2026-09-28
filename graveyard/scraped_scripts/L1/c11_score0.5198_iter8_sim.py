import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
result = union_df[['sex', 'births']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)