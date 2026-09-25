import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

agg_df = df0.groupby("Batsman on strike").agg({
    "overs": "max",
    "runs scored": "sum",
    "extras": "sum"
}).reset_index()

agg_df["overs"] = agg_df["overs"].astype(float)
agg_df["runs scored"] = agg_df["runs scored"].astype(int)
agg_df["extras"] = agg_df["extras"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)