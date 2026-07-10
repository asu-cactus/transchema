import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_83/training_0.csv", index_col=0)

if "Fare" in df0.columns:
    df0 = df0.rename(columns={"Fare": "price"})

if "date" not in df0.columns:
    df0["date"] = df0.index.astype(str)

df0 = df0[["date", "price"]]

df0["date"] = df0["date"].astype(str)
df0["price"] = df0["price"].astype(float)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length2_83/target_multisource_mcts.csv", index=False)