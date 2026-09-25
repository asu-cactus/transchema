import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

result = df.groupby("WarNum", as_index=False).agg({"TransTo": lambda x: 0})

result["WarNum"] = result["WarNum"].astype(int)
result["TransTo"] = result["TransTo"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)