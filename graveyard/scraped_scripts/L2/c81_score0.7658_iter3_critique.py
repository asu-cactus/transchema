import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)

# Join on city (inner join to keep only matching cities)
joined = pd.merge(source0, source1, on="city", how="inner")

# Group by city and sum driver_count
agg = joined.groupby("city", as_index=False)["driver_count"].sum()

agg["driver_count"] = agg["driver_count"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_81/target_multisource_mcts.csv", index=False)