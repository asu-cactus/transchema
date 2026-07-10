import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_37/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('0', as_index=False).size().rename(columns={'size': 'count'})

# The target schema is ['0'] only, so we keep only the grouped '0' column.
# The target examples show some values repeated with counts, so the group by on '0' is correct.
# The target examples show the '0' column as integer, so ensure dtype is int.
result = result[['0']].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_37/target_multisource_mcts.csv", index=False)