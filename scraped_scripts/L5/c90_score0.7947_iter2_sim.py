import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv", index_col=0)

agg = df0.groupby("city").agg(
    Average_Fare=("fare", "mean"),
    ride_id=("ride_id", "mean"),
    Total_Number_of_Rides=("ride_id", "count"),
).reset_index()

merged = pd.merge(df1, agg, how="inner", left_on="city", right_on="city")

result = merged.rename(columns={
    "city": "City",
    "Average_Fare": "Average Fare",
    "ride_id": "ride_id",
    "Total_Number_of_Rides": "Total Number of Rides",
    "type": "City Type",
    "driver_count": "Total Number of Drivers"
})[
    ["City", "Average Fare", "ride_id", "Total Number of Rides", "City Type", "Total Number of Drivers"]
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv", index=False)