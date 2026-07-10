import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_1.csv", index_col=0)

agg = source0.groupby("city").agg(
    **{
        "Ride Count": ("ride_id", "count"),
        "Average Fare": ("fare", "mean"),
    }
).reset_index()

result = pd.merge(source1, agg, how="inner", on="city")

result = result.rename(columns={"driver_count": "driver_count", "type": "type"})

result = result[["city", "driver_count", "type", "Average Fare", "Ride Count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_50/target_multisource_mcts.csv", index=False)