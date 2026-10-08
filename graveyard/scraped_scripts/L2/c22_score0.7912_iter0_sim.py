import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_22/training_1.csv", index_col=0)

grouped = df0.groupby("city", as_index=False).agg({"ride_id": "count"})
grouped = grouped.rename(columns={"ride_id": "ride_id"})
grouped["ride_id"] = grouped["ride_id"].astype(int)
grouped["city"] = grouped["city"].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_22/target_multisource_mcts.csv", index=False)