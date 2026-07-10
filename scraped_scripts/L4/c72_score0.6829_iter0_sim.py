import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

grouped = df0.groupby("city").agg(a=("fare", "mean"), b=("ride_id", "count")).reset_index()

result = pd.merge(grouped, df1[["city"]], on="city", how="inner")

result = result[["city", "a", "b"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)