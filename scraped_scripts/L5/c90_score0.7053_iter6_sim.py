import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv", index_col=0)

agg = source0.groupby("city").agg(
    Average_Fare=("fare", "mean"),
    Total_Number_of_Rides=("ride_id", "count"),
).reset_index()

joined = pd.merge(agg, source1, how="inner", left_on="city", right_on="city")

result = pd.DataFrame()
result["City"] = joined["city"]
result["Average Fare"] = joined["Average_Fare"].astype(float)
result["ride_id"] = joined["Total_Number_of_Rides"].astype(float)  # ride_id column in target is float, use count as proxy
result["Total Number of Rides"] = joined["Total_Number_of_Rides"].astype(int)
result["City Type"] = joined["type"]
result["Total Number of Drivers"] = joined["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv", index=False)