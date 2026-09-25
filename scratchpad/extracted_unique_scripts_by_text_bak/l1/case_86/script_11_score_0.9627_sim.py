import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)
result = df0.groupby("neighbourhood", as_index=False).agg(price_24=("price", "mean"))
result["price_24"] = result["price_24"].round().astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)