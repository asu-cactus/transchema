import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_46/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('purpose', as_index=False).size().rename(columns={'size': 'purpose'})

# The target schema is ['purpose': integer], and target examples show purpose values as integers.
# The groupby size counts occurrences per purpose, but target schema only has 'purpose' column.
# The target examples show 'purpose' column with integer values, which match the grouped keys.
# So the final output is the grouped keys (unique purposes), not counts.
# Therefore, we only keep the grouped keys (unique purposes).

result = df_all[['purpose']].drop_duplicates().sort_values('purpose').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_46/target_multisource_mcts.csv", index=False)