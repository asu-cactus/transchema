import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

agg_df1 = df1.groupby("city").agg(
    Average_Fare=("fare", "mean"),
    ride_id=("ride_id", "mean"),
    Total_Number_of_Rides=("ride_id", "count")
).reset_index().rename(columns={"city": "City"})

df0_renamed = df0.rename(columns={"city": "City", "driver_count": "Total Number of Drivers", "type": "City Type"})

result = pd.merge(
    agg_df1,
    df0_renamed,
    how="inner",
    on="City"
)

result = result[[
    "City",
    "Average_Fare",
    "ride_id",
    "Total_Number_of_Rides",
    "City Type",
    "Total Number of Drivers"
]]

result.columns = [
    "City",
    "Average Fare",
    "ride_id",
    "Total Number of Rides",
    "City Type",
    "Total Number of Drivers"
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)