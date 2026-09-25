import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_50/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_50/training_1.csv", index_col=0)

merged = pd.merge(df0[['ID', 'sex']], df1, on='ID')
result = merged[['sex', 'G1', 'G2', 'G3']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_50/target_multisource_mcts.csv", index=False)