import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_9.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby("PRECINCT", as_index=False).agg({
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