import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)

grouped = df.groupby("Date", as_index=False).agg({"NumMosquitos": "mean"})

grouped["ResultDir"] = float('nan')

grouped = grouped[["Date", "ResultDir", "NumMosquitos"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv", index=False)