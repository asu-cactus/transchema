import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_15/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Ensure correct types
df['State Name'] = df['State Name'].astype(str)
df['county Name'] = df['county Name'].astype(str)
df['Date'] = df['Date'].astype(str)
df['Category'] = df['Category'].astype(str)
df['Defining Parameter'] = df['Defining Parameter'].astype(str)
df['Defining Site'] = df['Defining Site'].astype(str)

df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
df['Month'] = pd.to_numeric(df['Month'], errors='coerce').astype('Int64')
df['State Code'] = pd.to_numeric(df['State Code'], errors='coerce').astype('Int64')
df['County Code'] = pd.to_numeric(df['County Code'], errors='coerce').astype('Int64')
df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce').astype('Int64')
df['Number of Sites Reporting'] = pd.to_numeric(df['Number of Sites Reporting'], errors='coerce').astype('Int64')

# Reorder columns to match target schema
df = df[['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']]

# Group by key columns and aggregate
group_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date']

agg_dict = {
    'AQI': 'mean',
    'Category': 'first',
    'Defining Parameter': 'first',
    'Defining Site': 'first',
    'Number of Sites Reporting': 'sum'
}

df_agg = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# AQI is float after mean, convert to Int64 to match target type
df_agg['AQI'] = df_agg['AQI'].round().astype('Int64')

# Ensure Number of Sites Reporting is Int64
df_agg['Number of Sites Reporting'] = df_agg['Number of Sites Reporting'].astype('Int64')

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)