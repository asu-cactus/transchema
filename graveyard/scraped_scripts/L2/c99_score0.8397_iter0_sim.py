import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_99/training_1.csv", index_col=0)

groupby_result = df1.groupby("city", as_index=False).size().rename(columns={"size": "driver_count"})

joined = pd.merge(df0, groupby_result, on="city", how="inner")

result = joined[["city", "driver_count_x"]].rename(columns={"driver_count_x": "driver_count"})
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_99/target_multisource_mcts.csv", index=False)