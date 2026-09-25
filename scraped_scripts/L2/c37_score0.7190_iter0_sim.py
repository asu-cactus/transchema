import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_37/training_1.csv", index_col=0)

agg0 = df0.groupby("Date").size().reset_index(name="Count0")
agg1 = df1.groupby("Date")["NumMosquitos"].sum().reset_index()

result = agg1.copy()
result["NumMosquitos"] = result["NumMosquitos"].astype(int)
result = result[["Date", "NumMosquitos"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_37/target_multisource_mcts.csv", index=False)