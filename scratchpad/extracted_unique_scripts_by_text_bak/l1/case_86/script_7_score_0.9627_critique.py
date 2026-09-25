import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

# Clean the 'neighbourhood' column by stripping leading/trailing spaces
df0["neighbourhood"] = df0["neighbourhood"].str.strip()

result = df0.groupby("neighbourhood", as_index=False)["price"].mean()
result["price_24"] = result["price"].round().astype(int)
result = result[["neighbourhood", "price_24"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)