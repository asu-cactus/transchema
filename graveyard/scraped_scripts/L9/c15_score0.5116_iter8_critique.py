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

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Convert 'Date' to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Extract Year and Month from 'Date' to ensure consistency (in case source Year/Month columns are inconsistent)
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Group by keys excluding 'Date'
group_cols = ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Category', 'Defining Parameter', 'Defining Site']

agg_df = df.groupby(group_cols).agg(
    AQI=('AQI', 'max'),
    Number_of_Sites_Reporting=('Number of Sites Reporting', 'max'),
    Date=('Date', 'max')  # max date in the month group, should be month-end or close
).reset_index()

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'Number_of_Sites_Reporting': 'Number of Sites Reporting'
})

# Convert 'Date' back to string in 'YYYY-MM-DD' format
agg_df['Date'] = agg_df['Date'].dt.strftime('%Y-%m-%d')

# Ensure correct data types
agg_df['Year'] = agg_df['Year'].astype(int)
agg_df['Month'] = agg_df['Month'].astype(int)
agg_df['State Code'] = agg_df['State Code'].astype(int)
agg_df['County Code'] = agg_df['County Code'].astype(int)
agg_df['AQI'] = agg_df['AQI'].astype(int)
agg_df['Number of Sites Reporting'] = agg_df['Number of Sites Reporting'].astype(int)

agg_df['State Name'] = agg_df['State Name'].astype(str)
agg_df['county Name'] = agg_df['county Name'].astype(str)
agg_df['Category'] = agg_df['Category'].astype(str)
agg_df['Defining Parameter'] = agg_df['Defining Parameter'].astype(str)
agg_df['Defining Site'] = agg_df['Defining Site'].astype(str)

# Reorder columns to match target schema
agg_df = agg_df[
    ['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']
]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)