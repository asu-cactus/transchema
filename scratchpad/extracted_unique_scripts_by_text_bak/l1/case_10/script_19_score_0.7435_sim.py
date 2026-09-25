import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

df = df.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

df["PRECINCT"] = df["PRECINCT"].astype(str)
df["ELIGIBLE_VOTERS"] = df["ELIGIBLE_VOTERS"].astype(int)
df["POLLS"] = df["POLLS"].astype(int)
df["EARLY_VOING"] = df["EARLY_VOING"].astype(int)
df["ABSENTEE"] = df["ABSENTEE"].astype(int)
df["PROVISIONAL"] = df["PROVISIONAL"].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)