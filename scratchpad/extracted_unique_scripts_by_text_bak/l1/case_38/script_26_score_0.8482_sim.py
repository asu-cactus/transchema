import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

result = df0.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

result = result.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

result["user_id"] = result["user_id"].astype(int)
result["sad"] = result["sad"].astype(float)
result["stressed"] = result["stressed"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)