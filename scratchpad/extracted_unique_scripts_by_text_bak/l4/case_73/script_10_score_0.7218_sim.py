import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg0 = df0.groupby("city").agg({"fare":"mean", "ride_id":"count"}).rename(columns={"fare":"Average Fare ($)", "ride_id":"Number of Rides"})
agg1 = df1.set_index("city")

merged = agg0.join(agg1, how="inner")

result = merged.rename(columns={"driver_count":"Number of Drivers", "type":"City Type"}).reset_index()
result["Number of Drivers"] = result["Number of Drivers"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)