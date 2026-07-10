import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg = source0.groupby("city").agg(
    **{
        "Average Fare ($)": ("fare", "mean"),
        "Number of Rides": ("ride_id", "count"),
    }
).reset_index()

joined = agg.merge(source1, how="inner", on="city")

result = joined.rename(columns={"city": "City", "driver_count": "Number of Drivers", "type": "City Type"})

result = result[["City", "Average Fare ($)", "Number of Rides", "Number of Drivers", "City Type"]]

result["Number of Drivers"] = result["Number of Drivers"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)