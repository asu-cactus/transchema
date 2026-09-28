import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

# Strip whitespace from 'neighbourhood' column
df0["neighbourhood"] = df0["neighbourhood"].str.strip()

# Group by 'neighbourhood' and aggregate mean price
result = df0.groupby("neighbourhood", as_index=False).agg(price_24=("price", "mean"))

# Round and convert price_24 to int
result["price_24"] = result["price_24"].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)