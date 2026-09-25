import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

# Add outcome column to df1 with default 0.0 (float)
df1["outcome"] = 0.0

# Ensure columns order and names match for union
df0_subset = df0[["bidder_id", "payment_account", "address", "outcome"]]
df1_subset = df1[["bidder_id", "payment_account", "address", "outcome"]]

# UNION Source0 and Source1
unioned = pd.concat([df0_subset, df1_subset], ignore_index=True)

# Group by bidder_id, payment_account, address and aggregate outcome by max (to keep 1 if any)
grouped_outcome = unioned.groupby(
    ["bidder_id", "payment_account", "address"], as_index=False
).agg(
    outcome=("outcome", "max")
)

# Count bids per bidder_id from Source2
bids_count = df2.groupby("bidder_id", as_index=False).agg(bids_count=("bid_id", "count"))

# Join grouped_outcome with bids_count on bidder_id
result = pd.merge(
    grouped_outcome,
    bids_count,
    on="bidder_id",
    how="inner"
)

# Reorder columns to match target schema
result = result[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

# Cast types to match target schema
result["outcome"] = result["outcome"].astype(float)
result["bids_count"] = result["bids_count"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)