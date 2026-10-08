import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df = df0.copy()
df = df.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})
df = df[["user_id", "sad", "stressed"]]
df["user_id"] = df["user_id"].astype(int)
df["sad"] = df["sad"].astype(float)
df["stressed"] = df["stressed"].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)