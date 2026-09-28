import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_67/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_67/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_67/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

grouped = df.groupby("Batsman on strike", as_index=False).agg({
    "overs": "max",
    "runs scored": "sum",
    "extras": "sum"
})

grouped["overs"] = grouped["overs"].astype(float)
grouped["runs scored"] = grouped["runs scored"].astype(int)
grouped["extras"] = grouped["extras"].astype(int)

grouped = grouped[["Batsman on strike", "overs", "runs scored", "extras"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)