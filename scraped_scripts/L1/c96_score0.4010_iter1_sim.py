import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0_unpivot = df0[['Publisher']].copy()

df1_renamed = df1.rename(columns={'hero_names': 'Publisher'})
df1_projected = df1_renamed[['Publisher']]

result = pd.concat([df0_unpivot, df1_projected], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)