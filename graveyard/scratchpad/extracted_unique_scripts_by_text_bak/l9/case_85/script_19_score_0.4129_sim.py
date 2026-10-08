import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_85/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_9.csv"
]

agg_dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    agg = df.groupby("prestige").agg(
        admit=("admit", "sum"),
        gre=("gre", "min"),
        gpa=("gpa", "max")
    ).reset_index()
    agg_dfs.append(agg)

union_df = pd.concat(agg_dfs, ignore_index=True)

final_df = union_df.groupby("prestige").agg(
    admit=("admit", "sum"),
    gre=("gre", "min"),
    gpa=("gpa", "max")
).reset_index()

final_df = final_df.astype({"admit": int, "gre": int, "gpa": float, "prestige": int})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_85/target_multisource_mcts.csv", index=False)