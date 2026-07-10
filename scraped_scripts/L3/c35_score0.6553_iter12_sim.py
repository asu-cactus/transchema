import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2], ignore_index=True, sort=False)

joined = pd.merge(union_result, source0, on="bidder_id", how="inner")

result = pd.DataFrame()
result["bidder_id"] = joined["bidder_id"].astype(str)
result["payment_account"] = joined["payment_account"].astype(str)
result["address"] = joined["address"].astype(str)
result["outcome"] = pd.to_numeric(joined["outcome"], errors='coerce').astype(float)
result["country"] = joined["country"].astype(str)
result["bids_count"] = joined.groupby("bidder_id")["bid_id"].transform("count").astype(int)

result = result[["bidder_id", "payment_account", "address", "outcome", "country", "bids_count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)