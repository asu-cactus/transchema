import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

cols = ['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 
        'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']

df = df[cols]

# Convert Outcome and WarID to numeric (integer)
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')

# PolityName and Initiator are strings in source, convert to integer codes
df['PolityName'] = pd.factorize(df['PolityName'])[0]
df['Initiator'] = pd.factorize(df['Initiator'])[0]

# Convert other year/month/day columns to numeric integer
for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Deaths to numeric float first (some NaNs), then sum aggregation later
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce')

# Group by all columns except Deaths, aggregate Deaths by sum
group_cols = ['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 
              'EndYear', 'EndMonth', 'EndDay', 'Initiator']

df_agg = df.groupby(group_cols, dropna=False, as_index=False)['Deaths'].sum()

# Convert Deaths to Int64 (sum of floats, NaNs become 0)
df_agg['Deaths'] = df_agg['Deaths'].fillna(0).astype('Int64')

# Ensure all other columns are Int64
for col in group_cols:
    df_agg[col] = df_agg[col].astype('Int64')

# Reorder columns to match target schema
df_agg = df_agg[cols]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)