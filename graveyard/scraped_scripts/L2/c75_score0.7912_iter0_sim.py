import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_1.csv", index_col=0)

grouped = df1.groupby("city", as_index=False)["ride_id"].count()
grouped.rename(columns={"ride_id": "ride_id"}, inplace=True)

result = grouped[["city", "ride_id"]]
result["ride_id"] = result["ride_id"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_75/target_multisource_mcts.csv", index=False)