import pandas as pd

# Read all source CSVs with index_col=0 to ignore the numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
df10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

# List of all dataframes in order matching target columns
dfs = [df0, df1, df2, df3, df4, df5, df6, df7, df8, df9, df10]

# Rename the second column of each df to match the target schema column names exactly
# The first df0's second column is '301.0' (integer)
# The rest are float columns with names as in target schema
target_float_cols = ['0.016157143', '242.364', '0.1646', '0.4332', '20.3333', '0.0075805085', '6.9', '0.0179', '0.17657143', '0.7268']

# Map dfs to their target column names (except df0 which is '301.0')
# From source info and target schema, assign columns accordingly:
# df0: '301.0'
# df1: '0.016157143'
# df2: '242.364'
# df3: '0.1646'
# df4: '0.4332'
# df5: '20.3333'
# df6: '0.0075805085'
# df7: '6.9'
# df8: '0.0179'
# df9: '0.17657143'
# df10: '0.7268'

# Rename columns accordingly
df0.columns = ['2012-12-05', '301.0']
df1.columns = ['2012-12-05', '0.016157143']
df2.columns = ['2012-12-05', '242.364']
df3.columns = ['2012-12-05', '0.1646']
df4.columns = ['2012-12-05', '0.4332']
df5.columns = ['2012-12-05', '20.3333']
df6.columns = ['2012-12-05', '0.0075805085']
df7.columns = ['2012-12-05', '6.9']
df8.columns = ['2012-12-05', '0.0179']
df9.columns = ['2012-12-05', '0.17657143']
df10.columns = ['2012-12-05', '0.7268']

# Merge all dataframes on '2012-12-05' using outer join to keep all dates
merged = df0
for df in [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10]:
    merged = pd.merge(merged, df, on='2012-12-05', how='outer')

# Convert '2012-12-05' to string type
merged['2012-12-05'] = merged['2012-12-05'].astype(str)

# Convert '301.0' to numeric integer type (nullable Int64)
merged['301.0'] = pd.to_numeric(merged['301.0'], errors='coerce').astype('Int64')

# Convert float columns to numeric float type
float_cols = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']
for col in float_cols:
    merged[col] = pd.to_numeric(merged[col], errors='coerce')

# Group by '2012-12-05' and aggregate:
# sum for '301.0' (integer column)
# mean for all float columns
agg_dict = {'301.0': 'sum'}
for col in float_cols:
    agg_dict[col] = 'mean'

result = merged.groupby('2012-12-05', as_index=False).agg(agg_dict)

# Ensure '301.0' is Int64 after aggregation (sum returns int64 or float64)
result['301.0'] = result['301.0'].astype('Int64')

# Write to CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)