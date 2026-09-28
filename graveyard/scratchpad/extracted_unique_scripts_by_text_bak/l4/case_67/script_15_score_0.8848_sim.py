import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

agg = df0.groupby("Batsman on strike").agg({
    "overs": "max",
    "runs scored": "sum",
    "extras": "sum"
}).reset_index()

agg["overs"] = agg["overs"].astype(float)
agg["runs scored"] = agg["runs scored"].astype(int)
agg["extras"] = agg["extras"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)