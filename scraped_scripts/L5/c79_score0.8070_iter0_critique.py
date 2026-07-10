import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Convert columns to appropriate types
# PolityName is string in source, but target expects integer (count distinct)
# Other columns to numeric, coercing errors to NaN
for col in ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Initiator as string
df['Initiator'] = df['Initiator'].astype(str)

# PolityName as string (for count distinct)
df['PolityName'] = df['PolityName'].astype(str)

# Group by Initiator
grouped = df.groupby('Initiator', dropna=False, as_index=False).agg({
    'WarID': 'sum',
    'PolityName': pd.Series.nunique,
    'StartYear': 'sum',
    'StartMonth': 'sum',
    'StartDay': 'sum',
    'EndYear': 'sum',
    'EndMonth': 'sum',
    'EndDay': 'sum',
    'Outcome': 'sum',
    'Deaths': 'sum'
})

# Rename PolityName nunique to integer type
grouped['PolityName'] = grouped['PolityName'].astype('Int64')

# Convert other columns to Int64 (nullable integer) to match target schema
for col in ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']:
    grouped[col] = grouped[col].astype('Int64')

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)