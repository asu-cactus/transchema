import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

grouped = df0.groupby("conservation_status", dropna=False).agg(scientific_name=("scientific_name", "count")).reset_index()

grouped = grouped.rename(columns={"conservation_status": "conservation_status", "scientific_name": "scientific_name"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)