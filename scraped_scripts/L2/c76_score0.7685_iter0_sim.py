import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_76/training_0.csv", index_col=0)

result = df0.groupby("city", as_index=False).agg({
    "fare": "mean",
    "ride_id": "count"
})

result = result.rename(columns={"ride_id": "ride_id"})
result["ride_id"] = result["ride_id"].astype(int)
result["fare"] = result["fare"].astype(float)
result["city"] = result["city"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_76/target_multisource_mcts.csv", index=False)