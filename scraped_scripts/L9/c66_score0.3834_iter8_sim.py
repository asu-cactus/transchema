import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

agg_df = df_all.groupby("prestige").agg({
    "admit": "sum",
    "gre": "mean",
    "gpa": "min"
}).reset_index()

agg_df["admit"] = agg_df["admit"].astype(int)
agg_df["gre"] = agg_df["gre"].round().astype(int)
agg_df["gpa"] = agg_df["gpa"].astype(float)
agg_df["prestige"] = agg_df["prestige"].astype(int)

agg_df = agg_df[["admit", "gre", "gpa", "prestige"]]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)