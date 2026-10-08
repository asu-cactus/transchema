import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_1.csv", index_col=0)

grouped = df1.groupby("city", as_index=False).agg(ride_id=("ride_id", "count"))

joined = pd.merge(df0, grouped, on="city", how="inner")

result = joined[["city", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_34/target_multisource_mcts.csv", index=False)