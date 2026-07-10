import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df = pd.concat([s0, s1, s2, s3], ignore_index=True)

df = df[["y", "x", "label"]]

df["y"] = df["y"].astype(float)
df["x"] = df["x"].astype(int)

label_map = {v: i for i, v in enumerate(sorted(df["label"].unique()))}
df["label"] = df["label"].map(label_map).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)