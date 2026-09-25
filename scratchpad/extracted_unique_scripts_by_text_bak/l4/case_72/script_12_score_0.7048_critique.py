import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(df0, df1, on="city", how="inner")

# Group by city and aggregate
final = joined.groupby("city").agg(
    a=("fare", "mean"),
    b=("ride_id", "count")
).reset_index()

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)