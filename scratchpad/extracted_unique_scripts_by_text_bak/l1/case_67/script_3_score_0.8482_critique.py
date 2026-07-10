import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)
df0 = df0.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})
df0 = df0[["user_id", "sad", "stressed"]]
df0["sad"] = df0["sad"].astype(float)
df0["stressed"] = df0["stressed"].astype(float)
df0["user_id"] = df0["user_id"].astype(int)

# Group by user_id and aggregate sad and stressed by mean
df_agg = df0.groupby("user_id", as_index=False).agg({"sad": "mean", "stressed": "mean"})

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)