import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

join_0_1 = pd.merge(source0, source1, on="bidder_id", how="inner")

union_1_2 = pd.concat([source1, source2], ignore_index=True, sort=False).drop_duplicates(subset=["bidder_id", "payment_account", "address", "outcome"])

final_join = pd.merge(union_1_2, source0, on="bidder_id", how="left")

result = final_join[["bidder_id", "payment_account", "address", "outcome", "country", "bid_id"]].copy()

result["bids_count"] = result.groupby("bidder_id")["bid_id"].transform("count")

result = result.drop(columns=["bid_id"])

result["outcome"] = pd.to_numeric(result["outcome"], errors="coerce")
result["bids_count"] = result["bids_count"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)