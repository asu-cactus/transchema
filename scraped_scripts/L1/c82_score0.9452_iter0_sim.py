import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df0_grouped = df0.groupby("conservation_status", dropna=True).agg(scientific_name=("scientific_name", "count")).reset_index()
df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)