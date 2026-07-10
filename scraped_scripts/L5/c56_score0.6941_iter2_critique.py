import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_56/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_4.csv"
]

# Read all sources
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Convert WarID to Int64 for joining
for i in range(len(dfs)):
    dfs[i]['WarID'] = pd.to_numeric(dfs[i]['WarID'], errors='coerce').astype('Int64')

# Join all sources on WarID (inner join)
df_joined = dfs[0]
for i in range(1, len(dfs)):
    df_joined = df_joined.merge(dfs[i], on='WarID', suffixes=('', f'_{i}'), how='inner')

# Coalesce PolityName columns from all sources (take first non-null)
polity_cols = ['PolityName'] + [f'PolityName_{i}' for i in range(1, len(dfs))]
df_joined['PolityName'] = df_joined[polity_cols].bfill(axis=1).iloc[:, 0]

# For other columns, take from the first source columns (they should be consistent)
# But some columns exist with suffixes, so we pick from first source columns only
# Columns to keep: PolityName (coalesced), WarID, StartYear, StartMonth, StartDay, EndYear, EndMonth, EndDay, Initiator, Outcome, Deaths

# Extract columns from first source (no suffix)
cols = ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']

df_final = df_joined[['PolityName'] + cols].copy()

# Convert numeric columns properly, fill NaNs in month/day with 0
for col in ['StartYear', 'EndYear']:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').astype('Int64')

for col in ['StartMonth', 'StartDay', 'EndMonth', 'EndDay']:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0).astype(int)

# Map Initiator from string to integer codes
initiator_map = {v: i+1 for i, v in enumerate(sorted(df_final['Initiator'].dropna().unique()))}
df_final['Initiator'] = df_final['Initiator'].map(initiator_map).astype('Int64')

df_final['Outcome'] = pd.to_numeric(df_final['Outcome'], errors='coerce').astype('Int64')

# Deaths: convert to numeric, fill NaN with 0 for aggregation
df_final['Deaths'] = pd.to_numeric(df_final['Deaths'], errors='coerce').fillna(0).astype(int)

# Group by PolityName and WarID, aggregate as per plan
agg_dict = {
    'StartYear': 'max',
    'StartMonth': 'max',
    'StartDay': 'max',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Initiator': 'max',
    'Outcome': 'max',
    'Deaths': 'sum'
}

df_grouped = df_final.groupby(['PolityName', 'WarID'], dropna=False, as_index=False).agg(agg_dict)

# Ensure column order matches target schema
df_grouped = df_grouped[['PolityName', 'WarID', 'StartYear', 'StartMonth', 'StartDay',
                         'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_56/target_multisource_mcts.csv", index=False)