import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df = df0.copy()
df_agg = df.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

df_agg = df_agg.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

df_agg["user_id"] = df_agg["user_id"].astype(int)
df_agg["sad"] = df_agg["sad"].astype(float)
df_agg["stressed"] = df_agg["stressed"].astype(float)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)