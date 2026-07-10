import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all source tables (UNION)
df_union = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes
df_union = df_union.astype({
    'State Name': str,
    'county Name': str,
    'State Code': 'Int64',
    'County Code': 'Int64',
    'Date': str,
    'AQI': 'Int64',
    'Category': str,
    'Defining Parameter': str,
    'Defining Site': str,
    'Number of Sites Reporting': 'Int64',
    'Year': 'Int64',
    'Month': 'Int64'
})

# Define group by columns
group_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code']

# Aggregate AQI by max and Number of Sites Reporting by sum
agg_df = df_union.groupby(group_cols, dropna=False).agg({
    'AQI': 'max',
    'Number of Sites Reporting': 'sum'
}).reset_index()

# Join back to get Date, Category, Defining Parameter, Defining Site corresponding to max AQI per group
# Merge on group_cols + AQI
df_joined = pd.merge(
    agg_df,
    df_union,
    on=group_cols + ['AQI'],
    how='left',
    suffixes=('', '_src')
)

# There might be multiple rows per group if multiple rows have same max AQI, pick first occurrence
df_joined = df_joined.drop_duplicates(subset=group_cols, keep='first')

# Select and reorder columns as per target schema
final_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code',
              'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']

df_final = df_joined[final_cols]

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)