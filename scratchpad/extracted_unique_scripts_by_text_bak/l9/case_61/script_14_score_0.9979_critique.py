import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)
# Drop duplicate rows based on 'start' column to match target unique keys
union_df = union_df.drop_duplicates(subset=['start'])
union_df['betterliving'] = union_df['betterliving'].astype(int)
union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_61/target_multisource_mcts.csv", index=False)