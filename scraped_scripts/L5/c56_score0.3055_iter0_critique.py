import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_56/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert PolityName to string, keep NaN as NaN (do not replace with 'None' string)
df['PolityName'] = df['PolityName'].astype(str).replace({'nan': pd.NA})

# Convert columns to appropriate types
# For numeric columns, convert to numeric with coercion, keep NaN for aggregation
for col in ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Deaths']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# For Initiator and Outcome, extract digits and convert to int, keep NaN if no digits
df['Initiator'] = df['Initiator'].astype(str).str.extract('(\d+)')[0]
df['Initiator'] = pd.to_numeric(df['Initiator'], errors='coerce')

df['Outcome'] = df['Outcome'].astype(str).str.extract('(\d+)')[0]
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce')

# Group by PolityName and WarID
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Initiator': 'max',
    'Outcome': 'max',
    'Deaths': 'sum'
}

# Group and aggregate
df_agg = df.groupby(['PolityName', 'WarID'], dropna=False).agg(agg_dict).reset_index()

# Fill NaN in integer columns with 0 (as in target examples)
for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']:
    df_agg[col] = df_agg[col].fillna(0).astype(int)

# Ensure WarID is int (already int from aggregation)
df_agg['WarID'] = df_agg['WarID'].fillna(0).astype(int)

# Reorder columns as per target schema
df_agg = df_agg[['PolityName', 'WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_56/target_multisource_mcts.csv", index=False)