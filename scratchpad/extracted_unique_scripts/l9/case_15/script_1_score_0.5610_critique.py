import pandas as pd
import numpy as np

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Convert 'Date' to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Convert 'Date' to last day of the month
df['Date'] = df['Date'] + pd.offsets.MonthEnd(0)

# Ensure correct types
df['Year'] = df['Year'].astype(int)
df['Month'] = df['Month'].astype(int)
df['State Code'] = df['State Code'].astype(int)
df['County Code'] = df['County Code'].astype(int)
df['AQI'] = df['AQI'].astype(int)
df['Number of Sites Reporting'] = df['Number of Sites Reporting'].astype(int)

# Group by the leftmost columns except 'Category' and aggregate AQI and Number of Sites Reporting
group_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'Defining Parameter', 'Defining Site']

agg_df = df.groupby(group_cols).agg({
    'AQI': 'max',
    'Number of Sites Reporting': 'sum'
}).reset_index()

# To get 'Category' corresponding to max AQI per group, merge back with original df on group_cols + AQI=max AQI
merged = pd.merge(agg_df, df, on=group_cols + ['AQI'], how='left', suffixes=('', '_orig'))

# Drop duplicates if multiple categories for same max AQI, keep first
merged = merged.drop_duplicates(subset=group_cols + ['AQI'])

# Select columns in target schema order
result = merged[[
    'State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code',
    'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting'
]]

# Convert 'Date' back to string in ISO format (YYYY-MM-DD)
result['Date'] = result['Date'].dt.strftime('%Y-%m-%d')

# Ensure string columns are string type
for col in ['State Name', 'county Name', 'Category', 'Defining Parameter', 'Defining Site']:
    result[col] = result[col].astype(str)

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)