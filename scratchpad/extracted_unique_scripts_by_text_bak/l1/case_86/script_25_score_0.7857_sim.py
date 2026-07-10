import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

grouped = df0.groupby("neighbourhood").agg(price_sum=("price", "sum"), id_count=("id", "count")).reset_index()

result = grouped.rename(columns={"neighbourhood": "neighbourhood", "price_sum": "price_24"})[["neighbourhood", "price_24"]]

result["price_24"] = result["price_24"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)