import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

# UNION Source3_83_0 and Source3_83_1 (both have bidder_id, payment_account, address, outcome in source0)
# For union, columns must match, so drop 'outcome' from source0 to match source1 schema
source0_bidder_info = source0.drop(columns=["outcome"])
unioned_bidder_info = pd.concat([source0_bidder_info, source1], ignore_index=True).drop_duplicates(subset=["bidder_id", "payment_account", "address"])

# JOIN unioned bidder info with source2 (bids) on bidder_id
joined = pd.merge(unioned_bidder_info, source2, on="bidder_id", how="inner")

# GROUP BY bidder_id, payment_account, address and count bids (bid_id)
grouped = joined.groupby(["bidder_id", "payment_account", "address"], as_index=False).agg(
    bids_count=("bid_id", "count")
)

# JOIN grouped result with source0 to get outcome (source0 has outcome)
result = pd.merge(grouped, source0[["bidder_id", "outcome"]], on="bidder_id", how="left")

# Reorder columns to match target schema
result = result[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

# Ensure correct dtypes
result = result.astype({
    "bidder_id": str,
    "payment_account": str,
    "address": str,
    "outcome": float,
    "bids_count": int
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)