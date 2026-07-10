import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

agg = merged.groupby(["city", "driver_count", "type"]).agg(
    **{
        "Average Fare": ("fare", "mean"),
        "Ride Count": ("ride_id", "count")
    }
).reset_index()

agg = agg[["city", "driver_count", "type", "Average Fare", "Ride Count"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_28/target_multisource_mcts.csv", index=False)