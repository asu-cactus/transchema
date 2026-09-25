import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

grouped = df0.groupby("neighbourhood").agg(price_24=("price", "sum")).reset_index()

grouped["price_24"] = grouped["price_24"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)