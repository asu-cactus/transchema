import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(source0, source1, how="inner", on="city")

# Group by city, driver_count, type and aggregate
agg = joined.groupby(["city", "driver_count", "type"]).agg(
    **{
        "Average Fare": ("fare", "mean"),
        "Ride Count": ("ride_id", "count"),
    }
).reset_index()

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_50/target_multisource_mcts.csv", index=False)