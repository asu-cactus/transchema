import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df_filtered = df0[df0['conservation_status'].notna()]
df_projected = df_filtered[['conservation_status', 'scientific_name']].copy()
df_projected['scientific_name'] = pd.to_numeric(df_projected['scientific_name'], errors='coerce').astype('Int64')
df_projected.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)