import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

s0 = s0.rename(columns=lambda c: f"Source4_41_0.{c}")
s1 = s1.rename(columns=lambda c: f"Source4_41_1.{c}")
s2 = s2.rename(columns=lambda c: f"Source4_41_2.{c}")
s3 = s3.rename(columns=lambda c: f"Source4_41_3.{c}")

df = s0.merge(s1, left_on="Source4_41_0.x", right_on="Source4_41_1.x") \
       .merge(s2, left_on="Source4_41_0.x", right_on="Source4_41_2.x") \
       .merge(s3, left_on="Source4_41_0.x", right_on="Source4_41_3.x")

df = df.rename(columns={
    "Source4_41_0.y": "y",
    "Source4_41_0.x": "x",
    "Source4_41_0.label": "label"
})

df = df[["y", "x", "label"]]

df["y"] = df["y"].astype(float)
df["x"] = df["x"].astype(int)

label_map = {v: i for i, v in enumerate(sorted(df["label"].unique()))}
df["label"] = df["label"].map(label_map).astype(int)

df = df.groupby(["y", "x", "label"], as_index=False).size()

df = df[["y", "x", "label"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)