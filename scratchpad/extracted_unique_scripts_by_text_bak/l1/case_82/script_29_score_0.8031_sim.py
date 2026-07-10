import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df_union = df0.copy()

df_grouped = df_union.groupby("conservation_status", dropna=False).agg(scientific_name=("scientific_name", "count")).reset_index()

df_grouped["conservation_status"] = df_grouped["conservation_status"].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)