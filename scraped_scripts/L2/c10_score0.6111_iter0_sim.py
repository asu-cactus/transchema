import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

groupby_result = df0.groupby("city", as_index=False).agg(driver_count=("ride_id", "count"))

union_df = pd.concat([groupby_result[["city", "driver_count"]], df1[["city", "driver_count"]]], ignore_index=True)

result = pd.merge(union_df, df1[["city", "driver_count"]], on="city", how="inner", suffixes=('_left', ''))
# After merge, driver_count from df1 is kept, so drop the left one
result = result[["city", "driver_count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)