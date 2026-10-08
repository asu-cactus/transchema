import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

# Clean 'neighbourhood' column by stripping spaces
df0["neighbourhood"] = df0["neighbourhood"].str.strip()

# Group by cleaned 'neighbourhood' and compute average price
result = df0.groupby("neighbourhood", as_index=False)["price"].mean()

# Rename and convert price to int
result.rename(columns={"price": "price_24"}, inplace=True)
result["price_24"] = result["price_24"].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)