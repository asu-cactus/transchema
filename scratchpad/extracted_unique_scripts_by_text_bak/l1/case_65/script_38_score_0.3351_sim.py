import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df_proj = df[['year', 'revenue']].copy()
df_proj['0'] = df_proj['revenue'].fillna(0).astype(int)
df_proj = df_proj[['year', '0']]
df_proj['year'] = df_proj['year'].astype(int)
df_proj['0'] = df_proj['0'].astype(int)
df_proj.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)