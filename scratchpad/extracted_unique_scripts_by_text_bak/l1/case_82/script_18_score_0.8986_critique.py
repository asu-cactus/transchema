import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df_filtered = df0[df0['conservation_status'].notna()]

result = df_filtered.groupby('conservation_status', as_index=False).agg(scientific_name=('scientific_name', pd.Series.nunique))

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)