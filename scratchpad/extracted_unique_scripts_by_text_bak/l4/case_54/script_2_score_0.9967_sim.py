import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

result = df.groupby("WhereFought", as_index=False)["WarNum"].count()
result.columns = ["WhereFought", "WarNum"]
result["WhereFought"] = result["WhereFought"].astype(int)
result["WarNum"] = result["WarNum"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)