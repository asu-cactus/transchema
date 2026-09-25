import pandas as pd

# Read all source tables with index_col=0 as per hint 22
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_13/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_9.csv",
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Join all dataframes on ['Date', 'Chaine'] iteratively
# Use inner join to keep only matching rows (as target examples suggest)
# pandas will automatically add suffixes _x, _y, _x_37, etc. to overlapping columns

key_cols = ['Date', 'Chaine']

df_merged = dfs[0]
for i in range(1, len(dfs)):
    df_merged = df_merged.merge(dfs[i], on=key_cols, how='inner', suffixes=('_x', '_y') if i == 1 else (None, None))

# After the first merge, suffixes are added automatically by pandas.
# For subsequent merges, pandas adds suffixes like _x_37, _y_38 automatically.

# Write the final dataframe to the target path
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_13/target_multisource_mcts.csv", index=False)