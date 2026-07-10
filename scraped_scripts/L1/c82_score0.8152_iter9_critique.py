import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Group by conservation_status and count distinct scientific_name
grouped = df0.groupby("conservation_status", dropna=False).agg(scientific_name=("scientific_name", pd.Series.nunique)).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)