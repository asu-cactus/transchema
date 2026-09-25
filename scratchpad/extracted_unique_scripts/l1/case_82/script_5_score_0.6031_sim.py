import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df_filtered = df0[(df0['conservation_status'].notna()) & (df0['conservation_status'] != '')]
df_filtered = df_filtered[['conservation_status', 'scientific_name']]
df_filtered['scientific_name'] = pd.to_numeric(df_filtered['scientific_name'], errors='coerce').fillna(0).astype(int)
df_filtered.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)