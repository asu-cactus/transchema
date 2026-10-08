import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df0 = df0.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})

df_pivot = df0.groupby("user_id")[["sad", "stressed"]].mean().reset_index()

df_pivot["sad"] = df_pivot["sad"].astype(float)
df_pivot["stressed"] = df_pivot["stressed"].astype(float)
df_pivot["user_id"] = df_pivot["user_id"].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)