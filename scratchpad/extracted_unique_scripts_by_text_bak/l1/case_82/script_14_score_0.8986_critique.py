import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df0_filtered = df0.dropna(subset=['conservation_status'])

grouped = df0_filtered.groupby('conservation_status').agg(scientific_name=('scientific_name', pd.Series.nunique)).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)