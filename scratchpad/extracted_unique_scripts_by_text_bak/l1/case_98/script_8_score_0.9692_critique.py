import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df = pd.merge(df1, df0, left_index=True, right_on="right_index", how="inner", suffixes=('_x', '_y'))

df = df[["0_x", "0_y"]].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)