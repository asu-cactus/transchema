import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv", index_col=0)

# Join s0 and s1 on WarID (inner join)
joined = pd.merge(s0, s1, on="WarID", suffixes=('_0', '_1'))

# Join with s2
joined = pd.merge(joined, s2, on="WarID", suffixes=('', '_2'))

# Join with s3
joined = pd.merge(joined, s3, on="WarID", suffixes=('', '_3'))

# Join with s4
joined = pd.merge(joined, s4, on="WarID", suffixes=('', '_4'))

# After joins, columns from multiple sources exist.
# We will select columns from s0 (suffix _0) for most fields, except Initiator and WarID from s0 (or any, they should be same).
# For PolityName, factorize the s0 PolityName_0 column to convert string to int.
# For other columns, take from s0 columns (_0 suffix).
# If any columns missing suffix, take from s0 columns without suffix (due to merge suffixes).

df = pd.DataFrame()

# Initiator from s0
df['Initiator'] = joined['Initiator_0'].astype(str)

# WarID from joined (no suffix)
df['WarID'] = pd.to_numeric(joined['WarID'], errors='coerce').fillna(0).astype(int)

# PolityName factorized from s0
polity_codes, _ = pd.factorize(joined['PolityName_0'])
df['PolityName'] = polity_codes.astype(int)

# Columns to aggregate
cols = ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']

for col in cols:
    # Convert to numeric, fill NaN with 0, convert to int
    df[col] = pd.to_numeric(joined[f'{col}_0'], errors='coerce').fillna(0).astype(int)

# Group by Initiator and WarID, aggregate other columns by max
df = df.groupby(['Initiator', 'WarID'], as_index=False).agg({
    'PolityName': 'max',
    'StartYear': 'max',
    'StartMonth': 'max',
    'StartDay': 'max',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Outcome': 'max',
    'Deaths': 'max'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)