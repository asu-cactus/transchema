import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_all['earliest_cr_line'] = pd.to_numeric(df_all['earliest_cr_line'], errors='coerce').dropna().astype(int)

result = df_all.groupby('earliest_cr_line', as_index=False).size().rename(columns={'size':'earliest_cr_line_count'})

# The target schema only requires 'earliest_cr_line' column, no aggregation count column.
# The target examples show just the distinct earliest_cr_line values, so we output unique values.

result = df_all[['earliest_cr_line']].drop_duplicates().sort_values('earliest_cr_line').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_54/target_multisource_mcts.csv", index=False)