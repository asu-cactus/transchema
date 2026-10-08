import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

grouped = df0.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

grouped = grouped.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

grouped["sad"] = grouped["sad"].astype(float)
grouped["stressed"] = grouped["stressed"].astype(float)
grouped["user_id"] = grouped["user_id"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)