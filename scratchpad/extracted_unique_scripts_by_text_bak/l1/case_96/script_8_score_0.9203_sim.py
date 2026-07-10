import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)

result = df0.groupby("Publisher", dropna=False).agg({"name": "count"}).reset_index()
result = result.rename(columns={"name": "Publisher"})
result = result[["Publisher"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)