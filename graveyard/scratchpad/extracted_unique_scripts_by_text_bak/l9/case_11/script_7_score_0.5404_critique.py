import pandas as pd
from functools import reduce

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

# Inner join all dataframes on '2012-12-05' to keep only dates present in all sources
df_merged = reduce(lambda left, right: pd.merge(left, right, on='2012-12-05', how='inner'), dfs)

# Convert '2012-12-05' to string type (date as string)
df_merged['2012-12-05'] = df_merged['2012-12-05'].astype(str)

# Rename columns to match target schema exactly:
# Each source has schema: ['2012-12-05', <value_column>]
# The value columns have different names in each source, but after merge, pandas will add suffixes if columns have same name.
# Since all sources have the same column name for the value column (the second column), after merge, columns will be suffixed automatically.
# We must rename columns to target schema columns in the correct order.

# The target schema columns are:
target_columns = ['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']

# After merging, the first column is '2012-12-05', the rest are the value columns from each source in order.
# The order of dfs corresponds to the order of target columns after the date column.

# Extract the value columns from each source dataframe to get their original column names (second column name)
value_col_names = [df.columns[0] for df in dfs]  # each df has only one column (excluding index), which is the value column

# After merging, the columns are: '2012-12-05', then each value column with suffixes if needed.
# Because all value columns have the same name in each df (the second column), pandas will suffix them as:
# 'value_col', 'value_col_x', 'value_col_y', etc.
# But since all have the same name, the first is 'value_col', second 'value_col_x', third 'value_col_y', etc.

# Let's get the list of columns excluding '2012-12-05'
value_columns_merged = list(df_merged.columns)
value_columns_merged.remove('2012-12-05')

# Rename these columns to target columns excluding '2012-12-05'
rename_dict = dict(zip(value_columns_merged, target_columns[1:]))

df_merged = df_merged.rename(columns=rename_dict)

# Convert columns to correct types:
# '2012-12-05': string
# '301.0': integer (nullable Int64)
# rest: float

df_merged['301.0'] = pd.to_numeric(df_merged['301.0'], errors='coerce').astype('Int64')

float_cols = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']
for col in float_cols:
    df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').astype(float)

# Reorder columns to match target schema exactly
df_merged = df_merged[target_columns]

# Write to CSV without index
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)