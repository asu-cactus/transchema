import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df0 = df0.rename(columns={"right_index": "0_x", "0": "0_y"})
df1 = df1.rename(columns={"0": "0_y"})

df0["0_x"] = df0["0_x"].astype(float)
df0["0_y"] = df0["0_y"].astype(float)
df1["0_y"] = df1["0_y"].astype(float)

df1["0_x"] = pd.NA

result = pd.concat([df0, df1], ignore_index=True, sort=False)
result = result[["0_x", "0_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)