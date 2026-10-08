import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

df_agg = df.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

df_agg["ELIGIBLE_VOTERS"] = df_agg["ELIGIBLE_VOTERS"].astype(int)
df_agg["POLLS"] = df_agg["POLLS"].astype(int)
df_agg["EARLY_VOING"] = df_agg["EARLY_VOING"].astype(int)
df_agg["ABSENTEE"] = df_agg["ABSENTEE"].astype(int)
df_agg["PROVISIONAL"] = df_agg["PROVISIONAL"].astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)