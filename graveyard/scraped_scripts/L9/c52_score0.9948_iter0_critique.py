import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

# Ensure column name and type matches target schema
df_all["zip_code"] = df_all["zip_code"].astype(int)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts.csv", index=False)