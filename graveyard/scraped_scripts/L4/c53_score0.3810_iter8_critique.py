import pandas as pd
import numpy as np

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Normalize Side columns to integer (A=1, B=2) if needed
def side_to_int(df):
    if df['Side'].dtype == object:
        df['Side'] = df['Side'].map({'A':1, 'B':2}).fillna(df['Side'])
    df['Side'] = pd.to_numeric(df['Side'], errors='coerce').fillna(0).astype(int)
    return df

s0 = side_to_int(s0)
s1 = side_to_int(s1)
s2 = side_to_int(s2)
s3 = side_to_int(s3)

# For s2, add missing PolityName column with NaN to align schema for later union
if 'PolityName' not in s2.columns:
    s2['PolityName'] = np.nan

# Prepare columns list as per target schema
cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# Prepare function to align columns and types
def prepare_df(df):
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    df = df[cols]
    # Convert numeric columns to appropriate types
    for c in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    # PolityName to string, keep NaN as is (do not fill with empty string here)
    df['PolityName'] = df['PolityName'].astype(object)
    # For integer columns, fill NaN with 0 and convert to int
    for c in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']:
        df[c] = df[c].fillna(0).astype(int)
    # Deaths can be float, fill NaN with 0 and convert to int
    df['Deaths'] = df['Deaths'].fillna(0).astype(int)
    # PolityName: replace NaN with None (keep as None for join)
    df['PolityName'] = df['PolityName'].where(df['PolityName'].notnull(), None)
    return df

s0p = prepare_df(s0)
s1p = prepare_df(s1)
s2p = prepare_df(s2)
s3p = prepare_df(s3)

# Join s2p with s0p on keys: WarID, PolityID, Side, IsInitiator, Outcome
join_keys = ['WarID', 'PolityID', 'Side', 'IsInitiator', 'Outcome']

# Perform inner join to get PolityName from s0p for s2p rows
joined_2_0 = pd.merge(
    s2p,
    s0p[['PolityName'] + join_keys].drop_duplicates(),
    on=join_keys,
    how='left',
    suffixes=('_s2', '_s0')
)

# After join, fill PolityName from s0p if missing in s2p
joined_2_0['PolityName'] = joined_2_0['PolityName_s2']
missing_polityname_mask = joined_2_0['PolityName'].isnull()
joined_2_0.loc[missing_polityname_mask, 'PolityName'] = joined_2_0.loc[missing_polityname_mask, 'PolityName_s0']

# Drop helper columns
joined_2_0 = joined_2_0.drop(columns=['PolityName_s2', 'PolityName_s0'])

# Reorder columns to target schema
joined_2_0 = joined_2_0[cols]

# Now union joined_2_0 with s1p and s3p (all have PolityName)
union_df = pd.concat([joined_2_0, s1p, s3p], ignore_index=True)

# Group by leftmost unique keys: PolityName, WarID, PolityID
group_cols = ['PolityName', 'WarID', 'PolityID']

# Aggregations:
# For start dates: min
# For end dates: max
# For Side, IsInitiator, Outcome: max (assuming these are categorical flags)
# For Deaths: sum

agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Side': 'max',
    'IsInitiator': 'max',
    'Outcome': 'max',
    'Deaths': 'sum'
}

final_df = union_df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# PolityName is string, ensure no NaN (replace None with empty string)
final_df['PolityName'] = final_df['PolityName'].fillna('')

# Ensure all columns have correct types as per target schema
final_df['WarID'] = final_df['WarID'].astype(int)
final_df['PolityID'] = final_df['PolityID'].astype(int)
final_df['StartYear'] = final_df['StartYear'].astype(int)
final_df['StartMonth'] = final_df['StartMonth'].astype(int)
final_df['StartDay'] = final_df['StartDay'].astype(int)
final_df['EndYear'] = final_df['EndYear'].astype(int)
final_df['EndMonth'] = final_df['EndMonth'].astype(int)
final_df['EndDay'] = final_df['EndDay'].astype(int)
final_df['Side'] = final_df['Side'].astype(int)
final_df['IsInitiator'] = final_df['IsInitiator'].astype(int)
final_df['Outcome'] = final_df['Outcome'].astype(int)
final_df['Deaths'] = final_df['Deaths'].astype(int)

# Reorder columns exactly as target schema
final_df = final_df[cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)