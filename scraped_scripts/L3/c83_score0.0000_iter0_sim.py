import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="bidder_id", suffixes=('_0', '_1'))
join_012 = pd.merge(join_01, df2, on="bidder_id")

grouped = join_012.groupby(
    ["bidder_id", "payment_account_0", "address_0"],
    as_index=False
).agg(
    outcome=("outcome", "sum"),
    bids_count=("bid_id", "count")
)

grouped = grouped.rename(columns={
    "payment_account_0": "payment_account",
    "address_0": "address",
    "outcome": "outcome",
    "bids_count": "bids_count"
})

grouped["outcome"] = grouped["outcome"].astype(float)
grouped["bids_count"] = grouped["bids_count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)