import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add missing PolityName column to s1 with NaN
if 'PolityName' not in s1.columns:
    s1['PolityName'] = pd.NA

# Select and reorder columns to match target schema (except PolityName type fix later)
cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# Concatenate all sources
df_all = pd.concat([s0[cols], s1[cols], s2[cols], s3[cols]], ignore_index=True)

# Convert PolityName to string to handle missing and categorical encoding
df_all['PolityName'] = df_all['PolityName'].astype('string')

# Define aggregation functions
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'IsInitiator': 'max',
    'Outcome': 'max',
    'Deaths': 'sum',
    'PolityName': 'first'  # take first non-null PolityName per group
}

# Group by keys
group_cols = ['Side', 'WarID', 'PolityID']

grouped = df_all.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

# PolityName is string in sources but integer in target schema, encode as categorical codes (starting from 0)
# Replace NaN with a placeholder before encoding to avoid -1 codes
grouped['PolityName'] = grouped['PolityName'].fillna('')

# Convert to categorical codes (integers)
grouped['PolityName'] = grouped['PolityName'].astype('category').cat.codes

# Convert columns to integer type with nullable Int64 dtype
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

for c in int_cols:
    grouped[c] = pd.to_numeric(grouped[c], errors='coerce').astype('Int64')

# Ensure Side is string as in target schema
grouped['Side'] = grouped['Side'].astype('string')

# Reorder columns exactly as target schema
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

final_df = grouped[target_cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)