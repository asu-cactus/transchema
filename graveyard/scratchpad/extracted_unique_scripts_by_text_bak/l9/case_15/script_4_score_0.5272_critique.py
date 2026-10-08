import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(path, index_col=0) for path in paths]
unioned = pd.concat(dfs, ignore_index=True)

# Define key columns for grouping
group_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date']

# Aggregate AQI by mean
agg_df = unioned.groupby(group_cols, dropna=False, as_index=False)['AQI'].mean()
agg_df['AQI'] = agg_df['AQI'].round().astype(int)

# Join aggregated AQI back to unioned data to get other columns
# We take the first occurrence of other columns per group
other_cols = ['Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']

# Drop duplicates to get one row per group with other columns
first_occurrence = unioned.drop_duplicates(subset=group_cols)[group_cols + other_cols]

# Merge aggregated AQI with other columns
result = pd.merge(agg_df, first_occurrence, on=group_cols, how='left')

# Ensure correct column order as per target schema
result = result[['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date',
                 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']]

# Cast columns to correct types
result['Year'] = result['Year'].astype(int)
result['Month'] = result['Month'].astype(int)
result['State Code'] = result['State Code'].astype(int)
result['County Code'] = result['County Code'].astype(int)
result['Number of Sites Reporting'] = result['Number of Sites Reporting'].astype(int)

result['Date'] = result['Date'].astype(str)
result['State Name'] = result['State Name'].astype(str)
result['county Name'] = result['county Name'].astype(str)
result['Category'] = result['Category'].astype(str)
result['Defining Parameter'] = result['Defining Parameter'].astype(str)
result['Defining Site'] = result['Defining Site'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)