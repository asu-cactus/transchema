import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_35/training_2.csv", index_col=0)

agg = src0.groupby("bidder_id", as_index=False).agg(bids_count=("bid_id", "count"))

join1 = pd.merge(agg, src1, on="bidder_id", how="left")

final = pd.merge(join1, src2[["bidder_id", "outcome"]], on="bidder_id", how="left")

final = final[["bidder_id", "payment_account", "address", "outcome", "bids_count"]]

final["outcome"] = pd.to_numeric(final["outcome"], errors='coerce').astype(float)

final["country"] = src0.groupby("bidder_id", as_index=False).agg(country=("country", "first"))["country"]

final = final[["bidder_id", "payment_account", "address", "outcome", "country", "bids_count"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_35/target_multisource_mcts.csv", index=False)