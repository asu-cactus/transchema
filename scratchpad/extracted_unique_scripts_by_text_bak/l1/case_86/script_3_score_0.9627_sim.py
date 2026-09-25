import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

agg = df0.groupby("neighbourhood", as_index=False)["price"].mean()
agg["price_24"] = agg["price"].round().astype(int)
result = agg[["neighbourhood", "price_24"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)