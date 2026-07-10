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

group_cols = ['State Name', 'county Name', 'State Code', 'County Code', 'Category', 'Defining Parameter', 'Defining Site', 'Year', 'Month', 'Date']
agg_df = df.groupby(group_cols).agg(
    AQI_min=('AQI', 'min'),
    AQI_max=('AQI', 'max'),
    Number_of_Sites_Reporting=('Defining Site', 'count')
).reset_index()

# According to target schema, AQI is a single integer column.
# The example shows AQI values like 69, 68, 93 (single values).
# The partial plan aggregates MIN and MAX AQI, but target has one AQI column.
# We must decide which AQI to keep.
# Since the source has AQI per Defining Site, and we count Defining Site,
# likely the target AQI is the MAX AQI per group (worst AQI).
# So we keep AQI_max as AQI.

agg_df.rename(columns={
    'AQI_max': 'AQI',
    'Number_of_Sites_Reporting': 'Number of Sites Reporting'
}, inplace=True)

# Ensure correct dtypes
agg_df['Year'] = agg_df['Year'].astype(int)
agg_df['Month'] = agg_df['Month'].astype(int)
agg_df['State Code'] = agg_df['State Code'].astype(int)
agg_df['County Code'] = agg_df['County Code'].astype(int)
agg_df['AQI'] = agg_df['AQI'].astype(int)
agg_df['Date'] = agg_df['Date'].astype(str)
agg_df['State Name'] = agg_df['State Name'].astype(str)
agg_df['county Name'] = agg_df['county Name'].astype(str)
agg_df['Category'] = agg_df['Category'].astype(str)
agg_df['Defining Parameter'] = agg_df['Defining Parameter'].astype(str)
agg_df['Defining Site'] = agg_df['Defining Site'].astype(str)
agg_df['Number of Sites Reporting'] = agg_df['Number of Sites Reporting'].astype(int)

# Reorder columns to match target schema
agg_df = agg_df[['State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 'Number of Sites Reporting']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts.csv", index=False)