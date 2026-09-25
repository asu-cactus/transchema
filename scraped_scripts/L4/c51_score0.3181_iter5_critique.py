import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add PolityName column to s1 (which lacks it) with NaNs
s1['PolityName'] = pd.NA

# Ensure all sources have the same columns in the same order as target schema (except Side is string, others int)
# Target schema: ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# Select and reorder columns for union
cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# For s1, PolityName is NaN, others as is
s0_sel = s0[cols]
s1_sel = s1[cols]
s2_sel = s2[cols]
s3_sel = s3[cols]

# Concatenate all sources
df_all = pd.concat([s0_sel, s1_sel, s2_sel, s3_sel], ignore_index=True, sort=False)

# Convert columns to appropriate types for aggregation
# Side is string, others integer or float (Deaths can be float)
df_all['Side'] = df_all['Side'].astype(str)

# Convert numeric columns to numeric with coercion
num_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

for c in num_cols:
    df_all[c] = pd.to_numeric(df_all[c], errors='coerce')

# PolityName is string, keep as is for count distinct
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
    'PolityName': lambda x: x.dropna().nunique()
}

# Group by Side, WarID, PolityID
result = df_all.groupby(['Side', 'WarID', 'PolityID'], dropna=False).agg(agg_dict).reset_index()

# PolityName aggregation returns int, convert to Int64
result['PolityName'] = result['PolityName'].astype('Int64')

# Convert other columns to Int64 as per target schema
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

for c in int_cols:
    result[c] = result[c].round().astype('Int64')

# Side is string, keep as is

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)