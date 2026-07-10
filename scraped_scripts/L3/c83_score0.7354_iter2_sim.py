import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

joined = pd.merge(source1, source2, on="bidder_id", how="inner")

agg = joined.groupby("bidder_id").agg(
    payment_account=("payment_account", "first"),
    address=("address", "first"),
    outcome=("bid_id", lambda x: float('nan')),  # outcome not in source1 or source2, will fill NaN
    bids_count=("bid_id", "count")
).reset_index()

# outcome column is in source0, so merge it in to get outcome values where available
agg = pd.merge(agg, source0[["bidder_id", "outcome"]], on="bidder_id", how="left", suffixes=("", "_src0"))
agg["outcome"] = agg["outcome_src0"]
agg.drop(columns=["outcome_src0"], inplace=True)

agg = agg.astype({
    "bidder_id": str,
    "payment_account": str,
    "address": str,
    "outcome": float,
    "bids_count": int
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)