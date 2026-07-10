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

# Convert earliest_cr_line to int, dropping rows with invalid values
df_all['earliest_cr_line'] = pd.to_numeric(df_all['earliest_cr_line'], errors='coerce')
df_all = df_all.dropna(subset=['earliest_cr_line'])
df_all['earliest_cr_line'] = df_all['earliest_cr_line'].astype(int)

# Output all rows as is, no grouping or aggregation
df_all[['earliest_cr_line']].to_csv("autopipeline-benchmarks/github-pipelines/length9_54/target_multisource_mcts.csv", index=False)