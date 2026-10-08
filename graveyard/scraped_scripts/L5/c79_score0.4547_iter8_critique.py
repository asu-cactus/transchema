import pandas as pd

# Read all source CSVs with index_col=0
paths = [
    "autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Fill NaN in Deaths with 0 for sum aggregation
df['Deaths'] = df['Deaths'].fillna(0)

# Group by Initiator and WarID
agg_df = df.groupby(['Initiator', 'WarID'], dropna=False).agg({
    'PolityName': 'count',          # count of PolityName as integer
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'min',
    'EndMonth': 'min',
    'EndDay': 'min',
    'Outcome': 'max',
    'Deaths': 'sum'
}).reset_index()

# Rename PolityName count to PolityName to match target schema
agg_df = agg_df.rename(columns={'PolityName': 'PolityName'})

# Convert all columns to int where possible, fill NaN with 0 before conversion
int_cols = ['PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']
for col in int_cols:
    agg_df[col] = agg_df[col].fillna(0).astype(int)

# Ensure Initiator is string
agg_df['Initiator'] = agg_df['Initiator'].astype(str)

# Reorder columns to match target schema exactly
agg_df = agg_df[['Initiator', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']]

# Write output CSV
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)