import pandas as pd

# Read all source tables (only one given here)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)

# If there were multiple source tables, they would be read similarly and concatenated here
df_union = pd.concat([df0], ignore_index=True)

# Group by movieId and compute mean rating
result = df_union.groupby("movieId", as_index=False)["rating"].mean()

# Ensure correct types as per target schema
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)