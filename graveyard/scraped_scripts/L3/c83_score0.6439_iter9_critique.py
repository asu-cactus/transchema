import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

# Add missing columns to source1 to match source0 schema
source1 = source1.assign(outcome=pd.NA, bids_count=pd.NA)
source1 = source1[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

# Add bids_count column to source0 to match schema for union
source0 = source0.assign(bids_count=pd.NA)
source0 = source0[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

# UNION source0 and source1
unioned_source = pd.concat([source0, source1], ignore_index=True)

# Aggregate source2 to get bids_count per bidder_id
agg_source2 = source2.groupby("bidder_id", as_index=False).agg(bids_count=("bid_id", "nunique"))

# JOIN unioned_source with agg_source2 on bidder_id (left join to keep all bidders)
joined = pd.merge(unioned_source, agg_source2, on="bidder_id", how="left", suffixes=("", "_agg"))

# bids_count from source2 aggregation is in bids_count_agg, fill missing with 0
joined["bids_count_agg"] = pd.to_numeric(joined["bids_count_agg"], errors='coerce').fillna(0).astype(int)

# For bids_count column, prefer bids_count_agg if present, else 0
# Since source0 and source1 have NaN bids_count, replace with bids_count_agg
joined["bids_count"] = joined["bids_count_agg"]

# Drop the extra bids_count_agg column
joined = joined.drop(columns=["bids_count_agg"])

# Group by key columns to remove duplicates and sum bids_count
result = joined.groupby(
    ["bidder_id", "payment_account", "address", "outcome"], as_index=False
).agg(bids_count=("bids_count", "sum"))

# Ensure correct dtypes
result["bidder_id"] = result["bidder_id"].astype(str)
result["payment_account"] = result["payment_account"].astype(str)
result["address"] = result["address"].astype(str)
result["outcome"] = pd.to_numeric(result["outcome"], errors='coerce')
result["bids_count"] = result["bids_count"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)