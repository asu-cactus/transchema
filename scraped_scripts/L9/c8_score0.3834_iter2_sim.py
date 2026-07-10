import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_8/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby("prestige").agg(
    admit=("admit", "count"),
    gre=("gre", "mean"),
    gpa=("gpa", "mean")
).reset_index()

agg = agg.rename(columns={"prestige": "prestige", "admit": "admit", "gre": "gre", "gpa": "gpa"})

agg["admit"] = agg["admit"].astype(int)
agg["gre"] = agg["gre"].round().astype(int)
agg["gpa"] = agg["gpa"].astype(float)
agg["prestige"] = agg["prestige"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length9_8/target_multisource_mcts.csv", index=False)