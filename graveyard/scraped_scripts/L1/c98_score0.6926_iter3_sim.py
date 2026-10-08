import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={"right_index": "0_x", "0": "0_y"})
df1_renamed = df1.rename(columns={"0": "0_y"})
df1_renamed["0_x"] = df1_renamed.index.astype(float)

result = pd.concat([df0_renamed[["0_x", "0_y"]], df1_renamed[["0_x", "0_y"]]], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)