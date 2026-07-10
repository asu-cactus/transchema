import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

agg = df0.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

agg["PRECINCT"] = agg["PRECINCT"].astype(str)
agg["ELIGIBLE_VOTERS"] = agg["ELIGIBLE_VOTERS"].astype(int)
agg["POLLS"] = agg["POLLS"].astype(int)
agg["EARLY_VOING"] = agg["EARLY_VOING"].astype(int)
agg["ABSENTEE"] = agg["ABSENTEE"].astype(int)
agg["PROVISIONAL"] = agg["PROVISIONAL"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)