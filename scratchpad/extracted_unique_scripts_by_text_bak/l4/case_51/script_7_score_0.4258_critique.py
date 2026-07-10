import pandas as pd
import numpy as np

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

dfs = [df0, df1, df2, df3]

for i, df in enumerate(dfs):
    # Add PolityName if missing
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    # Consistent dtypes
    df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
    if df['PolityName'].dtype != 'string':
        df['PolityName'] = df['PolityName'].astype('string')
    if df['Side'].dtype != 'string':
        df['Side'] = df['Side'].astype('string')
    for col in ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Encode PolityName as categorical codes (integer)
df_all['PolityName'] = df_all['PolityName'].astype('category').cat.codes.replace(-1, pd.NA).astype('Int64')

# Define group by columns
group_cols = ['Side', 'WarID', 'PolityID']

# Aggregations:
# For integer columns except group_cols and PolityName:
#   Use mean and round to int
# For Deaths: sum
# For PolityName: max (to keep the highest category code)
agg_dict = {
    'StartYear': 'mean',
    'StartMonth': 'mean',
    'StartDay': 'mean',
    'EndYear': 'mean',
    'EndMonth': 'mean',
    'EndDay': 'mean',
    'IsInitiator': 'mean',
    'Outcome': 'mean',
    'Deaths': 'sum',
    'PolityName': 'max'
}

# Perform aggregation
df_grouped = df_all.groupby(group_cols, dropna=False).agg(agg_dict)

# Round mean columns to nearest integer and convert to Int64
for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome']:
    df_grouped[col] = df_grouped[col].round().astype('Int64')

# Deaths already sum, convert to Int64
df_grouped['Deaths'] = df_grouped['Deaths'].astype('Int64')

# Reset index to flatten
df_grouped = df_grouped.reset_index()

# Reorder columns to target schema
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

df_grouped = df_grouped[target_cols]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)