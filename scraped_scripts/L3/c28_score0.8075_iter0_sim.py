import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_1.csv", index_col=0)

agg = df1.groupby("city").agg(Average_Fare=("fare", "mean"), Ride_Count=("ride_id", "count")).reset_index()

result = pd.merge(df0, agg, on="city", how="inner")

result = result.rename(columns={"Average_Fare": "Average Fare", "Ride_Count": "Ride Count"})

result = result[["city", "driver_count", "type", "Average Fare", "Ride Count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_28/target_multisource_mcts.csv", index=False)