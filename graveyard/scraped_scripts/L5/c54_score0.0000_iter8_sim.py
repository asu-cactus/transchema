import pandas as pd
import numpy as np

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_54/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby("msno")["date_diff"].agg([
    ("date_diff", "mean"),
    ("date_diff-min", "min"),
    ("date_diff-max", "max"),
    ("date_diff-median", "median"),
    ("date_diff-std", "std")
]).reset_index()

agg["date_diff-min"] = agg["date_diff-min"].astype(int)
agg["date_diff-max"] = agg["date_diff-max"].astype(int)
agg["date_diff-median"] = agg["date_diff-median"].astype(int)
agg["date_diff-std"] = agg["date_diff-std"].fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_54/target_multisource_mcts.csv", index=False)