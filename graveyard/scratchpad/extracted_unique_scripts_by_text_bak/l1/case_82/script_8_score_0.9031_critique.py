import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df_filtered = df0[df0['conservation_status'].notna()]
df_grouped = df_filtered.groupby('conservation_status', dropna=False).agg({'scientific_name': 'count'}).reset_index()
df_grouped['scientific_name'] = df_grouped['scientific_name'].astype('Int64')
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)