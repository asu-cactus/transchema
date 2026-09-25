import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Define target columns
target_cols = ['Side', 'WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

# Add missing PolityName column to s1 (which lacks it)
if 'PolityName' not in s1.columns:
    s1['PolityName'] = pd.NA

# Align columns for all sources
def prepare_df(df):
    df = df.copy()
    for c in target_cols:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[target_cols]
    return df

s0 = prepare_df(s0)
s1 = prepare_df(s1)
s2 = prepare_df(s2)
s3 = prepare_df(s3)

# Concatenate all sources (UNION)
df = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Convert columns to appropriate types before aggregation
df['Side'] = df['Side'].astype('string')
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']
for c in int_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')

# PolityName is string, keep as string for now
df['PolityName'] = df['PolityName'].astype('string')

# Define aggregation functions
agg_dict = {
    'StartYear': 'sum',
    'StartMonth': 'sum',
    'StartDay': 'sum',
    'EndYear': 'sum',
    'EndMonth': 'sum',
    'EndDay': 'sum',
    'IsInitiator': 'sum',
    'Outcome': 'sum',
    'Deaths': 'sum',
    'PolityName': 'first'  # take first non-null PolityName per group
}

# Group by keys and aggregate
grouped = df.groupby(['Side', 'WarID', 'PolityID'], dropna=False).agg(agg_dict).reset_index()

# Convert PolityName string to integer codes (factorize)
# NaN will be -1, convert to pd.NA
codes, uniques = pd.factorize(grouped['PolityName'])
codes = pd.Series(codes).replace(-1, pd.NA).astype('Int64')
grouped['PolityName'] = codes

# Convert Side to string type again (groupby may change type)
grouped['Side'] = grouped['Side'].astype('string')

# Ensure all integer columns are Int64 dtype
for c in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
          'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']:
    grouped[c] = pd.to_numeric(grouped[c], errors='coerce').astype('Int64')

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)