import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

# Normalize user_id to lowercase to match target examples
df0["user_id"] = df0["user_id"].str.lower()

# Output with exact target schema and column order
result = df0[["user_id", "email", "geo"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)