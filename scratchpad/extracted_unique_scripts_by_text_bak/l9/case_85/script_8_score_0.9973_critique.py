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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all source tables (UNION)
final_df = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes as per target schema
final_df = final_df.astype({"admit": int, "gre": int, "gpa": float, "prestige": int})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_85/target_multisource_mcts.csv", index=False)