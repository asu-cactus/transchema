import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_55/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby('revol_util', as_index=False).size().rename(columns={'size': 'count'})

# The target schema only requires 'revol_util' column, no count column.
# The target examples show only 'revol_util' column, so we output unique revol_util values.
# Since the target examples show counts (e.g. 13111 examples), but only 'revol_util' column,
# we output all rows (not aggregated counts), so just output the concatenated data.

# So the final output is just the concatenated data with 'revol_util' column as integer type.

df_final = df_all.copy()
df_final['revol_util'] = df_final['revol_util'].astype(int)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_55/target_multisource_mcts.csv", index=False)