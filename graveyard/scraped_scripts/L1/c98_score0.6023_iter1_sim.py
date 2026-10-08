import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={'0': '0_x', 'right_index': '0_y'})[['0_x', '0_y']]
df1_expanded = df1.copy()
df1_expanded['0_y'] = pd.NA
df1_expanded = df1_expanded.rename(columns={'0': '0_x'})[['0_x', '0_y']]

result = pd.concat([df0_renamed, df1_expanded], ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)