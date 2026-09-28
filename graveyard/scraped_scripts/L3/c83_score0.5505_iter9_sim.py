import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_83/training_2.csv", index_col=0)

agg_source2 = source2.groupby("bidder_id").agg(bids_count=("bid_id", "nunique")).reset_index()

joined_0_2 = pd.merge(agg_source2, source0, on="bidder_id", how="left")

joined_0_2 = joined_0_2[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

source1 = source1.assign(outcome=pd.NA, bids_count=pd.NA)
source1 = source1[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

result = pd.concat([joined_0_2, source1], ignore_index=True)

result["bidder_id"] = result["bidder_id"].astype(str)
result["payment_account"] = result["payment_account"].astype(str)
result["address"] = result["address"].astype(str)
result["outcome"] = pd.to_numeric(result["outcome"], errors='coerce')
result["bids_count"] = pd.to_numeric(result["bids_count"], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_83/target_multisource_mcts.csv", index=False)