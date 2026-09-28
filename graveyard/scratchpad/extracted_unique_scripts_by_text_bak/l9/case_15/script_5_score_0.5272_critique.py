import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3, df4, df5], ignore_index=True)

# Group by the leftmost columns of the target schema that are string or integer and unique identifiers
group_by_cols = [
    'State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code',
    'Date', 'Category', 'Defining Parameter', 'Defining Site'
]

agg_df = df_all.groupby(group_by_cols, dropna=False).agg({
    'AQI': 'mean',
    'Number of Sites Reporting': 'sum'
}).reset_index()

# Round AQI to nearest integer and convert to integer type
agg_df['AQI'] = agg_df['AQI'].round().astype('Int64')
agg_df['Number of Sites Reporting'] = agg_df['Number of Sites Reporting'].astype('Int64')

# Reorder columns to match target schema exactly
result = agg_df[[
    'State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code',
    'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting'
]]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)