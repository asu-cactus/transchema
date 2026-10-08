import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

# Join on city
joined = source0.merge(source1, how="inner", on="city")

# Group by city to get average fare and number of rides
agg = joined.groupby("city").agg(
    **{
        "Average Fare ($)": ("fare", "mean"),
        "Number of Rides": ("ride_id", "count"),
        "Number of Drivers": ("driver_count", "first"),
        "City Type": ("type", "first"),
    }
).reset_index()

# Rename city to City
result = agg.rename(columns={"city": "City"})

# Ensure Number of Drivers is integer type
result["Number of Drivers"] = result["Number of Drivers"].astype("Int64")

# Reorder columns to match target schema
result = result[["City", "Average Fare ($)", "Number of Rides", "Number of Drivers", "City Type"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)