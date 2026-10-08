import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv", index_col=0)

union_result = pd.concat([s1, s2, s3, s4], ignore_index=True)

joined = pd.merge(s0, union_result, on="WarID", suffixes=('_0', '_u'))

# After join, columns from s0 and union_result exist with suffixes.
# We want to produce the target schema:
# ['Initiator': string, 'WarID': int, 'PolityName': int, 'StartYear': int, 'StartMonth': int, 'StartDay': int,
#  'EndYear': int, 'EndMonth': int, 'EndDay': int, 'Outcome': int, 'Deaths': int]

# The target examples show Initiator is string, WarID int, PolityName int (though source has string),
# and other columns int.

# We must choose columns from either s0 or union_result for each field.
# Since s0 and union_result have same schema, but union_result columns have suffix '_u', s0 columns '_0'.

# For Initiator, target examples show string, source columns are string, so take from s0 (or union_result).
# For PolityName, source is string, target expects int. We must convert PolityName to int.
# Since PolityName is string in source, we can convert it by factorizing (assigning integer codes).
# For other columns, convert to int, filling NaN with 0.

# We will take Initiator from s0 (or union_result, they should be same after join on WarID).
# For other columns, take from s0 (suffix '_0').

df = pd.DataFrame()
df['Initiator'] = joined['Initiator_0'].astype(str)

df['WarID'] = pd.to_numeric(joined['WarID'], errors='coerce').fillna(0).astype(int)

# Convert PolityName string to int codes
polity_codes, uniques = pd.factorize(joined['PolityName_0'])
df['PolityName'] = polity_codes.astype(int)

for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']:
    df[col] = pd.to_numeric(joined[f'{col}_0'], errors='coerce').fillna(0).astype(int)

# Group by Initiator as per plan
df = df.groupby('Initiator', as_index=False).agg({
    'WarID': 'max',
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