import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df_proj = df0[['fac_type', 'capacity']]
df_grouped = df_proj.groupby('fac_type', as_index=False)['capacity'].sum()
df_grouped['capacity'] = df_grouped['capacity'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)