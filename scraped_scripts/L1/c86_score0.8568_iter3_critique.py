import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

df0["neighbourhood"] = df0["neighbourhood"].str.strip()

filtered = df0[df0["price"] <= 24]

result = filtered.groupby("neighbourhood", as_index=False)["id"].count()

result = result.rename(columns={"id": "price_24"})

result["price_24"] = result["price_24"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)