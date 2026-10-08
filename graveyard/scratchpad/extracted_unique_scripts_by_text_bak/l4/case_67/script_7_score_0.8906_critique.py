import pandas as pd

# Read the single source table (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

# If multiple source tables existed, we would union them here, but only one is given.
# So union is trivial (just df0).

# Group by "Batsman on strike" and sum overs, runs scored, extras
agg = df0.groupby("Batsman on strike").agg({
    "overs": "sum",
    "runs scored": "sum",
    "extras": "sum"
}).reset_index()

# Convert types to match target schema
agg["overs"] = agg["overs"].astype(float)
agg["runs scored"] = agg["runs scored"].astype(int)
agg["extras"] = agg["extras"].astype(int)

# Write output with exact target schema column order
agg = agg[["Batsman on strike", "overs", "runs scored", "extras"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)