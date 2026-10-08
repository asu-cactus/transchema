import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

agg = df2.groupby("bidder_id").agg(
    bids_count=("auction", "count"),
    device_count=("device", pd.Series.nunique),
    country_count=("country", pd.Series.nunique)
).reset_index()

join_0 = pd.merge(agg, df0, on="bidder_id", how="left")
join_1 = pd.merge(join_0, df1, on="bidder_id", how="left", suffixes=('', '_y'))

result = join_1[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)