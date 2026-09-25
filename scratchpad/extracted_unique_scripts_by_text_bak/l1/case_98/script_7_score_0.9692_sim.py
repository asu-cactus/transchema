import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df = pd.merge(df0, df1, left_on="right_index", right_index=True, how="inner")

df = df.rename(columns={"0_x": "0_x", "0_y": "0_y"})  # no rename needed actually, but keep consistent
df = df.rename(columns={"0": "0_y"})
df = df.rename(columns={"0_x": "0_x"})

df = df[["0_x", "0_y"]].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)