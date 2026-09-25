import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_2.csv", index_col=0)

df_union = pd.concat([df0, df1, df2], ignore_index=True)
df_proj = df_union[['fac_type', 'capacity']]
df_grouped = df_proj.groupby('fac_type', as_index=False)['capacity'].sum()
df_grouped['capacity'] = df_grouped['capacity'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)