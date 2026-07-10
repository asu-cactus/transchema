import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg = df0.groupby("city").agg({"fare": "mean", "ride_id": "count"}).reset_index()
agg.columns = ["city", "Average Fare ($)", "Number of Rides"]

merged = pd.merge(agg, df1, how="inner", on="city")

result = merged.rename(columns={"driver_count": "Number of Drivers", "type": "City Type"})

result["Number of Drivers"] = result["Number of Drivers"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)